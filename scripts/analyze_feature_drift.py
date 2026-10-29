"""Aggregate saved out-of-sample feature diagnostics into year/group drift tables."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from quantfin.io import atomic_json_dump, stable_object_hash
from quantfin.research_extension import load_feature_dataset


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--feature-dataset-id", default="features_yahoo_20261020T055638Z_799f619a4f")
    parser.add_argument("--feature-set", default="F2")
    parser.add_argument("--output-root", default="artifacts/research/feature_drift")
    args = parser.parse_args()
    run_dir = ROOT / "artifacts/runs" / args.run_id
    files = sorted(run_dir.glob("checkpoints/*/*_features.parquet"))
    if not files:
        raise FileNotFoundError(f"No saved feature diagnostics under {run_dir}")
    frames = []
    for path in files:
        frame = pd.read_parquet(path)
        frame["refit_origin"] = pd.to_datetime(frame["refit_origin"])
        frames.append(frame)
    diagnostics = pd.concat(frames, ignore_index=True)
    _, manifest, features, _ = load_feature_dataset(ROOT, args.feature_dataset_id, args.feature_set)
    groups = {feature: group for group, names in manifest["feature_groups"].items() for feature in names}
    diagnostics["feature_group"] = diagnostics["feature"].map(groups).fillna("unclassified")
    diagnostics["year"] = diagnostics["refit_origin"].dt.year
    diagnostics["absolute_value"] = diagnostics["value"].abs()
    group_year = diagnostics.groupby(["config_id", "measure", "year", "feature_group"], as_index=False).agg(mean_absolute_importance=("absolute_value", "mean"), median_absolute_importance=("absolute_value", "median"), refits=("refit_origin", "nunique"))
    feature_year = diagnostics.groupby(["config_id", "measure", "year", "feature"], as_index=False).agg(mean_value=("value", "mean"), mean_absolute_value=("absolute_value", "mean"), refits=("refit_origin", "nunique"))
    identity = {"run_id": args.run_id, "feature_dataset_id": args.feature_dataset_id, "feature_set": args.feature_set}
    output = ROOT / args.output_root / ("drift_" + stable_object_hash(identity)[:16])
    output.mkdir(parents=True, exist_ok=True)
    group_year.to_csv(output / "group_importance_by_year.csv", index=False)
    feature_year.to_csv(output / "feature_importance_by_year.csv", index=False)
    atomic_json_dump({"schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(), "status": "complete", "identity": identity, "diagnostic_files": len(files), "interpretation": "Impurity importance and standardized coefficients describe fitted models; they are not causal effects. Correlated groups should be interpreted together."}, output / "manifest.json")
    print(json.dumps({"status": "complete", "output_directory": str(output), "diagnostic_files": len(files)}, indent=2))


if __name__ == "__main__":
    main()

