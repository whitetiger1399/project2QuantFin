"""Cross-vendor overlap diagnostics; never modifies the primary dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from quantfin.io import atomic_json_dump, read_manifest, sha256_file, utc_now


def record_skipped_verification(
    yahoo_snapshot: Path,
    reason: str,
    artifacts_root: Path,
) -> Path:
    """Record why the optional independent-source comparison did not run."""
    yahoo_manifest = read_manifest(yahoo_snapshot / "manifest.json")
    destination = artifacts_root / "source_verification" / (
        f"{yahoo_manifest['snapshot_id']}__stooq_unavailable"
    )
    report = {
        "schema_version": 1,
        "created_at_utc": utc_now().isoformat(),
        "status": "skipped",
        "yahoo_snapshot": yahoo_manifest["snapshot_id"],
        "verification_source": "stooq",
        "reason": reason,
        "impact": (
            "The optional independent-source comparison was not performed. "
            "The Yahoo data audit, cleaning, feature construction, and timing checks can continue."
        ),
    }
    report_path = destination / "comparison_skipped.json"
    atomic_json_dump(report, report_path)
    return report_path


def compare_yahoo_stooq(
    yahoo_snapshot: Path,
    stooq_snapshot: Path,
    protocol: dict[str, Any],
    artifacts_root: Path,
) -> Path:
    yahoo_manifest = read_manifest(yahoo_snapshot / "manifest.json")
    stooq_manifest = read_manifest(stooq_snapshot / "manifest.json")
    traded = protocol["market_data"]["traded_asset"]

    yahoo_entry = next(item for item in yahoo_manifest["files"] if item["symbol"] == traded)
    stooq_entry = next(item for item in stooq_manifest["files"] if item["symbol"] == traded)
    yahoo = pd.read_parquet(yahoo_snapshot / yahoo_entry["path"])
    stooq = pd.read_parquet(stooq_snapshot / stooq_entry["path"])
    yahoo["session"] = pd.to_datetime(yahoo["session"]).dt.normalize()
    stooq["session"] = pd.to_datetime(stooq["session"]).dt.normalize()

    joined = yahoo[["session", "close", "adjusted_close"]].rename(
        columns={"close": "yahoo_close", "adjusted_close": "yahoo_adjusted_close"}
    ).merge(
        stooq[["session", "close"]].rename(columns={"close": "stooq_close"}),
        on="session",
        how="inner",
        validate="one_to_one",
    )
    if len(joined) < 2:
        raise ValueError("Fewer than two overlapping Yahoo/Stooq sessions")

    joined["yahoo_adjusted_return"] = joined["yahoo_adjusted_close"].pct_change()
    joined["stooq_close_return"] = joined["stooq_close"].pct_change()
    difference = joined["yahoo_adjusted_return"] - joined["stooq_close_return"]
    largest = joined.assign(abs_return_difference=difference.abs()).nlargest(
        20, "abs_return_difference"
    )

    destination = artifacts_root / "source_verification" / (
        f"{yahoo_manifest['snapshot_id']}__{stooq_manifest['snapshot_id']}"
    )
    report = {
        "schema_version": 1,
        "created_at_utc": utc_now().isoformat(),
        "symbol": traded,
        "yahoo_snapshot": yahoo_manifest["snapshot_id"],
        "stooq_snapshot": stooq_manifest["snapshot_id"],
        "overlapping_sessions": len(joined),
        "return_correlation": float(
            joined[["yahoo_adjusted_return", "stooq_close_return"]].corr().iloc[0, 1]
        ),
        "mean_absolute_return_difference": float(difference.abs().dropna().mean()),
        "largest_return_differences": largest[
            ["session", "yahoo_adjusted_return", "stooq_close_return", "abs_return_difference"]
        ].to_dict(orient="records"),
        "source_manifest_hashes": {
            "yahoo": sha256_file(yahoo_snapshot / "manifest.json"),
            "stooq": sha256_file(stooq_snapshot / "manifest.json"),
        },
        "interpretation_warning": (
            "A discrepancy can reflect different adjustment conventions, session definitions, or vendor errors. "
            "This report does not authorize splicing the two series."
        ),
    }
    atomic_json_dump(report, destination / "comparison.json")
    return destination / "comparison.json"

