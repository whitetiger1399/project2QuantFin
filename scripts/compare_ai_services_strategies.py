#!/usr/bin/env python3
"""Compare predeclared long-only, signed, services, event, and hybrid rules."""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from quantfin.cross_market.common import load_research_config, root_path
from quantfin.cross_market.experiments import _annualized_metrics, _strategy_ledger
from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_ai_services_research.yaml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    run = root_path(config["outputs"]["runs_root"]) / args.run_id
    manifest_path = run / "manifest.json"
    if not manifest_path.is_file(): raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    predictions_path = run / "predictions.parquet"
    variants = [
        "signed_forecast", "cohort_mean_signed", "cross_sectional_residual_signed",
        "always_long_cohort", "always_short_cohort", "services_direction_equal_weight",
        "frontier_event_short_only", "hybrid_ai_services_signed",
    ]
    content_hash = stable_object_hash({"run": sha256_file(manifest_path), "predictions": sha256_file(predictions_path),
                                      "config": config, "variants": variants, "script": sha256_file(Path(__file__))})[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    comparison_id = f"ai_strategy_comparison_{stamp}_{content_hash}"
    output = root_path(config["outputs"]["analysis_root"]) / comparison_id
    plan = {"action": "compare_ai_services_strategies", "comparison_id": comparison_id,
            "content_hash": content_hash, "source_run_id": args.run_id, "directory": str(output)}
    if args.plan_only: print(json.dumps(plan, indent=2)); return
    output.mkdir(parents=True, exist_ok=False)
    predictions = pd.read_parquet(predictions_path)
    selected = predictions.loc[predictions["config_id"].eq(manifest["selected_config_id"])].copy()
    ledgers = []; rows = []
    for name in progress(variants, description="Comparing trading strategies", unit="strategy"):
        trial = copy.deepcopy(config); trial["strategy"]["primary"]["name"] = name
        ledger = _strategy_ledger(selected, trial); ledger["strategy"] = name; ledgers.append(ledger)
        metrics = _annualized_metrics(ledger["net_return"], int(config["validation"]["annualization_sessions"]))
        rows.append({"strategy": name, **metrics, "mean_turnover": float(ledger["turnover"].mean()),
                     "active_sessions": int(ledger["gross_exposure"].gt(0).sum()),
                     "short_sessions": int(ledger["short_exposure"].gt(0).sum())})
    ledger_frame = pd.concat(ledgers, ignore_index=True); summary = pd.DataFrame(rows).sort_values("sharpe", ascending=False)
    atomic_parquet_dump(ledger_frame, output / "strategy_ledgers.parquet"); summary.to_csv(output / "strategy_summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(11, 6))
    for name, group in ledger_frame.groupby("strategy"):
        group = group.sort_values("decision_date"); ax.plot(group["decision_date"], (1 + group["net_return"]).cumprod(), label=name)
    ax.axhline(1, color="black", lw=.7); ax.set_ylabel("Growth of one, net of costs"); ax.set_title("Predeclared intraday strategy comparison")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(output / "strategy_equity_curves.png", dpi=220); plt.close(fig)
    files = [p for p in output.iterdir() if p.is_file()]
    atomic_json_dump({"schema_version": 1, **plan, "status": "complete", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                      "selected_config_id": manifest["selected_config_id"],
                      "files": {p.name: sha256_file(p) for p in files}}, output / "manifest.json")
    print(json.dumps({**plan, "status": "complete"}, indent=2))


if __name__ == "__main__":
    main()
