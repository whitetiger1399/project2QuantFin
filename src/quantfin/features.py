"""Causal daily feature construction and delayed next-session labels."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from quantfin.io import (
    atomic_json_dump,
    atomic_parquet_dump,
    package_versions,
    read_manifest,
    sha256_file,
    stable_object_hash,
    utc_now,
)


def _rolling_zscore(series: pd.Series, window: int) -> pd.Series:
    mean = series.rolling(window=window, min_periods=window).mean()
    standard_deviation = series.rolling(window=window, min_periods=window).std(ddof=1)
    return (series - mean) / standard_deviation.replace(0, np.nan)


def _downside_deviation(series: pd.Series, window: int) -> pd.Series:
    squared_downside = series.clip(upper=0).pow(2)
    return np.sqrt(squared_downside.rolling(window, min_periods=window).mean())


def _rsi(price: pd.Series, window: int = 14) -> pd.Series:
    change = price.diff()
    average_gain = change.clip(lower=0).ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    average_loss = (-change.clip(upper=0)).ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    relative_strength = average_gain / average_loss.replace(0, np.nan)
    return 100 - 100 / (1 + relative_strength)


def _split_name(sessions: pd.Series, splits: dict[str, Any]) -> pd.Series:
    result = pd.Series("outside_declared_splits", index=sessions.index, dtype="string")
    for name, bounds in splits.items():
        start = pd.Timestamp(bounds["start"])
        end = pd.Timestamp(bounds["end"])
        result.loc[sessions.between(start, end, inclusive="both")] = name
    return result


def build_feature_frame(
    panel: pd.DataFrame,
    protocol: dict[str, Any],
    feature_config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Build deterministic features whose value at t uses observations through t only."""
    frame = panel.copy().sort_values("session").reset_index(drop=True)
    frame["session"] = pd.to_datetime(frame["session"], errors="raise").dt.normalize()
    traded = protocol["market_data"]["traded_asset"].lower()
    parameters = feature_config["parameters"]

    adjusted_close = frame[f"{traded}_adjusted_close"].astype(float)
    raw_close = frame[f"{traded}_close"].astype(float)
    raw_open = frame[f"{traded}_open"].astype(float)
    raw_high = frame[f"{traded}_high"].astype(float)
    raw_low = frame[f"{traded}_low"].astype(float)
    volume = frame[f"{traded}_volume"].astype(float)
    log_return = np.log(adjusted_close / adjusted_close.shift(1))

    features: dict[str, pd.Series] = {}
    groups: dict[str, list[str]] = {}

    def add(group: str, name: str, values: pd.Series) -> None:
        features[name] = values.replace([np.inf, -np.inf], np.nan)
        groups.setdefault(group, []).append(name)

    for offset in parameters["return_lag_offsets"]:
        add("returns", f"spy_log_return_lag_{offset}", log_return.shift(int(offset)))

    for window in parameters["momentum_windows"]:
        window = int(window)
        add("momentum", f"spy_momentum_{window}", adjusted_close / adjusted_close.shift(window) - 1)

    for window in parameters["moving_average_windows"]:
        window = int(window)
        moving_average = adjusted_close.rolling(window, min_periods=window).mean()
        add("trend", f"spy_price_to_sma_{window}", adjusted_close / moving_average - 1)
    ema_12 = adjusted_close.ewm(span=12, adjust=False, min_periods=12).mean()
    ema_26 = adjusted_close.ewm(span=26, adjust=False, min_periods=26).mean()
    sma_20 = adjusted_close.rolling(20, min_periods=20).mean()
    sma_50 = adjusted_close.rolling(50, min_periods=50).mean()
    sma_200 = adjusted_close.rolling(200, min_periods=200).mean()
    add("trend", "spy_ema_12_to_26", ema_12 / ema_26 - 1)
    add("trend", "spy_sma_20_slope_5", sma_20 / sma_20.shift(5) - 1)
    add("trend", "spy_sma_50_to_200", sma_50 / sma_200 - 1)

    volatility_by_window: dict[int, pd.Series] = {}
    for window in parameters["volatility_windows"]:
        window = int(window)
        volatility = log_return.rolling(window, min_periods=window).std(ddof=1)
        volatility_by_window[window] = volatility
        add("volatility", f"spy_volatility_{window}", volatility)
    if 10 in volatility_by_window and 60 in volatility_by_window:
        add(
            "volatility",
            "spy_volatility_10_to_60",
            volatility_by_window[10] / volatility_by_window[60],
        )
    add("volatility", "spy_downside_deviation_20", _downside_deviation(log_return, 20))
    add("volatility", "spy_ewma_volatility_20", log_return.ewm(span=20, adjust=False, min_periods=20).std())
    for window in parameters["distribution_windows"]:
        window = int(window)
        add("volatility", f"spy_return_skew_{window}", log_return.rolling(window, min_periods=window).skew())
        add("volatility", f"spy_return_excess_kurtosis_{window}", log_return.rolling(window, min_periods=window).kurt())
        add(
            "volatility",
            f"spy_return_autocorrelation_{window}",
            log_return.rolling(window, min_periods=window).corr(log_return.shift(1)),
        )

    for window in parameters["drawdown_windows"]:
        window = int(window)
        trailing_maximum = adjusted_close.rolling(window, min_periods=window).max()
        add("drawdown", f"spy_drawdown_{window}", adjusted_close / trailing_maximum - 1)

    rolling_mean_20 = adjusted_close.rolling(20, min_periods=20).mean()
    rolling_std_20 = adjusted_close.rolling(20, min_periods=20).std(ddof=1)
    rolling_low_14 = adjusted_close.rolling(14, min_periods=14).min()
    rolling_high_14 = adjusted_close.rolling(14, min_periods=14).max()
    macd = ema_12 - ema_26
    macd_signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    add("technical", "spy_rsi_14_scaled", _rsi(adjusted_close, 14) / 100)
    add("technical", "spy_bollinger_z_20", (adjusted_close - rolling_mean_20) / rolling_std_20)
    add(
        "technical",
        "spy_stochastic_14_scaled",
        (adjusted_close - rolling_low_14) / (rolling_high_14 - rolling_low_14).replace(0, np.nan),
    )
    add("technical", "spy_macd_to_price", macd / adjusted_close)
    add("technical", "spy_macd_signal_to_price", macd_signal / adjusted_close)
    add("technical", "spy_macd_histogram_to_price", (macd - macd_signal) / adjusted_close)

    add("intraday", "spy_intraday_return", raw_close / raw_open - 1)
    add("intraday", "spy_overnight_gap", raw_open / raw_close.shift(1) - 1)
    add("intraday", "spy_daily_range", (raw_high - raw_low) / raw_close)

    log_volume = np.log1p(volume)
    for window in parameters["volume_windows"]:
        window = int(window)
        volume_average = volume.rolling(window, min_periods=window).mean()
        add("volume", f"spy_volume_to_sma_{window}", volume / volume_average)
        add("volume", f"spy_log_volume_zscore_{window}", _rolling_zscore(log_volume, window))
    add("volume", "spy_log_volume_change_5", log_volume - log_volume.shift(5))
    signed_volume = np.sign(log_return.fillna(0)) * volume
    on_balance_volume = signed_volume.cumsum()
    add("volume", "spy_obv_change_20_scaled", on_balance_volume.diff(20) / volume.rolling(20, min_periods=20).sum())
    add("volume", "spy_amihud_illiquidity_20", (log_return.abs() / volume.replace(0, np.nan)).rolling(20, min_periods=20).mean())
    add("interactions", "spy_return_x_volume_z20", log_return * features["spy_log_volume_zscore_20"])
    add("interactions", "spy_momentum_20_x_volatility_20", features["spy_momentum_20"] * volatility_by_window[20])
    add("interactions", "spy_drawdown_60_x_volatility_20", features["spy_drawdown_60"] * volatility_by_window[20])
    add("calendar", "weekday_sin", np.sin(2 * np.pi * frame["session"].dt.dayofweek / 5))
    add("calendar", "weekday_cos", np.cos(2 * np.pi * frame["session"].dt.dayofweek / 5))
    add("calendar", "month_sin", np.sin(2 * np.pi * frame["session"].dt.month / 12))
    add("calendar", "month_cos", np.cos(2 * np.pi * frame["session"].dt.month / 12))
    calendar_month_end = frame["session"].dt.to_period("M").dt.to_timestamp("M")
    days_to_calendar_month_end = (calendar_month_end - frame["session"]).dt.days
    add("calendar", "is_last_five_calendar_days", days_to_calendar_month_end.le(4).astype(float))

    cross_assets = [symbol.lower() for symbol in protocol["market_data"].get("predictor_assets", [])]
    cross_returns: dict[str, pd.Series] = {}
    for symbol in cross_assets:
        series = frame[f"{symbol}_adjusted_close"].astype(float)
        cross_returns[symbol] = np.log(series / series.shift(1))
        for window in parameters["cross_asset_windows"]:
            window = int(window)
            add(
                "cross_asset",
                f"{symbol}_momentum_{window}",
                series / series.shift(window) - 1,
            )
        add(
            "cross_asset",
            f"{symbol}_volatility_20",
            cross_returns[symbol].rolling(20, min_periods=20).std(ddof=1),
        )
        add(
            "cross_asset",
            f"spy_{symbol}_return_correlation_60",
            log_return.rolling(60, min_periods=60).corr(cross_returns[symbol]),
        )
    spy_momentum_20 = features["spy_momentum_20"]
    if "qqq" in cross_assets:
        add("cross_asset", "qqq_minus_spy_momentum_20", features["qqq_momentum_20"] - spy_momentum_20)
    if "iwm" in cross_assets:
        add("cross_asset", "iwm_minus_spy_momentum_20", features["iwm_momentum_20"] - spy_momentum_20)
    if "tlt" in cross_returns and "gld" in cross_returns:
        add(
            "cross_asset",
            "tlt_gld_return_correlation_60",
            cross_returns["tlt"].rolling(60, min_periods=60).corr(cross_returns["gld"]),
        )

    feature_frame = pd.DataFrame({"signal_session": frame["session"], **features})
    # Signal after close t; entry at close t+1; earn adjusted close t+1 to t+2.
    feature_frame["entry_session"] = frame["session"].shift(-1)
    feature_frame["label_end_session"] = frame["session"].shift(-2)
    feature_frame["label_available_session"] = feature_frame["label_end_session"]
    feature_frame["target_return"] = adjusted_close.shift(-2) / adjusted_close.shift(-1) - 1
    feature_frame["split"] = _split_name(feature_frame["signal_session"], protocol["splits"])

    if feature_config.get("output", {}).get("retain_base_columns", True):
        feature_frame["spy_adjusted_close_at_signal"] = adjusted_close
        feature_frame["spy_adjusted_close_at_entry"] = adjusted_close.shift(-1)
        feature_frame["spy_adjusted_close_at_label_end"] = adjusted_close.shift(-2)

    return feature_frame, groups


