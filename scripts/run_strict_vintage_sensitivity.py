#!/usr/bin/env python3
"""Run the exact selected model with and without fallback-flagged features."""
from __future__ import annotations

import argparse
import copy
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

from quantfin.cross_market.common import (
    environment_record,
    load_research_config,
    read_panel_dataset,
    resolve_dataset,
    root_path,
)
from quantfin.cross_market.experiments import (
    _fit_block,
    evaluate_predictions,
    feature_columns,
    run_walk_forward,
    set_thread_limits,
)
from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash

ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _read_configurations(path: Path) -> list[dict]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError(f"Expected configuration list: {path}")
    return value


def _circular_indices(rng: np.random.Generator, n: int, block: int) -> np.ndarray:
    starts = rng.integers(0, n, size=int(np.ceil(n / block)))
    return np.concatenate([(start + np.arange(block)) % n for start in starts])[:n]


def _sharpe(values: np.ndarray) -> float:
    standard_deviation = float(np.std(values, ddof=1))
    return float(np.sqrt(252) * np.mean(values) / standard_deviation) if standard_deviation > 0 else float("nan")


def _cumulative(values: pd.Series) -> float:
    return float((1.0 + values.fillna(0.0)).prod() - 1.0)


def _paired_inference(
    reference: pd.DataFrame,
    strict: pd.DataFrame,
    *,
    period: str,
    draws: int,
    block: int,
    seed: int,
) -> dict:
    aligned = reference[["decision_date", "net_return"]].rename(columns={"net_return": "reference"}).merge(
        strict[["decision_date", "net_return"]].rename(columns={"net_return": "strict"}),
        on="decision_date",
        how="inner",
        validate="one_to_one",
    ).sort_values("decision_date")
    if len(aligned) != len(reference) or len(aligned) != len(strict):
        raise ValueError(f"Strict-vintage comparison has unmatched dates in {period}")
    reference_values = aligned["reference"].to_numpy(float)
    strict_values = aligned["strict"].to_numpy(float)
    mean_draws = np.empty(draws)
    sharpe_draws = np.empty(draws)
    rng = np.random.default_rng(seed)
    for draw in tqdm(range(draws), desc=f"{period} paired bootstrap", unit="draw"):
        index = _circular_indices(rng, len(aligned), block)
        mean_draws[draw] = np.mean(strict_values[index] - reference_values[index]) * 10_000
        sharpe_draws[draw] = _sharpe(strict_values[index]) - _sharpe(reference_values[index])
    return {
        "period": period,
        "sessions": int(len(aligned)),
        "block_length_sessions": block,
        "draws": draws,
        "seed": seed,
        "strict_minus_reference_mean_daily_bps": float(np.mean(strict_values - reference_values) * 10_000),
        "mean_daily_ci_low_bps": float(np.quantile(mean_draws, 0.025)),
        "mean_daily_ci_high_bps": float(np.quantile(mean_draws, 0.975)),
        "reference_sharpe": _sharpe(reference_values),
        "strict_sharpe": _sharpe(strict_values),
        "strict_minus_reference_sharpe": _sharpe(strict_values) - _sharpe(reference_values),
        "sharpe_ci_low": float(np.nanquantile(sharpe_draws, 0.025)),
        "sharpe_ci_high": float(np.nanquantile(sharpe_draws, 0.975)),
    }


def _metric_rows(
    period: str,
    reference_id: str,
    strict_id: str,
    reference_leaderboard: pd.DataFrame,
    strict_leaderboard: pd.DataFrame,
    reference_ledger: pd.DataFrame,
    strict_ledger: pd.DataFrame,
) -> list[dict]:
    rows = []
    for variant, config_id, leaderboard, ledger in [
        ("selected_reference", reference_id, reference_leaderboard, reference_ledger),
        ("strict_vintage", strict_id, strict_leaderboard, strict_ledger),
    ]:
        metric = leaderboard.loc[leaderboard["config_id"].eq(config_id)].iloc[0]
        rows.append({
            "period": period,
            "variant": variant,
            "config_id": config_id,
            "sessions": int(ledger["decision_date"].nunique()),
            "cumulative_net_return": _cumulative(ledger["net_return"]),
            "annualized_net_return": float(metric["net_annual_return"]),
            "net_sharpe": float(metric["net_sharpe"]),
            "oos_r2_asset_mean": float(metric["oos_r2_asset_mean"]),
            "spearman_ic": float(metric["spearman_ic"]),
            "directional_accuracy": float(metric["directional_accuracy"]),
            "mean_input_features": float(metric["mean_input_features"]),
            "mean_daily_turnover": float(metric["mean_daily_turnover"]),
        })
    return rows


