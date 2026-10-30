"""Shared configuration, snapshot, hashing, and run-state helpers."""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from quantfin.io import atomic_json_dump, package_versions, sha256_file, stable_object_hash


ROOT = Path(__file__).resolve().parents[3]


def root_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def load_research_config(path: str | Path) -> dict[str, Any]:
    location = root_path(path)
    with location.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError(f"Unsupported research configuration: {location}")
    return config


def latest_snapshot(root: str | Path, prefix: str) -> Path:
    base = root_path(root)
    candidates = [p for p in base.glob(f"{prefix}_*") if (p / "manifest.json").is_file()]
    if not candidates:
        raise FileNotFoundError(f"No completed {prefix} snapshot under {base}")
    return max(candidates, key=lambda p: (p / "manifest.json").stat().st_mtime_ns)


def latest_audit(root: str | Path) -> tuple[Path, dict[str, Any]]:
    base = root_path(root)
    candidates = list(base.glob("audit_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No cross-market audit under {base}")
    path = max(candidates, key=lambda p: p.stat().st_mtime_ns)
    with path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    if report.get("status") not in {"pass", "pass_with_warnings"}:
        raise RuntimeError(f"Latest raw-data audit does not pass: {path}")
    return path, report


def manifest(path: Path) -> dict[str, Any]:
    with (path / "manifest.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def snapshot_inventory(config: dict[str, Any]) -> dict[str, Path]:
    raw = config["raw_data"]
    inventory: dict[str, Path] = {}
    for group in [*raw["required_groups"], *raw.get("optional_groups", [])]:
        try:
            inventory[group] = latest_snapshot(raw["yahoo_root"], f"yahoo_{group}")
        except FileNotFoundError:
            if group in raw["required_groups"]:
                raise
    inventory["fred_alfred"] = latest_snapshot(raw["fred_root"], "fred_alfred")
    return inventory


def source_fingerprint(config_path: str | Path, inventory: dict[str, Path], audit_path: Path) -> str:
    with audit_path.open("r", encoding="utf-8") as handle:
        audit = json.load(handle)
    audit_contract = {
        "status": audit.get("status"),
        "issues": audit.get("issues", []),
        "warnings": audit.get("warnings", []),
        "missing_required_groups": audit.get("missing_required_groups", []),
        "cleaning_restrictions": audit.get("cleaning_restrictions", []),
    }
    payload = {
        "config_sha256": sha256_file(root_path(config_path)),
        "audit_contract_hash": stable_object_hash(audit_contract),
        "snapshots": {
            name: {
                "id": path.name,
                "manifest_sha256": sha256_file(path / "manifest.json"),
            }
            for name, path in sorted(inventory.items())
        },
    }
    return stable_object_hash(payload)[:16]


def environment_record() -> dict[str, Any]:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "packages": package_versions(
            ["numpy", "pandas", "pyarrow", "scikit-learn", "scipy", "statsmodels", "matplotlib", "seaborn"]
        ),
    }


def research_code_hash(extra_paths: list[str | Path] | None = None) -> str:
    """Hash executable research code so model-run hashes change after code edits."""
    files = sorted((ROOT / "src" / "quantfin" / "cross_market").glob("*.py"))
    files.extend(root_path(path) for path in (extra_paths or []))
    payload = {str(path.relative_to(ROOT)): sha256_file(path) for path in files if path.is_file()}
    return stable_object_hash(payload)


def read_panel_dataset(path: str | Path) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    directory = root_path(path)
    if not directory.is_dir():
        raise FileNotFoundError(directory)
    panel = pd.read_parquet(directory / "panel.parquet")
    dictionary = pd.read_csv(directory / "feature_dictionary.csv")
    with (directory / "manifest.json").open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    panel["decision_date"] = pd.to_datetime(panel["decision_date"])
    return panel, metadata, dictionary


def resolve_dataset(config: dict[str, Any], dataset_id: str | None) -> Path:
    root = root_path(config["outputs"]["processed_root"])
    if dataset_id:
        path = root / dataset_id
        if not (path / "manifest.json").is_file():
            raise FileNotFoundError(f"Dataset does not exist or is incomplete: {path}")
        return path
    candidates = [p for p in root.glob("cross_market_panel_*") if (p / "manifest.json").is_file()]
    if not candidates:
        raise FileNotFoundError(f"No completed cross-market panel under {root}")
    return max(candidates, key=lambda p: (p / "manifest.json").stat().st_mtime_ns)


def write_run_state(run_directory: Path, **values: Any) -> None:
    """Update run state while allowing a user-facing ``directory`` metadata key."""
    state_path = run_directory / "run_state.json"
    current: dict[str, Any] = {}
    if state_path.is_file():
        with state_path.open("r", encoding="utf-8") as handle:
            current = json.load(handle)
    current.update(values)
    current["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    atomic_json_dump(current, state_path)
