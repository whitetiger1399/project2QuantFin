#!/usr/bin/env python3
"""Analyze disclosed frontier-model scale against U.S. services and Nifty IT returns."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from quantfin.cross_market.common import load_research_config, resolve_dataset, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


def _spearman(x: pd.Series, y: pd.Series) -> dict[str, float | int]:
    valid = pd.concat([x, y], axis=1).dropna()
    if len(valid) < 4 or valid.iloc[:, 0].nunique() < 2 or valid.iloc[:, 1].nunique() < 2:
        return {"n": len(valid), "rho": float("nan"), "pvalue": float("nan")}
    result = stats.spearmanr(valid.iloc[:, 0], valid.iloc[:, 1])
    return {"n": len(valid), "rho": float(result.statistic), "pvalue": float(result.pvalue)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_ai_capability_research.yaml")
    parser.add_argument("--dataset-id")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    dataset = resolve_dataset(config, args.dataset_id)
    content_hash = stable_object_hash({"dataset": sha256_file(dataset / "manifest.json"),
                                      "script": sha256_file(Path(__file__))})[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    analysis_id = f"ai_capability_analysis_{stamp}_{content_hash}"
    output = root_path(config["outputs"]["analysis_root"]) / analysis_id
    plan = {"action": "analyze_ai_capability_effects", "analysis_id": analysis_id,
            "content_hash": content_hash, "dataset_id": dataset.name, "directory": str(output)}
    if args.plan_only: print(json.dumps(plan, indent=2)); return
    output.mkdir(parents=True, exist_ok=False); plots = output / "plots"; plots.mkdir()
    panel = pd.read_parquet(dataset / "panel.parquet")
    mapping = pd.read_csv(dataset / "capability_event_mapping.csv")
    mapping["tradable_date"] = pd.to_datetime(mapping["tradable_date"])
    mapping["post_us_reaction_date"] = pd.to_datetime(mapping["post_us_reaction_date"])
    disclosed = mapping.loc[mapping["parameter_disclosed"].astype(str).str.lower().isin({"true", "1", "yes"})].copy()
    targets = panel.pivot(index="decision_date", columns="asset", values="target_oc_return")
    daily = panel.drop_duplicates("decision_date").set_index("decision_date")
    service_columns = [column for column in panel if column.startswith("us_it_services__") and column.endswith("__ret_lag_1")]
    daily_services = daily[service_columns].mean(axis=1)
    rows = []
    for row in progress(disclosed.itertuples(index=False), description="Measuring capability event returns", total=len(disclosed), unit="event"):
        direct = pd.Timestamp(row.tradable_date); post = pd.Timestamp(row.post_us_reaction_date)
        record = {"event_id": row.event_id, "provider": row.provider, "model_family": row.model_family,
                  "release_date": row.release_date, "tradable_date": direct,
                  "post_us_reaction_date": post, "total_parameters_b": row.total_parameters_b,
                  "active_parameters_b": row.active_parameters_b,
                  "log1p_total_parameters_b": np.log1p(row.total_parameters_b)}
        if direct in targets.index:
            for asset, value in targets.loc[direct].items(): record[f"direct__{asset}"] = value
            record["direct__cohort"] = float(targets.loc[direct].mean())
        if post in targets.index:
            for asset, value in targets.loc[post].items(): record[f"post_us__{asset}"] = value
            record["post_us__cohort"] = float(targets.loc[post].mean())
            record["post_us__us_services_mean"] = float(daily_services.get(post, np.nan))
        rows.append(record)
    event_returns = pd.DataFrame(rows).sort_values("release_date")
    event_returns.to_csv(output / "disclosed_parameter_event_returns.csv", index=False)
    correlations = []
    x = event_returns["log1p_total_parameters_b"]
    for column in [c for c in event_returns if c.startswith("direct__") or c.startswith("post_us__")]:
        correlations.append({"outcome": column, **_spearman(x, event_returns[column])})
    correlation_table = pd.DataFrame(correlations)
    correlation_table.to_csv(output / "parameter_return_spearman.csv", index=False)

    asset_columns = list(targets.columns)
    heat = pd.DataFrame(index=["Direct tradable NSE session", "After observable U.S. reaction"], columns=asset_columns, dtype=float)
    for asset in asset_columns:
        heat.loc["Direct tradable NSE session", asset] = _spearman(x, event_returns[f"direct__{asset}"])["rho"]
        heat.loc["After observable U.S. reaction", asset] = _spearman(x, event_returns[f"post_us__{asset}"])["rho"]
    heat.to_csv(output / "parameter_nifty_it_correlation_heatmap.csv")
    plt.figure(figsize=(12, 3.8)); sns.heatmap(heat, cmap="vlag", center=0, annot=True, fmt=".2f",
                                                   cbar_kws={"label": "Spearman correlation"})
    plt.title("Disclosed frontier-model scale vs. Nifty IT event-window returns")
    plt.xlabel("Nifty IT constituent"); plt.ylabel(""); plt.tight_layout()
    plt.savefig(plots / "parameter_nifty_it_correlation_heatmap.png", dpi=220); plt.close()

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    outcomes = [("direct__cohort", "Direct Nifty IT response"),
                ("post_us__us_services_mean", "U.S. services response"),
                ("post_us__cohort", "Subsequent Nifty IT response")]
    for ax, (column, title) in zip(axes, outcomes):
        ax.scatter(event_returns["total_parameters_b"], event_returns[column], color="#005f73")
        for _, row in event_returns.iterrows():
            ax.annotate(str(row["model_family"]), (row["total_parameters_b"], row[column]), fontsize=6, alpha=.8)
        ax.axhline(0, color="black", lw=.7); ax.set_xscale("log"); ax.set_title(title)
        ax.set_xlabel("Officially disclosed total parameters (B)"); ax.set_ylabel("Return")
    fig.tight_layout(); fig.savefig(plots / "parameter_scale_event_scatter.png", dpi=220); plt.close(fig)

    cohort = correlation_table.set_index("outcome")
    summary = {
        "disclosed_parameter_events": len(event_returns),
        "total_frontier_events": len(mapping),
        "disclosure_fraction": len(event_returns) / len(mapping),
        "direct_nifty_it": cohort.loc["direct__cohort"].to_dict(),
        "post_us_services": cohort.loc["post_us__us_services_mean"].to_dict(),
        "post_us_nifty_it": cohort.loc["post_us__cohort"].to_dict(),
        "guardrails": [
            "Parameter count is not a universal capability metric.",
            "The disclosed subset is small and non-random; correlations are exploratory.",
            "MoE total and active parameters are not interchangeable.",
            "Release-date and model-scale trends may be confounded with calendar time and macro conditions.",
        ],
    }
    atomic_json_dump(summary, output / "capability_effect_summary.json")
    files = [path for path in output.rglob("*") if path.is_file()]
    atomic_json_dump({"schema_version": 1, **plan, "status": "complete",
                      "created_at_utc": datetime.now(timezone.utc).isoformat(), "summary": summary,
                      "files": {str(path.relative_to(output)): sha256_file(path) for path in files}}, output / "manifest.json")
    print(json.dumps({**plan, "status": "complete", **summary}, indent=2))


if __name__ == "__main__":
    main()
