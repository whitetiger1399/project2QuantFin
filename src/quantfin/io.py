"""Small, deterministic filesystem helpers used by data pipeline commands."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def make_snapshot_id(source: str, timestamp: datetime | None = None) -> str:
    stamp = (timestamp or utc_now()).strftime("%Y%m%dT%H%M%SZ")
    return f"{source}_{stamp}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_object_hash(value: Any) -> str:
    """Hash a JSON-compatible configuration independent of dictionary order."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def atomic_json_dump(value: Any, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, default=str)
            handle.write("\n")
        os.replace(temporary_name, destination)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def atomic_parquet_dump(frame: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".parquet", dir=destination.parent
    )
    os.close(fd)
    try:
        frame.to_parquet(temporary_name, index=False)
        os.replace(temporary_name, destination)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def package_versions(names: list[str]) -> dict[str, str | None]:
    from importlib.metadata import PackageNotFoundError, version

    versions: dict[str, str | None] = {}
    for name in names:
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            versions[name] = None
    return versions


def read_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if not isinstance(manifest, dict):
        raise ValueError(f"Manifest must contain a JSON object: {path}")
    return manifest


def resolve_snapshot(raw_root: Path, source: str, snapshot_id: str | None) -> Path:
    source_root = raw_root / source
    if snapshot_id:
        path = source_root / snapshot_id
        if not path.is_dir():
            raise FileNotFoundError(f"Snapshot does not exist: {path}")
        if not (path / "manifest.json").is_file():
            failure_record = path / "FAILED.json"
            detail = (
                f" Failure details: {failure_record}"
                if failure_record.is_file()
                else ""
            )
            raise FileNotFoundError(
                f"Snapshot is not complete because manifest.json is absent: {path}.{detail}"
            )
        return path

    candidates = sorted(
        path for path in source_root.glob(f"{source}_*") if (path / "manifest.json").is_file()
    )
    if not candidates:
        raise FileNotFoundError(
            f"No completed {source} snapshots found under {source_root}. Run fetch first."
        )
    return candidates[-1]

