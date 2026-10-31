"""Build the auditable, point-in-time aligned Nifty IT research panel."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from quantfin.cross_market.common import manifest, root_path
from quantfin.progress import progress


OUTCOME_COLUMNS = [
    "target_oc_return",
    "target_direction",
    "benchmark_nifty_it_cc_return",
    "benchmark_nifty50_cc_return",
    "benchmark_cohort_ew_oc_return",
]


def _safe(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return text or "unknown"


def _read_snapshot(snapshot: Path, excluded: set[str] | None = None) -> dict[str, pd.DataFrame]:
    excluded = excluded or set()
    frames: dict[str, pd.DataFrame] = {}
    records = manifest(snapshot).get("files", [])
    for record in progress(records, description=f"Loading {snapshot.name}", total=len(records), unit="file"):
        symbol = str(record["symbol"])
        if symbol in excluded:
            continue
        path = snapshot / record["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        frame = pd.read_parquet(path)
        frame["session"] = pd.to_datetime(frame["session"]).dt.normalize()
        frames[symbol] = frame.sort_values("session").drop_duplicates("session", keep="last")
    return frames


def _clean_market_frame(
    frame: pd.DataFrame,
    *,
    symbol: str,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    clean = frame.copy()
    numeric = ["open", "high", "low", "close", "adjusted_close", "volume"]
    clean[numeric] = clean[numeric].apply(pd.to_numeric, errors="coerce")
    invalid = clean[["open", "high", "low", "close"]].isna().any(axis=1)
    if config["cleaning"]["require_positive_ohlc"]:
        invalid |= clean[["open", "high", "low", "close"]].le(0).any(axis=1)
    maximum = clean[["open", "close", "low"]].max(axis=1)
    minimum = clean[["open", "close", "high"]].min(axis=1)
    invalid |= (clean["high"] < maximum) | (clean["low"] > minimum)
    for date in config["cleaning"].get("explicit_quarantine", {}).get(symbol, []):
        invalid |= clean["session"].eq(pd.Timestamp(date))
    records = [
        {"symbol": symbol, "session": str(value.date()), "reason": "invalid_or_impossible_ohlc"}
        for value in clean.loc[invalid, "session"]
    ]
    if symbol.endswith("=X") and config["cleaning"].get("fx_close_to_close_only", True):
        # Vendor FX OHLC envelopes are unreliable, but close-to-close observations remain usable.
        clean.loc[:, ["open", "high", "low"]] = np.nan
        invalid = clean[["close", "adjusted_close"]].isna().all(axis=1) | clean["close"].le(0)
    clean = clean.loc[~invalid].copy()
    if clean["session"].duplicated().any():
        raise ValueError(f"Duplicate sessions remain for {symbol}")
    return clean, records


def _market_features(frame: pd.DataFrame, settings: dict[str, Any]) -> pd.DataFrame:
    data = frame.set_index("session").sort_index()
    adjusted = data["adjusted_close"].where(data["adjusted_close"].gt(0), data["close"])
    close = data["close"]
    returns = np.log(adjusted).diff()
    result = pd.DataFrame(index=data.index)
    for lag in settings["return_lags"]:
        result[f"ret_lag_{lag}"] = returns.shift(lag - 1)
    for window in settings["momentum_windows"]:
        result[f"momentum_{window}"] = np.log(adjusted / adjusted.shift(window))
        result[f"drawdown_{window}"] = adjusted / adjusted.rolling(window, min_periods=max(3, window // 2)).max() - 1.0
    for window in settings["volatility_windows"]:
        rolling = returns.rolling(window, min_periods=max(3, window // 2))
        result[f"volatility_{window}"] = rolling.std(ddof=1)
        result[f"downside_volatility_{window}"] = returns.where(returns.lt(0), 0).rolling(
            window, min_periods=max(3, window // 2)
        ).std(ddof=1)
        result[f"return_z_{window}"] = (returns - rolling.mean()) / rolling.std(ddof=1).replace(0, np.nan)
    for window in settings["moving_average_windows"]:
        moving = adjusted.rolling(window, min_periods=max(3, window // 2)).mean()
        result[f"price_to_ma_{window}"] = adjusted / moving - 1.0
    previous_close = close.shift(1)
    result["gap_return"] = data["open"] / previous_close - 1.0
    result["intraday_return"] = data["close"] / data["open"] - 1.0
    result["intraday_range"] = (data["high"] - data["low"]) / previous_close
    result["close_location"] = (data["close"] - data["low"]) / (data["high"] - data["low"]).replace(0, np.nan)
    for window in settings["volume_windows"]:
        volume = data["volume"].replace(0, np.nan)
        log_volume = np.log1p(volume)
        result[f"log_volume_z_{window}"] = (
            (log_volume - log_volume.rolling(window, min_periods=max(3, window // 2)).mean())
            / log_volume.rolling(window, min_periods=max(3, window // 2)).std(ddof=1).replace(0, np.nan)
        )
    rsi_window = int(settings["rsi_window"])
    delta = adjusted.diff()
    gain = delta.clip(lower=0).rolling(rsi_window, min_periods=rsi_window).mean()
    loss = -delta.clip(upper=0).rolling(rsi_window, min_periods=rsi_window).mean()
    result[f"rsi_{rsi_window}"] = 100.0 - 100.0 / (1.0 + gain / loss.replace(0, np.nan))
    return result.replace([np.inf, -np.inf], np.nan)


def _compact_features(frame: pd.DataFrame, settings: dict[str, Any]) -> pd.DataFrame:
    full = _market_features(frame, settings)
    desired = [
        "ret_lag_1", "ret_lag_2", "ret_lag_5", "momentum_5", "momentum_21", "momentum_63",
        "volatility_5", "volatility_21", "price_to_ma_10", "price_to_ma_50", "gap_return",
        "intraday_return", "intraday_range", "close_location", "log_volume_z_21", "rsi_14",
    ]
    return full[[column for column in desired if column in full.columns]]


def _asof_align(source: pd.DataFrame, decision_dates: pd.DatetimeIndex) -> pd.DataFrame:
    left = pd.DataFrame({"decision_date": pd.DatetimeIndex(decision_dates).sort_values()})
    right = source.sort_index().reset_index().rename(columns={source.index.name or "index": "source_session"})
    right["source_session"] = pd.to_datetime(right["source_session"])
    aligned = pd.merge_asof(
        left,
        right.sort_values("source_session"),
        left_on="decision_date",
        right_on="source_session",
        direction="backward",
        allow_exact_matches=False,
    ).set_index("decision_date")
    if "source_session" in aligned:
        aligned["observation_age_days"] = (aligned.index - aligned["source_session"]).dt.days
        aligned = aligned.drop(columns="source_session")
    return aligned


def _prefix(frame: pd.DataFrame, family: str, symbol: str | None = None) -> pd.DataFrame:
    stem = f"{family}__{_safe(symbol)}" if symbol else family
    return frame.rename(columns={column: f"{stem}__{column}" for column in frame.columns})


def _align_group(
    frames: dict[str, pd.DataFrame],
    decision_dates: pd.DatetimeIndex,
    settings: dict[str, Any],
    family: str,
    *,
    symbols: Iterable[str] | None = None,
) -> pd.DataFrame:
    pieces: list[pd.DataFrame] = []
    selected = list(symbols) if symbols is not None else sorted(frames)
    for symbol in progress(selected, description=f"Engineering {family}", total=len(selected), unit="asset"):
        if symbol not in frames:
            continue
        features = _compact_features(frames[symbol], settings)
        pieces.append(_prefix(_asof_align(features, decision_dates), family, symbol))
    return pd.concat(pieces, axis=1) if pieces else pd.DataFrame(index=decision_dates)


def _group_return_aggregate(aligned: pd.DataFrame, family: str) -> pd.DataFrame:
    """Cross-sectional summary of the latest completed one-session returns."""
    returns = aligned.filter(regex=r"__ret_lag_1$")
    result = pd.DataFrame(index=aligned.index)
    if returns.empty:
        return result
    result[f"{family}_aggregate__mean"] = returns.mean(axis=1)
    result[f"{family}_aggregate__median"] = returns.median(axis=1)
    result[f"{family}_aggregate__std"] = returns.std(axis=1)
    result[f"{family}_aggregate__minimum"] = returns.min(axis=1)
    result[f"{family}_aggregate__maximum"] = returns.max(axis=1)
    result[f"{family}_aggregate__negative_share"] = returns.lt(0).sum(axis=1) / returns.notna().sum(axis=1).replace(0, np.nan)
    result[f"{family}_aggregate__available_count"] = returns.notna().sum(axis=1)
    return result


def _frontier_event_features(snapshot: Path, dates: pd.DatetimeIndex) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Map releases to the first NSE pre-open cutoff after public availability."""
    path = snapshot / "frontier_ai_releases.csv"
    if not path.is_file():
        raise FileNotFoundError(path)
    events = pd.read_csv(path)
    required = {"event_id", "provider", "public_at_utc", "primary_event"}
    missing = sorted(required.difference(events.columns))
    if missing:
        raise ValueError(f"Frontier-event calendar is missing columns: {missing}")
    cutoffs = pd.Series(
        pd.DatetimeIndex(dates).tz_localize("Asia/Kolkata") + pd.Timedelta(hours=8, minutes=55),
        index=dates,
    ).dt.tz_convert("UTC")
    events["public_at_utc"] = pd.to_datetime(events["public_at_utc"], utc=True, errors="raise")
    events["primary_event"] = events["primary_event"].astype(str).str.lower().isin({"true", "1", "yes"})
    mapped: list[pd.Timestamp] = []
    for value in events["public_at_utc"]:
        eligible = cutoffs.index[cutoffs.gt(value)]
        mapped.append(eligible[0] if len(eligible) else pd.NaT)
    events["tradable_date"] = mapped
    result = pd.DataFrame(index=dates)
    result["ai_event__frontier_release_today"] = 0.0
    result["ai_event__all_release_today"] = 0.0
    for provider in sorted(events["provider"].dropna().astype(str).unique()):
        result[f"ai_event__provider_{_safe(provider)}_today"] = 0.0
        result[f"ai_event__provider_{_safe(provider)}_post_us_reaction_today"] = 0.0
    for row in events.dropna(subset=["tradable_date"]).itertuples(index=False):
        date = pd.Timestamp(row.tradable_date)
        result.loc[date, "ai_event__all_release_today"] += 1.0
        if bool(row.primary_event):
            result.loc[date, "ai_event__frontier_release_today"] += 1.0
        result.loc[date, f"ai_event__provider_{_safe(str(row.provider))}_today"] += 1.0
        later = dates[dates > date]
        if len(later):
            result.loc[later[0], f"ai_event__provider_{_safe(str(row.provider))}_post_us_reaction_today"] += 1.0
    provider_post_columns = [column for column in result if column.endswith("_post_us_reaction_today")]
    result["ai_event__post_us_reaction_today"] = result[provider_post_columns].sum(axis=1)
    primary = result["ai_event__frontier_release_today"].gt(0).astype(float)
    for half_life in [1, 3, 5]:
        result[f"ai_event__frontier_decay_{half_life}"] = primary.ewm(
            halflife=half_life, adjust=False
        ).mean()
    result["ai_event__frontier_count_5"] = primary.rolling(5, min_periods=1).sum()
    result["ai_event__frontier_count_21"] = primary.rolling(21, min_periods=1).sum()
    event_dates = result.index[primary.gt(0)]
    for date in dates:
        previous = event_dates[event_dates <= date]
        result.loc[date, "ai_event__days_since_frontier_release"] = (
            (date - previous[-1]).days if len(previous) else np.nan
        )
    evidence = {
        "calendar_snapshot": snapshot.name,
        "calendar_events": int(len(events)),
        "mapped_events": int(events["tradable_date"].notna().sum()),
        "primary_event_sessions": int(primary.sum()),
        "mapping_policy": "first NSE 08:55 IST cutoff strictly after public_at_utc",
    }
    return result, evidence


