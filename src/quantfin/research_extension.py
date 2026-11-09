"""Shared, leakage-aware utilities for the dated research extension."""

from __future__ import annotations

import json
import math
import os
import platform
import resource
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import yaml

from .evaluation import strategy_returns
from .io import package_versions, sha256_file, stable_object_hash


def read_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return value


def load_feature_dataset(
    project_root: Path, dataset_id: str, feature_set: str
) -> tuple[pd.DataFrame, dict[str, Any], list[str], Path]:
    directory = project_root / "data" / "processed" / dataset_id
    manifest_path = directory / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Feature manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("dataset_id") != dataset_id:
        raise ValueError("Feature directory and manifest dataset IDs disagree")
    try:
        columns = list(manifest["feature_sets"][feature_set])
    except KeyError as exc:
        raise ValueError(f"Unknown feature set {feature_set!r}") from exc
    parquet = directory / manifest["file"]["path"]
    if sha256_file(parquet) != manifest["file"]["sha256"]:
        raise ValueError(f"Feature parquet hash does not match manifest: {parquet}")
    frame = pd.read_parquet(parquet)
    for column in ["signal_session", "entry_session", "label_end_session", "label_available_session"]:
        frame[column] = pd.to_datetime(frame[column])
    missing = sorted(set(columns).difference(frame.columns))
    if missing:
        raise ValueError(f"Feature parquet is missing declared columns: {missing}")
    return frame.sort_values("signal_session"), manifest, columns, directory


def monthly_blocks(frame: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.DataFrame]]:
    ordered = frame.sort_values("signal_session").copy()
    ordered["_month"] = ordered["signal_session"].dt.to_period("M")
    return [
        (pd.Timestamp(group["signal_session"].min()), group.drop(columns="_month").copy())
        for _, group in ordered.groupby("_month", sort=True)
    ]


def completed_round_trips(position: pd.Series) -> int:
    values = position.fillna(0.0).gt(0).astype(int)
    changes = values.diff().fillna(values.iloc[0] if len(values) else 0)
    entries = int(changes.gt(0).sum())
    exits = int(changes.lt(0).sum())
    if len(values) and values.iloc[-1] > 0:
        exits += 1
    return min(entries, exits)


def metric_status(returns: pd.Series, position: pd.Series) -> str:
    clean = returns.dropna()
    if clean.empty:
        return "insufficient_observations"
    if float(position.fillna(0).abs().sum()) == 0.0:
        return "no_trade"
    if len(clean) < 20:
        return "insufficient_observations"
    if not np.isfinite(clean.std(ddof=1)) or clean.std(ddof=1) <= 0:
        return "zero_variance"
    return "valid"


def annualized_metrics(returns: pd.Series, annualization: int = 252) -> dict[str, float]:
    clean = returns.dropna().astype(float)
    if clean.empty:
        return {k: np.nan for k in ["annualized_mean", "annualized_volatility", "sharpe", "cagr", "max_drawdown"]}
    volatility = float(clean.std(ddof=1) * np.sqrt(annualization))
    annual_mean = float(clean.mean() * annualization)
    wealth = np.concatenate([[1.0], np.cumprod(1.0 + clean.to_numpy())])
    drawdown = wealth / np.maximum.accumulate(wealth) - 1.0
    years = len(clean) / annualization
    terminal = float(wealth[-1])
    return {
        "annualized_mean": annual_mean,
        "annualized_volatility": volatility,
        "sharpe": annual_mean / volatility if volatility > 0 else np.nan,
        "cagr": terminal ** (1.0 / years) - 1.0 if years > 0 and terminal > 0 else np.nan,
        "max_drawdown": float(drawdown.min()),
    }


