"""Exploratory, date-level inference; never used for model or policy selection."""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests


def regression(frame, outcome, terms, tested, *, minimum_events=None, covariance="HAC"):
    """Report unidentified/sparse designs explicitly, rather than manufacture p-values."""
    columns = list(dict.fromkeys([outcome, *terms, *(minimum_events or {})]))
    data = frame[columns].replace([np.inf, -np.inf], np.nan).dropna()
    result = {"n_dates": len(data), "term": tested, "coefficient": None,
              "ci_low": None, "ci_high": None, "pvalue": None}
    if minimum_events:
        for column, minimum in minimum_events.items():
            n = int(data[column].gt(0).sum())
            result[f"count_{column}"] = n
            if n < minimum or len(data) - n < minimum:
                return {**result, "status": "insufficient_event_sessions"}
    design = sm.add_constant(data[terms], has_constant="add")
    if len(data) < max(30, 5 * design.shape[1]):
        return {**result, "status": "insufficient_dates"}
    if np.linalg.matrix_rank(design.to_numpy()) < design.shape[1]:
        return {**result, "status": "unidentified_design"}
    kwargs = {"maxlags": 5} if covariance == "HAC" else {}
    fit = sm.OLS(data[outcome], design).fit(cov_type=covariance, cov_kwds=kwargs)
    interval = fit.conf_int().loc[tested]
    return {**result, "coefficient": float(fit.params[tested]),
            "ci_low": float(interval.iloc[0]), "ci_high": float(interval.iloc[1]),
            "pvalue": float(fit.pvalues[tested]), "status": "estimated",
            "covariance": covariance}


def adjust_tests(rows):
    """One Holm family for every reported primary/secondary regression in this run."""
    output = pd.DataFrame(rows)
    output["pvalue_holm"] = np.nan
    mask = pd.to_numeric(output["pvalue"], errors="coerce").notna()
    if mask.any():
        output.loc[mask, "pvalue_holm"] = multipletests(
            output.loc[mask, "pvalue"].astype(float), method="holm")[1]
    output["interpretation"] = "inconclusive_or_not_estimable"
    significant = output["pvalue_holm"].lt(.05)
    direction = pd.to_numeric(output["expected_sign"], errors="coerce")
    agrees = output["coefficient"].astype(float).mul(direction).gt(0)
    output.loc[significant & agrees, "interpretation"] = "exploratory_support"
    output.loc[significant & ~agrees, "interpretation"] = "opposite_direction"
    return output


def return_summary(values):
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if not len(x):
        return {"n_dates": 0}
    wealth = np.cumprod(1 + x)
    # Starting capital belongs in the high-water mark, including on day one.
    peak = np.maximum.accumulate(np.r_[1., wealth])[1:]
    std = x.std(ddof=1) if len(x) > 1 else 0
    return {"n_dates": len(x), "cumulative_return": float(wealth[-1] - 1),
            "annualized_return": float(wealth[-1] ** (252 / len(x)) - 1),
            "sharpe_zero_cash": float(np.sqrt(252) * x.mean() / std) if std > 0 else None,
            "maximum_drawdown": float((wealth / peak - 1).min())}


def block_indices(n, block, rng):
    starts = rng.integers(0, n, size=int(np.ceil(n / block)))
    return ((starts[:, None] + np.arange(block)) % n).ravel()[:n]


def headcount_changes(records):
    data = pd.DataFrame(records)
    data["period_end"] = pd.to_datetime(data["period_end"])
    if data.duplicated(["company", "period_end"]).any():
        raise ValueError("Duplicate company-quarter observations")
    if data["headcount"].le(0).any():
        raise ValueError("Headcount must be positive")
    rows = []
    for company, group in data.groupby("company"):
        group = group.sort_values("period_end").copy()
        lookup = group.set_index(group.period_end.dt.to_period("Q"))["headcount"]
        for row in group.to_dict("records"):
            quarter = row["period_end"].to_period("Q")
            for lag, name in [(1, "qoq"), (2, "six_month"), (4, "yoy")]:
                prior = lookup.get(quarter - lag, np.nan)
                row[f"headcount_{name}_pct"] = 100 * (row["headcount"] / prior - 1)
                row[f"headcount_{name}_absolute"] = row["headcount"] - prior
            rows.append(row)
    return pd.DataFrame(rows)