def _peer_features(
    india: dict[str, pd.DataFrame],
    target_symbols: list[str],
    dates: pd.DatetimeIndex,
    settings: dict[str, Any],
) -> dict[str, pd.DataFrame]:
    """Leave-one-out Nifty IT peer summaries known before each NSE decision."""
    metrics = [
        "ret_lag_1", "ret_lag_2", "ret_lag_5", "momentum_5", "momentum_21",
        "momentum_63", "volatility_5", "volatility_21", "intraday_return",
        "intraday_range", "price_to_ma_10", "price_to_ma_50", "log_volume_z_21",
    ]
    compact = {symbol: _compact_features(india[symbol], settings) for symbol in target_symbols}
    output: dict[str, pd.DataFrame] = {}
    for target in progress(target_symbols, description="Engineering leave-one-out Nifty IT peers", unit="asset"):
        peers = [symbol for symbol in target_symbols if symbol != target]
        result = pd.DataFrame()
        for metric in metrics:
            values = pd.concat(
                [compact[symbol][metric].rename(symbol) for symbol in peers if metric in compact[symbol]],
                axis=1,
            )
            if values.empty:
                continue
            result[f"{metric}_mean"] = values.mean(axis=1)
            result[f"{metric}_median"] = values.median(axis=1)
            result[f"{metric}_std"] = values.std(axis=1)
            result[f"{metric}_positive_share"] = values.gt(0).sum(axis=1) / values.notna().sum(axis=1).replace(0, np.nan)
        output[target] = _prefix(_asof_align(result, dates), "nifty_it_peers")
    return output


