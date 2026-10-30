#!/usr/bin/env python3
"""Run resumable screening, confirmation, or one-time final cross-market tests."""

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
    write_run_state,
)
from quantfin.cross_market.experiments import (
    cost_sensitivity,
    enumerate_configurations,
    inferential_tests,
    run_walk_forward,
    set_thread_limits,
)
from quantfin.cross_market.plots import create_run_plots
from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash


def _load_run(config: dict, run_id: str) -> Path:
    path = root_path(config["outputs"]["runs_root"]) / run_id
    if not (path / "manifest.json").is_file():
        raise FileNotFoundError(f"Completed parent run not found: {path}")
    return path


def _read_configurations(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, list):
        raise ValueError(f"Expected configuration list: {path}")
    return value


def _confirmation_candidates(screening: Path, config: dict) -> list[dict]:
    leaderboard = pd.read_csv(screening / "leaderboard.csv")
    configurations = {row["config_id"]: row for row in _read_configurations(screening / "configurations.json")}
    eligible = leaderboard.loc[leaderboard["prediction_coverage"] >= float(config["selection"]["minimum_prediction_coverage"])]
    per_family = int(config["selection"]["screening_top_per_family"])
    selected = eligible.groupby("family", sort=False).head(per_family)
    selected = selected.sort_values("rank").head(int(config["selection"]["confirmation_candidates"]))
    baseline_ids = leaderboard.loc[leaderboard["family"].isin(["zero", "asset_mean", "autoregression"]), "config_id"].tolist()
    ids = list(dict.fromkeys([*baseline_ids, *selected["config_id"].tolist()]))
    return [configurations[config_id] for config_id in ids]


