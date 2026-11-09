#!/usr/bin/env python3
"""Fit the frozen specification once on pre-2026 data and forecast through September 2026."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from quantfin.cross_market.common import (
    environment_record,
    load_research_config,
    read_panel_dataset,
    resolve_dataset,
    root_path,
)
from quantfin.cross_market.experiments import (
    _fit_block,
    cost_sensitivity,
    evaluate_predictions,
    inferential_tests,
    set_thread_limits,
)
from quantfin.cross_market.plots import create_run_plots
from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


def _read_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forecast-config", default="configs/cross_market_ai_capability_2026_extension.yaml")
    parser.add_argument("--source-config", default="configs/cross_market_ai_capability_research.yaml")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--freeze-id", required=True)
    parser.add_argument("--start", default="2026-01-01")
    parser.add_argument("--end", default="2026-09-30")
    parser.add_argument("--training-scheme", choices=["rolling", "expanding"], default="rolling")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()

    forecast_config = load_research_config(args.forecast_config)
    source_config = load_research_config(args.source_config)
    set_thread_limits(forecast_config)
    dataset = resolve_dataset(forecast_config, args.dataset_id)
    dataset_manifest = _read_json(dataset / "manifest.json")
    freeze_path = root_path(source_config["outputs"]["freezes_root"]) / f"{args.freeze_id}.json"
    freeze = _read_json(freeze_path)
    if freeze.get("final_model_count") != 1:
        raise ValueError("The source freeze must contain exactly one selected model")
    confirmation = root_path(source_config["outputs"]["runs_root"]) / freeze["confirmation_run_id"]
    confirmation_manifest = _read_json(confirmation / "manifest.json")
    if confirmation_manifest.get("status") != "complete" or confirmation_manifest.get("stage") != "confirmation":
        raise ValueError("The freeze must reference a completed confirmation run")
    configurations = json.loads((confirmation / "configurations.json").read_text(encoding="utf-8"))
    lookup = {row["config_id"]: row for row in configurations}
    selected_id = freeze["selected_config_id"]
    if selected_id not in lookup:
        raise ValueError("Frozen configuration is absent from its confirmation run")
    selected = lookup[selected_id]
    baselines = [row for row in configurations if row["family"] in {"zero", "asset_mean", "autoregression"}]
    selected_configurations = list({row["config_id"]: row for row in [*baselines, selected]}.values())

    start = pd.Timestamp(args.start)
    end = pd.Timestamp(args.end)
    configured_start, configured_end = map(pd.Timestamp, forecast_config["sample"]["splits"]["final_test"])
    if start < configured_start or end > configured_end or end < start:
        raise ValueError("Requested interval must lie within the configured 2026 extension")
    identity = {
        "dataset_manifest_sha256": sha256_file(dataset / "manifest.json"),
        "freeze_sha256": sha256_file(freeze_path),
        "confirmation_manifest_sha256": sha256_file(confirmation / "manifest.json"),
        "forecast_config_sha256": sha256_file(root_path(args.forecast_config)),
        "source_config_sha256": sha256_file(root_path(args.source_config)),
        "selected_config_id": selected_id,
        "selected_configuration": selected,
        "start": str(start.date()), "end": str(end.date()),
        "training_scheme": args.training_scheme,
        "fit_policy": "single_fit_before_2026_no_updates_no_reselection",
        "script_sha256": sha256_file(Path(__file__)),
    }
    content_hash = stable_object_hash(identity)[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"cm_ai_capability_2026_forward_{stamp}_{content_hash}"
    output = root_path(forecast_config["outputs"]["runs_root"]) / run_id
    plan = {
        "action": "run_frozen_2026_extension", "run_id": run_id,
        "content_hash": content_hash, "stage": "forward_extension_2026",
        "dataset_id": dataset.name, "source_freeze_id": args.freeze_id,
        "source_confirmation_run_id": freeze["confirmation_run_id"],
        "selected_config_id": selected_id, "selected_family": selected["family"],
        "selected_feature_set": selected["feature_set"],
        "evaluation_start": str(start.date()), "evaluation_end": str(end.date()),
        "refit_count_selected_model": 1, "model_reselection_performed": False,
        "hyperparameter_tuning_performed": False, "directory": str(output),
    }
    if args.plan_only:
        print(json.dumps(plan, indent=2)); return

    print(json.dumps({**plan, "status": "starting"}, indent=2), flush=True)
    output.mkdir(parents=True, exist_ok=False)
    atomic_json_dump({**plan, "status": "running", "environment": environment_record()}, output / "run_state.json")
    try:
        panel, _, dictionary = read_panel_dataset(dataset)
        block = pd.DatetimeIndex(sorted(panel.loc[panel["decision_date"].between(start, end), "decision_date"].unique()))
        if block.empty:
            raise ValueError("The extension panel contains no decision sessions in the requested interval")
        prediction_frames = []
        diagnostic_rows = []
        importance_frames = []
        for configuration in progress(selected_configurations, description="Fitting frozen 2026 extension", unit="model"):
            prediction, diagnostics, importance = _fit_block(
                configuration, panel, dictionary, block, forecast_config,
                args.training_scheme, explain=configuration["config_id"] == selected_id,
            )
            diagnostics.update({
                "config_id": configuration["config_id"], "family": configuration["family"],
                "feature_set": configuration["feature_set"],
            })
            prediction_frames.append(prediction); diagnostic_rows.append(diagnostics)
            if not importance.empty: importance_frames.append(importance)
        predictions = pd.concat(prediction_frames, ignore_index=True)
        diagnostics = pd.DataFrame(diagnostic_rows)
        importance = pd.concat(importance_frames, ignore_index=True) if importance_frames else pd.DataFrame()
        leaderboard, ledgers = evaluate_predictions(predictions, diagnostics, forecast_config)
        configuration_json = {row["config_id"]: json.dumps(row, sort_keys=True) for row in selected_configurations}
        leaderboard["configuration"] = leaderboard["config_id"].map(configuration_json)
        sensitivity = cost_sensitivity(predictions, forecast_config, selected_id)
        comparisons, inference, annual = inferential_tests(predictions, ledgers, selected_id, forecast_config)

        atomic_json_dump(selected_configurations, output / "configurations.json")
        atomic_parquet_dump(predictions, output / "predictions.parquet")
        atomic_parquet_dump(ledgers, output / "strategy_ledgers.parquet")
        diagnostics.to_csv(output / "refit_diagnostics.csv", index=False)
        leaderboard.to_csv(output / "leaderboard.csv", index=False)
        sensitivity.to_csv(output / "cost_sensitivity.csv", index=False)
        comparisons.to_csv(output / "forecast_hac_comparisons.csv", index=False)
        annual.to_csv(output / "annual_performance.csv", index=False)
        atomic_json_dump(inference, output / "selected_model_inference.json")
        if not importance.empty:
            importance.to_csv(output / "feature_importance_by_refit.csv", index=False)
        create_run_plots(leaderboard, ledgers, predictions, output / "plots", selected_config_id=selected_id)

        selected_diag = diagnostics.loc[diagnostics["config_id"].eq(selected_id)].iloc[0]
        if pd.Timestamp(selected_diag["training_end"]) >= start:
            raise RuntimeError("Leakage guard failed: selected model used 2026 training observations")
        files = {
            str(path.relative_to(output)): sha256_file(path)
            for path in sorted(output.rglob("*"))
            if path.is_file() and path.name not in {"manifest.json", "run_state.json"}
        }
        manifest = {
            "schema_version": 1, **plan, "status": "complete",
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_identity": identity, "training_start": selected_diag["training_start"],
            "training_end": selected_diag["training_end"],
            "prediction_dates": int(predictions["decision_date"].nunique()),
            "prediction_rows": int(len(predictions)), "configuration_count": len(selected_configurations),
            "files": files, "environment": environment_record(),
            "disclosure": (
                "The frozen specification was fitted once on observations strictly before 2026. "
                "No 2026 labels were used for fitting, tuning, reselection, or estimator updates. "
                "Realized 2026 returns are used only for retrospective evaluation."
            ),
        }
        atomic_json_dump(manifest, output / "manifest.json")
        atomic_json_dump({**plan, "status": "complete", "completed_at_utc": manifest["completed_at_utc"]}, output / "run_state.json")
    except BaseException as exc:
        atomic_json_dump({**plan, "status": "failed", "error": repr(exc)}, output / "run_state.json")
        raise
    print(json.dumps({**plan, "status": "complete", "training_end": manifest["training_end"],
                      "prediction_dates": manifest["prediction_dates"]}, indent=2))


if __name__ == "__main__":
    main()
