#!/usr/bin/env python3
"""Paired date-block inference for the saved signed strategy and timing comparators."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def annualized_sharpe(values: np.ndarray) -> float:
    std = float(np.std(values, ddof=1))
    return float(np.sqrt(252) * np.mean(values) / std) if std > 0 else float("nan")


def circular_indices(rng: np.random.Generator, n: int, block: int) -> np.ndarray:
    starts = rng.integers(0, n, size=int(np.ceil(n / block)))
    return np.concatenate([(start + np.arange(block)) % n for start in starts])[:n]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-registry", type=Path, required=True)
    parser.add_argument("--draws", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--block-lengths", type=int, nargs="+", default=[5, 10, 20])
    args = parser.parse_args()
    registry_path = args.release_registry if args.release_registry.is_absolute() else ROOT / args.release_registry
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    ids = registry["ids"]
    sources = {
        "2025 historical replication": ROOT / "artifacts/cross_market_ai_capability/analysis" / ids["STRATEGY_ANALYSIS_ID"] / "strategy_ledgers.parquet",
        "2026 retrospective extension": ROOT / "artifacts/cross_market_ai_capability_2026/analysis" / ids["FORWARD_STRATEGY_ANALYSIS_ID"] / "strategy_ledgers.parquet",
    }
    comparators = ["cohort_mean_signed", "services_direction_equal_weight"]
    identity = {
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in sources.values()},
        "comparators": comparators,
        "draws": args.draws,
        "seed": args.seed,
        "block_lengths": args.block_lengths,
    }
    content_hash = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:12]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    analysis_id = f"paired_strategy_inference_{timestamp}_{content_hash}"
    output = ROOT / "artifacts/cross_market_ai_capability/analysis" / analysis_id
    output.mkdir(parents=True, exist_ok=False)

    rows = []
    total = len(sources) * len(comparators) * len(args.block_lengths) * args.draws
    progress = tqdm(total=total, desc="Paired strategy bootstrap", unit="draw")
    for period_index, (period, path) in enumerate(sources.items()):
        frame = pd.read_parquet(path)
        frame["decision_date"] = pd.to_datetime(frame["decision_date"])
        selected = frame.loc[frame.strategy.eq("signed_forecast"), ["decision_date", "net_return", "turnover", "gross_exposure"]]
        selected = selected.rename(columns={"net_return": "selected", "turnover": "selected_turnover", "gross_exposure": "selected_gross"})
        for comparator_index, comparator in enumerate(comparators):
            other = frame.loc[frame.strategy.eq(comparator), ["decision_date", "net_return", "turnover", "gross_exposure"]]
            other = other.rename(columns={"net_return": "comparator", "turnover": "comparator_turnover", "gross_exposure": "comparator_gross"})
            aligned = selected.merge(other, on="decision_date", how="inner", validate="one_to_one").sort_values("decision_date")
            if len(aligned) != len(selected) or len(aligned) != len(other):
                raise ValueError(f"Unmatched dates for {period} / {comparator}")
            a = aligned.selected.to_numpy(float)
            b = aligned.comparator.to_numpy(float)
            for block in args.block_lengths:
                mean_draws = np.empty(args.draws)
                sharpe_draws = np.empty(args.draws)
                rng = np.random.default_rng(args.seed + 1000 * period_index + 100 * comparator_index + block)
                for draw in range(args.draws):
                    index = circular_indices(rng, len(aligned), block)
                    mean_draws[draw] = np.mean(a[index] - b[index]) * 10000
                    sharpe_draws[draw] = annualized_sharpe(a[index]) - annualized_sharpe(b[index])
                    progress.update(1)
                rows.append({
                    "period": period,
                    "comparator": comparator,
                    "sessions": len(aligned),
                    "block_length_sessions": block,
                    "draws": args.draws,
                    "seed": args.seed,
                    "mean_daily_difference_bps": float(np.mean(a - b) * 10000),
                    "mean_daily_difference_ci_low_bps": float(np.quantile(mean_draws, .025)),
                    "mean_daily_difference_ci_high_bps": float(np.quantile(mean_draws, .975)),
                    "selected_sharpe": annualized_sharpe(a),
                    "comparator_sharpe": annualized_sharpe(b),
                    "sharpe_difference": annualized_sharpe(a) - annualized_sharpe(b),
                    "sharpe_difference_ci_low": float(np.nanquantile(sharpe_draws, .025)),
                    "sharpe_difference_ci_high": float(np.nanquantile(sharpe_draws, .975)),
                    "selected_mean_turnover": float(aligned.selected_turnover.mean()),
                    "comparator_mean_turnover": float(aligned.comparator_turnover.mean()),
                    "selected_mean_gross_exposure": float(aligned.selected_gross.mean()),
                    "comparator_mean_gross_exposure": float(aligned.comparator_gross.mean()),
                })
    progress.close()
    summary = pd.DataFrame(rows)
    summary_path = output / "paired_strategy_inference.csv"
    summary.to_csv(summary_path, index=False)
    manifest = {
        "analysis_id": analysis_id,
        "status": "complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": "paired circular date-block bootstrap; identical resampled dates for both policies",
        "identity": identity,
        "files": {summary_path.name: sha256(summary_path)},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"analysis_id": analysis_id, "status": "complete", "directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()