def _final_configurations(freeze_path: Path, confirmation: Path) -> list[dict]:
    with freeze_path.open("r", encoding="utf-8") as handle:
        freeze = json.load(handle)
    configurations = {row["config_id"]: row for row in _read_configurations(confirmation / "configurations.json")}
    winner = configurations[freeze["selected_config_id"]]
    baseline = [row for row in configurations.values() if row["family"] in {"zero", "asset_mean", "autoregression"}]
    return list({row["config_id"]: row for row in [*baseline, winner]}.values())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_research.yaml")
    parser.add_argument("--dataset-id")
    parser.add_argument("--stage", choices=["screening", "confirmation", "final_test"], required=True)
    parser.add_argument("--profile", choices=["quick", "standard", "deep"], default="standard")
    parser.add_argument("--screening-run-id")
    parser.add_argument("--freeze-id")
    parser.add_argument("--resume-run-id")
    parser.add_argument("--training-scheme", choices=["rolling", "expanding"], default="rolling")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    set_thread_limits(config)
    dataset = resolve_dataset(config, args.dataset_id)
    with (dataset / "manifest.json").open("r", encoding="utf-8") as handle:
        dataset_manifest = json.load(handle)
    parent: dict[str, str] = {}
    parent_content: dict[str, str] = {}
    if args.stage == "screening":
        configurations = enumerate_configurations(config, args.profile)
    elif args.stage == "confirmation":
        if not args.screening_run_id:
            parser.error("--screening-run-id is required for confirmation")
        screening = _load_run(config, args.screening_run_id)
        configurations = _confirmation_candidates(screening, config)
        parent["screening_run_id"] = args.screening_run_id
        with (screening / "manifest.json").open("r", encoding="utf-8") as handle:
            parent_content["screening_content_hash"] = json.load(handle)["content_hash"]
    else:
        if not args.freeze_id:
            parser.error("--freeze-id is required for final_test")
        freeze_path = root_path(config["outputs"]["freezes_root"]) / f"{args.freeze_id}.json"
        if not freeze_path.is_file():
            raise FileNotFoundError(freeze_path)
        with freeze_path.open("r", encoding="utf-8") as handle:
            freeze = json.load(handle)
        confirmation = _load_run(config, freeze["confirmation_run_id"])
        configurations = _final_configurations(freeze_path, confirmation)
        parent.update({"freeze_id": args.freeze_id, "confirmation_run_id": freeze["confirmation_run_id"]})
        parent_content.update({
            "freeze_content_hash": freeze["content_hash"],
            "confirmation_content_hash": freeze["confirmation_content_hash"],
        })

    content_hash = stable_object_hash({
        "stage": args.stage, "profile": args.profile,
        "dataset_source_hash": dataset_manifest["source_hash"],
        "panel_sha256": dataset_manifest["files"]["panel.parquet"],
        "feature_dictionary_sha256": dataset_manifest["files"]["feature_dictionary.csv"],
        "config_sha256": sha256_file(root_path(args.config)), "configurations": configurations,
        "training_scheme": args.training_scheme, **parent_content,
    })[:12]
    split_key = {"screening": "screening", "confirmation": "confirmation", "final_test": "final_test"}[args.stage]
    split_start, split_end = config["sample"]["splits"][split_key]
    expected_months = len(pd.period_range(split_start, split_end, freq="M"))
    expected_checkpoints = len(configurations) * expected_months
    runs_root = root_path(config["outputs"]["runs_root"])
    if args.resume_run_id:
        run_id = args.resume_run_id
        output = runs_root / run_id
        if not (output / "run_state.json").is_file():
            raise FileNotFoundError(f"Cannot resume missing run: {output}")
        with (output / "run_state.json").open("r", encoding="utf-8") as handle:
            state = json.load(handle)
        if state.get("content_hash") != content_hash or state.get("stage") != args.stage:
            raise ValueError("Resume request does not match the original run content hash or stage")
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_id = f"cm_{args.stage}_{stamp}_{content_hash}"
        output = runs_root / run_id
    plan = {
        "action": "run_cross_market_experiments", "run_id": run_id, "content_hash": content_hash,
        "stage": args.stage, "profile": args.profile, "training_scheme": args.training_scheme,
        "dataset_id": dataset.name, "configuration_count": len(configurations),
        "expected_checkpoint_count": expected_checkpoints, **parent, "directory": str(output),
    }
    if args.plan_only:
        print(json.dumps(plan, indent=2)); return
    print(json.dumps({**plan, "status": "starting"}, indent=2), flush=True)
    output.mkdir(parents=True, exist_ok=bool(args.resume_run_id))
    atomic_json_dump(configurations, output / "configurations.json")
    write_run_state(output, **plan, status="running", environment=environment_record())
    try:
        panel, _, dictionary = read_panel_dataset(dataset)
        predictions, diagnostics, importance, leaderboard, ledgers = run_walk_forward(
            panel, dictionary, configurations, config, args.stage, output, training_scheme=args.training_scheme
        )
        atomic_parquet_dump(predictions, output / "predictions.parquet")
        atomic_parquet_dump(ledgers, output / "strategy_ledgers.parquet")
        diagnostics.to_csv(output / "refit_diagnostics.csv", index=False)
        leaderboard.to_csv(output / "leaderboard.csv", index=False)
        if not importance.empty:
            importance.to_csv(output / "feature_importance_by_refit.csv", index=False)
        winner = freeze["selected_config_id"] if args.stage == "final_test" else str(leaderboard.iloc[0]["config_id"])
        sensitivity = cost_sensitivity(predictions, config, winner)
        sensitivity.to_csv(output / "cost_sensitivity.csv", index=False)
        comparisons, inference, annual = inferential_tests(predictions, ledgers, winner, config)
        comparisons.to_csv(output / "forecast_hac_comparisons.csv", index=False)
        annual.to_csv(output / "annual_performance.csv", index=False)
        atomic_json_dump(inference, output / "selected_model_inference.json")
        create_run_plots(leaderboard, ledgers, predictions, output / "plots", selected_config_id=winner)
        completed = {
            "schema_version": 1, **plan, "status": "complete", "selected_config_id": winner,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "dataset_manifest_sha256": sha256_file(dataset / "manifest.json"),
            "config_sha256": sha256_file(root_path(args.config)), "environment": environment_record(),
            "checkpoint_count": len(diagnostics),
        }
        atomic_json_dump(completed, output / "manifest.json")
        write_run_state(output, **plan, status="complete", selected_config_id=winner, completed_at_utc=completed["completed_at_utc"], checkpoint_count=len(diagnostics))
    except BaseException as exc:
        write_run_state(output, **plan, status="failed", error=repr(exc)); raise
    print(json.dumps({"run_id": run_id, "content_hash": content_hash, "status": "complete", "selected_config_id": winner, "directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()