def build_feature_dataset(
    processed_dataset: Path,
    protocol: dict[str, Any],
    feature_config: dict[str, Any],
    processed_root: Path,
) -> Path:
    source_manifest = read_manifest(processed_dataset / "manifest.json")
    panel_path = processed_dataset / "market_panel.parquet"
    expected = next(item["sha256"] for item in source_manifest["files"] if item["path"] == panel_path.name)
    if sha256_file(panel_path) != expected:
        raise ValueError(f"Processed market panel hash mismatch: {panel_path}")
    panel = pd.read_parquet(panel_path)
    frame, groups = build_feature_frame(panel, protocol, feature_config)

    selected_sets: dict[str, list[str]] = {}
    for set_name, definition in feature_config["feature_sets"].items():
        selected_sets[set_name] = [
            feature
            for group in definition["include_groups"]
            for feature in groups.get(group, [])
        ]

    feature_fingerprint_payload = {
        "feature_config": feature_config,
        "data_policy": protocol["data_policy"],
        "splits": protocol["splits"],
        "traded_asset": protocol["market_data"]["traded_asset"],
        "predictor_assets": protocol["market_data"].get("predictor_assets", []),
    }
    feature_fingerprint = stable_object_hash(feature_fingerprint_payload)[:10]
    dataset_id = f"features_{source_manifest['source_snapshot_id']}_{feature_fingerprint}"
    destination = processed_root / dataset_id
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite feature dataset: {destination}")
    destination.mkdir(parents=True, exist_ok=False)
    output_path = destination / "features_and_labels.parquet"
    atomic_parquet_dump(frame, output_path)
    manifest = {
        "schema_version": 1,
        "dataset_id": dataset_id,
        "created_at_utc": utc_now().isoformat(),
        "source_market_dataset_id": source_manifest["dataset_id"],
        "source_market_manifest_sha256": sha256_file(processed_dataset / "manifest.json"),
        "feature_config_sha256": stable_object_hash(feature_config),
        "feature_protocol_sha256": stable_object_hash(feature_fingerprint_payload),
        "timing": protocol["data_policy"],
        "feature_groups": groups,
        "feature_sets": selected_sets,
        "feature_counts": {name: len(columns) for name, columns in selected_sets.items()},
        "rows": len(frame),
        "rows_with_mature_labels": int(frame["target_return"].notna().sum()),
        "rows_complete_by_feature_set": {
            name: int(frame[columns].notna().all(axis=1).sum()) for name, columns in selected_sets.items()
        },
        "file": {"path": output_path.name, "sha256": sha256_file(output_path)},
        "packages": package_versions(["numpy", "pandas", "pyarrow"]),
        "warnings": [
            "This table intentionally contains future labels beside causal features. Training code must filter by label_available_session at every fit cutoff.",
            "Predictor-asset missing values remain null and must be handled inside each training-only preprocessing pipeline.",
        ],
    }
    atomic_json_dump(manifest, destination / "manifest.json")
    return destination


