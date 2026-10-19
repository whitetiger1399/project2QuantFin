"""Conservative audits and cleaning for immutable daily market snapshots."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from quantfin.io import (
    atomic_json_dump,
    atomic_parquet_dump,
    package_versions,
    read_manifest,
    sha256_file,
    utc_now,
)


PRICE_COLUMNS = ["open", "high", "low", "close", "adjusted_close"]
NUMERIC_COLUMNS = [*PRICE_COLUMNS, "volume", "dividend", "split_ratio", "capital_gain"]


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    serializable = frame.astype(object).where(frame.notna(), None)
    return serializable.to_dict(orient="records")


def _audit_symbol(frame: pd.DataFrame, symbol: str) -> dict[str, Any]:
    if frame.empty:
        return {
            "symbol": symbol,
            "rows": 0,
            "first_session": None,
            "last_session": None,
            "duplicate_rows": 0,
            "conflicting_duplicate_sessions": [],
            "null_counts": {column: 0 for column in NUMERIC_COLUMNS},
            "nonpositive_price_rows": 0,
            "negative_volume_rows": 0,
            "zero_volume_rows": 0,
            "impossible_ohlc_rows": 0,
            "weekend_rows": 0,
            "dividend_events": 0,
            "split_events": 0,
            "capital_gain_events": 0,
            "sample_flagged_rows": [],
        }
    duplicates = frame.loc[frame.duplicated("session", keep=False)].copy()
    conflicting_sessions: list[str] = []
    for session, group in duplicates.groupby("session"):
        compared = group.loc[:, [column for column in NUMERIC_COLUMNS if column in group]]
        if len(compared.drop_duplicates()) > 1:
            conflicting_sessions.append(pd.Timestamp(session).date().isoformat())

    invalid_price = frame[PRICE_COLUMNS].le(0).any(axis=1)
    invalid_volume = frame["volume"].lt(0)
    impossible_ohlc = (
        frame["low"].gt(frame[["open", "close"]].min(axis=1))
        | frame["high"].lt(frame[["open", "close"]].max(axis=1))
        | frame["low"].gt(frame["high"])
    )
    weekday = frame["session"].dt.dayofweek
    weekend = weekday.ge(5)

    return {
        "symbol": symbol,
        "rows": len(frame),
        "first_session": frame["session"].min().date().isoformat(),
        "last_session": frame["session"].max().date().isoformat(),
        "duplicate_rows": int(len(duplicates)),
        "conflicting_duplicate_sessions": conflicting_sessions,
        "null_counts": {column: int(frame[column].isna().sum()) for column in NUMERIC_COLUMNS},
        "nonpositive_price_rows": int(invalid_price.sum()),
        "negative_volume_rows": int(invalid_volume.sum()),
        "zero_volume_rows": int(frame["volume"].eq(0).sum()),
        "impossible_ohlc_rows": int(impossible_ohlc.sum()),
        "weekend_rows": int(weekend.sum()),
        "dividend_events": int(frame["dividend"].fillna(0).ne(0).sum()),
        "split_events": int(frame["split_ratio"].fillna(0).ne(0).sum()),
        "capital_gain_events": int(frame["capital_gain"].fillna(0).ne(0).sum()),
        "sample_flagged_rows": _records(
            frame.loc[invalid_price | invalid_volume | impossible_ohlc | weekend].head(20)
        ),
    }


def _load_and_normalize(snapshot: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    manifest = read_manifest(snapshot / "manifest.json")
    if manifest.get("status") != "complete" or manifest.get("source") != "yahoo":
        raise ValueError(f"Expected a complete Yahoo snapshot: {snapshot}")

    frames: list[pd.DataFrame] = []
    for entry in manifest["files"]:
        path = snapshot / entry["path"]
        actual_hash = sha256_file(path)
        if actual_hash != entry["sha256"]:
            raise ValueError(f"Snapshot file hash mismatch: {path}")
        frame = pd.read_parquet(path)
        frame["session"] = pd.to_datetime(frame["session"], errors="raise").dt.normalize()
        for column in NUMERIC_COLUMNS:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        frames.append(frame)
    return pd.concat(frames, ignore_index=True), manifest


def audit_yahoo_snapshot(
    snapshot: Path, protocol: dict[str, Any], artifacts_root: Path
) -> Path:
    frame, manifest = _load_and_normalize(snapshot)
    traded = protocol["market_data"]["traded_asset"]
    symbols = [traded, *protocol["market_data"].get("predictor_assets", [])]
    audits = [_audit_symbol(frame.loc[frame["symbol"].eq(symbol)].copy(), symbol) for symbol in symbols]

    traded_sessions = set(frame.loc[frame["symbol"].eq(traded), "session"])
    calendar_gaps = {}
    for symbol in symbols:
        sessions = set(frame.loc[frame["symbol"].eq(symbol), "session"])
        missing = sorted(traded_sessions.difference(sessions))
        extra = sorted(sessions.difference(traded_sessions))
        calendar_gaps[symbol] = {
            "missing_on_traded_asset_sessions": len(missing),
            "sample_missing_sessions": [item.date().isoformat() for item in missing[:20]],
            "extra_sessions": len(extra),
            "sample_extra_sessions": [item.date().isoformat() for item in extra[:20]],
        }

    blocking = []
    for audit in audits:
        if audit["rows"] == 0:
            blocking.append(f"{audit['symbol']}: configured symbol absent")
        if audit["conflicting_duplicate_sessions"]:
            blocking.append(f"{audit['symbol']}: conflicting duplicate sessions")
        if audit["nonpositive_price_rows"]:
            blocking.append(f"{audit['symbol']}: nonpositive prices")
        if audit["negative_volume_rows"]:
            blocking.append(f"{audit['symbol']}: negative volume")
        if audit["impossible_ohlc_rows"]:
            blocking.append(f"{audit['symbol']}: impossible OHLC relationships")
        if audit["weekend_rows"]:
            blocking.append(f"{audit['symbol']}: weekend sessions")
        if audit["null_counts"].get("adjusted_close", 0):
            blocking.append(f"{audit['symbol']}: missing adjusted close")

    report_dir = artifacts_root / "data_audits" / manifest["snapshot_id"]
    report = {
        "schema_version": 1,
        "created_at_utc": utc_now().isoformat(),
        "snapshot_id": manifest["snapshot_id"],
        "snapshot_path": str(snapshot),
        "source_manifest_sha256": sha256_file(snapshot / "manifest.json"),
        "status": "blocked" if blocking else "pass",
        "blocking_issues": blocking,
        "symbol_audits": audits,
        "calendar_comparison_to_traded_asset": calendar_gaps,
        "limitations": [
            "The SPY observed-session index is used as the research calendar; this audit does not prove exchange-calendar completeness.",
            "Extreme but structurally valid returns are retained for later inspection.",
            "Zero volume is reported for investigation and is not automatically removed.",
        ],
    }
    atomic_json_dump(report, report_dir / "quality_report.json")
    return report_dir / "quality_report.json"


def audit_corporate_actions(snapshot: Path, artifacts_root: Path) -> Path:
    """Export event windows and return comparisons without changing source prices."""
    frame, manifest = _load_and_normalize(snapshot)
    event_rows: list[dict[str, Any]] = []
    event_windows: list[dict[str, Any]] = []

    for symbol, part in frame.groupby("symbol", sort=True):
        part = part.sort_values("session").reset_index(drop=True)
        part["raw_close_return"] = part["close"].pct_change()
        part["adjusted_close_return"] = part["adjusted_close"].pct_change()
        part["cash_dividend_return_check"] = (
            (part["close"] + part["dividend"].fillna(0)) / part["close"].shift(1) - 1
        )
        events = part.index[
            part["dividend"].fillna(0).ne(0)
            | part["split_ratio"].fillna(0).ne(0)
            | part["capital_gain"].fillna(0).ne(0)
        ]
        for position in events:
            row = part.loc[position]
            event_rows.append(
                {
                    "symbol": symbol,
                    "session": row["session"],
                    "dividend": row["dividend"],
                    "split_ratio": row["split_ratio"],
                    "capital_gain": row["capital_gain"],
                    "raw_close_return": row["raw_close_return"],
                    "adjusted_close_return": row["adjusted_close_return"],
                    "cash_dividend_return_check": row["cash_dividend_return_check"],
                    "adjusted_minus_cash_check": (
                        row["adjusted_close_return"] - row["cash_dividend_return_check"]
                    ),
                }
            )
            window = part.loc[
                max(0, position - 2) : min(len(part) - 1, position + 2),
                [
                    "session",
                    "open",
                    "high",
                    "low",
                    "close",
                    "adjusted_close",
                    "volume",
                    "dividend",
                    "split_ratio",
                    "capital_gain",
                    "raw_close_return",
                    "adjusted_close_return",
                ],
            ].copy()
            for record in _records(window):
                record["symbol"] = symbol
                record["event_session"] = row["session"]
                event_windows.append(record)

    destination = artifacts_root / "corporate_actions" / manifest["snapshot_id"]
    events_frame = pd.DataFrame(
        event_rows,
        columns=[
            "symbol",
            "session",
            "dividend",
            "split_ratio",
            "capital_gain",
            "raw_close_return",
            "adjusted_close_return",
            "cash_dividend_return_check",
            "adjusted_minus_cash_check",
        ],
    )
    windows_frame = pd.DataFrame(
        event_windows,
        columns=[
            "session",
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "dividend",
            "split_ratio",
            "capital_gain",
            "raw_close_return",
            "adjusted_close_return",
            "symbol",
            "event_session",
        ],
    )
    events_path = destination / "events.parquet"
    windows_path = destination / "event_windows.parquet"
    atomic_parquet_dump(events_frame, events_path)
    atomic_parquet_dump(windows_frame, windows_path)
    report = {
        "schema_version": 1,
        "created_at_utc": utc_now().isoformat(),
        "snapshot_id": manifest["snapshot_id"],
        "event_count": len(events_frame),
        "event_counts_by_symbol": (
            events_frame.groupby("symbol").size().astype(int).to_dict()
            if not events_frame.empty
            else {}
        ),
        "files": [
            {"path": events_path.name, "sha256": sha256_file(events_path)},
            {"path": windows_path.name, "sha256": sha256_file(windows_path)},
        ],
        "interpretation": [
            "Adjusted Close is the primary total-return research proxy; dividends must not be added to it again.",
            "cash_dividend_return_check is a diagnostic based on raw close and cash dividend, not an assertion that vendor reinvestment conventions are identical.",
            "Split-event windows require manual review because vendor raw OHLC may already apply split normalization.",
            "Check the original assignment PDF before implementing the dividend factor printed in the converted Markdown.",
        ],
    }
    atomic_json_dump(report, destination / "action_report.json")
    return destination / "action_report.json"


def clean_yahoo_snapshot(
    snapshot: Path, protocol: dict[str, Any], processed_root: Path
) -> Path:
    """Create a clean long table and SPY-calendar panel; fail on structural errors."""
    frame, source_manifest = _load_and_normalize(snapshot)
    symbols = [
        protocol["market_data"]["traded_asset"],
        *protocol["market_data"].get("predictor_assets", []),
    ]
    unknown = sorted(set(frame["symbol"]).difference(symbols))
    if unknown:
        raise ValueError(f"Snapshot contains unconfigured symbols: {unknown}")

    cleaned_parts: list[pd.DataFrame] = []
    for symbol in symbols:
        part = frame.loc[frame["symbol"].eq(symbol)].copy().sort_values("session")
        if part.empty:
            raise ValueError(f"Configured symbol is absent: {symbol}")
        audit = _audit_symbol(part, symbol)
        blockers = [
            bool(audit["conflicting_duplicate_sessions"]),
            audit["nonpositive_price_rows"] > 0,
            audit["negative_volume_rows"] > 0,
            audit["impossible_ohlc_rows"] > 0,
            audit["weekend_rows"] > 0,
            audit["null_counts"]["adjusted_close"] > 0,
        ]
        if any(blockers):
            raise ValueError(
                f"{symbol} failed structural quality checks. Run audit-data and inspect its report."
            )
        part = part.drop_duplicates("session", keep="first")
        cleaned_parts.append(part)

    clean_long = pd.concat(cleaned_parts, ignore_index=True).sort_values(["session", "symbol"])
    traded = protocol["market_data"]["traded_asset"]
    research_sessions = (
        clean_long.loc[clean_long["symbol"].eq(traded), ["session"]]
        .drop_duplicates()
        .sort_values("session")
    )
    panel = research_sessions.copy()
    panel_fields = [
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
        "dividend",
        "split_ratio",
        "capital_gain",
    ]
    for symbol in symbols:
        part = clean_long.loc[clean_long["symbol"].eq(symbol), ["session", *panel_fields]].copy()
        part = part.rename(columns={column: f"{symbol.lower()}_{column}" for column in panel_fields})
        panel = panel.merge(part, on="session", how="left", validate="one_to_one")

    if panel[f"{traded.lower()}_adjusted_close"].isna().any():
        raise AssertionError("The traded-asset calendar contains missing traded adjusted prices")

    dataset_id = f"market_{source_manifest['snapshot_id']}"
    destination = processed_root / dataset_id
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite processed dataset: {destination}")
    destination.mkdir(parents=True, exist_ok=False)
    long_path = destination / "market_long.parquet"
    panel_path = destination / "market_panel.parquet"
    atomic_parquet_dump(clean_long.reset_index(drop=True), long_path)
    atomic_parquet_dump(panel.reset_index(drop=True), panel_path)

    missing_counts = {
        symbol: int(panel[f"{symbol.lower()}_adjusted_close"].isna().sum()) for symbol in symbols
    }
    manifest = {
        "schema_version": 1,
        "dataset_id": dataset_id,
        "created_at_utc": utc_now().isoformat(),
        "source_snapshot_id": source_manifest["snapshot_id"],
        "source_manifest_sha256": sha256_file(snapshot / "manifest.json"),
        "symbols": symbols,
        "traded_asset": traded,
        "research_calendar": f"observed {traded} sessions",
        "cleaning_rules": [
            "Coerce configured numeric fields; block missing adjusted close and invalid structural bars.",
            "Drop only value-identical duplicate sessions; conflicting duplicates block processing.",
            "Retain genuine extreme returns and zero-volume observations for analysis.",
            "Align predictor assets to observed SPY sessions without forward/backward filling.",
        ],
        "rows": {"long": len(clean_long), "panel": len(panel)},
        "missing_adjusted_close_on_research_calendar": missing_counts,
        "files": [
            {"path": long_path.name, "sha256": sha256_file(long_path)},
            {"path": panel_path.name, "sha256": sha256_file(panel_path)},
        ],
        "packages": package_versions(["numpy", "pandas", "pyarrow"]),
    }
    atomic_json_dump(manifest, destination / "manifest.json")
    return destination

