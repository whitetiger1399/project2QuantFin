#!/usr/bin/env python3
"""Verify hashes, parent links, stage order, and completeness of cross-market outputs."""

from __future__ import annotations

import argparse
import json

import pandas as pd

from quantfin.cross_market.common import load_research_config, root_path
from quantfin.io import sha256_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_research.yaml")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--analysis-run-id")
    parser.add_argument("--screening-run-id")
    parser.add_argument("--confirmation-run-id")
    parser.add_argument("--freeze-id")
    parser.add_argument("--final-run-id")
    args = parser.parse_args()
    config = load_research_config(args.config)
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(condition), "detail": detail})

    dataset = root_path(config["outputs"]["processed_root"]) / args.dataset_id
    check("dataset_manifest", (dataset / "manifest.json").is_file(), str(dataset))
    if (dataset / "manifest.json").is_file():
        metadata = json.load(open(dataset / "manifest.json", encoding="utf-8"))
        check("dataset_complete", metadata.get("status") == "complete")
        for filename, expected in metadata.get("files", {}).items():
            check(f"dataset_hash:{filename}", (dataset / filename).is_file() and sha256_file(dataset / filename) == expected)
        panel = pd.read_parquet(dataset / "panel.parquet", columns=["decision_date", "asset", "target_oc_return"])
        check("unique_panel_key", not panel.duplicated(["decision_date", "asset"]).any())
        check("target_complete", panel["target_oc_return"].notna().all())
    if args.analysis_run_id:
        analysis = root_path(config["outputs"]["analysis_root"]) / args.analysis_run_id
        analysis_manifest = analysis / "manifest.json"
        check("analysis_manifest", analysis_manifest.is_file(), str(analysis))
        if analysis_manifest.is_file():
            record = json.load(open(analysis_manifest, encoding="utf-8"))
            check("analysis_complete", record.get("status") == "complete")
            check("analysis_dataset", record.get("dataset_id") == args.dataset_id)
            for filename in ["analysis_summary.json", "dataset_quality_by_asset.csv", "return_statistical_tests.csv", "feature_target_tests.csv"]:
                check(f"analysis_file:{filename}", (analysis / filename).is_file())

    run_ids = {
        "screening": args.screening_run_id,
        "confirmation": args.confirmation_run_id,
        "final_test": args.final_run_id,
    }
    manifests: dict[str, dict] = {}
    for stage, run_id in run_ids.items():
        if not run_id:
            continue
        directory = root_path(config["outputs"]["runs_root"]) / run_id
        path = directory / "manifest.json"
        check(f"{stage}_manifest", path.is_file(), str(directory))
        if path.is_file():
            record = json.load(open(path, encoding="utf-8")); manifests[stage] = record
            check(f"{stage}_complete", record.get("status") == "complete")
            check(f"{stage}_label", record.get("stage") == stage)
            check(f"{stage}_dataset", record.get("dataset_id") == args.dataset_id)
            for filename in ["predictions.parquet", "leaderboard.csv", "refit_diagnostics.csv", "strategy_ledgers.parquet", "cost_sensitivity.csv"]:
                check(f"{stage}_file:{filename}", (directory / filename).is_file())
    if "confirmation" in manifests and args.screening_run_id:
        check("confirmation_parent", manifests["confirmation"].get("screening_run_id") == args.screening_run_id)
    if args.freeze_id:
        freeze_path = root_path(config["outputs"]["freezes_root"]) / f"{args.freeze_id}.json"
        check("freeze_file", freeze_path.is_file(), str(freeze_path))
        if freeze_path.is_file():
            freeze = json.load(open(freeze_path, encoding="utf-8"))
            check("freeze_confirmation_parent", freeze.get("confirmation_run_id") == args.confirmation_run_id)
            check("freeze_single_model", freeze.get("final_model_count") == 1)
            if "final_test" in manifests:
                check("final_freeze_parent", manifests["final_test"].get("freeze_id") == args.freeze_id)
                check("final_frozen_config", manifests["final_test"].get("selected_config_id") == freeze.get("selected_config_id"))
    failed = [row for row in checks if not row["passed"]]
    report = {"status": "pass" if not failed else "fail", "checks_passed": len(checks) - len(failed), "checks_failed": len(failed), "checks": checks}
    print(json.dumps(report, indent=2))
    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
