"""Audit completed cross-market raw snapshots and write one evidence report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from quantfin.io import atomic_json_dump, read_manifest, sha256_file
from quantfin.progress import progress


ROOT = Path(__file__).resolve().parents[1]


def _path(value: str) -> Path:
    candidate = Path(value).expanduser()
    return candidate if candidate.is_absolute() else ROOT / candidate


def _completed(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(root.glob("*/manifest.json"), key=lambda path: path.stat().st_mtime_ns)


def _audit_yahoo(manifest_path: Path) -> dict[str, Any]:
    manifest = read_manifest(manifest_path)
    issues: list[str] = []
    warnings: list[str] = []
    files: list[dict[str, Any]] = []
    records = manifest.get("files", [])
    group = manifest.get("request", {}).get("group", manifest.get("snapshot_id", "Yahoo"))
    for record in progress(records, description=f"Auditing {group}", total=len(records), unit="file"):
        path = manifest_path.parent / record["path"]
        if not path.is_file():
            issues.append(f"missing:{record['path']}")
            continue
        digest = sha256_file(path)
        if digest != record.get("sha256"):
            issues.append(f"hash_mismatch:{record['path']}")
            continue
        frame = pd.read_parquet(path)
        required = {"session", "open", "high", "low", "close", "adjusted_close", "volume", "symbol"}
        missing = sorted(required.difference(frame.columns))
        if missing:
            issues.append(f"columns:{record['path']}:{missing}")
        duplicate_sessions = int(frame["session"].duplicated().sum()) if "session" in frame else -1
        impossible = 0
        if {"open", "high", "low", "close"}.issubset(frame.columns):
            maximum = frame[["open", "close", "low"]].max(axis=1)
            minimum = frame[["open", "close", "high"]].min(axis=1)
            impossible = int(((frame["high"] < maximum) | (frame["low"] > minimum)).sum())
        if duplicate_sessions:
            issues.append(f"duplicate_sessions:{record['path']}:{duplicate_sessions}")
        if impossible:
            symbol = str(record.get("symbol", ""))
            fraction = impossible / max(len(frame), 1)
            if symbol.endswith("=X"):
                warnings.append(
                    f"fx_ohlc_envelope:{record['path']}:{impossible}:{fraction:.6f}:"
                    "close_to_close_only_no_intraday_features"
                )
            elif impossible <= max(2, int(0.001 * len(frame))):
                warnings.append(
                    f"isolated_ohlc_anomaly:{record['path']}:{impossible}:{fraction:.6f}:"
                    "quarantine_affected_rows"
                )
            else:
                issues.append(f"impossible_ohlc:{record['path']}:{impossible}:{fraction:.6f}")
        files.append(
            {
                "symbol": record.get("symbol"),
                "rows": len(frame),
                "first_session": str(pd.to_datetime(frame["session"]).min().date()) if len(frame) else None,
                "last_session": str(pd.to_datetime(frame["session"]).max().date()) if len(frame) else None,
            }
        )
    return {
        "snapshot_id": manifest.get("snapshot_id"),
        "group": manifest.get("request", {}).get("group"),
        "status": manifest.get("status"),
        "file_count": len(files),
        "failures": manifest.get("failures", {}),
        "issues": issues,
        "warnings": warnings,
        "files": files,
    }


def _audit_csv_snapshot(manifest_path: Path) -> dict[str, Any]:
    manifest = read_manifest(manifest_path)
    issues: list[str] = []
    records = manifest.get("files", [])
    for record in records:
        path = manifest_path.parent / record["path" if "path" in record else "filename"]
        if not path.is_file():
            issues.append(f"missing:{path.name}")
            continue
        expected = record.get("sha256") or record.get("copied_sha256")
        if expected and sha256_file(path) != expected:
            issues.append(f"hash_mismatch:{path.name}")
        frame = pd.read_csv(path)
        if frame.empty:
            issues.append(f"empty:{path.name}")
        if {"realtime_start", "date", "value"}.issubset(frame.columns):
            if pd.to_datetime(frame["realtime_start"], errors="coerce").isna().any():
                issues.append(f"invalid_realtime_start:{path.name}")
    return {
        "snapshot_id": manifest.get("snapshot_id"),
        "status": manifest.get("status"),
        "file_count": len(records),
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", default="data/raw/cross_market")
    parser.add_argument("--output-root", default="artifacts/data_audits/cross_market")
    parser.add_argument(
        "--required-group",
        action="append",
        default=[],
        help="Repeat for each Yahoo market group that must have a completed snapshot",
    )
    args = parser.parse_args()
    raw = _path(args.raw_root)
    yahoo_reports = [_audit_yahoo(path) for path in _completed(raw / "yahoo")]
    latest_by_group: dict[str, dict[str, Any]] = {}
    for report in yahoo_reports:
        if report.get("group"):
            latest_by_group[str(report["group"])] = report
    missing_groups = sorted(set(args.required_group).difference(latest_by_group))
    fred_reports = [_audit_csv_snapshot(path) for path in _completed(raw / "fred_alfred")]
    manual_reports = [_audit_csv_snapshot(path) for path in _completed(raw / "manual_official")]

    # Pass/fail is scoped to the latest snapshot of each explicitly required
    # Yahoo group. Optional exploratory universes can contain stale/delisted
    # vendor symbols or quarantinable rows; those defects must remain visible
    # without invalidating an otherwise complete primary research dataset.
    required_yahoo_reports = [
        latest_by_group[group]
        for group in args.required_group
        if group in latest_by_group
    ]
    optional_group_issues = {
        group: report.get("issues", [])
        for group, report in sorted(latest_by_group.items())
        if group not in set(args.required_group) and report.get("issues")
    }
    latest_fred_reports = fred_reports[-1:]
    latest_manual_reports = manual_reports[-1:]
    issues = [
        issue
        for report in [*required_yahoo_reports, *latest_fred_reports, *latest_manual_reports]
        for issue in report.get("issues", [])
    ]
    warnings = [
        warning
        for report in [*latest_by_group.values(), *latest_fred_reports, *latest_manual_reports]
        for warning in report.get("warnings", [])
    ]
    if not fred_reports:
        issues.append("missing_completed_fred_alfred_snapshot")
    status = (
        "fail"
        if issues or missing_groups
        else ("pass_with_warnings" if warnings else "pass")
    )
    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "missing_required_groups": missing_groups,
        "issues": issues,
        "warnings": warnings,
        "nonblocking_optional_group_issues": optional_group_issues,
        "cleaning_restrictions": [
            "Use INR=X as a close-to-close FX series only; do not construct intraday OHLC features from Yahoo FX bars.",
            "Quarantine the NIFTYBEES.NS 2009-07-07 row from any open-to-close calculation because its reported open is zero.",
            "For optional broad-universe predictors, quarantine every row named by an OHLC warning and exclude any symbol named by nonblocking_optional_group_issues until repaired or independently verified.",
        ],
        "latest_yahoo_by_group": latest_by_group,
        "fred_alfred_snapshots": fred_reports,
        "manual_official_snapshots": manual_reports,
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = _path(args.output_root) / f"audit_{stamp}.json"
    atomic_json_dump(report, destination)
    print(
        json.dumps(
            {
                "status": status,
                "report": str(destination),
                "issues": len(issues),
                "warnings": len(warnings),
            },
            indent=2,
        )
    )
    if status == "fail":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
