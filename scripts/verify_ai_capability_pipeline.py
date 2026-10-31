#!/usr/bin/env python3
"""Verify the complete AI-capability dataset, analyses, stage lineage, hashes, and final freeze."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from quantfin.cross_market.common import load_research_config, root_path
from quantfin.io import sha256_file
from quantfin.progress import progress


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_ai_capability_research.yaml")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--epoch-snapshot-id", required=True)
    parser.add_argument("--eda-run-id", required=True)
    parser.add_argument("--capability-analysis-id", required=True)
    parser.add_argument("--epoch-analysis-id", required=True)
    parser.add_argument("--screening-run-id", required=True)
    parser.add_argument("--confirmation-run-id", required=True)
    parser.add_argument("--freeze-id", required=True)
    parser.add_argument("--final-run-id", required=True)
    args = parser.parse_args()
    config = load_research_config(args.config)
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(condition), "detail": detail})

    def verify_manifest(directory: Path, label: str) -> dict:
        path = directory / "manifest.json"
        check(f"{label}:manifest_exists", path.is_file(), str(path))
        if not path.is_file():
            return {}
        record = json.loads(path.read_text(encoding="utf-8"))
        check(f"{label}:complete", record.get("status") == "complete")
        for relative, expected in progress(record.get("files", {}).items(), description=f"Verifying {label}", unit="file"):
            file_path = directory / relative
            check(f"{label}:hash:{relative}", file_path.is_file() and sha256_file(file_path) == expected)
        return record

    dataset = root_path(config["outputs"]["processed_root"]) / args.dataset_id
    dataset_manifest = verify_manifest(dataset, "dataset")
    if dataset_manifest:
        panel = pd.read_parquet(dataset / "panel.parquet", columns=["decision_date", "asset", "target_oc_return"])
        check("dataset:unique_date_asset", not panel.duplicated(["decision_date", "asset"]).any())
        check("dataset:target_complete", panel["target_oc_return"].notna().all())
        check("dataset:final_period_ends_2025", pd.to_datetime(panel["decision_date"]).max() <= pd.Timestamp("2025-12-31"))

    epoch = root_path("data/raw/cross_market/epoch_benchmarks") / args.epoch_snapshot_id
    epoch_manifest = verify_manifest(epoch, "epoch_snapshot")
    check("epoch_snapshot:ex_post_policy", "ex-post" in str(epoch_manifest.get("leakage_policy", "")).lower())

    analysis_root = root_path(config["outputs"]["analysis_root"])
    eda = verify_manifest(analysis_root / args.eda_run_id, "eda")
    check("eda:dataset_parent", eda.get("dataset_id") == args.dataset_id)
    capability = verify_manifest(analysis_root / args.capability_analysis_id, "parameter_analysis")
    check("parameter_analysis:dataset_parent", capability.get("dataset_id") == args.dataset_id)
    epoch_analysis = verify_manifest(analysis_root / args.epoch_analysis_id, "epoch_analysis")
    check("epoch_analysis:dataset_parent", epoch_analysis.get("dataset_id") == args.dataset_id)
    check("epoch_analysis:not_tradable", epoch_analysis.get("classification") == "ex_post_not_tradable")

    runs_root = root_path(config["outputs"]["runs_root"])
    screening = verify_manifest(runs_root / args.screening_run_id, "screening")
    confirmation = verify_manifest(runs_root / args.confirmation_run_id, "confirmation")
    final = verify_manifest(runs_root / args.final_run_id, "final_test")
    for label, record in [("screening", screening), ("confirmation", confirmation), ("final_test", final)]:
        check(f"{label}:stage", record.get("stage") == label)
        check(f"{label}:dataset_parent", record.get("dataset_id") == args.dataset_id)
    check("confirmation:screening_parent", confirmation.get("screening_run_id") == args.screening_run_id)

    freeze_path = root_path(config["outputs"]["freezes_root"]) / f"{args.freeze_id}.json"
    check("freeze:exists", freeze_path.is_file(), str(freeze_path))
    freeze = json.loads(freeze_path.read_text(encoding="utf-8")) if freeze_path.is_file() else {}
    check("freeze:confirmation_parent", freeze.get("confirmation_run_id") == args.confirmation_run_id)
    check("freeze:single_model", freeze.get("final_model_count") == 1)
    check("final_test:freeze_parent", final.get("freeze_id") == args.freeze_id)
    check("final_test:frozen_model", final.get("selected_config_id") == freeze.get("selected_config_id"))

    if final:
        final_predictions = pd.read_parquet(runs_root / args.final_run_id / "predictions.parquet", columns=["decision_date"])
        dates = pd.to_datetime(final_predictions["decision_date"])
        check("final_test:start_2025", dates.min() >= pd.Timestamp("2025-01-01"))
        check("final_test:end_2025", dates.max() <= pd.Timestamp("2025-12-31"))
        check("final_test:has_predictions", len(dates) > 0)

    failed = [row for row in checks if not row["passed"]]
    report = {"status": "pass" if not failed else "fail", "checks_passed": len(checks) - len(failed),
              "checks_failed": len(failed), "checks": checks}
    print(json.dumps(report, indent=2))
    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
