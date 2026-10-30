#!/usr/bin/env python3
"""Create hashed, report-ready feature progression, model, complexity, and explainability tables."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import pandas as pd

from quantfin.cross_market.common import environment_record, load_research_config, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_research.yaml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    run = root_path(config["outputs"]["runs_root"]) / args.run_id
    if not (run / "manifest.json").is_file():
        raise FileNotFoundError(run / "manifest.json")
    with (run / "manifest.json").open("r", encoding="utf-8") as handle:
        parent_manifest = json.load(handle)
    content_hash = stable_object_hash({
        "action": "summarize_cross_market_run", "parent_content_hash": parent_manifest["content_hash"],
        "leaderboard": sha256_file(run / "leaderboard.csv"),
    })[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary_id = f"model_summary_{stamp}_{content_hash}"
    output = root_path(config["outputs"]["analysis_root"]) / summary_id
    plan = {"action": "summarize_cross_market_run", "summary_id": summary_id, "content_hash": content_hash, "parent_run_id": args.run_id, "directory": str(output)}
    if args.plan_only:
        print(json.dumps(plan, indent=2)); return
    print(json.dumps({**plan, "status": "starting"}, indent=2), flush=True)
    output.mkdir(parents=True, exist_ok=False)
    leaderboard = pd.read_csv(run / "leaderboard.csv")
    configurations = {row["config_id"]: row for row in json.load(open(run / "configurations.json", encoding="utf-8"))}
    leaderboard["experiment"] = leaderboard["config_id"].map(lambda value: configurations[value]["experiment"])
    leaderboard["parameters"] = leaderboard["config_id"].map(lambda value: json.dumps(configurations[value]["parameters"], sort_keys=True))
    progression = leaderboard.loc[leaderboard["experiment"].eq("feature_progression")].sort_values("rank")
    progression.groupby("feature_set", sort=False).head(1).to_csv(output / "best_feature_progression.csv", index=False)
    leaderboard.sort_values("rank").groupby("family", sort=False).head(1).to_csv(output / "best_by_model_family.csv", index=False)
    leaderboard.loc[leaderboard["experiment"].eq("complexity")].sort_values("rank").to_csv(output / "complexity_results.csv", index=False)
    importance_path = run / "feature_importance_by_refit.csv"
    if importance_path.is_file():
        importance = pd.read_csv(importance_path)
        importance.groupby(["config_id", "measure", "feature"])["importance"].agg(
            mean="mean", std="std", count="count"
        ).reset_index().sort_values(
            "mean", key=lambda values: values.abs(), ascending=False
        ).to_csv(output / "aggregated_feature_importance.csv", index=False)
    record = {
        "schema_version": 1, **plan, "status": "complete", "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "parent_manifest_sha256": sha256_file(run / "manifest.json"), "environment": environment_record(),
    }
    atomic_json_dump(record, output / "manifest.json")
    print(json.dumps({"summary_id": summary_id, "content_hash": content_hash, "status": "complete", "directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()
