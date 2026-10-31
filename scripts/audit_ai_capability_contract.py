#!/usr/bin/env python3
"""Audit the revised dataset, experiment lineage, event clocks, and ledgers."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from quantfin.cross_market.common import load_research_config, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_ai_capability_research.yaml")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--run-id", action="append", default=[], help="May be repeated for screening/confirmation/final runs.")
    args = parser.parse_args()
    config = load_research_config(args.config)
    dataset = root_path(config["outputs"]["processed_root"]) / args.dataset_id
    required = [dataset / "manifest.json", dataset / "panel.parquet", dataset / "feature_dictionary.csv",
                dataset / "capability_event_mapping.csv"]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing revised dataset evidence:\n" + "\n".join(missing))

    dictionary = pd.read_csv(dataset / "feature_dictionary.csv")
    panel = pd.read_parquet(dataset / "panel.parquet")
    events = pd.read_csv(dataset / "capability_event_mapping.csv")
    needed_event_columns = {
        "public_at_utc", "tradable_date", "first_us_reaction_session",
        "first_us_close_utc", "first_nse_after_us_reaction_date",
    }
    absent = sorted(needed_event_columns.difference(events.columns))
    if absent:
        raise ValueError(f"Capability panel predates corrected event-clock mapping: {absent}")
    events["public_at_utc"] = pd.to_datetime(events["public_at_utc"], utc=True)
    events["first_us_close_utc"] = pd.to_datetime(events["first_us_close_utc"], utc=True)
    events["tradable_date"] = pd.to_datetime(events["tradable_date"])
    events["first_nse_after_us_reaction_date"] = pd.to_datetime(events["first_nse_after_us_reaction_date"])

    checks: list[dict[str, object]] = []
    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "passed": bool(condition), "detail": detail})

    check("panel_unique_date_asset", not panel.duplicated(["decision_date", "asset"]).any())
    check("target_complete", panel["target_oc_return"].notna().all())
    check("feature_dictionary_unique", dictionary["feature"].is_unique)
    check("feature_sets_assigned", dictionary["feature_sets"].fillna("").ne("").all())
    check("event_us_close_after_publication", events["first_us_close_utc"].dropna().gt(
        events.loc[events["first_us_close_utc"].notna(), "public_at_utc"]).all())
    check("nse_after_us_reaction_order", events["first_nse_after_us_reaction_date"].dropna().ge(
        events.loc[events["first_nse_after_us_reaction_date"].notna(), "first_us_reaction_session"]).all())

    run_records = []
    runs_root = root_path(config["outputs"]["runs_root"])
    for run_id in progress(args.run_id, description="Auditing experiment runs", unit="run"):
        run = runs_root / run_id
        manifest_path = run / "manifest.json"
        if not manifest_path.is_file():
            check(f"run_exists:{run_id}", False, str(manifest_path))
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        leaderboard = pd.read_csv(run / "leaderboard.csv")
        configurations = json.loads((run / "configurations.json").read_text(encoding="utf-8"))
        check(f"run_complete:{run_id}", manifest.get("status") == "complete")
        check(f"run_dataset_parent:{run_id}", manifest.get("dataset_id") == args.dataset_id)
        check(f"run_configuration_count:{run_id}", len(leaderboard) == len(configurations),
              {"leaderboard": len(leaderboard), "configurations": len(configurations)})
        ledger_path = run / "strategy_ledgers.parquet"
        if ledger_path.is_file():
            ledger = pd.read_parquet(ledger_path)
            expected_net = ledger["gross_return"] - ledger["trading_cost"]
            check(f"ledger_net_reconciles:{run_id}", np.allclose(ledger["net_return"], expected_net, equal_nan=True))
            check(f"ledger_turnover_nonnegative:{run_id}", ledger["turnover"].ge(0).all())
        run_records.append({
            "run_id": run_id, "stage": manifest.get("stage"), "configuration_count": len(leaderboard),
            "families": leaderboard.groupby("family").size().to_dict(),
            "selected_config_id": manifest.get("selected_config_id"),
        })

    feature_sets = {
        name: int(dictionary["feature_sets"].fillna("").str.split("|").map(lambda values: name in values).sum())
        for name in config["feature_sets"]
    }
    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if all(row["passed"] for row in checks) else "fail",
        "dataset_id": args.dataset_id,
        "dataset_manifest_sha256": sha256_file(dataset / "manifest.json"),
        "config_sha256": sha256_file(root_path(args.config)),
        "rows": len(panel), "decision_dates": int(pd.to_datetime(panel["decision_date"]).nunique()),
        "assets": sorted(panel["asset"].unique().tolist()),
        "feature_count_by_set": feature_sets,
        "current_vintage_fallback_feature_count": int(dictionary["current_vintage_fallback"].fillna(False).astype(bool).sum()),
        "event_count": len(events), "runs": run_records, "checks": checks,
    }
    identity = stable_object_hash({"dataset": report["dataset_manifest_sha256"], "config": report["config_sha256"],
                                   "runs": args.run_id, "checks": checks})[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = root_path("artifacts/cross_market_ai_capability/audits") / f"contract_{stamp}_{identity}"
    output.mkdir(parents=True, exist_ok=False)
    atomic_json_dump(report, output / "contract_audit.json")
    print(json.dumps({"status": report["status"], "checks": len(checks), "output": str(output)}, indent=2))
    if report["status"] != "pass":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
