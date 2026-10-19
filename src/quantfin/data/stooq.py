"""Optional Stooq adapter used only for independent price checks."""

from __future__ import annotations

from datetime import timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas_datareader import data as web

from quantfin.errors import SourceFetchError
from quantfin.io import (
    atomic_json_dump,
    atomic_parquet_dump,
    make_snapshot_id,
    package_versions,
    sha256_file,
    utc_now,
)


def fetch_stooq_snapshot(protocol: dict[str, Any], raw_root: Path) -> Path:
    market = protocol["market_data"]
    mappings = market.get("stooq", {}).get("symbols", {})
    if not mappings:
        raise ValueError("No Stooq symbol mappings configured")

    retrieved = utc_now()
    retrieved_iso = retrieved.astimezone(timezone.utc).isoformat()
    snapshot_id = make_snapshot_id("stooq", retrieved)
    destination = raw_root / "stooq" / snapshot_id
    destination.mkdir(parents=True, exist_ok=False)
    files: list[dict[str, Any]] = []

    try:
        for canonical_symbol, stooq_symbol in mappings.items():
            frame = web.DataReader(
                stooq_symbol,
                "stooq",
                start=market["start"],
                end=pd.Timestamp(market["end_exclusive"]) - pd.Timedelta(days=1),
            ).sort_index()
            if frame.empty:
                raise ValueError(f"Stooq returned no rows for {stooq_symbol}")
            frame = frame.reset_index()
            frame.columns = [str(column).strip().lower().replace(" ", "_") for column in frame]
            frame = frame.rename(columns={"date": "session"})
            frame["session"] = pd.to_datetime(frame["session"]).dt.normalize()
            frame["symbol"] = canonical_symbol
            frame["vendor_symbol"] = stooq_symbol
            frame["source"] = "stooq"
            frame["retrieved_at_utc"] = retrieved_iso
            file_path = destination / f"{canonical_symbol}.parquet"
            atomic_parquet_dump(frame, file_path)
            files.append(
                {
                    "symbol": canonical_symbol,
                    "vendor_symbol": stooq_symbol,
                    "path": file_path.name,
                    "rows": len(frame),
                    "first_session": frame["session"].min().date().isoformat(),
                    "last_session": frame["session"].max().date().isoformat(),
                    "sha256": sha256_file(file_path),
                }
            )
        atomic_json_dump(
            {
                "schema_version": 1,
                "snapshot_id": snapshot_id,
                "source": "stooq",
                "status": "complete",
                "retrieved_at_utc": retrieved_iso,
                "request": {
                    "symbols": mappings,
                    "start": market["start"],
                    "end_inclusive": str(
                        (pd.Timestamp(market["end_exclusive"]) - pd.Timedelta(days=1)).date()
                    ),
                },
                "notes": [
                    "Stooq is a verification source only.",
                    "Do not splice its prices into the Yahoo series without reconciling adjustment semantics.",
                ],
                "packages": package_versions(["pandas", "pandas-datareader", "pyarrow"]),
                "files": files,
            },
            destination / "manifest.json",
        )
    except BaseException as exc:
        failure_record = destination / "FAILED.json"
        atomic_json_dump(
            {
                "schema_version": 1,
                "snapshot_id": snapshot_id,
                "source": "stooq",
                "status": "failed",
                "retrieved_at_utc": retrieved_iso,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "files_written_before_failure": files,
            },
            failure_record,
        )
        raise SourceFetchError("Stooq", failure_record, exc) from exc

    return destination

