#!/usr/bin/env python3
"""Relate ex-post Epoch capability scores to U.S. services and Nifty IT event returns."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import yaml
from scipy import stats

from quantfin.cross_market.common import load_research_config, resolve_dataset, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


PRIMARY_BENCHMARKS = [
    "SWE-Bench verified", "Aider polyglot", "GPQA diamond", "MATH level 5", "MMLU"
]


def _resolve_snapshot(root: Path, snapshot_id: str | None) -> Path:
    if snapshot_id:
        path = root / snapshot_id
        if not (path / "manifest.json").is_file():
            raise FileNotFoundError(path / "manifest.json")
        return path
    candidates = [path for path in root.glob("epoch_benchmarks_*") if (path / "manifest.json").is_file()]
    if not candidates:
        raise FileNotFoundError(f"No ingested Epoch benchmark snapshots under {root}")
    return max(candidates, key=lambda path: (path / "manifest.json").stat().st_mtime_ns)


def _spearman(frame: pd.DataFrame, x: str, y: str) -> dict[str, float | int]:
    valid = frame[[x, y]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(valid) < 5 or valid[x].nunique() < 2 or valid[y].nunique() < 2:
        return {"n": len(valid), "rho": float("nan"), "pvalue": float("nan")}
    value = stats.spearmanr(valid[x], valid[y])
    return {"n": len(valid), "rho": float(value.statistic), "pvalue": float(value.pvalue)}


def _time_controlled(frame: pd.DataFrame, outcome: str) -> dict[str, float | int]:
    valid = frame[["eci", "release_date", outcome]].dropna().copy()
    if len(valid) < 8:
        return {"n": len(valid), "coefficient": float("nan"), "t_statistic": float("nan"), "pvalue": float("nan")}
    valid["calendar_year"] = valid["release_date"].dt.year + (valid["release_date"].dt.dayofyear - 1) / 365.25
    design = sm.add_constant(valid[["eci", "calendar_year"]])
    fit = sm.OLS(valid[outcome], design).fit(cov_type="HC3")
    return {
        "n": int(fit.nobs), "coefficient": float(fit.params["eci"]),
        "t_statistic": float(fit.tvalues["eci"]), "pvalue": float(fit.pvalues["eci"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_ai_capability_research.yaml")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--epoch-snapshot-id")
    parser.add_argument("--mapping", default="configs/frontier_ai_epoch_model_mapping.yaml")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()

    config = load_research_config(args.config)
    dataset = resolve_dataset(config, args.dataset_id)
    epoch = _resolve_snapshot(root_path("data/raw/cross_market/epoch_benchmarks"), args.epoch_snapshot_id)
    mapping_path = root_path(args.mapping)
    mapping_config = yaml.safe_load(mapping_path.read_text(encoding="utf-8"))
    content_hash = stable_object_hash({
        "dataset_manifest": sha256_file(dataset / "manifest.json"),
        "epoch_manifest": sha256_file(epoch / "manifest.json"),
        "mapping": sha256_file(mapping_path),
        "script": sha256_file(Path(__file__)),
    })[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    analysis_id = f"epoch_capability_analysis_{stamp}_{content_hash}"
    output = root_path(config["outputs"]["analysis_root"]) / analysis_id
    plan = {
        "action": "analyze_epoch_capability_market_effects", "analysis_id": analysis_id,
        "content_hash": content_hash, "dataset_id": dataset.name,
        "epoch_snapshot_id": epoch.name, "directory": str(output),
        "classification": "ex_post_not_tradable",
    }
    if args.plan_only:
        print(json.dumps(plan, indent=2))
        return
    output.mkdir(parents=True, exist_ok=False)
    plots = output / "plots"
    plots.mkdir()

    panel = pd.read_parquet(dataset / "panel.parquet")
    events = pd.read_csv(dataset / "capability_event_mapping.csv")
    events["release_date"] = pd.to_datetime(events["release_date"])
    events["tradable_date"] = pd.to_datetime(events["tradable_date"])
    events["post_us_reaction_date"] = pd.to_datetime(events["post_us_reaction_date"])
    eci = pd.read_csv(epoch / "epoch_capabilities_index/eci_scores.csv")
    processed = pd.read_csv(epoch / "epoch_capabilities_index/processed_data_for_eci.csv")
    exact = {key: value["epoch_display_name"] for key, value in mapping_config["mappings"].items()}
    events["epoch_display_name"] = events["event_id"].map(exact)
    events = events.merge(
        eci[["Display name", "eci", "eci_ci_low", "eci_ci_high", "date"]].rename(
            columns={"Display name": "epoch_display_name", "date": "epoch_model_date"}
        ), on="epoch_display_name", how="left", validate="many_to_one"
    )

    target = panel.pivot(index="decision_date", columns="asset", values="target_oc_return")
    daily = panel.drop_duplicates("decision_date").set_index("decision_date")
    service_cols = [column for column in panel if column.startswith("us_it_services__") and column.endswith("__ret_lag_1")]
    us_services = daily[service_cols].mean(axis=1)
    response_rows = []
    for row in progress(events.itertuples(index=False), description="Joining capability event responses", total=len(events), unit="event"):
        direct = pd.Timestamp(row.tradable_date) if pd.notna(row.tradable_date) else pd.NaT
        post = pd.Timestamp(row.post_us_reaction_date) if pd.notna(row.post_us_reaction_date) else pd.NaT
        record = row._asdict()
        record["direct_nifty_it_return"] = float(target.loc[direct].mean()) if direct in target.index else np.nan
        record["post_us_services_return"] = float(us_services.get(post, np.nan)) if pd.notna(post) else np.nan
        record["post_us_nifty_it_return"] = float(target.loc[post].mean()) if post in target.index else np.nan
        for asset in target.columns:
            record[f"direct__{asset}"] = float(target.at[direct, asset]) if direct in target.index else np.nan
            record[f"post_us__{asset}"] = float(target.at[post, asset]) if post in target.index else np.nan
        response_rows.append(record)
    event_table = pd.DataFrame(response_rows)
    event_table.to_csv(output / "epoch_event_capability_returns.csv", index=False)

    benchmark_long = processed.loc[processed["Model"].isin(event_table["epoch_display_name"].dropna())].copy()
    benchmark_long = benchmark_long.merge(
        event_table[["event_id", "epoch_display_name"]], left_on="Model", right_on="epoch_display_name", how="inner"
    )
    benchmark_long.to_csv(output / "mapped_epoch_benchmark_scores_long.csv", index=False)
    primary = benchmark_long.loc[benchmark_long["benchmark"].isin(PRIMARY_BENCHMARKS)].copy()
    primary.to_csv(output / "mapped_primary_benchmark_scores_long.csv", index=False)

    outcomes = ["direct_nifty_it_return", "post_us_services_return", "post_us_nifty_it_return"]
    result_rows = []
    for outcome in outcomes:
        result_rows.append({"metric": "eci", "outcome": outcome, **_spearman(event_table, "eci", outcome),
                            **{f"time_controlled_{k}": v for k, v in _time_controlled(event_table, outcome).items()}})
    for benchmark, group in primary.groupby("benchmark"):
        scores = group.groupby("event_id", as_index=False)["performance"].mean()
        joined = event_table.merge(scores, on="event_id", how="left")
        for outcome in outcomes:
            result_rows.append({"metric": benchmark, "outcome": outcome, **_spearman(joined, "performance", outcome)})
    results = pd.DataFrame(result_rows)
    results.to_csv(output / "capability_market_statistical_tests.csv", index=False)

    heat_rows = []
    mapped = event_table.dropna(subset=["eci"])
    for window in ["direct", "post_us"]:
        for asset in target.columns:
            test = _spearman(mapped, "eci", f"{window}__{asset}")
            heat_rows.append({"window": window, "asset": asset, **test})
    heat = pd.DataFrame(heat_rows)
    heat.to_csv(output / "eci_nifty_it_asset_correlations.csv", index=False)
    matrix = heat.pivot(index="window", columns="asset", values="rho")
    fig, ax = plt.subplots(figsize=(12, 3.8))
    sns.heatmap(matrix, center=0, cmap="vlag", annot=True, fmt=".2f", ax=ax,
                cbar_kws={"label": "Spearman correlation"})
    ax.set(title="Ex-post Epoch capability and Nifty IT event responses", xlabel="Nifty IT constituent", ylabel="Window")
    fig.tight_layout(); fig.savefig(plots / "01_eci_nifty_it_heatmap.png", dpi=220); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.7))
    for ax, outcome in zip(axes, outcomes):
        view = mapped[["eci", outcome, "model_family"]].dropna()
        ax.scatter(view["eci"], view[outcome], color="#003D7C")
        for row in view.itertuples(index=False):
            ax.annotate(str(row.model_family), (row.eci, getattr(row, outcome)), fontsize=6, alpha=.75)
        ax.axhline(0, color="#444", lw=.8)
        ax.set(xlabel="Epoch Capabilities Index (current vintage)", ylabel="Return", title=outcome.replace("_", " ").title())
    fig.tight_layout(); fig.savefig(plots / "02_eci_event_response_scatter.png", dpi=220); plt.close(fig)

    coverage = pd.DataFrame({
        "measure": ["Frontier events", "Mapped ECI events", "Events with primary benchmark observations"],
        "count": [len(event_table), int(event_table["eci"].notna().sum()), int(primary["event_id"].nunique())],
    })
    coverage.to_csv(output / "benchmark_mapping_coverage.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4.4))
    sns.barplot(data=coverage, x="count", y="measure", color="#2A9D8F", ax=ax)
    ax.set(title="Capability-data mapping coverage", xlabel="Event count", ylabel="")
    fig.tight_layout(); fig.savefig(plots / "03_benchmark_mapping_coverage.png", dpi=220); plt.close(fig)

    summary = {
        "frontier_events": len(event_table), "eci_mapped_events": int(event_table["eci"].notna().sum()),
        "primary_benchmark_mapped_events": int(primary["event_id"].nunique()),
        "classification": "ex_post_not_tradable",
        "guardrails": [
            "Current-vintage Epoch scores are never backfilled into historical prediction features.",
            "Benchmark scores remain benchmark-specific; no uncalibrated arithmetic composite is used.",
            "Small event samples and calendar-time confounding preclude causal claims.",
            "The time-controlled HC3 regression is a sensitivity analysis, not identification.",
        ],
    }
    atomic_json_dump(summary, output / "epoch_capability_summary.json")
    files = [path for path in output.rglob("*") if path.is_file()]
    atomic_json_dump({
        "schema_version": 1, **plan, "status": "complete",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(), "summary": summary,
        "dataset_manifest_sha256": sha256_file(dataset / "manifest.json"),
        "epoch_manifest_sha256": sha256_file(epoch / "manifest.json"),
        "mapping_sha256": sha256_file(mapping_path),
        "files": {str(path.relative_to(output)): sha256_file(path) for path in files},
    }, output / "manifest.json")
    print(json.dumps({**plan, "status": "complete", **summary}, indent=2))


if __name__ == "__main__":
    main()
