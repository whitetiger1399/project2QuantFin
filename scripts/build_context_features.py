"""As-of join release-aware macro/VIX context into a new F3 feature dataset."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash
from quantfin.research_extension import load_feature_dataset, read_yaml


ROOT = Path(__file__).resolve().parents[1]


def release_series(path: Path, name: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    required = {"date", "realtime_start", "value"}
    if not required.issubset(raw.columns):
        raise ValueError(f"{path.name} missing columns {sorted(required - set(raw.columns))}")
    raw["observation_date"] = pd.to_datetime(raw["date"])
    raw["available_session"] = pd.to_datetime(raw["realtime_start"])
    raw["value"] = pd.to_numeric(raw["value"].replace(".", np.nan), errors="coerce")
    raw = raw.dropna(subset=["available_session", "observation_date", "value"])
    # At each release/vintage date retain the latest observation then carry it
    # forward through an as-of join. This does not use today's revised history.
    updates = raw.sort_values(["available_session", "observation_date"]).groupby("available_session", as_index=False).tail(1)
    return updates[["available_session", "observation_date", "value"]].rename(columns={"value": name})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/research_extension_2026-10-21.yaml")
    parser.add_argument("--context-snapshot", required=True, help="Snapshot ID under data/raw/fred_alfred")
    args = parser.parse_args()
    config_path = ROOT / args.config
    config = read_yaml(config_path)
    frame, source_manifest, _, source_dir = load_feature_dataset(ROOT, config["feature_dataset_id"], config["feature_set"])
    context_dir = ROOT / "data/raw/fred_alfred" / args.context_snapshot
    context_manifest_path = context_dir / "manifest.json"
    context_manifest = json.loads(context_manifest_path.read_text(encoding="utf-8"))
    if context_manifest.get("status") != "complete":
        raise ValueError("Context snapshot is not complete")
    enriched = frame.sort_values("signal_session").copy()
    new_columns = []
    for series_id, description in config["external_data"]["fred_series"].items():
        updates = release_series(context_dir / f"{series_id}.csv", description)
        enriched = pd.merge_asof(enriched.sort_values("signal_session"), updates.sort_values("available_session"), left_on="signal_session", right_on="available_session", direction="backward", allow_exact_matches=True)
        if (enriched["available_session"].dropna() > enriched.loc[enriched["available_session"].notna(), "signal_session"]).any():
            raise AssertionError(f"Availability violation for {series_id}")
        enriched[f"{description}_age_days"] = (enriched["signal_session"] - enriched["observation_date"]).dt.days
        enriched[f"{description}_change_5"] = enriched[description].diff(5)
        enriched[f"{description}_change_20"] = enriched[description].diff(20)
        new_columns.extend([description, f"{description}_age_days", f"{description}_change_5", f"{description}_change_20"])
        enriched = enriched.drop(columns=["available_session", "observation_date"])
    vix = context_dir / "vix_history.csv"
    if vix.is_file():
        raw_vix = pd.read_csv(vix)
        date_column = next((x for x in raw_vix.columns if x.lower() in {"date", "trade date"}), None)
        close_column = next((x for x in raw_vix.columns if x.lower() in {"close", "vix close"}), None)
        if not date_column or not close_column:
            raise ValueError("VIX CSV needs Date and Close columns")
        vix_frame = pd.DataFrame({"signal_session": pd.to_datetime(raw_vix[date_column]), "vix_close": pd.to_numeric(raw_vix[close_column], errors="coerce")}).dropna().sort_values("signal_session")
        enriched = enriched.merge(vix_frame, on="signal_session", how="left", validate="one_to_one")
        enriched["vix_change_5"] = enriched["vix_close"].pct_change(5, fill_method=None)
        enriched["vix_zscore_60"] = (enriched["vix_close"] - enriched["vix_close"].rolling(60).mean()) / enriched["vix_close"].rolling(60).std()
        new_columns.extend(["vix_close", "vix_change_5", "vix_zscore_60"])
    f3 = list(source_manifest["feature_sets"][config["feature_set"]]) + new_columns
    identity = {"source_feature_manifest_sha256": sha256_file(source_dir / "manifest.json"), "context_manifest_sha256": sha256_file(context_manifest_path), "config_sha256": sha256_file(config_path), "new_columns": new_columns}
    dataset_id = f"features_context_{args.context_snapshot}_{stable_object_hash(identity)[:10]}"
    output = ROOT / "data/processed" / dataset_id
    output.mkdir(parents=True, exist_ok=False)
    parquet = output / "features.parquet"
    atomic_parquet_dump(enriched, parquet)
    manifest = {
        "schema_version": 1,
        "dataset_id": dataset_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_feature_dataset_id": source_manifest["dataset_id"],
        "context_snapshot_id": args.context_snapshot,
        "identity": identity,
        "rows": len(enriched),
        "feature_sets": {**source_manifest["feature_sets"], "F3": f3},
        "feature_counts": {**source_manifest["feature_counts"], "F3": len(f3)},
        "feature_groups": {**source_manifest["feature_groups"], "macro_context": new_columns},
        "file": {"path": parquet.name, "sha256": sha256_file(parquet)},
        "timing_contract": "Every FRED value is joined using realtime_start <= signal_session; VIX close is available at the configured after-close decision time.",
    }
    atomic_json_dump(manifest, output / "manifest.json")
    print(json.dumps({"dataset_id": dataset_id, "features_F3": len(f3), "output_directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()

