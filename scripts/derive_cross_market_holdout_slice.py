#!/usr/bin/env python3
"""Derive an immutable calendar-date evaluation slice from a completed final run.

This command never refits or reselects a model. It filters already-issued
walk-forward predictions and recomputes every evaluation artifact on the
requested date interval. The source run remains unchanged.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from quantfin.cross_market.common import environment_record, load_research_config, root_path
from quantfin.cross_market.experiments import cost_sensitivity, evaluate_predictions, inferential_tests
from quantfin.cross_market.plots import create_run_plots
from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _file_inventory(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): sha256_file(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_research.yaml")
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()

    config = load_research_config(args.config)
    runs_root = root_path(config["outputs"]["runs_root"])
    source = runs_root / args.source_run_id
    source_manifest_path = source / "manifest.json"
    if not source_manifest_path.is_file():
        raise FileNotFoundError(f"Completed source run not found: {source}")
    source_manifest = _read_json(source_manifest_path)
    if source_manifest.get("stage") != "final_test" or source_manifest.get("status") != "complete":
        raise ValueError("Source must be a completed final_test run")

    required = [
        "predictions.parquet",
        "refit_diagnostics.csv",
        "configurations.json",
    ]
    missing = [name for name in required if not (source / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Source run is missing required files: {missing}")

    start = pd.Timestamp(args.start)
    end = pd.Timestamp(args.end)
    if end < start:
        raise ValueError("--end must not precede --start")

    source_prediction_sha256 = sha256_file(source / "predictions.parquet")
    derivation_contract = {
        "source_run_id": args.source_run_id,
        "source_manifest_sha256": sha256_file(source_manifest_path),
        "source_predictions_sha256": source_prediction_sha256,
        "evaluation_start": str(start.date()),
        "evaluation_end": str(end.date()),
        "policy": "filter_preexisting_predictions_without_refit_or_reselection",
        "selected_config_id": source_manifest["selected_config_id"],
    }
    content_hash = stable_object_hash(derivation_contract)[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"cm_final_slice_{start.year}_{stamp}_{content_hash}"
    output = runs_root / run_id
    plan = {
        "action": "derive_cross_market_holdout_slice",
        "run_id": run_id,
        "content_hash": content_hash,
        "stage": "derived_final_evaluation",
        "source_run_id": args.source_run_id,
        "dataset_id": source_manifest["dataset_id"],
        "freeze_id": source_manifest.get("freeze_id"),
        "selected_config_id": source_manifest["selected_config_id"],
        "evaluation_start": str(start.date()),
        "evaluation_end": str(end.date()),
        "refit_performed": False,
        "model_reselection_performed": False,
        "directory": str(output),
    }
    if args.plan_only:
        print(json.dumps(plan, indent=2))
        return

    print(json.dumps({**plan, "status": "starting"}, indent=2), flush=True)

    predictions = pd.read_parquet(source / "predictions.parquet")
    predictions["decision_date"] = pd.to_datetime(predictions["decision_date"])
    available_start = predictions["decision_date"].min()
    available_end = predictions["decision_date"].max()
    if start < available_start or end > available_end:
        raise ValueError(
            f"Requested interval {start.date()}..{end.date()} is outside source "
            f"predictions {available_start.date()}..{available_end.date()}"
        )
    sliced_predictions = predictions.loc[
        predictions["decision_date"].between(start, end, inclusive="both")
    ].copy()
    if sliced_predictions.empty:
        raise ValueError("The requested evaluation interval contains no predictions")

    diagnostics = pd.read_csv(source / "refit_diagnostics.csv")
    diagnostic_dates = pd.to_datetime(diagnostics["block_start"])
    sliced_diagnostics = diagnostics.loc[diagnostic_dates.between(start, end, inclusive="both")].copy()
    if sliced_diagnostics.empty:
        raise ValueError("The requested evaluation interval contains no refit diagnostics")

    leaderboard, ledgers = evaluate_predictions(sliced_predictions, sliced_diagnostics, config)
    with (source / "configurations.json").open("r", encoding="utf-8") as handle:
        configurations = json.load(handle)
    configuration_lookup = {
        row["config_id"]: json.dumps(row, sort_keys=True) for row in configurations
    }
    leaderboard["configuration"] = leaderboard["config_id"].map(configuration_lookup)

    selected_config_id = source_manifest["selected_config_id"]
    if selected_config_id not in set(sliced_predictions["config_id"]):
        raise ValueError("Frozen selected model is absent from the sliced predictions")
    sensitivity = cost_sensitivity(sliced_predictions, config, selected_config_id)
    comparisons, inference, annual = inferential_tests(
        sliced_predictions, ledgers, selected_config_id, config
    )

    output.mkdir(parents=True, exist_ok=False)
    atomic_parquet_dump(sliced_predictions, output / "predictions.parquet")
    atomic_parquet_dump(ledgers, output / "strategy_ledgers.parquet")
    sliced_diagnostics.to_csv(output / "refit_diagnostics.csv", index=False)
    leaderboard.to_csv(output / "leaderboard.csv", index=False)
    sensitivity.to_csv(output / "cost_sensitivity.csv", index=False)
    comparisons.to_csv(output / "forecast_hac_comparisons.csv", index=False)
    annual.to_csv(output / "annual_performance.csv", index=False)
    atomic_json_dump(inference, output / "selected_model_inference.json")
    atomic_json_dump(configurations, output / "configurations.json")

    importance_path = source / "feature_importance_by_refit.csv"
    if importance_path.is_file():
        importance = pd.read_csv(importance_path)
        importance_dates = pd.to_datetime(importance["block_start"])
        sliced_importance = importance.loc[
            importance_dates.between(start, end, inclusive="both")
        ].copy()
        if not sliced_importance.empty:
            sliced_importance.to_csv(output / "feature_importance_by_refit.csv", index=False)

    create_run_plots(
        leaderboard,
        ledgers,
        sliced_predictions,
        output / "plots",
        selected_config_id=selected_config_id,
    )

    manifest = {
        "schema_version": 1,
        **plan,
        "status": "complete",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": derivation_contract,
        "source_stage": source_manifest["stage"],
        "source_config_sha256": source_manifest.get("config_sha256"),
        "prediction_rows": int(len(sliced_predictions)),
        "prediction_dates": int(sliced_predictions["decision_date"].nunique()),
        "configuration_count": int(sliced_predictions["config_id"].nunique()),
        "refit_diagnostic_count": int(len(sliced_diagnostics)),
        "files": _file_inventory(output),
        "environment": environment_record(),
        "disclosure": (
            "Derived calendar-year evaluation of predictions already produced by the source "
            "final run. No fitting, tuning, model selection, or forecast regeneration occurred."
        ),
    }
    atomic_json_dump(manifest, output / "manifest.json")
    print(
        json.dumps(
            {
                "run_id": run_id,
                "content_hash": content_hash,
                "status": "complete",
                "source_run_id": args.source_run_id,
                "evaluation_interval": [str(start.date()), str(end.date())],
                "prediction_dates": manifest["prediction_dates"],
                "refit_diagnostic_count": manifest["refit_diagnostic_count"],
                "directory": str(output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
