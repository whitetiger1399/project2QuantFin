"""Export a reproducible feature dictionary from the feature manifest and names."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

from quantfin.io import atomic_json_dump
from quantfin.research_extension import load_feature_dataset


ROOT = Path(__file__).resolve().parents[1]


def definition(name: str) -> tuple[str, str, str]:
    window = next(iter(re.findall(r"(?:^|_)(\d+)(?:_|$)", name)), "")
    if "log_return_lag" in name:
        return "log(P_t/P_{t-1}) shifted by the stated lag", "return", "adjusted close"
    if "momentum" in name:
        return "P_t/P_{t-w}-1", "ratio", "adjusted close"
    if "volatility" in name:
        return "rolling standard deviation of daily log returns", "daily standard deviation", "adjusted close"
    if "correlation" in name:
        return "rolling Pearson correlation of named asset returns", "correlation", "adjusted close"
    if "drawdown" in name:
        return "P_t/max(P over trailing window)-1", "ratio", "adjusted close"
    if "sma" in name or "ema" in name:
        return "named moving-average price ratio or slope", "ratio", "adjusted close"
    if "volume" in name or "obv" in name or "illiquidity" in name:
        return "causal rolling transformation of observed volume and return", "ratio or standardized value", "volume and adjusted close"
    if any(token in name for token in ["rsi", "bollinger", "stochastic", "macd"]):
        return "causal technical indicator named by the feature", "scaled indicator", "OHLC adjusted consistently"
    if any(token in name for token in ["weekday", "month", "calendar"]):
        return "deterministic calendar encoding known at decision time", "indicator", "exchange session date"
    if "intraday" in name or "overnight" in name or "daily_range" in name:
        return "same-session OHLC ratio available after close", "return or range", "OHLC adjusted consistently"
    if "_x_" in name:
        return "product of the two named, already-causal features", "interaction", "derived"
    if "change_" in name:
        return "difference or percentage change over stated sessions", "change", "release-aware context source"
    if "age_days" in name:
        return "signal date minus source observation date", "days", "release-aware context source"
    return "See feature builder implementation for the named causal transformation", "varies", "derived"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feature-dataset-id", default="features_yahoo_20261020T055638Z_799f619a4f")
    parser.add_argument("--feature-set", default="F2")
    parser.add_argument("--output-dir", default="artifacts/research/feature_dictionary_2026-10-21")
    args = parser.parse_args()
    _, manifest, features, _ = load_feature_dataset(ROOT, args.feature_dataset_id, args.feature_set)
    group_map = {feature: group for group, names in manifest.get("feature_groups", {}).items() for feature in names}
    rows = []
    for feature in features:
        formula, units, source = definition(feature)
        rows.append({
            "feature": feature,
            "feature_set": args.feature_set,
            "group": group_map.get(feature, "unclassified"),
            "definition": formula,
            "units": units,
            "source": source,
            "availability": "computed using information observed by signal_session after market close",
            "missing_policy": "median imputation fitted independently on each eligible training window",
        })
    output = ROOT / args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame(rows)
    table.to_csv(output / "feature_dictionary.csv", index=False)
    atomic_json_dump({"dataset_id": args.feature_dataset_id, "feature_set": args.feature_set, "declared_features": len(features), "dictionary_rows": len(table), "complete": set(features) == set(table["feature"])}, output / "manifest.json")
    print(json.dumps({"output_directory": str(output), "rows": len(table), "complete": True}, indent=2))


if __name__ == "__main__":
    main()

