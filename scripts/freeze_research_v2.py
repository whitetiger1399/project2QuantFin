"""Validate and freeze the v2 research protocol after baseline accounting audit."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash


ROOT = Path(__file__).resolve().parents[1]


def latest_manifest(root: Path, filename: str) -> Path:
    candidates = sorted(root.glob(f"*/{filename}"))
    if not candidates:
        raise FileNotFoundError(f"No {filename} found under {root}")
    return max(candidates, key=lambda path: path.stat().st_mtime_ns)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate(config: dict[str, Any]) -> None:
    required = ["schema_version", "protocol_name", "information_status", "outer_forward_blocks", "timing_contract", "research_space", "selection_contract", "accounting_contract", "compute_budget"]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError("Missing v2 protocol sections: " + ", ".join(missing))
    retrospective = config["information_status"]["retrospective_stress"]
    if retrospective.get("untouched_holdout") is not False:
        raise ValueError("2022-2025 must be declared inspected and not an untouched holdout")
    if config["selection_contract"].get("retrospective_period_must_not_select_winner") is not True:
        raise ValueError("Retrospective results must be prohibited from selecting a winner")
    blocks = config["outer_forward_blocks"]
    if any(block["train_start"] >= block["test_start"] for block in blocks):
        raise ValueError("Every outer block must train strictly before its test start")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/research_v2.yaml")
    parser.add_argument("--archive-manifest")
    parser.add_argument("--accounting-audit")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    validate(config)
    archive = Path(args.archive_manifest).resolve() if args.archive_manifest else latest_manifest(
        ROOT / "artifacts/research_v2/baseline_archives", "manifest.json"
    )
    audit = Path(args.accounting_audit).resolve() if args.accounting_audit else latest_manifest(
        ROOT / "artifacts/research_v2/accounting_audits", "audit_report.json"
    )
    audit_report = read_json(audit)
    if audit_report.get("status") not in {"pass", "pass_with_findings"}:
        raise ValueError(f"Accounting audit has not passed: {audit}")
    identity = {
        "protocol": config,
        "protocol_sha256": sha256_file(config_path),
        "baseline_archive_sha256": sha256_file(archive),
        "accounting_audit_sha256": sha256_file(audit),
    }
    freeze_id = "research_v2_" + stable_object_hash(identity)[:16]
    destination = ROOT / "artifacts/research_v2/freezes" / f"{freeze_id}.json"
    result = {
        "schema_version": 1,
        "freeze_id": freeze_id,
        "status": "frozen",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_path": config_path.relative_to(ROOT).as_posix(),
        "archive_manifest_path": archive.relative_to(ROOT).as_posix(),
        "accounting_audit_path": audit.relative_to(ROOT).as_posix(),
        **identity,
        "immutability_rule": "Any protocol, data, feature, timing, selection, cost, or model-space change requires a new freeze ID.",
    }
    if args.dry_run:
        print(json.dumps({"status": "valid", "freeze_id": freeze_id, "destination": str(destination)}, indent=2))
        return
    if destination.exists():
        existing = read_json(destination)
        if existing.get("protocol_sha256") != result["protocol_sha256"]:
            raise FileExistsError(f"Freeze ID collision: {destination}")
        print(destination)
        return
    atomic_json_dump(result, destination)
    print(destination)


if __name__ == "__main__":
    main()
