"""Verify all evidence chains and optional completed research-extension runs."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from quantfin.io import atomic_json_dump, sha256_file
from quantfin.research_extension import read_yaml


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="configs/report_inputs_2026-10-21.yaml")
    parser.add_argument("--complexity-run-dir", action="append", default=[])
    parser.add_argument("--learning-run-dir", action="append", default=[])
    parser.add_argument("--output", default="artifacts/research/verification_2026-10-21.json")
    args = parser.parse_args()
    spec = read_yaml(ROOT / args.manifest)
    checks: list[dict[str, str]] = []

    def check(value: bool, label: str) -> None:
        checks.append({"check": label, "status": "pass" if value else "fail"})
        if not value:
            raise AssertionError(label)

    run_ids = []
    for chain in ["canonical", "retrospective_comparison"]:
        for stage in ["screening", "confirmation"]:
            run_ids.append((chain, stage, spec[chain][f"{stage}_run_id"]))
    run_ids.append(("canonical", "final_test", spec["canonical"]["final_run_id"]))
    for chain, stage, run_id in run_ids:
        directory = ROOT / "artifacts/runs" / run_id
        manifest_path = directory / "run_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        check(manifest.get("status") == "complete", f"{chain}.{stage} is complete")
        check(manifest["inputs"]["stage"] == stage, f"{chain}.{stage} stage matches")
        check(manifest["inputs"]["feature_dataset_id"] == spec["feature_dataset_id"], f"{chain}.{stage} feature lineage matches")
        predictions = pd.read_parquet(directory / "predictions.parquet")
        check(not predictions.duplicated(["config_id", "signal_session"]).any(), f"{chain}.{stage} predictions unique")
        check(predictions["prediction"].notna().all(), f"{chain}.{stage} predictions complete")
        check((pd.to_datetime(predictions["train_last_label_available"]) <= pd.to_datetime(predictions["refit_origin"])).all(), f"{chain}.{stage} training labels available at fit")
        if "predictions_sha256" in manifest.get("outputs", {}):
            check(sha256_file(directory / "predictions.parquet") == manifest["outputs"]["predictions_sha256"], f"{chain}.{stage} prediction hash matches")

    for kind, directories in [("complexity", args.complexity_run_dir), ("learning", args.learning_run_dir)]:
        for name in directories:
            directory = (ROOT / name).resolve()
            manifest = json.loads((directory / "run_manifest.json").read_text(encoding="utf-8"))
            check(manifest.get("status") == "complete", f"{kind} run {directory.name} complete")
            predictions = pd.read_parquet(directory / "predictions.parquet")
            check(not predictions.duplicated(["config_id", "signal_session"]).any(), f"{kind} {directory.name} predictions unique")
            check((pd.to_datetime(predictions["train_last_label_available"]) <= pd.to_datetime(predictions["refit_origin"])).all(), f"{kind} {directory.name} leakage boundary passes")

    result = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "checks_passed": len(checks),
        "checks": checks,
        "scope": {
            "report_input_manifest": args.manifest,
            "complexity_runs": args.complexity_run_dir,
            "learning_runs": args.learning_run_dir,
        },
    }
    destination = (ROOT / args.output).resolve()
    atomic_json_dump(result, destination)
    print(json.dumps({"status": "pass", "checks_passed": len(checks), "output": str(destination)}, indent=2))


if __name__ == "__main__":
    main()

