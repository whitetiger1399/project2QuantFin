"""Normalize provisional S&P 500 and Nifty 50 snapshots into intervals.

The command is plan-only unless ``--execute`` is supplied. The outputs remain
explicitly provisional and must later be reconciled against WRDS/CRSP and an
official NSE Indices source. ``valid_to`` is an exclusive boundary.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from quantfin.io import atomic_json_dump, sha256_file


ROOT = Path(__file__).resolve().parents[1]
SP500_SOURCE_URL = (
    "https://github.com/fja05680/sp500/blob/master/"
    "S%26P%20500%20Historical%20Components%20%26%20Changes%20%28Updated%29.csv"
)
NIFTY50_SOURCE_URL = "https://niftyhistory.in/"


def _path(value: str) -> Path:
    candidate = Path(value).expanduser()
    return candidate if candidate.is_absolute() else ROOT / candidate


def _symbols(value: Any) -> set[str]:
    if pd.isna(value):
        return set()
    return {item.strip() for item in str(value).split(",") if item.strip()}


def _intervals(
    snapshots: pd.DataFrame,
    date_column: str,
    members_column: str,
    coverage_end: pd.Timestamp,
) -> pd.DataFrame:
    ordered = snapshots.sort_values(date_column).drop_duplicates(date_column, keep="last")
    active: dict[str, pd.Timestamp] = {}
    previous: set[str] = set()
    records: list[dict[str, Any]] = []
    for row in ordered.itertuples(index=False):
        date = pd.Timestamp(getattr(row, date_column)).normalize()
        current = _symbols(getattr(row, members_column))
        for symbol in sorted(previous - current):
            start = active.pop(symbol)
            records.append({"symbol": symbol, "valid_from": start, "valid_to": date})
        for symbol in sorted(current - previous):
            active[symbol] = date
        previous = current
    exclusive_end = coverage_end.normalize() + pd.Timedelta(days=1)
    for symbol, start in sorted(active.items()):
        records.append({"symbol": symbol, "valid_from": start, "valid_to": exclusive_end})
    frame = pd.DataFrame(records)
    if frame.empty:
        raise ValueError("No membership intervals were produced")
    if (frame["valid_to"] <= frame["valid_from"]).any():
        raise ValueError("Membership conversion produced nonpositive intervals")
    return frame.sort_values(["symbol", "valid_from"]).reset_index(drop=True)


def _atomic_csv(frame: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    os.close(fd)
    try:
        frame.to_csv(temporary, index=False)
        os.replace(temporary, destination)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def _protect(destination: Path, overwrite: bool) -> None:
    if not destination.exists():
        return
    try:
        rows = len(pd.read_csv(destination))
    except pd.errors.EmptyDataError:
        rows = 0
    if rows and not overwrite:
        raise FileExistsError(
            f"Refusing to replace populated output {destination}; pass --overwrite after review"
        )


def _sp500(source: Path, study_start: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame = pd.read_csv(source, dtype=str)
    if list(frame.columns) != ["date", "tickers"]:
        raise ValueError(f"Unexpected S&P schema: {list(frame.columns)}")
    frame["date"] = pd.to_datetime(frame["date"], errors="raise")
    if frame["date"].duplicated().any():
        raise ValueError("S&P source contains duplicate snapshot dates")
    counts = frame["tickers"].map(lambda value: len(_symbols(value)))
    coverage_end = frame["date"].max()
    intervals = _intervals(frame, "date", "tickers", coverage_end)
    intervals = intervals.loc[intervals["valid_to"] > pd.Timestamp(study_start)].copy()
    intervals["valid_from"] = intervals["valid_from"].clip(lower=pd.Timestamp(study_start))
    intervals["yahoo_symbol"] = intervals["symbol"].str.replace(".", "-", regex=False)
    intervals["sector"] = pd.NA
    intervals["sub_industry"] = pd.NA
    intervals["announced_at"] = pd.NA
    intervals["source_url"] = SP500_SOURCE_URL
    intervals["source_sha256"] = sha256_file(source)
    intervals["provisional"] = True
    intervals["availability_assumption"] = "effective_membership_snapshot_only"
    intervals["valid_from"] = intervals["valid_from"].dt.date.astype(str)
    intervals["valid_to"] = intervals["valid_to"].dt.date.astype(str)
    columns = [
        "symbol", "yahoo_symbol", "valid_from", "valid_to", "sector", "sub_industry",
        "announced_at", "source_url", "source_sha256", "provisional", "availability_assumption",
    ]
    audit = {
        "rows": len(frame),
        "coverage_start": frame["date"].min().date().isoformat(),
        "coverage_end": coverage_end.date().isoformat(),
        "minimum_snapshot_members": int(counts.min()),
        "median_snapshot_members": float(counts.median()),
        "maximum_snapshot_members": int(counts.max()),
        "snapshots_below_494_members": int((counts < 494).sum()),
        "intervals": len(intervals),
        "unique_symbols": int(intervals["symbol"].nunique()),
        "limitations": [
            "Third-party reconstruction; not official S&P/WRDS data.",
            "Repository author states Wikipedia selected changes are not always complete.",
            "Local source ends before the 2026-10-29 study cutoff.",
            "Historical sector and announcement timestamps are unavailable.",
            "Yahoo may not cover delisted or renamed securities.",
        ],
    }
    return intervals.loc[:, columns], audit


def _nifty50(source: Path, study_start: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame = pd.read_csv(source, dtype=str)
    required = {"effective_date", "index_type", "inclusions", "exclusions", "symbols"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Nifty 50 source is missing columns: {missing}")
    frame["effective_date"] = pd.to_datetime(frame["effective_date"], errors="raise")
    frame = frame.loc[frame["index_type"].eq("Nifty50")].copy()
    if frame["effective_date"].duplicated().any():
        raise ValueError("Nifty 50 source contains duplicate effective dates")
    counts = frame["symbols"].map(lambda value: len(_symbols(value)))
    coverage_end = frame["effective_date"].max()
    intervals = _intervals(frame, "effective_date", "symbols", coverage_end)
    intervals = intervals.loc[intervals["valid_to"] > pd.Timestamp(study_start)].copy()
    intervals["valid_from"] = intervals["valid_from"].clip(lower=pd.Timestamp(study_start))
    intervals["yahoo_symbol"] = intervals["symbol"] + ".NS"
    intervals["announced_at"] = pd.NA
    intervals["source_url"] = NIFTY50_SOURCE_URL
    intervals["source_sha256"] = sha256_file(source)
    intervals["provisional"] = True
    intervals["availability_assumption"] = "effective_date_only_announcement_unknown"
    intervals["valid_from"] = intervals["valid_from"].dt.date.astype(str)
    intervals["valid_to"] = intervals["valid_to"].dt.date.astype(str)
    columns = [
        "symbol", "yahoo_symbol", "valid_from", "valid_to", "announced_at", "source_url",
        "source_sha256", "provisional", "availability_assumption",
    ]
    audit = {
        "rows": len(frame),
        "coverage_start": frame["effective_date"].min().date().isoformat(),
        "coverage_end": coverage_end.date().isoformat(),
        "minimum_snapshot_members": int(counts.min()),
        "median_snapshot_members": float(counts.median()),
        "maximum_snapshot_members": int(counts.max()),
        "snapshots_not_equal_to_50": int((counts != 50).sum()),
        "intervals": len(intervals),
        "unique_symbols": int(intervals["symbol"].nunique()),
        "limitations": [
            "Third-party Nifty 50 reconstruction; not an official NSE Indices feed.",
            "This file does not contain Nifty IT membership.",
            "Announcement timestamps and transparent source-level citations are unavailable.",
            "Three snapshots contain 51 symbols and require later reconciliation.",
        ],
    }
    return intervals.loc[:, columns], audit


def _nifty500(source: Path, study_start: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame = pd.read_csv(source, dtype=str)
    required = {"effective_date", "index_type", "inclusions", "exclusions", "symbols"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Nifty 500 source is missing columns: {missing}")
    frame["effective_date"] = pd.to_datetime(frame["effective_date"], errors="raise")
    frame = frame.loc[frame["index_type"].eq("Nifty500")].copy()
    if frame.empty or frame["effective_date"].duplicated().any():
        raise ValueError("Nifty 500 source is empty or contains duplicate effective dates")
    counts = frame["symbols"].map(lambda value: len(_symbols(value)))
    coverage_end = frame["effective_date"].max()
    intervals = _intervals(frame, "effective_date", "symbols", coverage_end)
    intervals = intervals.loc[intervals["valid_to"] > pd.Timestamp(study_start)].copy()
    intervals["valid_from"] = intervals["valid_from"].clip(lower=pd.Timestamp(study_start))
    intervals["yahoo_symbol"] = intervals["symbol"] + ".NS"
    intervals["announced_at"] = pd.NA
    intervals["source_url"] = NIFTY50_SOURCE_URL
    intervals["source_sha256"] = sha256_file(source)
    intervals["provisional"] = True
    intervals["availability_assumption"] = "effective_date_only_announcement_unknown"
    intervals["valid_from"] = intervals["valid_from"].dt.date.astype(str)
    intervals["valid_to"] = intervals["valid_to"].dt.date.astype(str)
    columns = [
        "symbol", "yahoo_symbol", "valid_from", "valid_to", "announced_at", "source_url",
        "source_sha256", "provisional", "availability_assumption",
    ]
    audit = {
        "rows": len(frame),
        "coverage_start": frame["effective_date"].min().date().isoformat(),
        "coverage_end": coverage_end.date().isoformat(),
        "minimum_snapshot_members": int(counts.min()),
        "median_snapshot_members": float(counts.median()),
        "maximum_snapshot_members": int(counts.max()),
        "snapshots_not_equal_to_500": int((counts != 500).sum()),
        "intervals": len(intervals),
        "unique_symbols": int(intervals["symbol"].nunique()),
        "limitations": [
            "Third-party Nifty 500 reconstruction; not an official NSE Indices feed.",
            "The source has no historical sector classifications and cannot define Nifty IT.",
            "Announcement timestamps and source-level citations are unavailable.",
            "Some snapshots contain 501 symbols and require later reconciliation.",
        ],
    }
    return intervals.loc[:, columns], audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sp500-source",
        default="data/external/reference/current_constituents/S&P 500 Historical Components & Changes (Updated).csv",
    )
    parser.add_argument(
        "--nifty50-source",
        default="data/external/reference/current_constituents/nifty50_2001-01-01_to_2026-12-31.csv",
    )
    parser.add_argument(
        "--nifty500-source",
        default="data/external/reference/current_constituents/nifty500_2001-01-01_to_2026-12-31.csv",
    )
    parser.add_argument("--output-dir", default="data/external/manual/cross_market")
    parser.add_argument("--study-start", default="2004-01-01")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    sp500_source = _path(args.sp500_source)
    nifty50_source = _path(args.nifty50_source)
    nifty500_source = _path(args.nifty500_source)
    for source in (sp500_source, nifty50_source, nifty500_source):
        if not source.is_file():
            raise FileNotFoundError(source)
    sp500, sp500_audit = _sp500(sp500_source, args.study_start)
    nifty50, nifty50_audit = _nifty50(nifty50_source, args.study_start)
    nifty500, nifty500_audit = _nifty500(nifty500_source, args.study_start)
    output = _path(args.output_dir)
    plan = {
        "mode": "execute" if args.execute else "plan_only",
        "study_start": args.study_start,
        "outputs": {
            "sp500_membership.csv": sp500_audit,
            "nifty50_membership.csv": nifty50_audit,
            "nifty500_membership.csv": nifty500_audit,
        },
        "nifty_it_status": "missing; Nifty 50 is not a substitute",
    }
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    sp500_destination = output / "sp500_membership.csv"
    nifty50_destination = output / "nifty50_membership.csv"
    nifty500_destination = output / "nifty500_membership.csv"
    _protect(sp500_destination, args.overwrite)
    _protect(nifty50_destination, args.overwrite)
    _protect(nifty500_destination, args.overwrite)
    _atomic_csv(sp500, sp500_destination)
    _atomic_csv(nifty50, nifty50_destination)
    _atomic_csv(nifty500, nifty500_destination)
    manifest = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "complete_provisional",
        "interval_convention": "valid_from inclusive; valid_to exclusive",
        "source_files": {
            str(sp500_source): sha256_file(sp500_source),
            str(nifty50_source): sha256_file(nifty50_source),
            str(nifty500_source): sha256_file(nifty500_source),
        },
        "outputs": {
            "sp500_membership.csv": {**sp500_audit, "sha256": sha256_file(sp500_destination)},
            "nifty50_membership.csv": {**nifty50_audit, "sha256": sha256_file(nifty50_destination)},
            "nifty500_membership.csv": {**nifty500_audit, "sha256": sha256_file(nifty500_destination)},
        },
        "nifty_it_status": "not available; no Nifty IT membership was inferred from Nifty 50",
    }
    atomic_json_dump(manifest, output / "provisional_membership_manifest.json")
    print(json.dumps({"status": manifest["status"], "manifest": str(output / "provisional_membership_manifest.json")}, indent=2))


if __name__ == "__main__":
    main()