def _draw_figure(metrics: pd.DataFrame, inference: pd.DataFrame, output: Path) -> None:
    periods = metrics["period"].drop_duplicates().tolist()
    variants = ["selected_reference", "strict_vintage"]
    labels = {"selected_reference": "Selected F7", "strict_vintage": "Strict-vintage F7"}
    colors = {"selected_reference": "#175B9A", "strict_vintage": "#138577"}
    figure, axes = plt.subplots(1, 2, figsize=(10.2, 4.3), constrained_layout=True)
    x = np.arange(len(periods))
    for offset, variant in zip([-0.18, 0.18], variants):
        values = [float(metrics.loc[(metrics.period.eq(period)) & (metrics.variant.eq(variant)), "cumulative_net_return"].iloc[0]) * 100 for period in periods]
        bars = axes[0].bar(x + offset, values, width=0.34, label=labels[variant], color=colors[variant])
        axes[0].bar_label(bars, labels=[f"{value:+.2f}%" for value in values], padding=3, fontsize=8)
    axes[0].axhline(0, color="#6B7785", linewidth=0.8)
    axes[0].set_xticks(x, periods)
    axes[0].set_ylabel("Cumulative net return (%)")
    axes[0].set_title("Same model and policy; flagged features removed")
    axes[0].legend(frameon=False, fontsize=8)
    forest = inference.set_index("period").loc[periods]
    point = forest["strict_minus_reference_mean_daily_bps"].to_numpy(float)
    low = forest["mean_daily_ci_low_bps"].to_numpy(float)
    high = forest["mean_daily_ci_high_bps"].to_numpy(float)
    axes[1].errorbar(point, x, xerr=np.vstack([point - low, high - point]), fmt="o", color="#B75B16", ecolor="#B75B16", capsize=4)
    axes[1].axvline(0, color="#6B7785", linestyle="--", linewidth=0.9)
    axes[1].set_yticks(x, periods)
    axes[1].set_xlabel("Strict minus selected mean daily return (bps)\n95% circular date-block interval")
    axes[1].set_title("Paired uncertainty on identical sessions")
    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", color="#E4E8ED", linewidth=0.6)
    figure.suptitle("Strict-vintage sensitivity: exact selected depth-6 Extra Trees", fontsize=13, fontweight="bold")
    figure.savefig(output / "strict_vintage_sensitivity.png", dpi=240, bbox_inches="tight")
    figure.savefig(output / "strict_vintage_sensitivity.pdf", bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-registry", type=Path, required=True)
    parser.add_argument("--source-config", default="configs/cross_market_ai_capability_research.yaml")
    parser.add_argument("--forward-config", default="configs/cross_market_ai_capability_2026_extension.yaml")
    parser.add_argument("--parallel-workers", type=int, choices=[1, 2, 3, 4], default=3)
    parser.add_argument("--draws", type=int, default=2000)
    parser.add_argument("--block-length", type=int, default=10)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--resume-analysis-id")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()

    registry_path = args.release_registry if args.release_registry.is_absolute() else ROOT / args.release_registry
    registry = _read_json(registry_path)
    ids = registry["ids"]
    source_config = load_research_config(args.source_config)
    forward_config = load_research_config(args.forward_config)
    set_thread_limits(source_config)
    source_dataset = resolve_dataset(source_config, ids["DATASET_ID"])
    forward_dataset = resolve_dataset(forward_config, ids["FORWARD_DATASET_ID"])
    source_run = root_path(source_config["outputs"]["runs_root"]) / ids["FINAL_RUN_ID"]
    forward_run = root_path(forward_config["outputs"]["runs_root"]) / ids["FORWARD_RUN_ID"]
    freeze_path = root_path(source_config["outputs"]["freezes_root"]) / f"{ids['FREEZE_ID']}.json"
    freeze = _read_json(freeze_path)
    if freeze["selected_config_id"] != ids["SELECTED_CONFIG_ID"]:
        raise ValueError("Registry and freeze selected configurations disagree")
    source_configurations = _read_configurations(source_run / "configurations.json")
    selected = next(row for row in source_configurations if row["config_id"] == ids["SELECTED_CONFIG_ID"])
    expected_parameters = {"n_estimators": 250, "max_depth": 6, "min_samples_leaf": 40, "max_features": 0.5}
    if selected["family"] != "extra_trees" or selected["feature_set"] != "F7_full_context" or selected["parameters"] != expected_parameters:
        raise ValueError(f"Selected specification is not the expected depth-6 Extra Trees model: {selected}")
    asset_mean = next(row for row in source_configurations if row["family"] == "asset_mean")
    strict_payload = {
        "family": selected["family"],
        "parameters": copy.deepcopy(selected["parameters"]),
        "feature_set": selected["feature_set"],
        "experiment": "strict_vintage_sensitivity",
        "exclude_current_vintage_fallback": True,
        "parent_config_id": selected["config_id"],
    }
    strict = {**strict_payload, "config_id": f"cm_extra_trees_strict_{stable_object_hash(strict_payload)[:12]}"}
    identity = {
        "registry_sha256": sha256_file(registry_path),
        "source_dataset_manifest_sha256": sha256_file(source_dataset / "manifest.json"),
        "forward_dataset_manifest_sha256": sha256_file(forward_dataset / "manifest.json"),
        "source_run_manifest_sha256": sha256_file(source_run / "manifest.json"),
        "forward_run_manifest_sha256": sha256_file(forward_run / "manifest.json"),
        "freeze_sha256": sha256_file(freeze_path),
        "source_config_sha256": sha256_file(root_path(args.source_config)),
        "forward_config_sha256": sha256_file(root_path(args.forward_config)),
        "script_sha256": sha256_file(Path(__file__)),
        "selected_configuration": selected,
        "strict_configuration": strict,
        "draws": args.draws,
        "block_length": args.block_length,
        "seed": args.seed,
    }
    content_hash = stable_object_hash(identity)[:12]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    analysis_id = args.resume_analysis_id or f"strict_vintage_sensitivity_{timestamp}_{content_hash}"
    output = ROOT / "artifacts/cross_market_ai_capability/analysis" / analysis_id
    plan = {
        "action": "run_strict_vintage_sensitivity",
        "analysis_id": analysis_id,
        "content_hash": content_hash,
        "selected_config_id": selected["config_id"],
        "strict_config_id": strict["config_id"],
        "parallel_workers": args.parallel_workers,
        "directory": str(output),
    }
    if args.plan_only:
        print(json.dumps(plan, indent=2))
        return
    print(json.dumps({**plan, "status": "starting"}, indent=2), flush=True)
    output.mkdir(parents=True, exist_ok=bool(args.resume_analysis_id))
    if args.resume_analysis_id:
        state = _read_json(output / "run_state.json")
        if state.get("content_hash") != content_hash:
            raise ValueError("Resume request does not match the original strict-vintage content hash")
    atomic_json_dump({**plan, "status": "running", "environment": environment_record()}, output / "run_state.json")
    try:
        source_panel, _, source_dictionary = read_panel_dataset(source_dataset)
        forward_panel, _, forward_dictionary = read_panel_dataset(forward_dataset)
        fallback_mask = source_dictionary["current_vintage_fallback"].fillna(False).astype(str).str.lower().isin({"true", "1"})
        f7_mask = source_dictionary["feature_sets"].fillna("").str.split("|").apply(lambda values: "F7_full_context" in values)
        excluded = source_dictionary.loc[fallback_mask & f7_mask, [column for column in ["feature", "source", "current_vintage_fallback"] if column in source_dictionary]].copy()
        strict_features = set(feature_columns(source_dictionary, "F7_full_context", exclude_current_vintage_fallback=True))
        if excluded.empty or set(excluded["feature"]) & strict_features:
            raise RuntimeError("Strict feature audit failed: fallback-flagged features were not fully excluded")
        excluded.to_csv(output / "excluded_features.csv", index=False)

        completed_outputs = [
            output / "strict_vintage_metrics.csv",
            output / "strict_vintage_paired_inference.csv",
            output / "strict_vintage_ledgers.parquet",
            output / "strict_vintage_refit_diagnostics.csv",
        ]
        if args.resume_analysis_id and all(path.is_file() for path in completed_outputs):
            metrics = pd.read_csv(output / "strict_vintage_metrics.csv")
            inference = pd.read_csv(output / "strict_vintage_paired_inference.csv")
            _draw_figure(metrics, inference, output)
            files = {
                str(path.relative_to(output)): sha256_file(path)
                for path in sorted(output.rglob("*"))
                if path.is_file() and path.name not in {"manifest.json", "run_state.json"}
            }
            manifest = {
                "schema_version": 1,
                **plan,
                "status": "complete",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "identity": identity,
                "selected_parameters_match_exactly": True,
                "fallback_flagged_features_excluded": int(len(excluded)),
                "fallback_flagged_features_retained": 0,
                "strict_feature_count_before_viability_filter": int(len(strict_features)),
                "method": "post-selection sensitivity; exact selected depth-6 Extra Trees; identical dates, rolling windows, seed and trading policy; paired circular date-block bootstrap",
                "files": files,
                "environment": environment_record(),
                "resumed_from_completed_statistics": True,
            }
            atomic_json_dump(manifest, output / "manifest.json")
            atomic_json_dump({**plan, "status": "complete", "completed_at_utc": manifest["created_at_utc"]}, output / "run_state.json")
            print(json.dumps({**plan, "status": "complete", "fallback_flagged_features_excluded": len(excluded), "resumed_from_completed_statistics": True}, indent=2))
            return

        runtime_source = copy.deepcopy(source_config)
        runtime_source["validation"]["n_jobs"] = max(1, int(source_config["validation"]["n_jobs"]) // args.parallel_workers)
        strict_2025_directory = output / "strict_2025"
        strict_2025_directory.mkdir()
        _, diagnostics_2025, _, leaderboard_2025, ledgers_2025 = run_walk_forward(
            source_panel,
            source_dictionary,
            [asset_mean, strict],
            runtime_source,
            "final_test",
            strict_2025_directory,
            training_scheme="rolling",
            parallel_workers=args.parallel_workers,
        )

        runtime_forward = copy.deepcopy(forward_config)
        runtime_forward["validation"]["n_jobs"] = max(1, int(forward_config["validation"]["n_jobs"]) // args.parallel_workers)
        start, end = map(pd.Timestamp, runtime_forward["sample"]["splits"]["final_test"])
        block = pd.DatetimeIndex(sorted(forward_panel.loc[forward_panel["decision_date"].between(start, end), "decision_date"].unique()))
        forward_results = []
        with ThreadPoolExecutor(max_workers=min(args.parallel_workers, 2), thread_name_prefix="strict-vintage") as executor:
            futures = {
                executor.submit(_fit_block, configuration, forward_panel, forward_dictionary, block, runtime_forward, "rolling", False): configuration
                for configuration in [asset_mean, strict]
            }
            for future in tqdm(as_completed(futures), total=len(futures), desc="2026 strict-vintage fit", unit="model"):
                prediction, diagnostics, importance = future.result()
                configuration = futures[future]
                diagnostics.update({"config_id": configuration["config_id"], "family": configuration["family"], "feature_set": configuration["feature_set"]})
                forward_results.append((prediction, diagnostics, importance))
        predictions_2026 = pd.concat([row[0] for row in forward_results], ignore_index=True)
        diagnostics_2026 = pd.DataFrame([row[1] for row in forward_results])
        leaderboard_2026, ledgers_2026 = evaluate_predictions(predictions_2026, diagnostics_2026, runtime_forward)

        reference_predictions_2025 = pd.read_parquet(source_run / "predictions.parquet")
        reference_ledgers_2025 = pd.read_parquet(source_run / "strategy_ledgers.parquet")
        reference_leaderboard_2025 = pd.read_csv(source_run / "leaderboard.csv")
        reference_predictions_2026 = pd.read_parquet(forward_run / "predictions.parquet")
        reference_ledgers_2026 = pd.read_parquet(forward_run / "strategy_ledgers.parquet")
        reference_leaderboard_2026 = pd.read_csv(forward_run / "leaderboard.csv")

        metric_rows = []
        inference_rows = []
        for index, (period, reference_leaderboard, strict_leaderboard, reference_ledgers, strict_ledgers) in enumerate([
            ("2025 historical replication", reference_leaderboard_2025, leaderboard_2025, reference_ledgers_2025, ledgers_2025),
            ("2026 Jan-Sep extension", reference_leaderboard_2026, leaderboard_2026, reference_ledgers_2026, ledgers_2026),
        ]):
            reference_ledger = reference_ledgers.loc[reference_ledgers["config_id"].eq(selected["config_id"])].copy()
            strict_ledger = strict_ledgers.loc[strict_ledgers["config_id"].eq(strict["config_id"])].copy()
            metric_rows.extend(_metric_rows(period, selected["config_id"], strict["config_id"], reference_leaderboard, strict_leaderboard, reference_ledger, strict_ledger))
            inference_rows.append(_paired_inference(reference_ledger, strict_ledger, period=period, draws=args.draws, block=args.block_length, seed=args.seed + index))

        metrics = pd.DataFrame(metric_rows)
        inference = pd.DataFrame(inference_rows)
        metrics.to_csv(output / "strict_vintage_metrics.csv", index=False)
        inference.to_csv(output / "strict_vintage_paired_inference.csv", index=False)
        atomic_parquet_dump(pd.concat([
            ledgers_2025.assign(period="2025 historical replication"),
            ledgers_2026.assign(period="2026 Jan-Sep extension"),
        ], ignore_index=True), output / "strict_vintage_ledgers.parquet")
        pd.concat([
            diagnostics_2025.assign(period="2025 historical replication"),
            diagnostics_2026.assign(period="2026 Jan-Sep extension"),
        ], ignore_index=True).to_csv(output / "strict_vintage_refit_diagnostics.csv", index=False)
        _draw_figure(metrics, inference, output)
        files = {
            str(path.relative_to(output)): sha256_file(path)
            for path in sorted(output.rglob("*"))
            if path.is_file() and path.name not in {"manifest.json", "run_state.json"}
        }
        manifest = {
            "schema_version": 1,
            **plan,
            "status": "complete",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "identity": identity,
            "selected_parameters_match_exactly": True,
            "fallback_flagged_features_excluded": int(len(excluded)),
            "fallback_flagged_features_retained": 0,
            "strict_feature_count_before_viability_filter": int(len(strict_features)),
            "method": "post-selection sensitivity; exact selected depth-6 Extra Trees; identical dates, rolling windows, seed and trading policy; paired circular date-block bootstrap",
            "files": files,
            "environment": environment_record(),
        }
        atomic_json_dump(manifest, output / "manifest.json")
        atomic_json_dump({**plan, "status": "complete", "completed_at_utc": manifest["created_at_utc"]}, output / "run_state.json")
    except BaseException as error:
        atomic_json_dump({**plan, "status": "failed", "error": repr(error)}, output / "run_state.json")
        raise
    print(json.dumps({**plan, "status": "complete", "fallback_flagged_features_excluded": len(excluded)}, indent=2))


if __name__ == "__main__":
    main()