def audit_feature_timing(feature_dataset: Path, artifacts_root: Path) -> Path:
    manifest = read_manifest(feature_dataset / "manifest.json")
    feature_path = feature_dataset / manifest["file"]["path"]
    if sha256_file(feature_path) != manifest["file"]["sha256"]:
        raise ValueError(f"Feature dataset hash mismatch: {feature_path}")
    frame = pd.read_parquet(feature_path)
    date_columns = ["signal_session", "entry_session", "label_end_session", "label_available_session"]
    for column in date_columns:
        frame[column] = pd.to_datetime(frame[column])

    mature = frame["target_return"].notna()
    invalid_order = mature & ~(
        frame["signal_session"].lt(frame["entry_session"])
        & frame["entry_session"].lt(frame["label_end_session"])
        & frame["label_end_session"].eq(frame["label_available_session"])
    )
    reconstructed = (
        frame["spy_adjusted_close_at_label_end"] / frame["spy_adjusted_close_at_entry"] - 1
    )
    mismatch = mature & ~np.isclose(
        reconstructed,
        frame["target_return"],
        rtol=1e-12,
        atol=1e-14,
        equal_nan=False,
    )
    duplicate_signals = frame["signal_session"].duplicated(keep=False)
    blocking = []
    if invalid_order.any():
        blocking.append(f"{int(invalid_order.sum())} rows have invalid signal/entry/label ordering")
    if mismatch.any():
        blocking.append(f"{int(mismatch.sum())} labels fail price reconstruction")
    if duplicate_signals.any():
        blocking.append(f"{int(duplicate_signals.sum())} rows have duplicate signal sessions")

    destination = artifacts_root / "timing_audits" / manifest["dataset_id"]
    report = {
        "schema_version": 1,
        "created_at_utc": utc_now().isoformat(),
        "feature_dataset_id": manifest["dataset_id"],
        "status": "blocked" if blocking else "pass",
        "blocking_issues": blocking,
        "rows": len(frame),
        "mature_label_rows": int(mature.sum()),
        "last_signal_with_mature_label": (
            frame.loc[mature, "signal_session"].max().date().isoformat() if mature.any() else None
        ),
        "last_two_rows_without_labels_expected": int(frame.tail(2)["target_return"].isna().sum()),
        "training_eligibility_rule": (
            "At a fit cutoff, require label_available_session <= cutoff in addition to the chronological split."
        ),
    }
    atomic_json_dump(report, destination / "timing_report.json")
    return destination / "timing_report.json"

