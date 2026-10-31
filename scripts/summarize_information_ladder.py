#!/usr/bin/env python3
"""Summarize controlled feature additions and every daily long/short decision."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from quantfin.cross_market.common import load_research_config, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


LABELS = {
    "F0_own": "Own history",
    "F1_nifty_it_peers": "+ Nifty IT peers",
    "F2_us_services": "+ U.S. IT services",
    "F3_nifty50": "+ Nifty 50",
    "F4_sp500_aggregate": "+ S&P 500 aggregate",
    "F5_sp500_constituents": "+ S&P 500 constituents",
    "F6_ai_events": "+ Frontier-AI events",
    "F7_full_context": "+ Full context",
}


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
    configurations = json.loads((run / "configurations.json").read_text(encoding="utf-8"))
    progression = {row["config_id"]: row for row in configurations if row.get("experiment") == "feature_progression"}
    if not progression: raise ValueError("Run contains no feature_progression configurations")
    content_hash = stable_object_hash({"manifest": sha256_file(manifest_path), "configurations": progression,
                                      "script": sha256_file(Path(__file__))})[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary_id = f"information_ladder_{manifest['stage']}_{stamp}_{content_hash}"
    output = root_path(config["outputs"]["analysis_root"]) / summary_id
    plan = {"action": "summarize_information_ladder", "summary_id": summary_id,
            "content_hash": content_hash, "source_run_id": args.run_id, "stage": manifest["stage"],
            "directory": str(output)}
    if args.plan_only: print(json.dumps(plan, indent=2)); return
    output.mkdir(parents=True, exist_ok=False)
    leaderboard = pd.read_csv(run / "leaderboard.csv")
    ledgers = pd.read_parquet(run / "strategy_ledgers.parquet")
    predictions = pd.read_parquet(run / "predictions.parquet")
    diagnostics = pd.read_csv(run / "refit_diagnostics.csv")
    order = config["models"]["profiles"]["deep"]["feature_sets"]
    rows = []; daily_frames = []; stock_decision_frames = []
    one_way_cost = (
        float(config["strategy"]["primary"]["one_way_cost_bps"])
        + float(config["strategy"]["primary"]["slippage_bps"])
    ) / 10_000.0
    for config_id, specification in progress(progression.items(), description="Summarizing information ladder", unit="rung"):
        feature_set = specification["feature_set"]
        ledger = ledgers.loc[ledgers["config_id"].eq(config_id)].sort_values("decision_date").copy()
        if ledger.empty: continue
        ledger["feature_set"] = feature_set
        ledger["information_set"] = LABELS.get(feature_set, feature_set)
        ledger["position"] = np.select(
            [ledger["long_exposure"].gt(0) & ledger["short_exposure"].eq(0),
             ledger["short_exposure"].gt(0) & ledger["long_exposure"].eq(0),
             ledger["short_exposure"].gt(0) & ledger["long_exposure"].gt(0)],
            ["LONG", "SHORT", "LONG_SHORT"], default="FLAT",
        )
        ledger["cumulative_net_wealth"] = (1 + ledger["net_return"]).cumprod()
        daily_frames.append(ledger)
        stock = predictions.loc[predictions["config_id"].eq(config_id)].copy()
        ledger_by_date = ledger.set_index("decision_date")
        stock["position"] = "FLAT"; stock["portfolio_weight"] = 0.0
        for date, indices in stock.groupby("decision_date").groups.items():
            row = ledger_by_date.loc[date]
            long_value = row["long_holdings"]
            short_value = row["short_holdings"]
            long_assets = set(long_value.split("|")) if isinstance(long_value, str) and long_value else set()
            short_assets = set(short_value.split("|")) if isinstance(short_value, str) and short_value else set()
            long_weight = float(row["long_exposure"]) / len(long_assets) if long_assets else 0.0
            short_weight = float(row["short_exposure"]) / len(short_assets) if short_assets else 0.0
            for index in indices:
                asset = stock.at[index, "asset"]
                if asset in long_assets:
                    stock.at[index, "position"] = "LONG"; stock.at[index, "portfolio_weight"] = long_weight
                elif asset in short_assets:
                    stock.at[index, "position"] = "SHORT"; stock.at[index, "portfolio_weight"] = short_weight
        stock["position_sign"] = stock["position"].map({"LONG": 1.0, "SHORT": -1.0, "FLAT": 0.0})
        stock["expected_gross_contribution"] = stock["prediction"] * stock["position_sign"] * stock["portfolio_weight"]
        stock["realized_gross_contribution"] = stock["target_oc_return"] * stock["position_sign"] * stock["portfolio_weight"]
        stock["allocated_round_trip_cost"] = 2.0 * stock["portfolio_weight"] * one_way_cost
        stock["expected_net_contribution"] = stock["expected_gross_contribution"] - stock["allocated_round_trip_cost"]
        stock["realized_net_contribution"] = stock["realized_gross_contribution"] - stock["allocated_round_trip_cost"]
        stock["feature_set"] = feature_set; stock["information_set"] = LABELS.get(feature_set, feature_set)
        stock_decision_frames.append(stock)
        active = ledger.loc[ledger["gross_exposure"].gt(0), "net_return"]
        board = leaderboard.loc[leaderboard["config_id"].eq(config_id)].iloc[0].to_dict()
        diag = diagnostics.loc[diagnostics["config_id"].eq(config_id)]
        rows.append({
            "ladder_order": order.index(feature_set), "feature_set": feature_set,
            "information_set": LABELS.get(feature_set, feature_set), "config_id": config_id,
            "mean_input_features": float(diag["input_features"].mean()),
            "mean_predicted_daily_net_return": float(ledger["expected_net_return"].mean()),
            "realized_mean_daily_net_return": float(ledger["net_return"].mean()),
            "realized_mean_active_trade_day_return": float(active.mean()) if len(active) else np.nan,
            "cumulative_net_return": float((1 + ledger["net_return"]).prod() - 1),
            "net_annual_return": board["net_annual_return"], "net_sharpe": board["net_sharpe"],
            "net_sortino": board["net_sortino"], "maximum_drawdown": board["maximum_drawdown"],
            "oos_r2_asset_mean": board["oos_r2_asset_mean"], "spearman_ic": board["spearman_ic"],
            "mean_daily_turnover": board["mean_daily_turnover"],
            "long_days": int(ledger["position"].eq("LONG").sum()),
            "short_days": int(ledger["position"].eq("SHORT").sum()),
            "flat_days": int(ledger["position"].eq("FLAT").sum()),
            "positive_net_days": int(ledger["net_return"].gt(0).sum()),
        })
    summary = pd.DataFrame(rows).sort_values("ladder_order")
    daily = pd.concat(daily_frames, ignore_index=True)
    stock_decisions = pd.concat(stock_decision_frames, ignore_index=True)
    summary.to_csv(output / "information_ladder_summary.csv", index=False)
    daily.to_csv(output / "daily_long_short_decisions.csv", index=False)
    stock_decisions.to_csv(output / "daily_stock_decisions.csv", index=False)

    fig, axes = plt.subplots(3, 1, figsize=(11, 11), sharex=True)
    x = np.arange(len(summary)); labels = summary["information_set"]
    axes[0].plot(x, summary["net_annual_return"], marker="o", color="#005f73")
    axes[0].axhline(0, color="black", lw=.7); axes[0].set_ylabel("Net annual return")
    axes[1].plot(x, summary["net_sharpe"], marker="o", color="#ee9b00")
    axes[1].axhline(0, color="black", lw=.7); axes[1].set_ylabel("Net Sharpe ratio")
    axes[2].plot(x, summary["mean_input_features"], marker="o", color="#9b2226")
    axes[2].set_ylabel("Mean usable features"); axes[2].set_xticks(x, labels, rotation=25, ha="right")
    fig.suptitle(f"Controlled information-set progression — {manifest['stage']}")
    fig.tight_layout(); fig.savefig(output / "information_ladder_performance.png", dpi=220); plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6))
    for feature_set, group in daily.groupby("feature_set"):
        group = group.sort_values("decision_date")
        ax.plot(pd.to_datetime(group["decision_date"]), group["cumulative_net_wealth"],
                label=LABELS.get(feature_set, feature_set), lw=1.2)
    ax.axhline(1, color="black", lw=.7); ax.set_ylabel("Growth of one, net of costs")
    ax.set_title(f"Signed strategy wealth by information set — {manifest['stage']}")
    ax.legend(fontsize=8, ncol=2); fig.tight_layout(); fig.savefig(output / "information_ladder_wealth.png", dpi=220); plt.close(fig)
    files = [path for path in output.iterdir() if path.is_file()]
    atomic_json_dump({"schema_version": 1, **plan, "status": "complete",
                      "created_at_utc": datetime.now(timezone.utc).isoformat(),
                      "rungs": len(summary), "daily_decision_rows": len(daily),
                      "daily_stock_decision_rows": len(stock_decisions),
                      "files": {path.name: sha256_file(path) for path in files}}, output / "manifest.json")
    print(json.dumps({**plan, "status": "complete", "rungs": len(summary)}, indent=2))


if __name__ == "__main__":
    main()
