"""Run a checkpointed random-feature complexity response surface.

The command is plan-only unless --execute is supplied. Existing canonical model
runs are read-only; results are written below artifacts/research/complexity_runs.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from tqdm import tqdm

from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash
from quantfin.research_extension import (
    activity_tables,
    deterministic_run_id,
    environment_record,
    estimate_dense_gb,
    evenly_spaced,
    load_feature_dataset,
    monthly_blocks,
    peak_rss_mb,
    read_yaml,
)


ROOT = Path(__file__).resolve().parents[1]


def rff_bank(x: np.ndarray, *, components: int, gamma: float, seed: int) -> np.ndarray:
    # Component-major draws and independent streams ensure the first P columns
    # are identical when a larger bank is requested with the same seed.
    weight_rng = np.random.default_rng(seed)
    offset_rng = np.random.default_rng(seed + 1_000_003)
    weights = weight_rng.normal(0.0, np.sqrt(2.0 * gamma), size=(components, x.shape[1])).T
    offsets = offset_rng.uniform(0.0, 2.0 * np.pi, size=components)
    # The common sqrt(2/P) factor is intentionally omitted before column
    # standardization; it cancels exactly and raw columns remain nested in P.
    return np.sqrt(2.0) * np.cos(x @ weights + offsets)


def ridge_path(
    z_train: np.ndarray,
    y_train: np.ndarray,
    z_eval: np.ndarray,
    penalties: list[float],
) -> tuple[dict[float, tuple[np.ndarray, np.ndarray, float]], dict[str, Any]]:
    n, p = z_train.shape
    y_mean = float(y_train.mean())
    centered_y = y_train - y_mean
    result: dict[float, tuple[np.ndarray, np.ndarray, float]] = {}
    if p < n:
        gram = z_train.T @ z_train
        eigenvalues, eigenvectors = np.linalg.eigh(gram)
        eigenvalues = np.maximum(eigenvalues, 0.0)
        projected = eigenvectors.T @ (z_train.T @ centered_y)
        train_basis = z_train @ eigenvectors
        eval_basis = z_eval @ eigenvectors
        solver = "primal_eigendecomposition"
    else:
        gram = z_train @ z_train.T
        eigenvalues, eigenvectors = np.linalg.eigh(gram)
        eigenvalues = np.maximum(eigenvalues, 0.0)
        projected = eigenvectors.T @ centered_y
        train_cross = gram @ eigenvectors
        eval_cross = (z_eval @ z_train.T) @ eigenvectors
        solver = "dual_eigendecomposition"
    for penalty in penalties:
        denominator = eigenvalues + n * penalty
        safe = np.where(denominator > np.finfo(float).eps, denominator, np.inf)
        if p < n:
            coefficients = projected / safe
            train_prediction = y_mean + train_basis @ coefficients
            evaluation_prediction = y_mean + eval_basis @ coefficients
        else:
            alpha_coordinates = projected / safe
            train_prediction = y_mean + train_cross @ alpha_coordinates
            evaluation_prediction = y_mean + eval_cross @ alpha_coordinates
        effective_df = float(np.sum(eigenvalues / safe))
        result[penalty] = (train_prediction, evaluation_prediction, effective_df)
    positive = eigenvalues[eigenvalues > np.finfo(float).eps]
    diagnostics = {
        "solver": solver,
        "rank": int((eigenvalues > max(float(eigenvalues.max(initial=0)) * 1e-10, 1e-12)).sum()),
        "largest_eigenvalue": float(eigenvalues.max(initial=0)),
        "smallest_positive_eigenvalue": float(positive.min()) if len(positive) else None,
        "condition_number_positive": float(positive.max() / positive.min()) if len(positive) else None,
    }
    return result, diagnostics


def mode_values(config: dict[str, Any], mode: str) -> tuple[list[float], list[int], list[int], int | None]:
    block = config["complexity"]["modes"][mode]
    return (
        [float(x) for x in block["ratios"]],
        [int(x) for x in block["windows"]],
        [int(x) for x in block["seeds"]],
        int(block["refit_origins"]) if "refit_origins" in block else None,
    )


def summarize(run_dir: Path, config: dict[str, Any]) -> None:
    checkpoints = sorted((run_dir / "checkpoints").glob("*.parquet"))
    if not checkpoints:
        raise RuntimeError("No completed checkpoints are available to summarize")
    predictions = pd.concat([pd.read_parquet(path) for path in checkpoints], ignore_index=True)
    predictions = predictions.sort_values(["config_id", "signal_session"])
    atomic_parquet_dump(predictions, run_dir / "predictions.parquet")
    evaluation = config["evaluation"]
    metrics, annual, ledgers = activity_tables(
        predictions,
        forecast_hurdle=float(evaluation["forecast_hurdle"]),
        one_way_cost_bps=float(evaluation["one_way_cost_bps"]),
        annualization=int(evaluation["annualization_sessions"]),
    )
    configuration_columns = ["config_id", "complexity_ratio", "realized_ratio", "window_observations", "map_seed", "penalty", "generated_features", "effective_df", "rank", "solver", "train_mse", "fit_seconds"]
    configuration = predictions[configuration_columns].groupby("config_id", as_index=False).median(numeric_only=True)
    first_text = predictions.groupby("config_id", as_index=False)[["solver"]].first()
    configuration = configuration.drop(columns=["solver"], errors="ignore").merge(first_text, on="config_id")
    metrics = metrics.merge(configuration, on="config_id", how="left", validate="one_to_one")
    metrics["activity_gate_pass"] = (
        metrics["active_sessions"].ge(config["diagnostics"]["minimum_active_sessions"])
        & metrics["completed_round_trips"].ge(config["diagnostics"]["minimum_completed_round_trips"])
        & metrics["metric_status"].eq("valid")
    )
    metrics.to_csv(run_dir / "config_metrics.csv", index=False)
    annual.to_csv(run_dir / "activity_by_year.csv", index=False)
    atomic_parquet_dump(ledgers, run_dir / "strategy_ledgers.parquet")

    plot_frame = metrics.groupby(["complexity_ratio", "penalty"], as_index=False).agg(
        median_oos_r2=("oos_r2_vs_historical_mean", "median"),
        median_net_sharpe=("net_sharpe", "median"),
        median_exposure=("average_exposure", "median"),
        median_effective_df=("effective_df", "median"),
    )
    figures = run_dir / "figures"
    figures.mkdir(exist_ok=True)
    for value, label, filename in [
        ("median_oos_r2", "Median OOS R² vs historical mean", "complexity_oos_r2_heatmap.png"),
        ("median_net_sharpe", "Median net Sharpe", "complexity_net_sharpe_heatmap.png"),
        ("median_exposure", "Median exposure", "complexity_exposure_heatmap.png"),
    ]:
        pivot = plot_frame.pivot(index="complexity_ratio", columns="penalty", values=value)
        fig, ax = plt.subplots(figsize=(9.0, 6.5))
        sns.heatmap(pivot, cmap="vlag", center=0 if value != "median_exposure" else None, annot=True, fmt=".3f", ax=ax)
        ax.set_xlabel("Ridge penalty λ")
        ax.set_ylabel("Nominal complexity P/T")
        ax.set_title(label)
        fig.tight_layout()
        fig.savefig(figures / filename, dpi=240)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/research_extension_2026-10-21.yaml")
    parser.add_argument("--mode", choices=["pilot", "primary", "window_sensitivity", "seed_sensitivity"], default="pilot")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-hours", type=float)
    parser.add_argument("--output-root", default="artifacts/research/complexity_runs")
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    config = read_yaml(config_path)
    frame, feature_manifest, feature_columns, feature_dir = load_feature_dataset(
        ROOT, config["feature_dataset_id"], config["feature_set"]
    )
    bounds = config["evaluation"]
    evaluation = frame.loc[
        frame["signal_session"].between(pd.Timestamp(bounds["start"]), pd.Timestamp(bounds["end"]))
        & frame["target_return"].notna()
    ].copy()
    blocks = monthly_blocks(evaluation)
    ratios, windows, seeds, origin_count = mode_values(config, args.mode)
    if origin_count:
        blocks = evenly_spaced(blocks, origin_count)
    penalties = [float(x) for x in config["complexity"]["penalties"]]
    tasks = [(window, seed, ratio, origin, block) for window in windows for seed in seeds for ratio in ratios for origin, block in blocks]
    largest_p = max(int(round(max(ratios) * window)) for window in windows)
    largest_window = max(windows)
    estimated_gb = estimate_dense_gb(largest_window, largest_p)
    identity = {
        "config_sha256": sha256_file(config_path),
        "feature_manifest_sha256": sha256_file(feature_dir / "manifest.json"),
        "mode": args.mode,
        "ratios": ratios,
        "windows": windows,
        "seeds": seeds,
        "penalties": penalties,
        "origins": [origin.isoformat() for origin, _ in blocks],
    }
    run_id = deterministic_run_id(f"complexity_{args.mode}", identity)
    run_dir = ROOT / args.output_root / run_id
    plan = {
        "mode": "execute" if args.execute else "plan_only",
        "run_id": run_id,
        "research_status": config["research_status"],
        "feature_dataset_id": feature_manifest["dataset_id"],
        "input_features": len(feature_columns),
        "refit_origins": len(blocks),
        "decompositions": len(tasks),
        "coefficient_solutions": len(tasks) * len(penalties),
        "largest_generated_feature_count": largest_p,
        "estimated_largest_dense_working_set_gb": round(estimated_gb, 3),
        "configured_memory_limit_gb": config["compute"]["maximum_memory_gb"],
        "output_directory": str(run_dir),
    }
    if estimated_gb > float(config["compute"]["maximum_memory_gb"]):
        raise MemoryError(f"Estimated dense working set {estimated_gb:.2f} GB exceeds configured limit")
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    if run_dir.exists() and not args.resume:
        raise FileExistsError(f"Run already exists; use --resume: {run_dir}")
    checkpoints = run_dir / "checkpoints"
    checkpoints.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "run_manifest.json"
    started_wall = time.perf_counter()
    maximum_hours = float(args.max_hours or config["compute"]["maximum_hours"])
    completed = 0
    skipped = 0
    recent_seconds: list[float] = []
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "status": "running",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "identity": identity,
        "plan": plan,
        "environment": environment_record(),
        "completed_decompositions": 0,
    }
    atomic_json_dump(manifest, manifest_path)
    progress = tqdm(tasks, desc=f"Complexity {args.mode}", unit="decomposition")
    for window, seed, ratio, origin, block in progress:
        if (time.perf_counter() - started_wall) / 3600 >= maximum_hours:
            manifest.update(status="budget_stop", completed_decompositions=completed, skipped_existing=skipped)
            atomic_json_dump(manifest, manifest_path)
            progress.close()
            print(json.dumps({"run_id": run_id, "status": "budget_stop", "resume_command": f"python scripts/run_complexity_experiment.py --mode {args.mode} --execute --resume"}, indent=2))
            return
        p = max(1, int(round(ratio * window)))
        task_id = stable_object_hash({"window": window, "seed": seed, "ratio": ratio, "origin": origin.isoformat()})[:20]
        checkpoint = checkpoints / f"{task_id}.parquet"
        metadata = checkpoints / f"{task_id}.json"
        if args.resume and checkpoint.is_file() and metadata.is_file():
            skipped += 1
            continue
        eligible = frame.loc[
            frame["target_return"].notna()
            & frame["label_available_session"].le(origin)
            & frame["signal_session"].ge(pd.Timestamp(bounds["initial_train_start"]))
        ].tail(window)
        if len(eligible) < window:
            raise ValueError(f"Only {len(eligible)} eligible rows for requested T={window} at {origin.date()}")
        task_started = time.perf_counter()
        imputer = SimpleImputer(strategy="median")
        scaler = StandardScaler()
        x_train = scaler.fit_transform(imputer.fit_transform(eligible[feature_columns]))
        x_eval = scaler.transform(imputer.transform(block[feature_columns]))
        y_train = eligible["target_return"].to_numpy(float)
        gamma = float(config["complexity"]["gamma_scale"]) / len(feature_columns)
        raw_train = rff_bank(x_train, components=p, gamma=gamma, seed=seed)
        raw_eval = rff_bank(x_eval, components=p, gamma=gamma, seed=seed)
        means = raw_train.mean(axis=0)
        scales = raw_train.std(axis=0, ddof=0)
        keep = scales > 1e-12
        z_train = (raw_train[:, keep] - means[keep]) / scales[keep]
        z_eval = (raw_eval[:, keep] - means[keep]) / scales[keep]
        with threadpool_limits(limits=int(config["compute"]["numerical_threads"])):
            paths, diagnostics = ridge_path(z_train, y_train, z_eval, penalties)
        elapsed = time.perf_counter() - task_started
        recent_seconds.append(elapsed)
        recent_seconds = recent_seconds[-int(config["compute"]["recent_jobs_for_eta"]):]
        output_rows: list[pd.DataFrame] = []
        for penalty in penalties:
            train_prediction, evaluation_prediction, effective_df = paths[penalty]
            config_id = "rff_complexity_" + stable_object_hash({"window": window, "seed": seed, "ratio": ratio, "penalty": penalty})[:12]
            output = block[["signal_session", "entry_session", "label_end_session", "label_available_session", "target_return", "split"]].copy()
            output["prediction"] = evaluation_prediction
            output["baseline_prediction"] = float(y_train.mean())
            output["config_id"] = config_id
            output["family"] = "rff_ridge_complexity"
            output["refit_origin"] = origin
            output["window_observations"] = window
            output["n_train"] = len(eligible)
            output["n_input_features"] = len(feature_columns)
            output["generated_features"] = int(z_train.shape[1])
            output["complexity_ratio"] = ratio
            output["realized_ratio"] = z_train.shape[1] / len(eligible)
            output["map_seed"] = seed
            output["penalty"] = penalty
            output["effective_df"] = effective_df
            output["rank"] = diagnostics["rank"]
            output["solver"] = diagnostics["solver"]
            output["train_mse"] = float(np.mean(np.square(y_train - train_prediction)))
            output["fit_seconds"] = elapsed
            output["train_start"] = eligible["signal_session"].min()
            output["train_last_signal"] = eligible["signal_session"].max()
            output["train_last_label_available"] = eligible["label_available_session"].max()
            output_rows.append(output)
        combined = pd.concat(output_rows, ignore_index=True)
        atomic_parquet_dump(combined, checkpoint)
        atomic_json_dump({
            "task_id": task_id,
            "origin": origin.isoformat(),
            "window_observations": window,
            "map_seed": seed,
            "requested_ratio": ratio,
            "requested_features": p,
            "retained_features": int(z_train.shape[1]),
            "raw_feature_normalization": "sqrt(2) then training-only column standardization",
            "nested_bank_contract": "first P columns from deterministic seed-specific maximum-compatible draw",
            "gamma": gamma,
            "penalties": penalties,
            "fit_seconds": elapsed,
            "peak_rss_mb": peak_rss_mb(),
            **diagnostics,
            "checkpoint_sha256": sha256_file(checkpoint),
        }, metadata)
        completed += 1
        remaining = len(tasks) - completed - skipped
        eta_minutes = remaining * float(np.median(recent_seconds)) / 60 if recent_seconds else math.nan
        progress.set_postfix(P=p, ratio=ratio, eta_min=f"{eta_minutes:.0f}")
        manifest.update(completed_decompositions=completed, skipped_existing=skipped, updated_at_utc=datetime.now(timezone.utc).isoformat())
        atomic_json_dump(manifest, manifest_path)
    progress.close()
    summarize(run_dir, config)
    manifest.update(
        status="complete",
        completed_at_utc=datetime.now(timezone.utc).isoformat(),
        completed_decompositions=len(tasks),
        skipped_existing=skipped,
        elapsed_seconds=time.perf_counter() - started_wall,
        outputs={
            "predictions": "predictions.parquet",
            "metrics": "config_metrics.csv",
            "annual_activity": "activity_by_year.csv",
            "ledgers": "strategy_ledgers.parquet",
            "figures": "figures",
        },
    )
    atomic_json_dump(manifest, manifest_path)
    print(json.dumps({"run_id": run_id, "status": "complete", "output_directory": str(run_dir)}, indent=2))


if __name__ == "__main__":
    main()

