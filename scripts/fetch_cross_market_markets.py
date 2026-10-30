"""Fetch immutable daily market snapshots for the cross-market Nifty IT study.

The command is plan-only unless ``--execute`` is supplied. One market group is
downloaded per invocation so a failure never invalidates unrelated sources.
Completed snapshots are immutable. An incomplete snapshot can be resumed with
``--resume-snapshot SNAPSHOT_ID``.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from quantfin.config import load_yaml
from quantfin.io import (
    atomic_json_dump,
    atomic_parquet_dump,
    make_snapshot_id,
    package_versions,
    sha256_file,
)
from quantfin.progress import progress


ROOT = Path(__file__).resolve().parents[1]
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


def _path(value: str) -> Path:
    candidate = Path(value).expanduser()
    return candidate if candidate.is_absolute() else ROOT / candidate


def _safe_name(symbol: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", symbol).strip("_") or "symbol"
    return f"{stem}.parquet"


def _normalize(history: pd.DataFrame, symbol: str, retrieved_at: str) -> pd.DataFrame:
    if history.empty:
        raise ValueError("empty response")
    frame = history.copy().reset_index()
    frame.columns = [str(column).strip().lower().replace(" ", "_") for column in frame.columns]
    date_column = "date" if "date" in frame.columns else "datetime"
    if date_column not in frame:
        raise ValueError("response has no Date/Datetime column")

    # Daily Yahoo indices are stamped in their exchange timezone. Preserve the
    # exchange-local calendar date; timezone conversion can shift an NSE date.
    session = pd.to_datetime(frame.pop(date_column), errors="raise")
    if getattr(session.dt, "tz", None) is not None:
        session = session.dt.tz_localize(None)
    frame.insert(0, "session", session.dt.normalize())
    frame = frame.rename(
        columns={
            "adj_close": "adjusted_close",
            "dividends": "dividend",
            "stock_splits": "split_ratio",
            "capital_gains": "capital_gain",
        }
    )
    for column, default in {
        "adjusted_close": pd.NA,
        "dividend": 0.0,
        "split_ratio": 0.0,
        "capital_gain": 0.0,
    }.items():
        if column not in frame:
            frame[column] = default
    missing = sorted({"open", "high", "low", "close", "volume"}.difference(frame.columns))
    if missing:
        raise ValueError(f"missing columns: {missing}")
    if frame["adjusted_close"].isna().all():
        frame["adjusted_close"] = frame["close"]
    frame["symbol"] = symbol
    frame["source"] = "yahoo"
    frame["retrieved_at_utc"] = retrieved_at
    result = frame.loc[:, EXPECTED_COLUMNS].sort_values("session").drop_duplicates("session")
    if result["session"].duplicated().any():
        raise ValueError("duplicate sessions remain after normalization")
    return result.reset_index(drop=True)


def _membership_symbols(path: Path, market: str) -> tuple[list[str], dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Membership file does not exist: {path}")
    frame = pd.read_csv(path, dtype=str)
    required = {"symbol", "yahoo_symbol", "valid_from", "valid_to"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Membership file is missing columns: {missing}")
    for column in ("valid_from", "valid_to"):
        parsed = pd.to_datetime(frame[column], errors="coerce")
        if column == "valid_from" and parsed.isna().any():
            raise ValueError(f"Membership file has invalid {column} values")
    symbols = sorted(frame["yahoo_symbol"].dropna().str.strip().loc[lambda x: x.ne("")].unique())
    if not symbols:
        raise ValueError("Membership file contains no yahoo_symbol values")
    metadata = {
        "market": market,
        "path": str(path),
        "sha256": sha256_file(path),
        "rows": int(len(frame)),
        "unique_symbols": len(symbols),
        "earliest_valid_from": str(pd.to_datetime(frame["valid_from"], errors="coerce").min().date()),
    }
    return symbols, metadata


def _download(symbol: str, settings: dict[str, Any], start: str, end: str, retrieved_at: str) -> pd.DataFrame:
    attempts = int(settings.get("maximum_attempts", 3))
    last_error: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            history = yf.Ticker(symbol).history(
                start=start,
                end=end,
                interval=settings.get("interval", "1d"),
                auto_adjust=bool(settings.get("auto_adjust", False)),
                actions=bool(settings.get("actions", True)),
                repair=bool(settings.get("repair", True)),
                timeout=int(settings.get("timeout_seconds", 45)),
                raise_errors=True,
            )
            return _normalize(history, symbol, retrieved_at)
        except BaseException as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(min(2 ** (attempt - 1), 8))
    assert last_error is not None
    raise last_error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_data_2026-10-29.yaml")
    parser.add_argument("--group", required=True)
    parser.add_argument("--membership-file")
    parser.add_argument("--output-root", default="data/raw/cross_market/yahoo")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume-snapshot")
    args = parser.parse_args()

    config_path = _path(args.config)
    config = load_yaml(config_path)
    groups = config["market_groups"]
    if args.group not in groups:
        raise KeyError(f"Unknown group {args.group!r}; choose from {sorted(groups)}")
    group = groups[args.group]
    symbols = list(dict.fromkeys(group.get("symbols", [])))
    membership_metadata = None
    if group.get("membership_file_required"):
        if not args.membership_file:
            raise ValueError(f"--membership-file is required for group {args.group}")
        symbols, membership_metadata = _membership_symbols(
            _path(args.membership_file), str(group.get("membership_market", args.group))
        )
    if not symbols:
        raise ValueError(f"Group {args.group} has no symbols")

    plan = {
        "mode": "execute" if args.execute else "plan_only",
        "group": args.group,
        "description": group.get("description"),
        "required": bool(group.get("required", True)),
        "start": config["start"],
        "end_exclusive": config["end_exclusive"],
        "symbol_count": len(symbols),
        "symbols": symbols,
        "membership": membership_metadata,
        "output_root": str(_path(args.output_root)),
    }
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return

    output_root = _path(args.output_root)
    if args.resume_snapshot:
        output = output_root / args.resume_snapshot
        if not output.is_dir():
            raise FileNotFoundError(output)
        if (output / "manifest.json").exists():
            raise FileExistsError(f"Snapshot is already complete and immutable: {output}")
        snapshot_id = output.name
    else:
        snapshot_id = make_snapshot_id(f"yahoo_{args.group}")
        output = output_root / snapshot_id
        output.mkdir(parents=True, exist_ok=False)

    retrieved_at = datetime.now(timezone.utc).isoformat()
    state_path = output / "state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    else:
        state = {"completed": {}, "failures": {}}
    # A configuration correction (for example an official exchange-symbol
    # change) may replace a failed ticker between the first attempt and resume.
    # Retain valid completed files, but do not let superseded symbols keep the
    # resumed snapshot permanently failed.
    state["completed"] = {
        symbol: record for symbol, record in state.get("completed", {}).items() if symbol in symbols
    }
    state["failures"] = {
        symbol: record for symbol, record in state.get("failures", {}).items() if symbol in symbols
    }
    atomic_json_dump(state, state_path)
    settings = config["market_download"]

    for symbol in progress(symbols, description=f"Yahoo {args.group}", total=len(symbols), unit="asset"):
        destination = output / _safe_name(symbol)
        completed = state["completed"].get(symbol)
        if completed and destination.is_file() and sha256_file(destination) == completed.get("sha256"):
            continue
        try:
            frame = _download(
                symbol, settings, str(config["start"]), str(config["end_exclusive"]), retrieved_at
            )
            atomic_parquet_dump(frame, destination)
            state["completed"][symbol] = {
                "path": destination.name,
                "rows": len(frame),
                "first_session": frame["session"].min().date().isoformat(),
                "last_session": frame["session"].max().date().isoformat(),
                "sha256": sha256_file(destination),
            }
            state["failures"].pop(symbol, None)
        except BaseException as exc:
            state["failures"][symbol] = {"type": type(exc).__name__, "error": str(exc)}
        atomic_json_dump(state, state_path)
        time.sleep(float(settings.get("pause_seconds", 0.25)))

    failed = sorted(state["failures"])
    required = bool(group.get("required", True))
    status = "complete" if not failed else ("complete_with_optional_failures" if not required else "failed")
    record = {
        "schema_version": 1,
        "snapshot_id": snapshot_id,
        "status": status,
        "source": "Yahoo Finance through yfinance",
        "retrieved_at_utc": retrieved_at,
        "request": plan,
        "files": [dict({"symbol": symbol}, **state["completed"][symbol]) for symbol in sorted(state["completed"])],
        "failures": state["failures"],
        "packages": package_versions(["pandas", "pyarrow", "yfinance"]),
        "availability_contract": "A daily bar becomes eligible only after its exchange session has completed and before the 08:55 Asia/Kolkata decision cutoff.",
        "limitations": [
            "Yahoo data are a research convenience and remain subject to vendor terms.",
            "Membership validity comes only from the separately supplied point-in-time membership file.",
            "A current constituent download must not be described as historical point-in-time membership.",
        ],
        "declared_symbol_changes": config.get("symbol_changes", []),
    }
    if status == "failed":
        atomic_json_dump(record, output / "FAILED.json")
        raise RuntimeError(
            f"Required group has {len(failed)} failed symbols. Resume after review with: "
            f"--execute --group {args.group} --resume-snapshot {snapshot_id}"
        )
    atomic_json_dump(record, output / "manifest.json")
    print(json.dumps({"snapshot_id": snapshot_id, "status": status, "directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()
