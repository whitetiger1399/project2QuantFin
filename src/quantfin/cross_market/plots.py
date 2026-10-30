"""Readable, publication-oriented experiment plots."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


BLUE = "#003D7C"
ORANGE = "#EF7C00"
GREEN = "#2A9D8F"
RED = "#9B2226"


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def create_run_plots(
    leaderboard: pd.DataFrame,
    ledgers: pd.DataFrame,
    predictions: pd.DataFrame,
    output: Path,
    *,
    selected_config_id: str | None = None,
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")
    top = leaderboard.head(20).sort_values("net_sharpe")
    labels = [f"{row.family} | {row.feature_set}" for row in top.itertuples()]
    fig, ax = plt.subplots(figsize=(10.5, max(5, len(top) * .35)))
    ax.barh(range(len(top)), top["net_sharpe"], color=[GREEN if value >= 0 else RED for value in top["net_sharpe"]])
    ax.set_yticks(range(len(top)), labels, fontsize=8)
    ax.axvline(0, color="#444", lw=.8)
    ax.set(title="Validation leaderboard: post-cost strategy Sharpe", xlabel="Annualized net Sharpe", ylabel="")
    _save(fig, output / "01_validation_leaderboard.png")

    best = selected_config_id or str(leaderboard.iloc[0]["config_id"])
    ledger = ledgers.loc[ledgers["config_id"].eq(best)].sort_values("decision_date").copy()
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    for column, label, color in [
        ("net_return", "Selected strategy (net)", BLUE),
        ("benchmark_nifty_it", "Nifty IT buy-and-hold proxy", ORANGE),
        ("benchmark_nifty50", "Nifty 50 buy-and-hold", GREEN),
        ("benchmark_cohort", "Equal-weight fixed cohort", "#6D597A"),
    ]:
        wealth = (1 + ledger[column].fillna(0)).cumprod()
        ax.plot(ledger["decision_date"], wealth, label=label, color=color, lw=1.7)
    ax.set(title="Out-of-sample cumulative wealth", ylabel="Growth of INR 1", xlabel="")
    ax.legend(frameon=False, ncol=2)
    _save(fig, output / "02_cumulative_wealth.png")

    wealth = (1 + ledger["net_return"].fillna(0)).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    fig, ax = plt.subplots(figsize=(10.5, 3.8))
    ax.fill_between(ledger["decision_date"], drawdown, 0, color=RED, alpha=.75)
    ax.set(title="Selected strategy drawdown", ylabel="Drawdown", xlabel="")
    _save(fig, output / "03_drawdown.png")

    complexity = leaderboard.loc[leaderboard["family"].eq("rff_ridge")].copy()
    if not complexity.empty:
        configuration = complexity["configuration"].str.extract(r'"complexity_ratio":\s*([0-9.]+)')[0].astype(float)
        complexity["complexity_ratio"] = configuration
        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        sns.scatterplot(data=complexity, x="complexity_ratio", y="net_sharpe", hue="feature_set", size="mean_trainable_parameters_proxy", sizes=(30, 180), ax=ax)
        ax.axhline(0, color="#444", lw=.8)
        ax.set_xscale("log")
        ax.set(title="Approximation complexity and generalization", xlabel="RFF components / input features", ylabel="Post-cost OOS Sharpe")
        _save(fig, output / "04_complexity_generalization.png")

    selected = predictions.loc[predictions["config_id"].eq(best)]
    ic = selected.groupby("decision_date").apply(lambda g: g["prediction"].corr(g["target_oc_return"], method="spearman"), include_groups=False)
    fig, ax = plt.subplots(figsize=(10.5, 4.2))
    ax.plot(ic.index, ic.rolling(63, min_periods=20).mean(), color=BLUE)
    ax.axhline(0, color="#444", lw=.8)
    ax.set(title="63-session rolling cross-sectional information coefficient", ylabel="Spearman IC", xlabel="")
    _save(fig, output / "05_rolling_information_coefficient.png")
