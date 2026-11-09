"""Plots and uncertainty summaries derived from saved model-run artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from quantfin.evaluation import block_bootstrap_difference, strategy_returns
from quantfin.io import atomic_json_dump, read_manifest, utc_now
from quantfin.progress import progress


def _save(figure: plt.Figure, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def plot_model_run(
    run_directory: Path,
    model_config: dict[str, Any],
    top_n: int = 8,
) -> Path:
    manifest = read_manifest(run_directory / "run_manifest.json")
    if manifest.get("status") != "complete":
        raise ValueError(f"Cannot plot incomplete run: {run_directory}")
    metrics = pd.read_csv(run_directory / "config_metrics.csv")
    predictions = pd.read_parquet(run_directory / "predictions.parquet")
    ledgers = pd.read_parquet(run_directory / "strategy_ledgers.parquet")
    with (run_directory / "configurations.json").open("r", encoding="utf-8") as handle:
        configurations = json.load(handle)
    primary = model_config["research"]["primary_selection_metric"]
    ranked = metrics.sort_values(primary, ascending=False)
    top_ids = list(ranked.head(top_n)["config_id"])
    winner_id = top_ids[0]
    winner = ledgers.loc[ledgers["config_id"].eq(winner_id)].sort_values("signal_session")
    date_column = "pnl_session" if "pnl_session" in winner.columns else "label_end_session"
    output = run_directory / "plots"
    sns.set_theme(style="whitegrid")

    for task in progress(
        ["leaderboard", "wealth", "drawdown", "annual", "rolling", "complexity", "overfit", "costs", "features"],
        description="Model plots",
        unit="plot",
    ):
        if task == "leaderboard":
            figure, axis = plt.subplots(figsize=(12, 7))
            table = ranked.head(20).sort_values(primary)
            axis.barh(table["config_id"], table[primary], color="#3182bd")
            axis.axvline(0, color="black", linewidth=0.8)
            axis.set(title=f"Validation leaderboard: {primary}", xlabel=primary, ylabel="")
            axis.tick_params(axis="y", labelsize=7)
            _save(figure, output / "01_leaderboard.png")

        elif task == "wealth":
            figure, axis = plt.subplots(figsize=(13, 6))
            for config_id in top_ids[:5]:
                ledger = ledgers.loc[ledgers["config_id"].eq(config_id)].sort_values("signal_session")
                axis.plot(pd.to_datetime(ledger[date_column]), ledger["strategy_wealth"], label=config_id, linewidth=1)
            axis.plot(pd.to_datetime(winner[date_column]), winner["benchmark_wealth"], label="SPY buy-and-hold", color="black", linewidth=1.5)
            axis.set_yscale("log")
            axis.legend(fontsize=7)
            axis.set(title="Out-of-sample cumulative wealth", ylabel="Wealth", xlabel="")
            _save(figure, output / "02_cumulative_wealth.png")

        elif task == "drawdown":
            figure, axis = plt.subplots(figsize=(13, 5))
            axis.fill_between(pd.to_datetime(winner[date_column]), winner["strategy_drawdown"], 0, alpha=0.5, label="Strategy")
            axis.plot(pd.to_datetime(winner[date_column]), winner["benchmark_drawdown"], color="black", linewidth=1, label="SPY")
            axis.legend()
            axis.set(title=f"Drawdown: {winner_id}", ylabel="Drawdown", xlabel="")
            _save(figure, output / "03_drawdown.png")

        elif task == "annual":
            annual = winner.assign(year=pd.to_datetime(winner[date_column]).dt.year).groupby("year").agg(
                strategy=("net_strategy_return", lambda x: (1 + x).prod() - 1),
                benchmark=("target_return", lambda x: (1 + x).prod() - 1),
            )
            annual.to_csv(run_directory / "annual_returns.csv")
            figure, axis = plt.subplots(figsize=(12, 5))
            annual.plot.bar(ax=axis)
            axis.axhline(0, color="black", linewidth=0.8)
            axis.set(title=f"Calendar-year returns: {winner_id}", ylabel="Return", xlabel="Year")
            _save(figure, output / "04_annual_returns.png")

        elif task == "rolling":
            returns = winner["net_strategy_return"]
            rolling_sharpe = returns.rolling(252, min_periods=126).mean() / returns.rolling(252, min_periods=126).std() * np.sqrt(252)
            figure, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
            axes[0].plot(pd.to_datetime(winner[date_column]), rolling_sharpe, color="#756bb1")
            axes[0].axhline(0, color="black", linewidth=0.8)
            axes[0].set(title="Rolling 252-session Sharpe", ylabel="Sharpe")
            axes[1].plot(pd.to_datetime(winner[date_column]), winner["position"].rolling(60).mean(), color="#31a354")
            axes[1].set(title="Rolling 60-session market exposure", ylabel="Exposure", xlabel="")
            _save(figure, output / "05_rolling_sharpe_exposure.png")

        elif task == "complexity":
            finite = metrics.replace([np.inf, -np.inf], np.nan).dropna(subset=["median_parameter_to_observation_ratio", "net_sharpe"])
            figure, axis = plt.subplots(figsize=(10, 6))
            sns.scatterplot(data=finite, x="median_parameter_to_observation_ratio", y="net_sharpe", hue="family", ax=axis)
            axis.axvline(1, color="black", linestyle="--", linewidth=1, label="P/T = 1")
            axis.set_xscale("log")
            axis.set(title="Performance around the interpolation boundary", xlabel="Median trainable parameters / training observations", ylabel="Net Sharpe")
            _save(figure, output / "06_complexity_vs_sharpe.png")

        elif task == "overfit":
            figure, axis = plt.subplots(figsize=(10, 6))
            sns.scatterplot(data=metrics, x="mean_train_mse", y="mse", hue="family", size="median_trainable_parameters", ax=axis)
            bounds = [metrics[["mean_train_mse", "mse"]].min().min(), metrics[["mean_train_mse", "mse"]].max().max()]
            axis.plot(bounds, bounds, color="black", linestyle="--", linewidth=1)
            axis.set(title="Training versus out-of-sample error", xlabel="Mean training MSE", ylabel="Out-of-sample MSE")
            _save(figure, output / "07_training_vs_oos_error.png")

        elif task == "costs":
            cost_rows = []
            winner_predictions = predictions.loc[predictions["config_id"].eq(winner_id)]
            for cost in [0, 2, 5, 10, 20]:
                ledger = strategy_returns(
                    winner_predictions,
                    forecast_hurdle=float(model_config["research"]["forecast_hurdle"]),
                    one_way_cost_bps=cost,
                )
                volatility = ledger["net_strategy_return"].std() * np.sqrt(252)
                cost_rows.append(
                    {
                        "one_way_cost_bps": cost,
                        "annualized_return": ledger["net_strategy_return"].mean() * 252,
                        "sharpe": ledger["net_strategy_return"].mean() * 252 / volatility if volatility > 0 else np.nan,
                    }
                )
            costs = pd.DataFrame(cost_rows)
            costs.to_csv(run_directory / "cost_sensitivity.csv", index=False)
            figure, axis = plt.subplots(figsize=(8, 5))
            axis.plot(costs["one_way_cost_bps"], costs["sharpe"], marker="o")
            axis.axhline(0, color="black", linewidth=0.8)
            axis.set(title="Transaction-cost sensitivity", xlabel="One-way cost (bps)", ylabel="Sharpe")
            _save(figure, output / "08_cost_sensitivity.png")

        elif task == "features":
            files = sorted((run_directory / "checkpoints" / winner_id).glob("*_features.parquet"))
            if files:
                diagnostics = pd.concat([pd.read_parquet(path) for path in files], ignore_index=True)
                summary = diagnostics.groupby(["feature", "measure"])["value"].agg(
                    median="median",
                    mean_absolute=lambda x: x.abs().mean(),
                    sign_stability=lambda x: max((x > 0).mean(), (x < 0).mean()),
                ).reset_index().sort_values("mean_absolute", ascending=False)
                summary.to_csv(run_directory / "feature_stability.csv", index=False)
                figure, axis = plt.subplots(figsize=(11, 7))
                display = summary.head(25).sort_values("mean_absolute")
                axis.barh(display["feature"], display["mean_absolute"], color="#fd8d3c")
                axis.set(title=f"Feature magnitude across refits: {winner_id}", xlabel="Mean absolute diagnostic value", ylabel="")
                axis.tick_params(axis="y", labelsize=7)
                _save(figure, output / "09_feature_stability.png")

    uncertainty_config = model_config["uncertainty"]
    uncertainty = block_bootstrap_difference(
        winner["net_strategy_return"],
        winner["target_return"],
        repetitions=int(uncertainty_config["bootstrap_repetitions"]),
        block_length=int(uncertainty_config["block_length_sessions"]),
        confidence_level=float(uncertainty_config["confidence_level"]),
        seed=int(uncertainty_config["random_seed"]),
        annualization=int(model_config["research"]["annualization_sessions"]),
    )
    report_path = run_directory / "evaluation_report.json"
    atomic_json_dump(
        {
            "schema_version": 1,
            "created_at_utc": utc_now().isoformat(),
            "run_id": manifest["run_id"],
            "winner_by_current_run_metric": winner_id,
            "winner_configuration": configurations[winner_id],
            "block_bootstrap_strategy_minus_spy": uncertainty,
            "plots": sorted(str(path.relative_to(run_directory)) for path in output.glob("*.png")),
            "warnings": [
                "The winner label is descriptive for this run; use the selection command and chronology before final claims.",
                "Impurity importance can favor continuous or high-cardinality variables and does not establish causality.",
                "RFF coefficients are intentionally not mapped to raw features; use feature-set ablations for interpretation.",
                "Bootstrap intervals are conditional on the selected strategy and do not remove model-selection bias.",
            ],
        },
        report_path,
    )
    return report_path

