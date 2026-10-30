"""Exploratory, temporal, and statistical diagnostics for the research panel."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tsa.stattools import adfuller, kpss

from quantfin.io import atomic_json_dump
from quantfin.progress import progress
from quantfin.cross_market.common import root_path


COLORS = ["#003D7C", "#EF7C00", "#2A9D8F", "#9B2226", "#6D597A", "#4D908E"]


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _metric_tests(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for asset, group in progress(panel.groupby("asset"), description="Return diagnostics", unit="asset"):
        values = group.sort_values("decision_date")["target_oc_return"].dropna().to_numpy()
        if len(values) < 100:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            adf = adfuller(values, autolag="AIC")
            kpss_result = kpss(values, regression="c", nlags="auto")
            lb = acorr_ljungbox(values, lags=[5, 10, 21], return_df=True)
            arch = het_arch(values, nlags=10)
            jb = stats.jarque_bera(values)
        rows.append({
            "asset": asset,
            "observations": len(values),
            "mean": float(np.mean(values)),
            "volatility": float(np.std(values, ddof=1)),
            "skewness": float(stats.skew(values)),
            "excess_kurtosis": float(stats.kurtosis(values)),
            "adf_statistic": float(adf[0]),
            "adf_pvalue": float(adf[1]),
            "kpss_statistic": float(kpss_result[0]),
            "kpss_pvalue": float(kpss_result[1]),
            "ljung_box_5_pvalue": float(lb.loc[5, "lb_pvalue"]),
            "ljung_box_10_pvalue": float(lb.loc[10, "lb_pvalue"]),
            "ljung_box_21_pvalue": float(lb.loc[21, "lb_pvalue"]),
            "arch_lm_10_pvalue": float(arch[1]),
            "jarque_bera_pvalue": float(jb.pvalue),
        })
    return pd.DataFrame(rows)


def _target_feature_tests(panel: pd.DataFrame, dictionary: pd.DataFrame, limit: int = 300) -> pd.DataFrame:
    eligible = dictionary.loc[~dictionary["family"].isin(["asset"]), "feature"].tolist()
    coverage = panel[eligible].notna().mean().sort_values(ascending=False)
    selected: list[str] = []
    per_family = max(5, limit // max(1, dictionary["family"].nunique()))
    for _, group in dictionary.loc[dictionary["feature"].isin(eligible)].groupby("family"):
        selected.extend(coverage.reindex(group["feature"]).sort_values(ascending=False).head(per_family).index.tolist())
    selected = list(dict.fromkeys(selected))[:limit]
    rows: list[dict[str, Any]] = []
    target = panel["target_oc_return"]
    for feature in progress(selected, description="Feature tests", unit="feature"):
        valid = panel[[feature, "target_oc_return"]].dropna()
        if len(valid) < 100 or valid[feature].nunique() < 2:
            continue
        pearson = stats.pearsonr(valid[feature], valid["target_oc_return"])
        spearman = stats.spearmanr(valid[feature], valid["target_oc_return"])
        rows.append({
            "feature": feature,
            "family": feature.split("__", 1)[0],
            "observations": len(valid),
            "pearson_correlation": float(pearson.statistic),
            "pearson_pvalue": float(pearson.pvalue),
            "spearman_correlation": float(spearman.statistic),
            "spearman_pvalue": float(spearman.pvalue),
        })
    result = pd.DataFrame(rows)
    if not result.empty:
        result["pearson_fdr_bh"] = _benjamini_hochberg(result["pearson_pvalue"].to_numpy())
        result["spearman_fdr_bh"] = _benjamini_hochberg(result["spearman_pvalue"].to_numpy())
    return result.sort_values("spearman_correlation", key=lambda s: s.abs(), ascending=False)


def _benjamini_hochberg(values: np.ndarray) -> np.ndarray:
    count = len(values)
    order = np.argsort(values)
    ranked = np.asarray(values)[order]
    adjusted = np.minimum.accumulate((ranked * count / np.arange(1, count + 1))[::-1])[::-1]
    result = np.empty(count)
    result[order] = np.clip(adjusted, 0, 1)
    return result


def run_analysis(
    panel: pd.DataFrame,
    dictionary: pd.DataFrame,
    output: Path,
    config: dict[str, Any],
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")

    quality = panel.groupby("asset").agg(
        first_date=("decision_date", "min"),
        last_date=("decision_date", "max"),
        observations=("target_oc_return", "size"),
        target_missing=("target_oc_return", lambda s: int(s.isna().sum())),
        mean_oc_return=("target_oc_return", "mean"),
        volatility_oc=("target_oc_return", "std"),
    ).reset_index()
    quality.to_csv(output / "dataset_quality_by_asset.csv", index=False)
    tests = _metric_tests(panel)
    tests.to_csv(output / "return_statistical_tests.csv", index=False)
    feature_tests = _target_feature_tests(panel, dictionary)
    feature_tests.to_csv(output / "feature_target_tests.csv", index=False)

    family_missing = pd.DataFrame([
        {
            "family": family,
            "feature_count": len(group),
            "mean_missing_fraction": float(panel[group["feature"]].isna().mean().mean()),
            "maximum_missing_fraction": float(panel[group["feature"]].isna().mean().max()),
        }
        for family, group in dictionary.groupby("family")
    ])
    family_missing.to_csv(output / "missingness_by_feature_family.csv", index=False)

    daily = panel.groupby("decision_date")["target_oc_return"].mean().sort_index()
    rolling_center = daily.rolling(63, min_periods=40).mean()
    rolling_scale = daily.rolling(252, min_periods=126).std(ddof=1)
    shift_score = rolling_center.diff(21).abs() / rolling_scale.replace(0, np.nan)
    trend_shifts = pd.DataFrame({"cohort_return": daily, "shift_score": shift_score}).nlargest(20, "shift_score").sort_index()
    trend_shifts.to_csv(output / "trend_shift_candidates.csv", index_label="decision_date")
    seasonality = panel.assign(
        weekday=panel["decision_date"].dt.day_name(),
        month=panel["decision_date"].dt.month_name().str[:3],
        year=panel["decision_date"].dt.year,
    )
    seasonality.groupby(["weekday", "asset"])["target_oc_return"].agg(["mean", "std", "count"]).reset_index().to_csv(
        output / "weekday_seasonality.csv", index=False
    )
    seasonality.groupby(["month", "asset"])["target_oc_return"].agg(["mean", "std", "count"]).reset_index().to_csv(
        output / "monthly_seasonality.csv", index=False
    )

    # 1. Coverage timeline.
    coverage = panel.pivot_table(index="decision_date", columns="asset", values="target_oc_return", aggfunc="size").notna().astype(int)
    fig, ax = plt.subplots(figsize=(11, 4.8))
    sns.heatmap(coverage.T, cmap=sns.light_palette(COLORS[0], as_cmap=True), cbar=False, yticklabels=True, xticklabels=False, ax=ax)
    ax.set(title="Fixed-cohort target coverage", xlabel="Decision sessions (2016–2026)", ylabel="Nifty IT constituent")
    _save(fig, figures / "01_target_coverage.png")

    # 2. Distribution by stock.
    fig, ax = plt.subplots(figsize=(11, 5.5))
    order = panel.groupby("asset")["target_oc_return"].std().sort_values().index
    sns.violinplot(data=panel, x="target_oc_return", y="asset", order=order, inner="quart", cut=0, color=COLORS[0], ax=ax)
    ax.axvline(0, color="#333333", lw=1)
    ax.set(title="Open-to-close return distributions", xlabel="Daily simple return", ylabel="")
    _save(fig, figures / "02_target_distributions.png")

    # 3. Rolling cohort return and volatility.
    rolling_mean = daily.rolling(63).mean() * 252
    rolling_vol = daily.rolling(63).std() * np.sqrt(252)
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.5), sharex=True)
    axes[0].plot(rolling_mean.index, rolling_mean, color=COLORS[0]); axes[0].axhline(0, color="#555", lw=.8)
    axes[0].set_ylabel("Annualized mean"); axes[0].set_title("63-session rolling fixed-cohort dynamics")
    axes[1].plot(rolling_vol.index, rolling_vol, color=COLORS[1]); axes[1].set_ylabel("Annualized volatility")
    _save(fig, figures / "03_rolling_return_volatility.png")

    # 4. Readable correlation extremes rather than an unreadable full matrix.
    if not feature_tests.empty:
        extremes = pd.concat([feature_tests.nsmallest(12, "spearman_correlation"), feature_tests.nlargest(12, "spearman_correlation")]).drop_duplicates("feature")
        extremes = extremes.sort_values("spearman_correlation")
        fig, ax = plt.subplots(figsize=(11, 8))
        colors = [COLORS[3] if value < 0 else COLORS[2] for value in extremes["spearman_correlation"]]
        ax.barh(range(len(extremes)), extremes["spearman_correlation"], color=colors)
        ax.set_yticks(range(len(extremes)), [_shorten(v, 60) for v in extremes["feature"]], fontsize=8)
        ax.set(title="Strongest pooled feature–target rank correlations", xlabel="Spearman correlation", ylabel="")
        _save(fig, figures / "04_feature_target_correlation_extremes.png")

    # 5. Cross-asset correlation.
    target_wide = panel.pivot(index="decision_date", columns="asset", values="target_oc_return")
    fig, ax = plt.subplots(figsize=(8.5, 7))
    sns.heatmap(target_wide.corr(), cmap="vlag", center=0, annot=True, fmt=".2f", square=True, ax=ax, cbar_kws={"shrink": .75})
    ax.set_title("Nifty IT constituent open-to-close correlation")
    _save(fig, figures / "05_cross_asset_correlation.png")

    # 6. Lead/lag diagnostic between completed US tech returns and Indian cohort outcome.
    us_cols = [c for c in panel if c.startswith("us_tech__") and c.endswith("__ret_lag_1")]
    lead_lag_rows: list[dict[str, float]] = []
    if us_cols:
        unique = panel.drop_duplicates("decision_date").set_index("decision_date")
        us = unique[us_cols].mean(axis=1)
        joined = pd.concat({"us": us, "india": daily}, axis=1).dropna()
        for lag in range(-5, 6):
            lead_lag_rows.append({"lag": lag, "correlation": float(joined["us"].shift(lag).corr(joined["india"]))})
        lead_lag = pd.DataFrame(lead_lag_rows)
        lead_lag.to_csv(output / "us_india_lead_lag.csv", index=False)
        fig, ax = plt.subplots(figsize=(8.5, 4.5))
        ax.bar(lead_lag["lag"], lead_lag["correlation"], color=COLORS[0])
        ax.axhline(0, color="#444", lw=.8)
        ax.set(title="US technology return lead/lag diagnostic", xlabel="US feature shift (sessions)", ylabel="Correlation with India cohort O→C")
        _save(fig, figures / "06_us_india_lead_lag.png")

    # 7. Regime distributions using lagged VIX information when available.
    vix_cols = [c for c in panel if "us_context__vix" in c and c.endswith("__ret_lag_1")]
    if vix_cols:
        regime = panel[["target_oc_return", vix_cols[0]]].dropna().copy()
        regime["US volatility-return regime"] = pd.qcut(regime[vix_cols[0]], 4, labels=["Q1 low", "Q2", "Q3", "Q4 high"], duplicates="drop")
        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        sns.boxenplot(data=regime, x="US volatility-return regime", y="target_oc_return", color=COLORS[1], showfliers=False, ax=ax)
        ax.set(title="Indian IT returns across lagged US volatility regimes", xlabel="", ylabel="Nifty IT stock O→C return")
        _save(fig, figures / "07_regime_distribution.png")

    # 8. Family missingness is itself a data-quality result.
    ordered = family_missing.sort_values("mean_missing_fraction")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(ordered["family"], ordered["mean_missing_fraction"], color=COLORS[0])
    ax.set(title="Feature availability by information family", xlabel="Mean missing fraction", ylabel="")
    _save(fig, figures / "08_feature_family_missingness.png")

    # 9. Statistical change markers and optional retrospective global-event annotations.
    fig, ax = plt.subplots(figsize=(11, 4.8))
    cumulative = (1 + daily.fillna(0)).cumprod()
    ax.plot(cumulative.index, cumulative, color=COLORS[0], lw=1.6, label="Equal-weight cohort O→C wealth")
    for date in trend_shifts.index:
        ax.axvline(date, color=COLORS[1], alpha=.18, lw=.8)
    event_path = root_path(config["raw_data"]["manual_context"]["global_events"])
    event_count = 0
    if event_path.is_file():
        events = pd.read_csv(event_path)
        if not events.empty and "first_public_at_utc" in events:
            event_dates = pd.to_datetime(events["first_public_at_utc"], utc=True, errors="coerce").dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
            for index, event_date in enumerate(event_dates.dropna()):
                if cumulative.index.min() <= event_date <= cumulative.index.max():
                    ax.axvline(event_date, color=COLORS[3], alpha=.45, lw=1.0, ls="--")
                    event_count += 1
    ax.set(title="Statistical trend-shift candidates and retrospective event markers", ylabel="Growth of INR 1", xlabel="")
    ax.legend(frameon=False)
    _save(fig, figures / "09_trend_shifts_and_events.png")

    summary = {
        "rows": len(panel),
        "assets": int(panel["asset"].nunique()),
        "decision_dates": int(panel["decision_date"].nunique()),
        "features": len(dictionary),
        "figures": len(list(figures.glob("*.png"))),
        "statistical_test_assets": len(tests),
        "feature_tests": len(feature_tests),
        "trend_shift_candidates": len(trend_shifts),
        "retrospective_event_markers": event_count,
        "interpretation_guardrail": "Event overlays and lead-lag correlations are descriptive and must not be presented as causal evidence.",
    }
    atomic_json_dump(summary, output / "analysis_summary.json")
    return summary


def _shorten(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 1] + "…"
