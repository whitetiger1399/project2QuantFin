#!/usr/bin/env python3
"""Build a comprehensive statistical, trading, complexity, and plotting pack for one model run."""

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
from scipy import stats

from quantfin.cross_market.common import load_research_config, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


COLORS = {"strategy": "#003D7C", "nifty_it": "#EF7C00", "nifty50": "#2A9D8F", "negative": "#9B2226"}


def _metrics(values: pd.Series, annualization: int = 252) -> dict[str, float | int]:
    returns = values.replace([np.inf, -np.inf], np.nan).dropna().astype(float)
    if returns.empty:
        return {"observations": 0}
    wealth = (1 + returns).cumprod()
    years = len(returns) / annualization
    volatility = returns.std(ddof=1) * np.sqrt(annualization)
    drawdown = wealth / wealth.cummax() - 1
    annual_return = wealth.iloc[-1] ** (1 / years) - 1 if years > 0 and wealth.iloc[-1] > 0 else np.nan
    return {
        "observations": len(returns), "cumulative_return": float(wealth.iloc[-1] - 1),
        "annual_return": float(annual_return), "annual_volatility": float(volatility),
        "sharpe": float(returns.mean() / returns.std(ddof=1) * np.sqrt(annualization)) if returns.std(ddof=1) > 0 else np.nan,
        "maximum_drawdown": float(drawdown.min()), "positive_day_fraction": float(returns.gt(0).mean()),
    }


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_ai_capability_research.yaml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    run = root_path(config["outputs"]["runs_root"]) / args.run_id
    manifest_path = run / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete":
        raise ValueError("Model-result analysis requires a completed run")
    content_hash = stable_object_hash({
        "parent_manifest": sha256_file(manifest_path), "script": sha256_file(Path(__file__)),
    })[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    analysis_id = f"model_evidence_{manifest['stage']}_{stamp}_{content_hash}"
    output = root_path(config["outputs"]["analysis_root"]) / analysis_id
    plan = {"action": "analyze_ai_capability_model_run", "analysis_id": analysis_id,
            "content_hash": content_hash, "parent_run_id": run.name, "stage": manifest["stage"],
            "directory": str(output)}
    if args.plan_only:
        print(json.dumps(plan, indent=2)); return
    output.mkdir(parents=True, exist_ok=False)
    plots = output / "plots"; plots.mkdir()
    sns.set_theme(style="whitegrid", context="notebook")

    leaderboard = pd.read_csv(run / "leaderboard.csv")
    predictions = pd.read_parquet(run / "predictions.parquet")
    ledgers = pd.read_parquet(run / "strategy_ledgers.parquet")
    diagnostics = pd.read_csv(run / "refit_diagnostics.csv")
    configurations = {row["config_id"]: row for row in json.loads((run / "configurations.json").read_text(encoding="utf-8"))}
    winner = manifest["selected_config_id"]
    selected_predictions = predictions.loc[predictions["config_id"].eq(winner)].copy()
    selected_ledger = ledgers.loc[ledgers["config_id"].eq(winner)].sort_values("decision_date").copy()
    selected_ledger.to_csv(output / "daily_long_short_decisions_and_returns.csv", index=False)

    leaderboard["experiment"] = leaderboard["config_id"].map(lambda value: configurations[value].get("experiment", "unknown"))
    leaderboard["model_parameters"] = leaderboard["config_id"].map(lambda value: json.dumps(configurations[value].get("parameters", {}), sort_keys=True))
    best_family = leaderboard.sort_values("rank").groupby("family", as_index=False).head(1)
    best_family.to_csv(output / "best_by_model_family.csv", index=False)
    best_feature = leaderboard.sort_values("rank").groupby("feature_set", as_index=False).head(1)
    best_feature.to_csv(output / "best_by_information_set.csv", index=False)
    complexity = leaderboard.loc[leaderboard["experiment"].eq("complexity")].sort_values("mean_parameter_to_observation_ratio")
    complexity.to_csv(output / "complexity_generalization.csv", index=False)

    portfolio_rows = []
    for name, column in [("selected_strategy_net", "net_return"), ("selected_strategy_gross", "gross_return"),
                         ("nifty_it_buy_hold", "benchmark_nifty_it"), ("nifty50_buy_hold", "benchmark_nifty50"),
                         ("fixed_cohort_equal_weight", "benchmark_cohort")]:
        portfolio_rows.append({"portfolio": name, **_metrics(selected_ledger[column])})
    portfolio = pd.DataFrame(portfolio_rows)
    portfolio.to_csv(output / "portfolio_performance_comparison.csv", index=False)

    valid = selected_predictions[["prediction", "target_oc_return"]].dropna().copy()
    if valid["prediction"].nunique() > 1:
        valid["prediction_decile"] = pd.qcut(valid["prediction"], 10, duplicates="drop").astype(str)
    else:
        valid["prediction_decile"] = "single_forecast_bin"
    calibration = valid.groupby("prediction_decile", observed=True).agg(
        mean_prediction=("prediction", "mean"), mean_realized_return=("target_oc_return", "mean"),
        observations=("target_oc_return", "size"), realized_std=("target_oc_return", "std"),
    ).reset_index()
    calibration["standard_error"] = calibration["realized_std"] / np.sqrt(calibration["observations"])
    calibration.to_csv(output / "prediction_calibration_deciles.csv", index=False)
    signs = pd.crosstab(np.sign(valid["prediction"]).map({-1.0: "predicted_short", 0.0: "predicted_flat", 1.0: "predicted_long"}),
                        np.sign(valid["target_oc_return"]).map({-1.0: "realized_down", 0.0: "realized_flat", 1.0: "realized_up"}))
    signs.to_csv(output / "direction_confusion_matrix.csv")
    correct = int((np.sign(valid["prediction"]) == np.sign(valid["target_oc_return"])).sum())
    sign_test = stats.binomtest(correct, len(valid), p=.5, alternative="greater") if len(valid) else None
    calibration_fit = None
    if len(valid) > 20 and valid["prediction"].nunique() > 1:
        design = sm.add_constant(valid["prediction"])
        calibration_fit = sm.OLS(valid["target_oc_return"], design).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    forecast_inference = {
        "observations": len(valid), "directionally_correct": correct,
        "directional_accuracy": correct / len(valid) if len(valid) else np.nan,
        "one_sided_binomial_pvalue_vs_50_percent": float(sign_test.pvalue) if sign_test else np.nan,
        "calibration_intercept": float(calibration_fit.params["const"]) if calibration_fit is not None else np.nan,
        "calibration_slope": float(calibration_fit.params["prediction"]) if calibration_fit is not None else np.nan,
        "calibration_slope_hac_t": float(calibration_fit.tvalues["prediction"]) if calibration_fit is not None else np.nan,
        "calibration_slope_hac_pvalue": float(calibration_fit.pvalues["prediction"]) if calibration_fit is not None else np.nan,
    }
    atomic_json_dump(forecast_inference, output / "forecast_inference.json")

    plot_tasks = list(range(8))
    for task in progress(plot_tasks, description="Rendering model-evidence plots", unit="plot"):
        if task == 0:
            view = best_family.sort_values("net_sharpe")
            fig, ax = plt.subplots(figsize=(10, max(4.5, .42 * len(view))))
            ax.barh(view["family"], view["net_sharpe"], color=[COLORS["strategy"] if x >= 0 else COLORS["negative"] for x in view["net_sharpe"]])
            ax.axvline(0, color="#444", lw=.8); ax.set(title="Best post-cost result by model family", xlabel="OOS net Sharpe", ylabel="")
            _save(fig, plots / "01_model_family_comparison.png")
        elif task == 1:
            view = best_feature.sort_values("net_sharpe")
            fig, ax = plt.subplots(figsize=(10, max(4.5, .42 * len(view))))
            ax.barh(view["feature_set"], view["net_sharpe"], color="#2A9D8F")
            ax.axvline(0, color="#444", lw=.8); ax.set(title="Information-set progression", xlabel="OOS net Sharpe", ylabel="")
            _save(fig, plots / "02_information_set_progression.png")
        elif task == 2:
            fig, ax = plt.subplots(figsize=(10.5, 5.2))
            for column, label, color in [("net_return", "Strategy net", COLORS["strategy"]),
                                         ("benchmark_nifty_it", "Nifty IT buy-and-hold", COLORS["nifty_it"]),
                                         ("benchmark_nifty50", "Nifty 50 buy-and-hold", COLORS["nifty50"])]:
                ax.plot(selected_ledger["decision_date"], (1 + selected_ledger[column].fillna(0)).cumprod(), label=label, color=color)
            ax.set(title=f"{manifest['stage'].replace('_', ' ').title()} cumulative wealth", ylabel="Growth of INR 1", xlabel="")
            ax.legend(frameon=False); _save(fig, plots / "03_cumulative_wealth.png")
        elif task == 3:
            wealth = (1 + selected_ledger["net_return"].fillna(0)).cumprod(); drawdown = wealth / wealth.cummax() - 1
            fig, ax = plt.subplots(figsize=(10.5, 3.8)); ax.fill_between(pd.to_datetime(selected_ledger["decision_date"]), drawdown, 0, color=COLORS["negative"], alpha=.75)
            ax.set(title="Selected strategy drawdown", ylabel="Drawdown", xlabel=""); _save(fig, plots / "04_drawdown.png")
        elif task == 4:
            fig, ax = plt.subplots(figsize=(7.5, 5)); ax.errorbar(calibration["mean_prediction"], calibration["mean_realized_return"], yerr=1.96 * calibration["standard_error"], fmt="o", color=COLORS["strategy"])
            limits = [min(calibration["mean_prediction"].min(), calibration["mean_realized_return"].min()), max(calibration["mean_prediction"].max(), calibration["mean_realized_return"].max())]
            ax.plot(limits, limits, ls="--", color="#777"); ax.axhline(0, color="#444", lw=.7)
            ax.set(title="Prediction calibration by forecast decile", xlabel="Mean predicted return", ylabel="Mean realized return (95% CI)")
            _save(fig, plots / "05_prediction_calibration.png")
        elif task == 5:
            daily = selected_predictions.groupby("decision_date").apply(lambda value: value["prediction"].corr(value["target_oc_return"], method="spearman"), include_groups=False)
            fig, ax = plt.subplots(figsize=(10.5, 4)); ax.plot(daily.index, daily.rolling(63, min_periods=20).mean(), color=COLORS["strategy"]); ax.axhline(0, color="#444", lw=.8)
            ax.set(title="63-session rolling cross-sectional information coefficient", ylabel="Spearman IC", xlabel="")
            _save(fig, plots / "06_rolling_information_coefficient.png")
        elif task == 6:
            dates = pd.to_datetime(selected_ledger["decision_date"])
            fig, ax = plt.subplots(figsize=(10.5, 4.5))
            ax.fill_between(dates, 0, selected_ledger["long_exposure"], label="Long", color=COLORS["nifty50"], alpha=.8)
            ax.fill_between(dates, 0, -selected_ledger["short_exposure"], label="Short", color=COLORS["negative"], alpha=.8)
            ax.axhline(0, color="#444", lw=.7); ax.set(title="Daily long/short exposure", ylabel="Portfolio exposure", xlabel=""); ax.legend(frameon=False)
            _save(fig, plots / "07_long_short_exposure.png")
        else:
            fig, ax = plt.subplots(figsize=(8.5, 4.8))
            if not complexity.empty:
                sns.scatterplot(data=complexity, x="mean_parameter_to_observation_ratio", y="net_sharpe", hue="family", size="mean_trainable_parameters_proxy", sizes=(40, 220), ax=ax)
                ax.set_xscale("log")
            ax.axhline(0, color="#444", lw=.8); ax.set(title="Complexity and out-of-sample generalization", xlabel="Trainable-parameter proxy / training observations", ylabel="Net Sharpe")
            _save(fig, plots / "08_complexity_generalization.png")

    importance_path = run / "feature_importance_by_refit.csv"
    if importance_path.is_file():
        importance = pd.read_csv(importance_path)
        aggregate = importance.groupby(["measure", "feature"])["importance"].agg(["mean", "std", "count"]).reset_index()
        aggregate = aggregate.sort_values("mean", key=lambda values: values.abs(), ascending=False)
        aggregate.to_csv(output / "aggregated_feature_importance.csv", index=False)
        top = aggregate.head(25).sort_values("mean")
        fig, ax = plt.subplots(figsize=(10.5, 8)); ax.barh(top["feature"].str.slice(0, 80), top["mean"], color=[COLORS["strategy"] if x >= 0 else COLORS["negative"] for x in top["mean"]])
        ax.set(title="Final-model feature importance", xlabel="Mean importance across refits", ylabel="")
        _save(fig, plots / "09_feature_importance.png")

    copied_evidence = {}
    for name in ["cost_sensitivity.csv", "forecast_hac_comparisons.csv", "annual_performance.csv", "selected_model_inference.json"]:
        source = run / name
        if source.is_file():
            copied_evidence[name] = sha256_file(source)
    summary = {
        "stage": manifest["stage"], "selected_config_id": winner,
        "selected_family": configurations[winner]["family"], "selected_feature_set": configurations[winner]["feature_set"],
        "forecast_inference": forecast_inference,
        "portfolio_performance": portfolio.to_dict(orient="records"),
        "trade_days": int(selected_ledger["gross_exposure"].gt(0).sum()),
        "long_exposure_days": int(selected_ledger["long_exposure"].gt(0).sum()),
        "short_exposure_days": int(selected_ledger["short_exposure"].gt(0).sum()),
        "mean_turnover": float(selected_ledger["turnover"].mean()),
    }
    atomic_json_dump(summary, output / "model_evidence_summary.json")
    files = [path for path in output.rglob("*") if path.is_file()]
    atomic_json_dump({"schema_version": 1, **plan, "status": "complete",
                      "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                      "parent_manifest_sha256": sha256_file(manifest_path), "parent_evidence_hashes": copied_evidence,
                      "summary": summary, "files": {str(path.relative_to(output)): sha256_file(path) for path in files}}, output / "manifest.json")
    print(json.dumps({**plan, "status": "complete", "selected_config_id": winner}, indent=2))


if __name__ == "__main__":
    main()
