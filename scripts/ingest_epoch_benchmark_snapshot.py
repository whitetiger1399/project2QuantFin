#!/usr/bin/env python3
"""Validate and ingest an immutable Epoch AI benchmark ZIP snapshot."""

from __future__ import annotations

import argparse
import csv
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from quantfin.cross_market.common import root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


EXPECTED_SHA256 = "28a006632f325e82c61ed28603056784ae185b5b596da6e019edd84fe02ddb43"
REQUIRED_FILES = {
    "README.md",
    "benchmark_metadata.csv",
    "model_metadata.csv",
    "epoch_capabilities_index/eci_scores.csv",
    "swe_bench_verified.csv",
    "aider_polyglot_external.csv",
    "gpqa_diamond.csv",
    "math_level_5.csv",
    "mmlu_external.csv",
}


def _safe_member(name: str) -> Path:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe ZIP member: {name}")
    return Path(*path.parts)


def _csv_schema(payload: bytes) -> tuple[list[str], int]:
    text = io.TextIOWrapper(io.BytesIO(payload), encoding="utf-8-sig", errors="replace", newline="")
    reader = csv.reader(text)
    try:
        columns = next(reader)
    except StopIteration:
        return [], 0
    return columns, sum(1 for _ in reader)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", default="data/external/reference/epoch_ai/benchmark_data.zip")
    parser.add_argument("--output-root", default="data/raw/cross_market/epoch_benchmarks")
    parser.add_argument("--expected-sha256", default=EXPECTED_SHA256)
    parser.add_argument("--source-url", default="https://epoch.ai/benchmarks/use-this-data")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    archive = root_path(args.zip)
    if not archive.is_file():
        raise FileNotFoundError(archive)
    archive_hash = sha256_file(archive)
    if args.expected_sha256 and archive_hash != args.expected_sha256:
        raise ValueError(f"Epoch ZIP SHA-256 mismatch: expected {args.expected_sha256}, found {archive_hash}")
    with zipfile.ZipFile(archive) as handle:
        names = [item.filename for item in handle.infolist() if not item.is_dir()]
        missing = sorted(REQUIRED_FILES.difference(names))
        if missing:
            raise ValueError(f"Epoch ZIP is missing required files: {missing}")
        for name in names:
            _safe_member(name)

    identity = stable_object_hash({
        "archive_sha256": archive_hash,
        "required_files": sorted(REQUIRED_FILES),
        "source_url": args.source_url,
        "script_sha256": sha256_file(Path(__file__)),
    })[:16]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_id = f"epoch_benchmarks_{stamp}_{identity}"
    output = root_path(args.output_root) / snapshot_id
    plan = {
        "action": "ingest_epoch_benchmark_snapshot",
        "mode": "execute" if args.execute else "plan_only",
        "snapshot_id": snapshot_id,
        "content_hash": identity,
        "archive": str(archive),
        "archive_sha256": archive_hash,
        "member_count": len(names),
        "output": str(output),
    }
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return

    output.mkdir(parents=True, exist_ok=False)
    schemas: list[dict[str, object]] = []
    file_hashes: dict[str, str] = {}
    with zipfile.ZipFile(archive) as handle:
        for member in progress(handle.infolist(), description="Ingesting Epoch benchmark snapshot", unit="file"):
            if member.is_dir():
                continue
            relative = _safe_member(member.filename)
            payload = handle.read(member)
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
            file_hashes[member.filename] = sha256_file(destination)
            if destination.suffix.lower() == ".csv":
                columns, rows = _csv_schema(payload)
                schemas.append({"file": member.filename, "rows": rows, "columns": columns})
    atomic_json_dump({"tables": schemas}, output / "schema_inventory.json")
    file_hashes["schema_inventory.json"] = sha256_file(output / "schema_inventory.json")
    manifest = {
        "schema_version": 1,
        **plan,
        "status": "complete",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": args.source_url,
        "license_and_citation_note": "Use and cite Epoch AI under the terms stated in the included README and source page.",
        "leakage_policy": "Current-vintage Epoch scores are ex-post research variables, not historical tradable features.",
        "files": file_hashes,
    }
    atomic_json_dump(manifest, output / "manifest.json")
    print(json.dumps({**plan, "status": "complete"}, indent=2))


if __name__ == "__main__":
    main()