def _membership_mask(
    sessions: pd.DatetimeIndex,
    membership: pd.DataFrame,
    symbol: str,
    *,
    terminal_date: pd.Timestamp,
    carry_forward_end: pd.Timestamp | None,
) -> np.ndarray:
    rows = membership.loc[membership["yahoo_symbol"].astype(str).eq(symbol)]
    mask = np.zeros(len(sessions), dtype=bool)
    for row in rows.itertuples(index=False):
        start = pd.Timestamp(row.valid_from)
        end = pd.Timestamp(row.valid_to)
        if carry_forward_end is not None and end == terminal_date:
            end = carry_forward_end
        mask |= (sessions >= start) & (sessions <= end)
    return mask


def _broad_features(
    frames: dict[str, pd.DataFrame],
    membership_path: Path,
    decision_dates: pd.DatetimeIndex,
    *,
    family: str,
    selection_cutoff: pd.Timestamp,
    max_symbols: int,
    carry_forward_end: pd.Timestamp | None,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    membership = pd.read_csv(membership_path)
    membership["valid_from"] = pd.to_datetime(membership["valid_from"])
    membership["valid_to"] = pd.to_datetime(membership["valid_to"])
    terminal_date = membership["valid_to"].max()
    rankings: list[tuple[str, int, float]] = []
    prepared: dict[str, pd.DataFrame] = {}
    for symbol, frame in frames.items():
        data = frame.set_index("session").sort_index()
        adjusted = data["adjusted_close"].where(data["adjusted_close"].gt(0), data["close"])
        returns = np.log(adjusted).diff()
        active = _membership_mask(
            data.index,
            membership,
            symbol,
            terminal_date=terminal_date,
            carry_forward_end=carry_forward_end,
        )
        values = pd.DataFrame({
            "ret_1": returns.where(active),
            "ret_5": np.log(adjusted / adjusted.shift(5)).where(active),
            "ret_21": np.log(adjusted / adjusted.shift(21)).where(active),
        })
        prepared[symbol] = values
        train = (data.index <= selection_cutoff) & active
        coverage = int(values.loc[train, "ret_1"].notna().sum())
        liquidity = float(np.nanmedian((data.loc[train, "close"] * data.loc[train, "volume"]).to_numpy())) if train.any() else 0.0
        rankings.append((symbol, coverage, liquidity if np.isfinite(liquidity) else 0.0))
    selected = [row[0] for row in sorted(rankings, key=lambda row: (row[1], row[2]), reverse=True)]
    if max_symbols > 0:
        selected = selected[:max_symbols]
    aligned_returns: list[pd.DataFrame] = []
    for symbol in progress(selected, description=f"Aligning {family} universe", total=len(selected), unit="asset"):
        aligned = _asof_align(prepared[symbol], decision_dates).drop(columns="observation_age_days", errors="ignore")
        aligned_returns.append(aligned.rename(columns={c: f"{family}_raw__{_safe(symbol)}__{c}" for c in aligned}))
    raw = pd.concat(aligned_returns, axis=1) if aligned_returns else pd.DataFrame(index=decision_dates)
    one_day = raw.filter(regex=r"__ret_1$")
    aggregate = pd.DataFrame(index=raw.index)
    aggregate[f"{family}_aggregate__mean"] = one_day.mean(axis=1)
    aggregate[f"{family}_aggregate__median"] = one_day.median(axis=1)
    aggregate[f"{family}_aggregate__std"] = one_day.std(axis=1)
    aggregate[f"{family}_aggregate__positive_share"] = one_day.gt(0).sum(axis=1) / one_day.notna().sum(axis=1).replace(0, np.nan)
    aggregate[f"{family}_aggregate__q10"] = one_day.quantile(0.10, axis=1)
    aggregate[f"{family}_aggregate__q90"] = one_day.quantile(0.90, axis=1)
    aggregate[f"{family}_aggregate__dispersion"] = aggregate[f"{family}_aggregate__q90"] - aggregate[f"{family}_aggregate__q10"]
    aggregate[f"{family}_aggregate__available_count"] = one_day.notna().sum(axis=1)
    return raw, aggregate, selected


def _macro_features(snapshot: Path, dates: pd.DatetimeIndex, config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, bool]]:
    info = manifest(snapshot)
    fallbacks = set(info.get("current_vintage_fallbacks", {}))
    lag_map = config["feature_engineering"]["macro_release_lags_calendar_days"]
    pieces: list[pd.DataFrame] = []
    fallback_flags: dict[str, bool] = {}
    csv_paths = sorted(snapshot.glob("*.csv"))
    for csv_path in progress(csv_paths, description="Aligning FRED/ALFRED", total=len(csv_paths), unit="series"):
        series = csv_path.stem
        frame = pd.read_csv(csv_path)
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        frame["date"] = pd.to_datetime(frame["date"])
        fallback = series in fallbacks
        fallback_flags[series] = fallback
        if fallback:
            frame["available_date"] = frame["date"] + pd.to_timedelta(int(lag_map.get(series, 45)), unit="D")
        else:
            frame["available_date"] = pd.to_datetime(frame["realtime_start"])
            minimum = frame["date"] + pd.to_timedelta(int(lag_map.get(series, 1)), unit="D")
            frame["available_date"] = frame["available_date"].where(frame["available_date"].ge(minimum), minimum)
        # For each availability date retain the newest observation known then.
        available = frame.sort_values(["available_date", "date"]).drop_duplicates("available_date", keep="last")
        level = available.set_index("available_date")[["value"]].rename(columns={"value": "level"})
        level["change_1"] = level["level"].diff()
        level["change_5"] = level["level"].diff(5)
        level["z_252"] = (level["level"] - level["level"].rolling(252, min_periods=20).mean()) / level[
            "level"
        ].rolling(252, min_periods=20).std(ddof=1).replace(0, np.nan)
        pieces.append(_prefix(_asof_align(level, dates), "macro", series))
    return (pd.concat(pieces, axis=1) if pieces else pd.DataFrame(index=dates)), fallback_flags


