"""Create a hash-addressed, non-destructive manifest of the inspected v1 evidence."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tqdm import tqdm

from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash


ROOT = Path(__file__).resolve().parents[1]
CORE_PATHS = [
    "configs/protocol.yaml",
    "configs/models.yaml",
    "configs/features.yaml",
    "data/processed/market_yahoo_20261019T010846Z",
    "data/processed/features_yahoo_20261019T010846Z_799f619a4f",
    "artifacts/runs/models_screening_8d1f4f8a10e794eb",
    "artifacts/runs/models_confirmation_5d6ed2ce5fa7b6cb",
    "artifacts/runs/models_final_test_53e047b58e92e27b",
    "artifacts/freezes/freeze_f98a78b584d0ca42.json",
    "reports/Project2_Team16_Report.docx",
    "reports/Project2_Team16_Report.pdf",
    "reports/output_verification.json",
]


def git_value(*args: str) -> str | None:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def inventory(include_checkpoints: bool) -> list[dict[str, Any]]:
    files: list[Path] = []
    missing: list[str] = []
    for relative in CORE_PATHS:
        path = ROOT / relative
        if not path.exists():
            missing.append(relative)
        elif path.is_file():
            files.append(path)
        else:
            files.extend(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file()
                and (include_checkpoints or "checkpoints" not in candidate.parts)
            )
    if missing:
        raise FileNotFoundError("Missing canonical v1 paths: " + ", ".join(missing))
    records = []
    for path in tqdm(sorted(set(files)), desc="Hashing v1 evidence", unit="file"):
        records.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return records


def copy_payload(records: list[dict[str, Any]], archive_directory: Path) -> None:
    payload_root = archive_directory / "payload"
    for record in tqdm(records, desc="Copying immutable v1 payload", unit="file"):
        source = ROOT / record["path"]
        destination = payload_root / record["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if sha256_file(destination) != record["sha256"]:
                raise FileExistsError(f"Archived payload differs from manifest: {destination}")
            continue
        fd, temporary = tempfile.mkstemp(
            prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
        )
        os.close(fd)
        try:
            shutil.copy2(source, temporary)
            if sha256_file(Path(temporary)) != record["sha256"]:
                raise IOError(f"Copied payload failed hash verification: {source}")
            os.replace(temporary, destination)
        except BaseException:
            Path(temporary).unlink(missing_ok=True)
            raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--include-checkpoints", action="store_true")
    parser.add_argument("--manifest-only", action="store_true")
    args = parser.parse_args()

    if args.plan_only:
        print(json.dumps({
            "action": "archive_v1",
            "mode": "plan_only",
            "roots": CORE_PATHS,
            "include_checkpoints": args.include_checkpoints,
            "manifest_only": args.manifest_only,
            "writes_under": "artifacts/research_v2/baseline_archives",
        }, indent=2))
        return

    records = inventory(args.include_checkpoints)
    stable_payload = {
        "schema_version": 1,
        "baseline": "v1",
        "files": records,
        "include_checkpoints": args.include_checkpoints,
        "archive_mode": "manifest_only" if args.manifest_only else "copied_payload",
        "inspected_periods": [
            {
                "start": "2015-01-01",
                "end": "2018-12-31",
                "role": "screening",
                "status": "inspected",
            },
            {
                "start": "2019-01-01",
                "end": "2021-12-31",
                "role": "confirmation",
                "status": "inspected",
            },
            {
                "start": "2022-01-01",
                "end": "2025-12-31",
                "role": "former_final_holdout",
                "status": "inspected_retrospective",
            },
        ],
    }
    archive_id = "v1_" + stable_object_hash(stable_payload)[:16]
    destination = ROOT / "artifacts/research_v2/baseline_archives" / archive_id / "manifest.json"
    manifest = {
        **stable_payload,
        "archive_id": archive_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_revision": git_value("rev-parse", "HEAD"),
        "git_status_porcelain": git_value("status", "--porcelain"),
        "total_bytes": sum(item["bytes"] for item in records),
        "recovery_contract": (
            "Restore each file from payload/<relative path> and verify SHA-256."
            if not args.manifest_only
            else "Resolve each relative path at the recorded Git revision and verify SHA-256."
        ),
    }
    if destination.exists():
        existing = json.loads(destination.read_text(encoding="utf-8"))
        if existing.get("files") != records:
            raise FileExistsError(f"Archive ID collision with different content: {destination}")
        print(destination)
        return
    if not args.manifest_only:
        copy_payload(records, destination.parent)
    atomic_json_dump(manifest, destination)
    print(destination)


if __name__ == "__main__":
    main()
