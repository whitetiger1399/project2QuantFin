"""Create an activity-aware, baseline-visible selection for a future stage."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from quantfin.io import atomic_json_dump, sha256_file
from quantfin.research_extension import activity_tables


ROOT = Path(__file__).resolve().parents[1]
BASELINES = {"historical_mean", "autoregression"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--primary-metric", default="median_annual_net_sharpe")
    parser.add_argument("--minimum-active-sessions", type=int, default=30)
    parser.add_argument("--minimum-round-trips", type=int, default=10)
    parser.add_argument("--forecast-hurdle", type=float, default=.001)
    parser.add_argument("--one-way-cost-bps", type=float, default=5)
    parser.add_argument("--output-name", default="selection_research.json")
    args = parser.parse_args()
    run_dir = ROOT / "artifacts/runs" / args.run_id
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete" or manifest["inputs"]["stage"] != "screening":
        raise ValueError("Research candidate selection requires a completed screening run")
    predictions = pd.read_parquet(run_dir / "predictions.parquet")
    for column in ["signal_session", "entry_session", "label_end_session", "label_available_session"]:
        predictions[column] = pd.to_datetime(predictions[column])
    activity, _, _ = activity_tables(predictions, forecast_hurdle=args.forecast_hurdle, one_way_cost_bps=args.one_way_cost_bps)
    saved_metrics = pd.read_csv(run_dir / "config_metrics.csv")
    metrics = saved_metrics.drop(columns=[x for x in activity.columns if x in saved_metrics.columns and x not in {"config_id", "family"}]).merge(activity, on=["config_id", "family"], validate="one_to_one")
    metrics["activity_gate_pass"] = metrics["active_sessions"].ge(args.minimum_active_sessions) & metrics["completed_round_trips"].ge(args.minimum_round_trips) & metrics["metric_status"].eq("valid")
    metric = args.primary_metric
    baseline = metrics.loc[metrics["family"].isin(BASELINES) & metrics[metric].notna()].sort_values(metric, ascending=False)
    candidates = metrics.loc[~metrics["family"].isin(BASELINES) & metrics["activity_gate_pass"] & metrics[metric].notna()].sort_values(metric, ascending=False)
    if candidates.empty:
        raise ValueError("No predictive model passes the declared activity gate")
    chosen = candidates.groupby("family", as_index=False, group_keys=False).head(1).nlargest(args.top, metric)
    baseline_value = float(baseline.iloc[0][metric]) if len(baseline) else None
    best_ml_value = float(chosen.iloc[0][metric])
    configurations = json.loads((run_dir / "configurations.json").read_text(encoding="utf-8"))
    selected = [configurations[config_id] for config_id in chosen["config_id"]]
    destination = run_dir / args.output_name
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite: {destination}")
    result = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_run_id": manifest["run_id"],
        "source_run_manifest_sha256": sha256_file(manifest_path),
        "source_context": {
            "stage": manifest["inputs"]["stage"],
            "feature_dataset_id": manifest["inputs"]["feature_dataset_id"],
            "feature_set": manifest["inputs"]["feature_set"],
            "window_observations": manifest["inputs"]["window_observations"],
        },
        "selection_rule": {
            "primary_metric": metric,
            "minimum_prediction_coverage": 0.98,
            "minimum_active_sessions": args.minimum_active_sessions,
            "minimum_completed_round_trips": args.minimum_round_trips,
            "distinct_families": True,
            "baseline_visible": True,
        },
        "baseline_review": baseline.to_dict("records"),
        "best_baseline_metric": baseline_value,
        "best_ml_metric": best_ml_value,
        "ml_exceeds_best_baseline_on_selection_metric": baseline_value is None or best_ml_value > baseline_value,
        "conclusion_if_false": "No demonstrated ML improvement at screening; candidates may proceed only as retrospective research checks.",
        "selected_metrics": chosen.to_dict("records"),
        "selected_configurations": selected,
    }
    atomic_json_dump(result, destination)
    print(json.dumps({"selection": str(destination), "selected": [item["config_id"] for item in selected], "ml_exceeds_baseline": result["ml_exceeds_best_baseline_on_selection_metric"]}, indent=2))


if __name__ == "__main__":
    main()