def _calendar_features(dates: pd.DatetimeIndex) -> pd.DataFrame:
    result = pd.DataFrame(index=dates)
    weekday = dates.dayofweek.to_numpy()
    month = dates.month.to_numpy()
    day_of_year = dates.dayofyear.to_numpy()
    result["calendar__weekday_sin"] = np.sin(2 * np.pi * weekday / 5)
    result["calendar__weekday_cos"] = np.cos(2 * np.pi * weekday / 5)
    result["calendar__month_sin"] = np.sin(2 * np.pi * (month - 1) / 12)
    result["calendar__month_cos"] = np.cos(2 * np.pi * (month - 1) / 12)
    result["calendar__annual_sin_1"] = np.sin(2 * np.pi * day_of_year / 365.25)
    result["calendar__annual_cos_1"] = np.cos(2 * np.pi * day_of_year / 365.25)
    result["calendar__annual_sin_2"] = np.sin(4 * np.pi * day_of_year / 365.25)
    result["calendar__annual_cos_2"] = np.cos(4 * np.pi * day_of_year / 365.25)
    result["calendar__month_end"] = dates.is_month_end.astype(float)
    result["calendar__quarter_end"] = dates.is_quarter_end.astype(float)
    return result


def _scheduled_features(path: Path, dates: pd.DatetimeIndex) -> pd.DataFrame:
    result = pd.DataFrame(index=dates)
    if not path.is_file():
        return result
    events = pd.read_csv(path)
    if events.empty or "scheduled_at_utc" not in events:
        return result
    scheduled = pd.to_datetime(events["scheduled_at_utc"], utc=True, errors="coerce").dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    event_dates = pd.DatetimeIndex(scheduled.dropna().dt.normalize().unique()).sort_values()
    if event_dates.empty:
        return result
    for date in dates:
        previous = event_dates[event_dates < date]
        future = event_dates[event_dates >= date]
        result.loc[date, "scheduled__days_since_event"] = (date - previous[-1]).days if len(previous) else np.nan
        result.loc[date, "scheduled__days_to_event"] = (future[0] - date).days if len(future) else np.nan
    return result


