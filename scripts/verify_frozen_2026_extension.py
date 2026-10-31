#!/usr/bin/env python3
"""Verify dates, leakage guards, frozen lineage, and hashes for the 2026 extension."""

from __future__ import annotations

import argparse
import json

import pandas as pd

from quantfin.cross_market.common import load_research_config, root_path
from quantfin.io import sha256_file
from quantfin.progress import progress


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_ai_capability_2026_extension.yaml")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    config = load_research_config(args.config)
    run = root_path(config["outputs"]["runs_root"]) / args.run_id
    manifest_path = run / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(condition), "detail": detail})

    check("status_complete", manifest.get("status") == "complete")
    check("stage_forward_extension", manifest.get("stage") == "forward_extension_2026")
    check("single_selected_refit", manifest.get("refit_count_selected_model") == 1)
    check("no_model_reselection", manifest.get("model_reselection_performed") is False)
    check("no_hyperparameter_tuning", manifest.get("hyperparameter_tuning_performed") is False)
    check("training_ends_before_2026", pd.Timestamp(manifest["training_end"]) < pd.Timestamp("2026-01-01"), manifest["training_end"])
    check("evaluation_start", manifest.get("evaluation_start") == "2026-01-01")
    check("evaluation_end", manifest.get("evaluation_end") == "2026-09-30")
    for relative, expected in progress(manifest.get("files", {}).items(), description="Verifying 2026 extension", unit="file"):
        path = run / relative
        check(f"hash:{relative}", path.is_file() and sha256_file(path) == expected)

    predictions = pd.read_parquet(run / "predictions.parquet")
    predictions["decision_date"] = pd.to_datetime(predictions["decision_date"])
    check("prediction_start", predictions["decision_date"].min() >= pd.Timestamp("2026-01-01"))
    check("prediction_end", predictions["decision_date"].max() <= pd.Timestamp("2026-09-30"))
    check("selected_model_present", manifest["selected_config_id"] in set(predictions["config_id"]))
    check("prediction_key_unique", not predictions.duplicated(["config_id", "decision_date", "asset"]).any())
    selected = predictions.loc[predictions["config_id"].eq(manifest["selected_config_id"])]
    check("selected_prediction_complete", selected["prediction"].notna().all())
    check("selected_target_complete", selected["target_oc_return"].notna().all())

    failed = [row for row in checks if not row["passed"]]
    report = {"status": "pass" if not failed else "fail", "checks_passed": len(checks) - len(failed),
              "checks_failed": len(failed), "checks": checks}
    print(json.dumps(report, indent=2))
    if failed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
