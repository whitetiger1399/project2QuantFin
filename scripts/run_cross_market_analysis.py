#!/usr/bin/env python3
"""Create report-ready EDA, statistical tests, trend, seasonality, and regime diagnostics."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from quantfin.cross_market.analysis import run_analysis
from quantfin.cross_market.common import environment_record, load_research_config, read_panel_dataset, resolve_dataset, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_research.yaml")
    parser.add_argument("--dataset-id")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    dataset = resolve_dataset(config, args.dataset_id)
    with (dataset / "manifest.json").open("r", encoding="utf-8") as handle:
        dataset_manifest = json.load(handle)
    run_hash = stable_object_hash({
        "action": "cross_market_analysis",
        "dataset_source_hash": dataset_manifest["source_hash"],
        "panel_sha256": dataset_manifest["files"]["panel.parquet"],
        "feature_dictionary_sha256": dataset_manifest["files"]["feature_dictionary.csv"],
        "config": sha256_file(root_path(args.config)),
    })[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"analysis_{stamp}_{run_hash}"
    output = root_path(config["outputs"]["analysis_root"]) / run_id
    plan = {"action": "run_cross_market_analysis", "run_id": run_id, "run_hash": run_hash, "dataset_id": dataset.name, "output": str(output)}
    if args.plan_only:
        print(json.dumps(plan, indent=2)); return
    print(json.dumps({**plan, "status": "starting"}, indent=2), flush=True)
    output.mkdir(parents=True, exist_ok=False)
    atomic_json_dump({**plan, "status": "running", "environment": environment_record()}, output / "run_state.json")
    try:
        panel, metadata, dictionary = read_panel_dataset(dataset)
        summary = run_analysis(panel, dictionary, output, config)
        manifest = {
            "schema_version": 1, **plan, "status": "complete",
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "parent_dataset_manifest_sha256": sha256_file(dataset / "manifest.json"),
            "config_sha256": sha256_file(root_path(args.config)),
            "summary": summary,
            "environment": environment_record(),
        }
        atomic_json_dump(manifest, output / "manifest.json")
        atomic_json_dump({**plan, "status": "complete", "completed_at_utc": manifest["completed_at_utc"]}, output / "run_state.json")
    except BaseException as exc:
        atomic_json_dump({**plan, "status": "failed", "error": repr(exc)}, output / "run_state.json"); raise
    print(json.dumps({"run_id": run_id, "status": "complete", "directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()
