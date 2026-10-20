"""Profile representative model fits before committing to the research budget.

The default mode prints the plan. Add --execute to fit models and write a
content-addressed profile. This script never starts the full research search.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from threadpoolctl import threadpool_limits
from tqdm import tqdm

from quantfin.io import atomic_json_dump, package_versions, sha256_file, stable_object_hash
from quantfin.models import build_estimator


ROOT = Path(__file__).resolve().parents[1]
FEATURE_DIRECTORY = ROOT / "data/processed/features_yahoo_20261019T010846Z_799f619a4f"
REPRESENTATIVE_CONFIGS = [
    {"family": "random_forest", "parameters": {"max_depth": 3, "min_samples_leaf": 50, "n_estimators": 300, "max_features": 0.5}},
]


def peak_rss_mb() -> float | None:
    try:
        import resource
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return float(value / (1024 * 1024) if platform.system() == "Darwin" else value / 1024)
    except (ImportError, AttributeError, ValueError):
        try:
            import psutil
            return float(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024))
        except (ImportError, OSError):
            return None


def load_sample(max_observations: int) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    manifest = json.loads((FEATURE_DIRECTORY / "manifest.json").read_text(encoding="utf-8"))
    path = FEATURE_DIRECTORY / manifest["file"]["path"]
    frame = pd.read_parquet(path)
    frame["signal_session"] = pd.to_datetime(frame["signal_session"])
    frame["label_available_session"] = pd.to_datetime(frame["label_available_session"])
    cutoff = pd.Timestamp("2021-12-31")
    eligible = frame.loc[
        frame["target_return"].notna()
        & frame["label_available_session"].notna()
        & frame["label_available_session"].le(cutoff)
    ].sort_values("signal_session")
    eligible = eligible.tail(max_observations)
    feature_names = list(manifest["feature_sets"]["F2"])
    return eligible[feature_names], eligible["target_return"], feature_names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/research.yaml")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--sample-sizes", type=int, nargs="+", default=[1000, 2500, 4000])
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--estimator-jobs", type=int, choices=[1, 2], default=1)
    parser.add_argument("--max-minutes", type=float, default=20.0)
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    plan = [
        {"family": item["family"], "sample_size": size, "repeat": repeat}
        for size in args.sample_sizes
        for item in REPRESENTATIVE_CONFIGS
        for repeat in range(1, args.repeats + 1)
    ]
    if not args.execute:
        print(json.dumps({
            "mode": "plan_only",
            "planned_fits": len(plan),
            "estimator_jobs": args.estimator_jobs,
            "max_minutes": args.max_minutes,
            "fits": plan,
            "next_step": "Repeat with --execute to run only this bounded profiler.",
        }, indent=2))
        return

    largest = max(args.sample_sizes)
    X_all, y_all, features = load_sample(largest)
    started = time.perf_counter()
    records: list[dict[str, Any]] = []
    stopped_for_budget = False
    progress = tqdm(plan, desc="Profiling representative fits", unit="fit")
    for task in progress:
        if (time.perf_counter() - started) / 60.0 >= args.max_minutes:
            stopped_for_budget = True
            break
        configuration = next(item for item in REPRESENTATIVE_CONFIGS if item["family"] == task["family"])
        sample_size = min(task["sample_size"], len(X_all))
        X = X_all.tail(sample_size)
        y = y_all.loc[X.index]
        estimator, selected_columns = build_estimator(
            configuration,
            random_seed=int(config["compute_budget"]["random_seed"]),
            n_jobs=args.estimator_jobs,
            input_feature_count=len(features),
        )
        if selected_columns is not None:
            X = X[selected_columns]
        rss_before = peak_rss_mb()
        fit_started = time.perf_counter()
        with threadpool_limits(limits=int(config["compute_budget"]["numerical_threads_per_fit"])):
            estimator.fit(X, y)
            prediction = estimator.predict(X.tail(min(20, len(X))))
        seconds = time.perf_counter() - fit_started
        rss_after = peak_rss_mb()
        record = {
            **task,
            "actual_observations": int(len(X)),
            "input_features": int(X.shape[1]),
            "fit_and_probe_seconds": seconds,
            "peak_rss_mb_before": rss_before,
            "peak_rss_mb_after": rss_after,
            "probe_prediction_mean": float(np.mean(prediction)),
            "status": "complete",
        }
        records.append(record)
        progress.set_postfix(family=task["family"], seconds=f"{seconds:.1f}")
    progress.close()

    completed_seconds = sum(item["fit_and_probe_seconds"] for item in records)
    median_seconds = float(np.median([item["fit_and_probe_seconds"] for item in records])) if records else None
    identity = {
        "protocol_sha256": sha256_file(config_path),
        "feature_manifest_sha256": sha256_file(FEATURE_DIRECTORY / "manifest.json"),
        "sample_sizes": args.sample_sizes,
        "repeats": args.repeats,
        "estimator_jobs": args.estimator_jobs,
        "representative_configs": REPRESENTATIVE_CONFIGS,
    }
    profile_id = "compute_" + stable_object_hash(identity)[:16]
    output = ROOT / "artifacts/research/compute_profiles" / profile_id / "profile.json"
    report = {
        "schema_version": 1,
        "profile_id": profile_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "budget_stop" if stopped_for_budget else "complete",
        "identity": identity,
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": platform.python_version(),
            "logical_cpus": os.cpu_count(),
            "packages": package_versions(["numpy", "pandas", "scikit-learn", "threadpoolctl", "pyarrow"]),
        },
        "planned_fits": len(plan),
        "completed_fits": len(records),
        "elapsed_seconds": time.perf_counter() - started,
        "sum_fit_seconds": completed_seconds,
        "median_representative_fit_seconds": median_seconds,
        "records": records,
        "guidance": "Use measured family-specific times and memory to bound A10. Run once with one estimator job and once with two; select the safer setting before the full search.",
    }
    if output.exists():
        raise FileExistsError(
            f"Profile already exists for these inputs: {output}. Change an explicit profiling input to create a new identity."
        )
    atomic_json_dump(report, output)
    print(output)


if __name__ == "__main__":
    main()