def _manual_context_features(config: dict[str, Any], dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Publication-aware optional RBI, rainfall, and holiday features."""
    pieces: list[pd.DataFrame] = []
    manual = config["raw_data"]["manual_context"]
    for key, id_columns in [("rbi_rates", ["series_id"]), ("rainfall", ["geography", "metric"])]:
        path = root_path(manual[key])
        if not path.is_file():
            continue
        frame = pd.read_csv(path)
        if frame.empty or "value" not in frame or "published_at" not in frame:
            continue
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        frame["available_date"] = pd.to_datetime(frame["published_at"], utc=True, errors="coerce").dt.tz_convert(
            "Asia/Kolkata"
        ).dt.tz_localize(None).dt.normalize()
        available_ids = [column for column in id_columns if column in frame]
        if not available_ids:
            frame["series"] = key
            available_ids = ["series"]
        for values, group in frame.groupby(available_ids, dropna=False):
            values = values if isinstance(values, tuple) else (values,)
            name = "_".join(_safe(str(value)) for value in values)
            source = group.dropna(subset=["available_date", "value"]).sort_values("available_date").drop_duplicates(
                "available_date", keep="last"
            ).set_index("available_date")[["value"]]
            source["change_1"] = source["value"].diff()
            pieces.append(_prefix(_asof_align(source, dates), "macro", f"manual_{key}_{name}"))
    for key, date_column in [("nse_holidays", "holiday_date"), ("nyse_holidays", "holiday_date")]:
        path = root_path(manual[key])
        if not path.is_file():
            continue
        frame = pd.read_csv(path)
        if frame.empty or date_column not in frame:
            continue
        frame[date_column] = pd.to_datetime(frame[date_column], errors="coerce").dt.normalize()
        if "announced_at" in frame:
            frame["known_date"] = pd.to_datetime(frame["announced_at"], utc=True, errors="coerce").dt.tz_convert(
                "Asia/Kolkata"
            ).dt.tz_localize(None).dt.normalize()
        else:
            frame["known_date"] = pd.Timestamp.min
        values = pd.DataFrame(index=dates)
        for date in dates:
            holidays = pd.DatetimeIndex(
                frame.loc[frame["known_date"].lt(date), date_column].dropna().unique()
            ).sort_values()
            previous = holidays[holidays < date]
            future = holidays[holidays >= date]
            values.loc[date, f"scheduled__days_since_{key}"] = (date - previous[-1]).days if len(previous) else np.nan
            values.loc[date, f"scheduled__days_to_{key}"] = (future[0] - date).days if len(future) else np.nan
        pieces.append(values)
    return pd.concat(pieces, axis=1) if pieces else pd.DataFrame(index=dates)


def _nonlinear_features(base: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame(index=base.index)
    candidates = [
        column for column in base.columns
        if any(token in column for token in ["volatility_21", "momentum_21", "positive_share", "vix", "dgs10", "intraday_return"])
    ][:40]
    for column in candidates:
        values = pd.to_numeric(base[column], errors="coerce")
        result[f"nonlinear__square__{column}"] = values.pow(2)
        result[f"nonlinear__signed_sqrt__{column}"] = np.sign(values) * np.sqrt(np.abs(values))
    interactions = candidates[:8]
    for index, left in enumerate(interactions):
        for right in interactions[index + 1 :]:
            result[f"nonlinear__interaction__{left}__x__{right}"] = base[left] * base[right]
    return result.replace([np.inf, -np.inf], np.nan)


def build_panel(config: dict[str, Any], inventory: dict[str, Path]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    settings = config["feature_engineering"]
    excluded = set(config["cleaning"].get("excluded_optional_symbols", []))
    needed_groups = {
        "india_core", "us_limited_tech", "us_context", "indian_it_adrs",
        "global_context", "nifty50_point_in_time", "sp500_point_in_time",
        "us_it_services", "us_it_enabled_payments", "us_enterprise_software",
    }
    raw_groups = {
        name: _read_snapshot(path, excluded)
        for name, path in inventory.items()
        if name in needed_groups
    }
    quarantine: list[dict[str, Any]] = []
    groups: dict[str, dict[str, pd.DataFrame]] = {}
    for group, frames in raw_groups.items():
        groups[group] = {}
        for symbol, frame in progress(frames.items(), description=f"Cleaning {group}", total=len(frames), unit="asset"):
            cleaned, records = _clean_market_frame(frame, symbol=symbol, config=config)
            groups[group][symbol] = cleaned
            quarantine.extend({"group": group, **record} for record in records)

    target_symbols = [f"{symbol}{config['study']['target_suffix']}" for symbol in config["study"]["target_symbols"]]
    india = groups["india_core"]
    missing = sorted(set(target_symbols).difference(india))
    if missing:
        raise ValueError(f"Missing fixed-cohort target data: {missing}")
    start = pd.Timestamp(config["sample"]["common_start"])
    end = pd.Timestamp(config["sample"]["end_exclusive"])
    target_dates = pd.DatetimeIndex(sorted(set().union(*[
        set(frame.loc[frame["session"].between(start, end, inclusive="left"), "session"])
        for frame in (india[symbol] for symbol in target_symbols)
    ])))

    common = _calendar_features(target_dates)
    index_symbols = ["^CNXIT", "^NSEI", "^NSEBANK", "^INDIAVIX", "INR=X", "ITBEES.NS", "NIFTYBEES.NS"]
    common = common.join(_align_group(india, target_dates, settings, "india_core", symbols=index_symbols))
    common = common.join(_align_group(groups["us_limited_tech"], target_dates, settings, "us_tech"))
    for group_name, family in [
        ("us_it_services", "us_it_services"),
        ("us_it_enabled_payments", "us_it_payments"),
        ("us_enterprise_software", "us_enterprise_software"),
    ]:
        if group_name in groups:
            aligned = _align_group(groups[group_name], target_dates, settings, family)
            common = common.join(aligned).join(_group_return_aggregate(aligned, family))
    common = common.join(_align_group(groups["indian_it_adrs"], target_dates, settings, "adr"))
    common = common.join(_align_group(groups["us_context"], target_dates, settings, "us_context"))
    common = common.join(_align_group(groups["global_context"], target_dates, settings, "global"))

    sp_raw, sp_agg, sp_selected = _broad_features(
        groups["sp500_point_in_time"],
        root_path(config["raw_data"]["membership_files"]["sp500"]),
        target_dates,
        family="sp500",
        selection_cutoff=pd.Timestamp(settings["broad_universe_selection_cutoff"]),
        max_symbols=int(settings["broad_universe_max_symbols"]["sp500"]),
        carry_forward_end=end if settings.get("membership_terminal_carry_forward", False) else None,
    )
    _, nifty_agg, nifty_selected = _broad_features(
        groups["nifty50_point_in_time"],
        root_path(config["raw_data"]["membership_files"]["nifty50"]),
        target_dates,
        family="nifty50",
        selection_cutoff=pd.Timestamp(settings["broad_universe_selection_cutoff"]),
        max_symbols=int(settings["broad_universe_max_symbols"]["nifty50"]),
        carry_forward_end=end if settings.get("membership_terminal_carry_forward", False) else None,
    )
    common = common.join(nifty_agg).join(sp_agg).join(sp_raw)
    macro, fallback_flags = _macro_features(inventory["fred_alfred"], target_dates, config)
    common = common.join(macro)
    common = common.join(_scheduled_features(root_path(config["raw_data"]["manual_context"]["scheduled_events"]), target_dates))
    common = common.join(_manual_context_features(config, target_dates))
    event_evidence: dict[str, Any] = {}
    if "frontier_ai_events" in inventory:
        event_features, event_evidence = _frontier_event_features(
            inventory["frontier_ai_events"], target_dates
        )
        common = common.join(event_features)
        service_mean = common.get("us_it_services_aggregate__mean")
        if service_mean is not None:
            common["ai_interaction__event_x_us_services_mean"] = (
                common["ai_event__frontier_release_today"] * service_mean
            )
            common["ai_interaction__event_x_us_services_negative"] = (
                common["ai_event__frontier_release_today"] * service_mean.lt(0).astype(float)
            )
    common = common.join(_nonlinear_features(common))

    own_features: dict[str, pd.DataFrame] = {}
    for symbol in target_symbols:
        own_features[symbol] = _prefix(
            _asof_align(_market_features(india[symbol], settings), target_dates), "own"
        )
    peer_features = _peer_features(india, target_symbols, target_dates, settings)
    cohort_returns = pd.concat(
        {
            symbol: _market_features(india[symbol], settings)["ret_lag_1"]
            for symbol in target_symbols
        }, axis=1
    )
    cohort_aggregate = pd.DataFrame(index=cohort_returns.index)
    cohort_aggregate["india_core__cohort_mean_return"] = cohort_returns.mean(axis=1)
    cohort_aggregate["india_core__cohort_dispersion"] = cohort_returns.std(axis=1)
    cohort_aggregate["india_core__cohort_positive_share"] = cohort_returns.gt(0).mean(axis=1)
    common = common.join(_asof_align(cohort_aggregate, target_dates).drop(columns="observation_age_days", errors="ignore"))

    # Benchmarks are outcomes for the decision session and are never included in feature sets.
    benchmark = pd.DataFrame(index=target_dates)
    for output, symbol in [("benchmark_nifty_it_cc_return", "ITBEES.NS"), ("benchmark_nifty50_cc_return", "NIFTYBEES.NS")]:
        fallback = "^CNXIT" if "nifty_it" in output else "^NSEI"
        source = india.get(symbol, india[fallback]).set_index("session")
        adjusted = source["adjusted_close"].where(source["adjusted_close"].gt(0), source["close"])
        benchmark[output] = adjusted.pct_change().reindex(target_dates)

    rows: list[pd.DataFrame] = []
    one_hot_names = [f"asset__{_safe(symbol)}" for symbol in target_symbols]
    target_returns: dict[str, pd.Series] = {}
    for symbol in target_symbols:
        source = india[symbol].set_index("session")
        target = (source["close"] / source["open"] - 1.0).reindex(target_dates)
        target_returns[symbol] = target
        frame = common.join(own_features[symbol]).join(peer_features[symbol]).join(benchmark)
        frame["decision_date"] = frame.index
        frame["asset"] = symbol
        frame["target_oc_return"] = target
        frame["target_direction"] = target.gt(0).astype(float).where(target.notna())
        for name, target_symbol in zip(one_hot_names, target_symbols):
            frame[name] = float(symbol == target_symbol)
        rows.append(frame.reset_index(drop=True))
    panel = pd.concat(rows, ignore_index=True)
    target_matrix = pd.DataFrame(target_returns)
    cohort_outcome = target_matrix.mean(axis=1)
    panel["benchmark_cohort_ew_oc_return"] = panel["decision_date"].map(cohort_outcome)
    panel = panel.loc[panel["target_oc_return"].notna()].sort_values(["decision_date", "asset"]).reset_index(drop=True)
    panel["sample_split"] = "pre_sample"
    for split_name, (split_start, split_end) in config["sample"]["splits"].items():
        mask = panel["decision_date"].between(pd.Timestamp(split_start), pd.Timestamp(split_end))
        panel.loc[mask, "sample_split"] = split_name

    families = config["feature_sets"]
    dictionary_rows: list[dict[str, Any]] = []
    metadata_columns = {"decision_date", "asset", "sample_split", *OUTCOME_COLUMNS}
    for column in panel.columns:
        if column in metadata_columns:
            continue
        family = column.split("__", 1)[0]
        sets = [name for name, included in families.items() if family in included]
        dictionary_rows.append({
            "feature": column,
            "family": family,
            "feature_sets": "|".join(sets),
            "known_at_0855_ist": True,
            "alignment": "latest completed observation strictly before decision date" if family not in {"asset", "calendar"} else "known at decision",
            "current_vintage_fallback": any(f"__{_safe(series)}__" in column and flag for series, flag in fallback_flags.items()),
        })
    dictionary = pd.DataFrame(dictionary_rows).sort_values(["family", "feature"])
    evidence = {
        "quarantined_rows": quarantine,
        "quarantined_row_count": len(quarantine),
        "sp500_selected_symbols": sp_selected,
        "nifty50_selected_symbols": nifty_selected,
        "macro_current_vintage_fallbacks": sorted(series for series, flag in fallback_flags.items() if flag),
        "frontier_ai_events": event_evidence,
        "membership_terminal_carry_forward": bool(settings.get("membership_terminal_carry_forward", False)),
        "rows": len(panel),
        "decision_dates": int(panel["decision_date"].nunique()),
        "assets": sorted(panel["asset"].unique()),
        "first_decision_date": str(panel["decision_date"].min().date()),
        "last_decision_date": str(panel["decision_date"].max().date()),
        "feature_count": len(dictionary),
    }
    return panel, dictionary, evidence
