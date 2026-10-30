"""Validate and snapshot official/manual source files without altering them.

Copy the completed CSV templates into ``data/external/manual/cross_market``.
This command is plan-only unless ``--execute`` is supplied. Empty templates are
rejected during execution.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from quantfin.config import load_yaml
from quantfin.io import atomic_json_dump, make_snapshot_id, sha256_file


ROOT = Path(__file__).resolve().parents[1]


def _path(value: str) -> Path:
    candidate = Path(value).expanduser()
    return candidate if candidate.is_absolute() else ROOT / candidate


def _validate_dates(frame: pd.DataFrame, filename: str) -> list[str]:
    date_columns = [
        column
        for column in frame.columns
        if column.endswith("_date")
        or column.endswith("_at")
        or column in {"valid_from", "valid_to", "observation_date", "holiday_date", "effective_at"}
    ]
    validated: list[str] = []
    for column in date_columns:
        nonempty = frame[column].dropna().astype(str).str.strip()
        nonempty = nonempty[nonempty.ne("")]
        if nonempty.empty:
            continue
        parsed = pd.to_datetime(nonempty, errors="coerce", utc=column.endswith("_utc"))
        if parsed.isna().any():
            examples = nonempty[parsed.isna()].head(3).tolist()
            raise ValueError(f"{filename}: invalid {column} values: {examples}")
        validated.append(column)
    return validated


def _validate_intervals(frame: pd.DataFrame, filename: str) -> None:
    if not {"valid_from", "valid_to"}.issubset(frame.columns):
        return
    start = pd.to_datetime(frame["valid_from"], errors="coerce")
    end = pd.to_datetime(frame["valid_to"], errors="coerce")
    invalid = end.notna() & start.notna() & end.lt(start)
    if invalid.any():
        raise ValueError(f"{filename}: {int(invalid.sum())} membership intervals end before they begin")


def _validate_source(name: str, specification: dict[str, Any], source: Path) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(source)
    frame = pd.read_csv(source)
    if frame.empty:
        raise ValueError(f"{source.name} contains no data rows")
    required = list(specification["required_columns"])
    nullable = set(specification.get("nullable_columns", []))
    missing = sorted(set(required).difference(frame.columns))
    if missing:
        raise ValueError(f"{source.name} is missing columns: {missing}")
    empty_required = [
        column
        for column in required
        if column not in {"valid_to", "end_at_utc", "revision_at", "actual_release_at_utc"}
        and column not in nullable
        and frame[column].isna().all()
    ]
    if empty_required:
        raise ValueError(f"{source.name} has entirely empty required columns: {empty_required}")
    validated_dates = _validate_dates(frame, source.name)
    _validate_intervals(frame, source.name)
    if "source_url" in frame and frame["source_url"].fillna("").astype(str).str.strip().eq("").any():
        raise ValueError(f"{source.name}: every row must retain source_url provenance")
    return {
        "source_name": name,
        "filename": source.name,
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "validated_date_columns": validated_dates,
        "sha256": sha256_file(source),
        "reason": specification.get("reason"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_data_2026-10-29.yaml")
    parser.add_argument("--input-dir", default="data/external/manual/cross_market")
    parser.add_argument("--output-root", default="data/raw/cross_market/manual_official")
    parser.add_argument("--source", action="append", help="Repeat to ingest a subset; default is all present files")
    parser.add_argument("--require-all", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    config = load_yaml(_path(args.config))
    specifications = config["manual_sources"]
    selected = args.source or list(specifications)
    unknown = sorted(set(selected).difference(specifications))
    if unknown:
        raise KeyError(f"Unknown manual sources: {unknown}")
    input_dir = _path(args.input_dir)
    present: list[tuple[str, dict[str, Any], Path]] = []
    missing: list[str] = []
    for name in selected:
        specification = specifications[name]
        source = input_dir / specification["filename"]
        if source.is_file():
            present.append((name, specification, source))
        else:
            missing.append(name)
    if args.require_all and missing:
        raise FileNotFoundError(f"Required manual files are absent: {missing}")
    plan = {
        "mode": "execute" if args.execute else "plan_only",
        "input_directory": str(input_dir),
        "selected": selected,
        "present": [name for name, _, _ in present],
        "missing": missing,
        "require_all": args.require_all,
        "template_directory": str(ROOT / "resources/data_templates"),
    }
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    if not present:
        raise FileNotFoundError(f"No selected manual files found under {input_dir}")

    snapshot_id = make_snapshot_id("manual_official")
    output = _path(args.output_root) / snapshot_id
    output.mkdir(parents=True, exist_ok=False)
    records: list[dict[str, Any]] = []
    try:
        for name, specification, source in present:
            record = _validate_source(name, specification, source)
            destination = output / source.name
            shutil.copy2(source, destination)
            record["copied_sha256"] = sha256_file(destination)
            records.append(record)
        manifest = {
            "schema_version": 1,
            "snapshot_id": snapshot_id,
            "status": "complete" if not missing else "complete_partial",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "files": records,
            "missing": missing,
            "request": plan,
            "availability_contract": "published_at, announced_at, actual_release_at_utc, or first_public_at_utc controls first eligibility; observation/reference dates alone never do.",
        }
        atomic_json_dump(manifest, output / "manifest.json")
        print(json.dumps({"snapshot_id": snapshot_id, "directory": str(output), "status": manifest["status"]}, indent=2))
    except BaseException as exc:
        atomic_json_dump(
            {"snapshot_id": snapshot_id, "status": "failed", "error": f"{type(exc).__name__}: {exc}"},
            output / "FAILED.json",
        )
        raise


if __name__ == "__main__":
    main()
