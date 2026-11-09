"""Yahoo Finance adapter with one immutable file per symbol."""

from __future__ import annotations

from datetime import timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from quantfin.errors import SourceFetchError
from quantfin.io import (
    atomic_json_dump,
    atomic_parquet_dump,
    make_snapshot_id,
    package_versions,
    sha256_file,
    utc_now,
)
from quantfin.progress import progress


EXPECTED_COLUMNS = [
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
    "symbol",
    "source",
    "retrieved_at_utc",
]


def _normalize_history(
    history: pd.DataFrame, symbol: str, retrieved_at_utc: str
) -> pd.DataFrame:
    if history.empty:
        raise ValueError(f"Yahoo returned no rows for {symbol}")

    frame = history.copy().reset_index()
    frame.columns = [str(column).strip().lower().replace(" ", "_") for column in frame.columns]
    date_column = "date" if "date" in frame.columns else "datetime"
    if date_column not in frame.columns:
        raise ValueError(f"Yahoo response for {symbol} has no Date/Datetime column")

    session = pd.to_datetime(frame.pop(date_column), errors="raise")
    if getattr(session.dt, "tz", None) is not None:
        session = session.dt.tz_convert("America/New_York").dt.tz_localize(None)
    frame.insert(0, "session", session.dt.normalize())

    rename = {
        "adj_close": "adjusted_close",
        "dividends": "dividend",
        "stock_splits": "split_ratio",
        "capital_gains": "capital_gain",
    }
    frame = frame.rename(columns=rename)
    for column, default in {
        "adjusted_close": pd.NA,
        "dividend": 0.0,
        "split_ratio": 0.0,
        "capital_gain": 0.0,
    }.items():
        if column not in frame.columns:
            frame[column] = default

    required = {"open", "high", "low", "close", "volume"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Yahoo response for {symbol} is missing columns: {missing}")

    frame["symbol"] = symbol
    frame["source"] = "yahoo"
    frame["retrieved_at_utc"] = retrieved_at_utc
    return frame.loc[:, EXPECTED_COLUMNS].sort_values("session").reset_index(drop=True)


def fetch_yahoo_snapshot(protocol: dict[str, Any], raw_root: Path) -> Path:
    """Fetch configured symbols and commit a snapshot only after all succeed."""
    market = protocol["market_data"]
    yahoo = market.get("yahoo", {})
    symbols = [market["traded_asset"], *market.get("predictor_assets", [])]
    if len(symbols) != len(set(symbols)):
        raise ValueError("Configured asset symbols must be unique")

    retrieved = utc_now()
    retrieved_iso = retrieved.astimezone(timezone.utc).isoformat()
    snapshot_id = make_snapshot_id("yahoo", retrieved)
    destination = raw_root / "yahoo" / snapshot_id
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing snapshot: {destination}")
    destination.mkdir(parents=True, exist_ok=False)

    files: list[dict[str, Any]] = []
    try:
        for symbol in progress(symbols, description="Yahoo download", total=len(symbols), unit="asset"):
            ticker = yf.Ticker(symbol)
            history = ticker.history(
                start=market["start"],
                end=market["end_exclusive"],
                interval=yahoo.get("interval", "1d"),
                auto_adjust=bool(yahoo.get("auto_adjust", False)),
                actions=bool(yahoo.get("actions", True)),
                repair=bool(yahoo.get("repair", True)),
                timeout=int(yahoo.get("timeout_seconds", 30)),
                raise_errors=True,
            )
            normalized = _normalize_history(history, symbol, retrieved_iso)
            file_path = destination / f"{symbol}.parquet"
            atomic_parquet_dump(normalized, file_path)
            files.append(
                {
                    "symbol": symbol,
                    "path": file_path.name,
                    "rows": len(normalized),
                    "first_session": normalized["session"].min().date().isoformat(),
                    "last_session": normalized["session"].max().date().isoformat(),
                    "sha256": sha256_file(file_path),
                }
            )

        manifest = {
            "schema_version": 1,
            "snapshot_id": snapshot_id,
            "source": "yahoo",
            "status": "complete",
            "retrieved_at_utc": retrieved_iso,
            "request": {
                "symbols": symbols,
                "start": market["start"],
                "end_exclusive": market["end_exclusive"],
                "interval": yahoo.get("interval", "1d"),
                "auto_adjust": bool(yahoo.get("auto_adjust", False)),
                "actions": bool(yahoo.get("actions", True)),
                "repair": bool(yahoo.get("repair", True)),
            },
            "notes": [
                "Yahoo/yfinance data is intended for research and personal use; do not redistribute without permission.",
                "Adjusted Close is retained as the vendor-provided research return proxy.",
                "A zero split_ratio means no split event; a split event stores the vendor ratio.",
            ],
            "packages": package_versions(["pandas", "pyarrow", "yfinance"]),
            "files": files,
        }
        atomic_json_dump(manifest, destination / "manifest.json")
    except BaseException as exc:
        failure_record = destination / "FAILED.json"
        atomic_json_dump(
            {
                "schema_version": 1,
                "snapshot_id": snapshot_id,
                "source": "yahoo",
                "status": "failed",
                "retrieved_at_utc": retrieved_iso,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "files_written_before_failure": files,
            },
            failure_record,
        )
        raise SourceFetchError("Yahoo", failure_record, exc) from exc

    return destination

