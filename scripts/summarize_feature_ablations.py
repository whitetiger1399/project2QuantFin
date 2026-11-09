"""Compare F0/F1/F2 screening runs on matched model/session observations."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from quantfin.io import atomic_json_dump, stable_object_hash


ROOT = Path(__file__).resolve().parents[1]


def moving_block_interval(values: np.ndarray, repetitions: int, block: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    samples = []
    for _ in range(repetitions):
        draw = []
        while len(draw) < n:
            start = int(rng.integers(0, n - block + 1))
            draw.extend(values[start:start + block])
        samples.append(float(np.mean(draw[:n])))
    return float(np.quantile(samples, .025)), float(np.quantile(samples, .975))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--f0-run-id", required=True)
    parser.add_argument("--f1-run-id", required=True)
    parser.add_argument("--f2-run-id", required=True)
    parser.add_argument("--family", default="random_forest")
    parser.add_argument("--bootstrap-repetitions", type=int, default=2000)
    parser.add_argument("--block-length", type=int, default=20)
    parser.add_argument("--output-root", default="artifacts/research/feature_ablations")
    args = parser.parse_args()
    run_map = {"F0": args.f0_run_id, "F1": args.f1_run_id, "F2": args.f2_run_id}
    predictions: dict[str, pd.DataFrame] = {}
    metrics = []
    dataset_id = None
    for feature_set, run_id in run_map.items():
        directory = ROOT / "artifacts/runs" / run_id
        manifest = json.loads((directory / "run_manifest.json").read_text(encoding="utf-8"))
        if manifest.get("status") != "complete" or manifest["inputs"]["stage"] != "screening":
            raise ValueError(f"{run_id} must be a completed screening run")
        if manifest["inputs"]["feature_set"] != feature_set:
            raise ValueError(f"{run_id} declares {manifest['inputs']['feature_set']}, expected {feature_set}")
        dataset_id = dataset_id or manifest["inputs"]["feature_dataset_id"]
        if manifest["inputs"]["feature_dataset_id"] != dataset_id:
            raise ValueError("Ablation runs use different feature datasets")
        data = pd.read_parquet(directory / "predictions.parquet")
        subset = data.loc[data["family"].eq(args.family)].copy()
        if subset["config_id"].nunique() != 1:
            raise ValueError(f"Expected one {args.family} configuration in {run_id}")
        predictions[feature_set] = subset[["signal_session", "target_return", "prediction"]].rename(columns={"prediction": f"prediction_{feature_set}"})
        table = pd.read_csv(directory / "config_metrics.csv")
        row = table.loc[table["family"].eq(args.family)].copy()
        row.insert(0, "feature_set", feature_set)
        row.insert(1, "run_id", run_id)
        metrics.append(row)
    merged = predictions["F0"]
    for feature_set in ["F1", "F2"]:
        merged = merged.merge(predictions[feature_set], on=["signal_session", "target_return"], validate="one_to_one")
    comparisons = []
    for left, right in [("F1", "F0"), ("F2", "F1"), ("F2", "F0")]:
        difference = np.square(merged["target_return"] - merged[f"prediction_{left}"]) - np.square(merged["target_return"] - merged[f"prediction_{right}"])
        lower, upper = moving_block_interval(difference.to_numpy(), args.bootstrap_repetitions, args.block_length, 29)
        comparisons.append({"comparison": f"{left}_minus_{right}", "mean_squared_error_difference": float(difference.mean()), "confidence_lower": lower, "confidence_upper": upper, "interpretation": "negative favors the first feature set"})
    identity = {"runs": run_map, "family": args.family, "bootstrap_repetitions": args.bootstrap_repetitions, "block_length": args.block_length}
    output = ROOT / args.output_root / ("ablation_" + stable_object_hash(identity)[:16])
    output.mkdir(parents=True, exist_ok=True)
    pd.concat(metrics, ignore_index=True).to_csv(output / "ablation_metrics.csv", index=False)
    pd.DataFrame(comparisons).to_csv(output / "paired_mse_differences.csv", index=False)
    atomic_json_dump({"schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(), "status": "complete", "identity": identity, "matched_sessions": len(merged), "dataset_id": dataset_id}, output / "manifest.json")
    print(json.dumps({"status": "complete", "output_directory": str(output), "matched_sessions": len(merged)}, indent=2))


if __name__ == "__main__":
    main()

