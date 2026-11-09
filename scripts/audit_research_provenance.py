"""Verify canonical and retrospective chains declared in a report-input manifest."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.research_extension import read_yaml


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def check(condition: bool, label: str, rows: list[dict[str, str]]) -> None:
    rows.append({"check": label, "status": "pass" if condition else "fail"})
    if not condition:
        raise AssertionError(label)


def run_manifest(run_id: str) -> tuple[Path, dict[str, Any]]:
    directory = ROOT / "artifacts" / "runs" / run_id
    return directory, load_json(directory / "run_manifest.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="configs/report_inputs_2026-10-21.yaml")
    parser.add_argument("--output-root", default="artifacts/research/provenance_audits")
    args = parser.parse_args()

    manifest_path = (ROOT / args.manifest).resolve()
    spec = read_yaml(manifest_path)
    checks: list[dict[str, str]] = []
    events: list[dict[str, Any]] = []
    feature_id = spec["feature_dataset_id"]

    loaded: dict[str, tuple[Path, dict[str, Any]]] = {}
    for chain_name in ["canonical", "retrospective_comparison"]:
        chain = spec[chain_name]
        for stage in ["screening", "confirmation"]:
            key = f"{chain_name}.{stage}"
            directory, manifest = run_manifest(chain[f"{stage}_run_id"])
            loaded[key] = (directory, manifest)
            check(manifest.get("status") == "complete", f"{key} is complete", checks)
            check(manifest["inputs"]["stage"] == stage, f"{key} declares stage {stage}", checks)
            check(manifest["inputs"]["feature_dataset_id"] == feature_id, f"{key} feature lineage matches", checks)
            check((directory / "predictions.parquet").is_file(), f"{key} predictions exist", checks)
            check((directory / "config_metrics.csv").is_file(), f"{key} metrics exist", checks)
            events.append({
                "chain": chain_name,
                "role": chain["role"],
                "event": f"{stage}_complete",
                "run_id": manifest["run_id"],
                "timestamp_utc": manifest.get("completed_at_utc"),
                "artifact_sha256": sha256_file(directory / "run_manifest.json"),
            })

    canonical = spec["canonical"]
    confirmation_dir, confirmation_manifest = loaded["canonical.confirmation"]
    selection_path = confirmation_dir / "selection.json"
    selection = load_json(selection_path)
    freeze_path = ROOT / "artifacts" / "freezes" / f"{canonical['freeze_id']}.json"
    freeze = load_json(freeze_path)
    final_dir, final_manifest = run_manifest(canonical["final_run_id"])
    check(freeze["selection_sha256"] == sha256_file(selection_path), "canonical freeze binds canonical confirmation selection", checks)
    check(final_manifest["inputs"]["freeze_id"] == freeze["freeze_id"], "canonical final run binds declared freeze", checks)
    check(final_manifest["inputs"]["stage"] == "final_test", "canonical final run declares final_test", checks)
    check(final_manifest["inputs"]["feature_dataset_id"] == feature_id, "canonical final feature lineage matches", checks)
    events.extend([
        {"chain": "canonical", "role": canonical["role"], "event": "freeze_created", "run_id": freeze["freeze_id"], "timestamp_utc": freeze.get("created_at_utc"), "artifact_sha256": sha256_file(freeze_path)},
        {"chain": "canonical", "role": canonical["role"], "event": "final_complete", "run_id": final_manifest["run_id"], "timestamp_utc": final_manifest.get("completed_at_utc"), "artifact_sha256": sha256_file(final_dir / "run_manifest.json")},
    ])

    retrospective_screen = loaded["retrospective_comparison.screening"][1]
    canonical_final_time = pd.Timestamp(final_manifest["completed_at_utc"])
    retrospective_start = pd.Timestamp(retrospective_screen["created_at_utc"])
    check(retrospective_start > canonical_final_time, "retrospective comparison began after canonical final completion", checks)
    check(bool(spec["policy"]["final_test_is_reused"]), "manifest discloses reused final period", checks)
    check(not bool(spec["policy"]["allow_new_final_test_claim"]), "manifest prevents a new untouched-final claim", checks)

    events_frame = pd.DataFrame(events).sort_values("timestamp_utc")
    identity = {"manifest_sha256": sha256_file(manifest_path), "events": events_frame.to_dict("records")}
    audit_id = "provenance_" + stable_object_hash(identity)[:16]
    output = ROOT / args.output_root / audit_id
    output.mkdir(parents=True, exist_ok=True)
    events_frame.to_csv(output / "chronology.csv", index=False)
    pd.DataFrame(checks).to_csv(output / "checks.csv", index=False)
    result = {
        "schema_version": 1,
        "audit_id": audit_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "checks_passed": len(checks),
        "report_input_manifest": str(manifest_path.relative_to(ROOT)),
        "report_input_manifest_sha256": sha256_file(manifest_path),
        "canonical_final_run": final_manifest["run_id"],
        "retrospective_comparison_started_after_final": True,
        "interpretation": "Canonical results and later retrospective comparisons are separate evidence chains.",
    }
    atomic_json_dump(result, output / "audit.json")
    print(json.dumps({**result, "output_directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()

