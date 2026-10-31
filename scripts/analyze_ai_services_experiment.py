#!/usr/bin/env python3
"""Create development-only US-services transmission and AI-event evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm

from quantfin.cross_market.common import load_research_config, read_panel_dataset, resolve_dataset, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_ai_services_research.yaml")
    parser.add_argument("--dataset-id")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    dataset = resolve_dataset(config, args.dataset_id)
    content_hash = stable_object_hash({
        "dataset_manifest": sha256_file(dataset / "manifest.json"),
        "config": config,
        "script": sha256_file(Path(__file__)),
    })[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    analysis_id = f"ai_services_analysis_{stamp}_{content_hash}"
    output = root_path(config["outputs"]["analysis_root"]) / analysis_id
    plan = {"action": "analyze_ai_services_experiment", "analysis_id": analysis_id,
            "content_hash": content_hash, "dataset_id": dataset.name, "directory": str(output)}
    if args.plan_only:
        print(json.dumps(plan, indent=2)); return
    output.mkdir(parents=True, exist_ok=False)
    plots = output / "plots"; plots.mkdir()
    panel, _, _ = read_panel_dataset(dataset)
    development_end = pd.Timestamp(config["sample"]["splits"]["confirmation"][1])
    panel = panel.loc[panel["decision_date"].le(development_end)].copy()
    daily = panel.sort_values("asset").groupby("decision_date").first()
    service_columns = [c for c in panel if c.startswith("us_it_services__") and c.endswith("__ret_lag_1")]
    targets = panel.pivot(index="decision_date", columns="asset", values="target_oc_return")
    correlations = pd.DataFrame(index=[c.split("__")[1].upper() for c in service_columns], columns=targets.columns, dtype=float)
    for column in progress(service_columns, description="Correlating US and Indian IT services", unit="asset"):
        label = column.split("__")[1].upper()
        for asset in targets:
            correlations.loc[label, asset] = daily[column].corr(targets[asset], method="spearman")
    correlations.to_csv(output / "us_india_it_services_spearman.csv")
    plt.figure(figsize=(12, 7))
    sns.heatmap(correlations, cmap="vlag", center=0, annot=True, fmt=".2f", linewidths=.4,
                cbar_kws={"label": "Spearman correlation"})
    plt.title("Prior U.S. IT-services return vs. Nifty IT open-to-close return\nDevelopment sample through 2024")
    plt.xlabel("Indian Nifty IT constituent"); plt.ylabel("U.S. IT-services firm")
    plt.tight_layout(); plt.savefig(plots / "us_india_services_heatmap.png", dpi=220); plt.close()

    provider_columns = [
        column for column in daily
        if column.startswith("ai_event__provider_") and column.endswith("_today")
        and not column.endswith("_post_us_reaction_today")
    ]
    provider_effects = pd.DataFrame(columns=targets.columns, dtype=float)
    provider_counts: list[dict[str, object]] = []
    for column in provider_columns:
        provider = column.removeprefix("ai_event__provider_").removesuffix("_today")
        mask = daily[column].fillna(0).gt(0)
        provider_counts.append({"provider": provider, "direct_event_sessions": int(mask.sum())})
        if mask.any():
            provider_effects.loc[provider] = targets.loc[mask].mean() - targets.loc[~mask].mean()
    provider_effects.to_csv(output / "provider_nifty_it_abnormal_returns.csv")
    pd.DataFrame(provider_counts).to_csv(output / "provider_event_counts.csv", index=False)
    if not provider_effects.empty:
        plt.figure(figsize=(12, 6.5))
        sns.heatmap(provider_effects, cmap="vlag", center=0, annot=True, fmt=".3%", linewidths=.4,
                    cbar_kws={"label": "Event minus non-event mean return"})
        plt.title("Frontier-model provider announcements and Nifty IT intraday response\nDevelopment sample; first conservatively tradable NSE session")
        plt.xlabel("Nifty IT constituent"); plt.ylabel("Publishing company")
        plt.tight_layout(); plt.savefig(plots / "provider_nifty_it_event_heatmap.png", dpi=220); plt.close()

    post_provider_columns = [column for column in daily if column.endswith("_post_us_reaction_today")]
    service_labels = [column.split("__")[1].upper() for column in service_columns]
    provider_us_effects = pd.DataFrame(columns=service_labels, dtype=float)
    mediated_india_effects = pd.DataFrame(columns=targets.columns, dtype=float)
    for column in post_provider_columns:
        provider = column.removeprefix("ai_event__provider_").removesuffix("_post_us_reaction_today")
        mask = daily[column].fillna(0).gt(0)
        if not mask.any():
            continue
        provider_us_effects.loc[provider] = [
            daily.loc[mask, service].mean() - daily.loc[~mask, service].mean()
            for service in service_columns
        ]
        mediated_india_effects.loc[provider] = targets.loc[mask].mean() - targets.loc[~mask].mean()
    provider_us_effects.to_csv(output / "provider_us_services_post_release_effects.csv")
    mediated_india_effects.to_csv(output / "provider_nifty_it_post_us_reaction_effects.csv")
    if not provider_us_effects.empty:
        plt.figure(figsize=(12, 6.5))
        sns.heatmap(provider_us_effects, cmap="vlag", center=0, annot=True, fmt=".3%", linewidths=.4,
                    cbar_kws={"label": "Post-release minus other-session U.S. return"})
        plt.title("U.S. IT-services response following frontier-model announcements")
        plt.xlabel("U.S. IT-services firm"); plt.ylabel("Publishing company")
        plt.tight_layout(); plt.savefig(plots / "provider_us_services_event_heatmap.png", dpi=220); plt.close()
    if not mediated_india_effects.empty:
        plt.figure(figsize=(12, 6.5))
        sns.heatmap(mediated_india_effects, cmap="vlag", center=0, annot=True, fmt=".3%", linewidths=.4,
                    cbar_kws={"label": "Post-U.S.-reaction minus other-session return"})
        plt.title("Nifty IT response after the first observable U.S. services reaction")
        plt.xlabel("Nifty IT constituent"); plt.ylabel("Publishing company")
        plt.tight_layout(); plt.savefig(plots / "provider_nifty_it_post_us_heatmap.png", dpi=220); plt.close()

    event = daily["ai_event__frontier_release_today"].fillna(0).gt(0)
    cohort = targets.mean(axis=1).rename("cohort_oc_return")
    event_table = pd.DataFrame({"event": event, "cohort_oc_return": cohort}).dropna()
    event_rows = event_table.loc[event_table["event"], "cohort_oc_return"]
    non_event_rows = event_table.loc[~event_table["event"], "cohort_oc_return"]
    design = sm.add_constant(event_table["event"].astype(float))
    fit = sm.OLS(event_table["cohort_oc_return"], design).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    rng = np.random.default_rng(int(config["validation"]["random_seed"]) + 401)
    observed = float(event_rows.mean() - non_event_rows.mean())
    permutations = []
    values = event_table["cohort_oc_return"].to_numpy()
    count = int(event_table["event"].sum())
    for _ in progress(range(5000), description="AI-event randomization inference", unit="draw"):
        chosen = rng.choice(len(values), size=count, replace=False)
        mask = np.zeros(len(values), dtype=bool); mask[chosen] = True
        permutations.append(float(values[mask].mean() - values[~mask].mean()))
    event_summary = {
        "development_end": str(development_end.date()), "event_sessions": count,
        "event_mean_return": float(event_rows.mean()), "non_event_mean_return": float(non_event_rows.mean()),
        "event_minus_non_event": observed, "hac_coefficient": float(fit.params.iloc[1]),
        "hac_t_statistic": float(fit.tvalues.iloc[1]), "hac_pvalue": float(fit.pvalues.iloc[1]),
        "two_sided_randomization_pvalue": float((np.abs(permutations) >= abs(observed)).mean()),
        "warning": "Small event counts imply low statistical power; this is hypothesis evidence, not causal identification.",
    }
    atomic_json_dump(event_summary, output / "frontier_event_study.json")
    event_table.loc[event_table["event"]].reset_index().to_csv(output / "frontier_event_sessions.csv", index=False)
    plt.figure(figsize=(8, 5))
    sns.boxenplot(data=event_table.assign(group=np.where(event_table["event"], "Frontier release", "Other session")),
                  x="group", y="cohort_oc_return", palette=["#9b2226", "#005f73"])
    plt.axhline(0, color="black", lw=.8); plt.ylabel("Equal-weight Nifty IT open-to-close return"); plt.xlabel("")
    plt.title("Nifty IT intraday returns on conservatively timed AI-release sessions")
    plt.tight_layout(); plt.savefig(plots / "frontier_event_return_distribution.png", dpi=220); plt.close()
    files = [p for p in output.rglob("*") if p.is_file()]
    manifest = {"schema_version": 1, **plan, "status": "complete", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "development_only": True, "event_summary": event_summary,
                "files": {str(p.relative_to(output)): sha256_file(p) for p in files}}
    atomic_json_dump(manifest, output / "manifest.json")
    print(json.dumps({**plan, "status": "complete", "event_sessions": count}, indent=2))


if __name__ == "__main__":
    main()
