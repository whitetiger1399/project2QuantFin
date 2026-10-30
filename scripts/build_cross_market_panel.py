#!/usr/bin/env python3
"""Build the cleaned and leakage-safe cross-market panel without fitting models."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from quantfin.cross_market.common import (
    environment_record,
    latest_audit,
    load_research_config,
    manifest,
    root_path,
    snapshot_inventory,
    source_fingerprint,
)
from quantfin.cross_market.panel import build_panel
from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_research.yaml")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    audit_path, audit = latest_audit(config["raw_data"]["audit_root"])
    inventory = snapshot_inventory(config)
    fingerprint = source_fingerprint(args.config, inventory, audit_path)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dataset_id = f"cross_market_panel_{stamp}_{fingerprint}"
    output = root_path(config["outputs"]["processed_root"]) / dataset_id
    plan = {
        "action": "build_cross_market_panel",
        "dataset_id": dataset_id,
        "source_hash": fingerprint,
        "raw_audit": str(audit_path),
        "raw_audit_status": audit["status"],
        "snapshots": {name: path.name for name, path in inventory.items()},
        "output": str(output),
    }
    if args.plan_only:
        print(json.dumps(plan, indent=2))
        return
    print(json.dumps({**plan, "status": "starting"}, indent=2), flush=True)
    output.mkdir(parents=True, exist_ok=False)
    atomic_json_dump({**plan, "status": "running", **environment_record()}, output / "run_state.json")
    try:
        panel, dictionary, evidence = build_panel(config, inventory)
        atomic_parquet_dump(panel, output / "panel.parquet")
        dictionary.to_csv(output / "feature_dictionary.csv", index=False)
        atomic_json_dump(evidence, output / "cleaning_evidence.json")
        completed = {
            "schema_version": 1,
            **plan,
            "status": "complete",
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": str(root_path(args.config)),
            "config_sha256": sha256_file(root_path(args.config)),
            "audit_sha256": sha256_file(audit_path),
            "snapshot_manifests": {
                name: {
                    "snapshot_id": manifest(path).get("snapshot_id", path.name),
                    "manifest_sha256": sha256_file(path / "manifest.json"),
                }
                for name, path in inventory.items()
            },
            "files": {
                "panel.parquet": sha256_file(output / "panel.parquet"),
                "feature_dictionary.csv": sha256_file(output / "feature_dictionary.csv"),
                "cleaning_evidence.json": sha256_file(output / "cleaning_evidence.json"),
            },
            "evidence_summary": evidence,
            "environment": environment_record(),
        }
        atomic_json_dump(completed, output / "manifest.json")
        atomic_json_dump({**plan, "status": "complete", "completed_at_utc": completed["completed_at_utc"]}, output / "run_state.json")
    except BaseException as exc:
        atomic_json_dump({**plan, "status": "failed", "error": repr(exc)}, output / "run_state.json")
        raise
    print(json.dumps({"dataset_id": dataset_id, "status": "complete", "directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()
