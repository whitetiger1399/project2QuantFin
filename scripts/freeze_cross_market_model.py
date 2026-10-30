#!/usr/bin/env python3
"""Freeze exactly one confirmed model before opening the final-test period."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import pandas as pd

from quantfin.cross_market.common import load_research_config, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_research.yaml")
    parser.add_argument("--confirmation-run-id", required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    run = root_path(config["outputs"]["runs_root"]) / args.confirmation_run_id
    with (run / "manifest.json").open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("stage") != "confirmation" or manifest.get("status") != "complete":
        raise ValueError("Only a completed confirmation run can be frozen")
    leaderboard = pd.read_csv(run / "leaderboard.csv")
    eligible = leaderboard.loc[leaderboard["prediction_coverage"] >= float(config["selection"]["minimum_prediction_coverage"])]
    if eligible.empty:
        raise ValueError("No confirmation candidate meets the predeclared prediction-coverage threshold")
    selected = eligible.iloc[0]
    identity_payload = {
        "confirmation_content_hash": manifest["content_hash"],
        "selected_config_id": selected["config_id"],
        "selection_metric": config["selection"]["primary_metric"],
        "selection_values": selected.to_dict(),
        "final_model_count": 1,
    }
    freeze_hash = stable_object_hash(identity_payload)[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    freeze_id = f"cm_freeze_{stamp}_{freeze_hash}"
    destination = root_path(config["outputs"]["freezes_root"]) / f"{freeze_id}.json"
    record = {
        "schema_version": 1, "freeze_id": freeze_id, "content_hash": freeze_hash,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "confirmation_run_id": args.confirmation_run_id,
        "confirmation_manifest_sha256": sha256_file(run / "manifest.json"),
        **identity_payload,
    }
    if args.plan_only:
        print(json.dumps({**record, "destination": str(destination)}, indent=2)); return
    atomic_json_dump(record, destination)
    print(json.dumps({"freeze_id": freeze_id, "content_hash": freeze_hash, "selected_config_id": selected["config_id"], "path": str(destination)}, indent=2))


if __name__ == "__main__":
    main()
