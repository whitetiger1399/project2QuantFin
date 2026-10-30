#!/usr/bin/env python3
"""Report dataset, analysis, experiment, or freeze status by immutable ID."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from quantfin.cross_market.common import load_research_config, root_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_research.yaml")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    config = load_research_config(args.config)
    candidates = [
        root_path(config["outputs"]["processed_root"]) / args.run_id,
        root_path(config["outputs"]["analysis_root"]) / args.run_id,
        root_path(config["outputs"]["runs_root"]) / args.run_id,
        root_path(config["outputs"]["freezes_root"]) / f"{args.run_id}.json",
    ]
    target = next((path for path in candidates if path.exists()), None)
    if target is None:
        raise FileNotFoundError(f"Unknown cross-market run ID: {args.run_id}")
    if target.is_file():
        print(target.read_text(encoding="utf-8")); return
    state_path = target / "run_state.json"
    manifest_path = target / "manifest.json"
    selected = state_path if state_path.is_file() else manifest_path
    with selected.open("r", encoding="utf-8") as handle:
        state = json.load(handle)
    checkpoint_count = len(list((target / "checkpoints").glob("*/*.json"))) if (target / "checkpoints").exists() else state.get("checkpoint_count", 0)
    state["checkpoint_count_on_disk"] = checkpoint_count
    expected = state.get("expected_checkpoint_count")
    if expected:
        state["percent"] = round(100.0 * checkpoint_count / expected, 2)
    state["directory"] = str(target)
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