def activity_tables(
    predictions: pd.DataFrame,
    *,
    forecast_hurdle: float,
    one_way_cost_bps: float,
    annualization: int = 252,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summaries: list[dict[str, Any]] = []
    yearly: list[dict[str, Any]] = []
    ledgers: list[pd.DataFrame] = []
    if "baseline_prediction" in predictions:
        baseline_lookup = None
    else:
        baseline_rows = predictions.loc[
            predictions["family"].eq("historical_mean"), ["signal_session", "prediction"]
        ].drop_duplicates("signal_session")
        baseline_lookup = baseline_rows.set_index("signal_session")["prediction"]
    for config_id, group in predictions.groupby("config_id", sort=False):
        group = group.copy()
        if "baseline_prediction" not in group:
            group["baseline_prediction"] = group["signal_session"].map(baseline_lookup)
        ledger = strategy_returns(
            group,
            forecast_hurdle=forecast_hurdle,
            one_way_cost_bps=one_way_cost_bps,
        )
        ledger["config_id"] = config_id
        ledgers.append(ledger)
        family = str(group["family"].iloc[0]) if "family" in group else "unknown"
        by_year = ledger.assign(year=ledger["pnl_session"].dt.year).groupby("year", sort=True)
        annual_sharpes: list[float] = []
        for year, annual in by_year:
            status = metric_status(annual["net_strategy_return"], annual["position"])
            measures = annualized_metrics(annual["net_strategy_return"], annualization)
            annual_sharpes.append(measures["sharpe"])
            yearly.append({
                "config_id": config_id,
                "family": family,
                "pnl_year": int(year),
                "observations": int(len(annual)),
                "active_sessions": int(annual["position"].gt(0).sum()),
                "average_exposure": float(annual["position"].mean()),
                "completed_round_trips": completed_round_trips(annual["position"]),
                "metric_status": status,
                **measures,
                "first_signal_session": annual["signal_session"].min(),
                "last_signal_session": annual["signal_session"].max(),
                "first_pnl_session": annual["pnl_session"].min(),
                "last_pnl_session": annual["pnl_session"].max(),
            })
        overall_status = metric_status(ledger["net_strategy_return"], ledger["position"])
        overall = annualized_metrics(ledger["net_strategy_return"], annualization)
        valid_annual = [x for x in annual_sharpes if np.isfinite(x)]
        error = ledger["target_return"] - ledger["prediction"]
        baseline_error = ledger["target_return"] - ledger["baseline_prediction"]
        denominator = float(np.square(baseline_error.dropna()).sum())
        summaries.append({
            "config_id": config_id,
            "family": family,
            "observations": int(len(ledger)),
            "mse": float(np.square(error).mean()),
            "mae": float(error.abs().mean()),
            "oos_r2_vs_historical_mean": (
                1.0 - float(np.square(error.dropna()).sum()) / denominator if denominator > 0 else np.nan
            ),
            "active_sessions": int(ledger["position"].gt(0).sum()),
            "average_exposure": float(ledger["position"].mean()),
            "completed_round_trips": completed_round_trips(ledger["position"]),
            "metric_status": overall_status,
            "valid_annual_sharpe_years": len(valid_annual),
            "median_annual_net_sharpe": float(np.median(valid_annual)) if valid_annual else np.nan,
            "signal_start": ledger["signal_session"].min(),
            "signal_end": ledger["signal_session"].max(),
            "pnl_start": ledger["pnl_session"].min(),
            "pnl_end": ledger["pnl_session"].max(),
            "prediction_std": float(ledger["prediction"].std(ddof=1)),
            "fraction_above_hurdle": float(ledger["prediction"].gt(forecast_hurdle).mean()),
            **{f"net_{key}": value for key, value in overall.items()},
        })
    return pd.DataFrame(summaries), pd.DataFrame(yearly), pd.concat(ledgers, ignore_index=True)


def peak_rss_mb() -> float | None:
    try:
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return float(value / (1024 * 1024) if platform.system() == "Darwin" else value / 1024)
    except (AttributeError, ValueError):
        return None


def environment_record() -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "logical_cpus": os.cpu_count(),
        "packages": package_versions(["numpy", "pandas", "pyarrow", "scikit-learn", "scipy", "statsmodels"]),
    }


def deterministic_run_id(prefix: str, identity: dict[str, Any]) -> str:
    return f"{prefix}_{stable_object_hash(identity)[:16]}"


def estimate_dense_gb(rows: int, columns: int, arrays: float = 2.5) -> float:
    return float(rows * columns * 8 * arrays / (1024**3))


def evenly_spaced(items: list[Any], count: int) -> list[Any]:
    if count >= len(items):
        return items
    indices = np.linspace(0, len(items) - 1, count).round().astype(int)
    return [items[index] for index in sorted(set(indices.tolist()))]


def finite_or_none(value: Any) -> float | None:
    number = float(value)
    return number if math.isfinite(number) else None

