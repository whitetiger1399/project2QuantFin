"""Finance-oriented diagnostics with explicit multiple-testing controls."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.stats.multitest import multipletests
from statsmodels.tsa.stattools import adfuller, kpss

from quantfin.io import atomic_json_dump, read_manifest, sha256_file, utc_now
from quantfin.progress import progress


def _safe_test(name: str, function: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return {"test": name, "status": "ok", **function()}
    except Exception as exc:
        return {"test": name, "status": "failed", "error_type": type(exc).__name__, "error": str(exc)}


def _variance_ratio(values: pd.Series, horizon: int) -> dict[str, float]:
    returns = values.dropna().to_numpy(dtype=float)
    if len(returns) <= horizon + 1:
        raise ValueError("Insufficient observations for variance-ratio test")
    one_period_variance = np.var(returns, ddof=1)
    aggregated = np.convolve(returns, np.ones(horizon), mode="valid")
    ratio = np.var(aggregated, ddof=1) / (horizon * one_period_variance)
    # Large-sample homoskedastic approximation; reported as a diagnostic only.
    variance = 2 * (2 * horizon - 1) * (horizon - 1) / (3 * horizon * len(returns))
    z_value = (ratio - 1) / np.sqrt(variance)
    return {
        "horizon": horizon,
        "variance_ratio": float(ratio),
        "z_statistic_homoskedastic": float(z_value),
        "p_value_two_sided_approximate": float(2 * stats.norm.sf(abs(z_value))),
    }


def _hac_mean_test(values: pd.Series, max_lags: int = 5) -> dict[str, float]:
    clean = values.dropna().to_numpy(dtype=float)
    result = sm.OLS(clean, np.ones((len(clean), 1))).fit(cov_type="HAC", cov_kwds={"maxlags": max_lags})
    return {
        "mean": float(result.params[0]),
        "hac_standard_error": float(result.bse[0]),
        "t_statistic": float(result.tvalues[0]),
        "p_value": float(result.pvalues[0]),
        "max_lags": max_lags,
    }


def run_statistical_tests(
    market_dataset: Path,
    feature_dataset: Path,
    feature_set: str,
    output_dir: Path,
    development_split: str = "initial_train",
) -> dict[str, Any]:
    market_manifest = read_manifest(market_dataset / "manifest.json")
    panel_path = market_dataset / "market_panel.parquet"
    panel_entry = next(item for item in market_manifest["files"] if item["path"] == panel_path.name)
    if sha256_file(panel_path) != panel_entry["sha256"]:
        raise ValueError(f"Market panel hash mismatch: {panel_path}")
    panel = pd.read_parquet(panel_path).sort_values("session")
    panel["session"] = pd.to_datetime(panel["session"])

    feature_manifest = read_manifest(feature_dataset / "manifest.json")
    if feature_manifest.get("source_market_dataset_id") != market_manifest["dataset_id"]:
        raise ValueError(
            "Feature and market datasets have different lineage: "
            f"{feature_manifest.get('source_market_dataset_id')} != {market_manifest['dataset_id']}"
        )
    feature_path = feature_dataset / feature_manifest["file"]["path"]
    if sha256_file(feature_path) != feature_manifest["file"]["sha256"]:
        raise ValueError(f"Feature file hash mismatch: {feature_path}")
    features = pd.read_parquet(feature_path)
    features["signal_session"] = pd.to_datetime(features["signal_session"])
    if feature_set not in feature_manifest["feature_sets"]:
        raise ValueError(f"Unknown feature set: {feature_set}")
    development = features.loc[features["split"].eq(development_split)].copy()
    if development.empty:
        raise ValueError(f"No feature rows in requested split: {development_split}")
    panel = panel.loc[
        panel["session"].between(
            development["signal_session"].min(),
            development["signal_session"].max(),
            inclusive="both",
        )
    ].copy()
    spy_price = panel["spy_adjusted_close"].astype(float)
    spy_log_price = np.log(spy_price)
    spy_log_return = spy_log_price.diff().dropna()
    feature_columns = feature_manifest["feature_sets"][feature_set]
    output_dir.mkdir(parents=True, exist_ok=True)

    tests: list[dict[str, Any]] = []
    test_jobs: list[tuple[str, Callable[[], dict[str, Any]]]] = [
        (
            "daily_mean_t_test_iid",
            lambda: {
                "statistic": float(stats.ttest_1samp(spy_log_return, 0, nan_policy="omit").statistic),
                "p_value": float(stats.ttest_1samp(spy_log_return, 0, nan_policy="omit").pvalue),
                "null": "mean daily log return equals zero under IID assumptions",
            },
        ),
        ("daily_mean_hac", lambda: {**_hac_mean_test(spy_log_return), "null": "mean daily log return equals zero with HAC uncertainty"}),
        (
            "jarque_bera_normality",
            lambda: {
                "statistic": float(stats.jarque_bera(spy_log_return).statistic),
                "p_value": float(stats.jarque_bera(spy_log_return).pvalue),
                "skewness": float(stats.skew(spy_log_return, bias=False)),
                "excess_kurtosis": float(stats.kurtosis(spy_log_return, fisher=True, bias=False)),
                "null": "daily log returns are Gaussian",
            },
        ),
        (
            "adf_log_price",
            lambda: {
                "statistic": float(adfuller(spy_log_price.dropna(), autolag="AIC")[0]),
                "p_value": float(adfuller(spy_log_price.dropna(), autolag="AIC")[1]),
                "null": "log price has a unit root",
            },
        ),
        (
            "adf_log_return",
            lambda: {
                "statistic": float(adfuller(spy_log_return, autolag="AIC")[0]),
                "p_value": float(adfuller(spy_log_return, autolag="AIC")[1]),
                "null": "log return has a unit root",
            },
        ),
        (
            "kpss_log_price",
            lambda: {
                "statistic": float(kpss(spy_log_price.dropna(), regression="ct", nlags="auto")[0]),
                "p_value": float(kpss(spy_log_price.dropna(), regression="ct", nlags="auto")[1]),
                "null": "log price is trend stationary",
            },
        ),
        (
            "ljung_box_returns",
            lambda: {
                "lags": [5, 10, 20],
                "statistics": acorr_ljungbox(spy_log_return, lags=[5, 10, 20], return_df=True)["lb_stat"].tolist(),
                "p_values": acorr_ljungbox(spy_log_return, lags=[5, 10, 20], return_df=True)["lb_pvalue"].tolist(),
                "null": "no return autocorrelation through each lag",
            },
        ),
        (
            "ljung_box_squared_returns",
            lambda: {
                "lags": [5, 10, 20],
                "statistics": acorr_ljungbox(spy_log_return.pow(2), lags=[5, 10, 20], return_df=True)["lb_stat"].tolist(),
                "p_values": acorr_ljungbox(spy_log_return.pow(2), lags=[5, 10, 20], return_df=True)["lb_pvalue"].tolist(),
                "null": "no volatility clustering through each lag",
            },
        ),
        (
            "arch_lm",
            lambda: {
                "lm_statistic": float(het_arch(spy_log_return, nlags=10)[0]),
                "lm_p_value": float(het_arch(spy_log_return, nlags=10)[1]),
                "null": "no ARCH effects through lag 10",
            },
        ),
        ("variance_ratio_5", lambda: {**_variance_ratio(spy_log_return, 5), "null": "random-walk variance ratio equals one"}),
        ("variance_ratio_20", lambda: {**_variance_ratio(spy_log_return, 20), "null": "random-walk variance ratio equals one"}),
    ]
    for name, function in progress(test_jobs, description="Statistical tests", unit="test"):
        tests.append(_safe_test(name, function))

    relationship_rows = []
    for column in progress(feature_columns, description="Feature significance", unit="feature"):
        paired = development[[column, "target_return"]].dropna()
        if len(paired) < 30 or paired[column].nunique() < 2:
            continue
        pearson = stats.pearsonr(paired[column], paired["target_return"])
        spearman = stats.spearmanr(paired[column], paired["target_return"])
        relationship_rows.append(
            {
                "feature": column,
                "observations": len(paired),
                "pearson_correlation": pearson.statistic,
                "pearson_p_value": pearson.pvalue,
                "spearman_correlation": spearman.statistic,
                "spearman_p_value": spearman.pvalue,
            }
        )
    relationships = pd.DataFrame(relationship_rows)
    if not relationships.empty:
        relationships["pearson_fdr_p_value"] = multipletests(
            relationships["pearson_p_value"], method="fdr_bh"
        )[1]
        relationships["spearman_fdr_p_value"] = multipletests(
            relationships["spearman_p_value"], method="fdr_bh"
        )[1]
        relationships["pearson_fdr_significant_5pct"] = relationships["pearson_fdr_p_value"] < 0.05
        relationships["spearman_fdr_significant_5pct"] = relationships["spearman_fdr_p_value"] < 0.05
        relationships = relationships.sort_values("pearson_fdr_p_value")
    relationships.to_csv(output_dir / "feature_target_tests.csv", index=False)

    report = {
        "schema_version": 1,
        "created_at_utc": utc_now().isoformat(),
        "market_dataset_id": market_manifest["dataset_id"],
        "feature_dataset_id": feature_manifest["dataset_id"],
        "feature_set": feature_set,
        "development_split": development_split,
        "tests": tests,
        "feature_tests_file": "feature_target_tests.csv",
        "interpretation": [
            "Tests are diagnostics and do not establish a tradable causal relationship.",
            "Feature/target p-values use Benjamini-Hochberg false-discovery-rate correction.",
            "The variance-ratio z-test uses a homoskedastic approximation and should be treated as descriptive.",
            "Financial returns are heteroskedastic; HAC and block-bootstrap inference is preferred for strategy comparisons.",
            "No test result authorizes inspecting or redesigning against the final holdout period.",
        ],
    }
    atomic_json_dump(report, output_dir / "statistical_tests.json")
    return report

