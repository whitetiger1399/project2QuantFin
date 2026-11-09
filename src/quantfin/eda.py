"""Reproducible exploratory analysis for market and feature datasets."""

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
from pandas.tseries.holiday import USFederalHolidayCalendar

from quantfin.io import atomic_json_dump, read_manifest, sha256_file, utc_now
from quantfin.progress import progress


def _save_figure(figure: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def _read_verified_parquet(dataset: Path, filename: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    manifest = read_manifest(dataset / "manifest.json")
    file_entry = next(
        (item for item in manifest.get("files", []) if item["path"] == filename),
        manifest.get("file") if manifest.get("file", {}).get("path") == filename else None,
    )
    if not file_entry:
        raise ValueError(f"{filename} is absent from {dataset / 'manifest.json'}")
    path = dataset / filename
    if sha256_file(path) != file_entry["sha256"]:
        raise ValueError(f"Dataset file hash mismatch: {path}")
    return pd.read_parquet(path), manifest


def _event_table(
    sessions: pd.Series,
    returns: pd.Series,
    events_config: dict[str, Any],
) -> pd.DataFrame:
    rows = []
    session_index = pd.DatetimeIndex(sessions)
    window = int(events_config.get("event_window_sessions", 10))
    for event in events_config.get("events", []):
        event_date = pd.Timestamp(event["date"])
        position = int(session_index.searchsorted(event_date, side="left"))
        if position >= len(session_index):
            continue
        matched = session_index[position]
        start = max(0, position - window)
        end = min(len(session_index) - 1, position + window)
        window_returns = returns.iloc[start : end + 1]
        rows.append(
            {
                **event,
                "matched_session": matched,
                "matched_session_return": returns.iloc[position],
                "window_start": session_index[start],
                "window_end": session_index[end],
                "window_cumulative_return": (1 + window_returns.fillna(0)).prod() - 1,
                "window_min_return": window_returns.min(),
                "window_max_return": window_returns.max(),
            }
        )
    return pd.DataFrame(rows)


def run_market_eda(
    market_dataset: Path,
    events_config: dict[str, Any],
    output_dir: Path,
    through: str | None = None,
) -> dict[str, Any]:
    panel, manifest = _read_verified_parquet(market_dataset, "market_panel.parquet")
    panel["session"] = pd.to_datetime(panel["session"])
    panel = panel.sort_values("session").reset_index(drop=True)
    if through is not None:
        panel = panel.loc[panel["session"].le(pd.Timestamp(through))].reset_index(drop=True)
    if panel.empty:
        raise ValueError(f"Market EDA has no rows through {through}")
    symbols = [symbol.lower() for symbol in manifest["symbols"]]
    adjusted = panel.set_index("session")[[f"{symbol}_adjusted_close" for symbol in symbols]]
    adjusted.columns = [column.removesuffix("_adjusted_close").upper() for column in adjusted]
    simple_returns = adjusted.pct_change(fill_method=None)
    log_returns = np.log(adjusted / adjusted.shift(1))
    spy = adjusted[manifest["traded_asset"]]
    spy_return = simple_returns[manifest["traded_asset"]]

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = output_dir / "plots"
    table_dir = output_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    tasks = [
        "coverage",
        "normalized_prices",
        "event_timeline",
        "return_distribution",
        "volatility",
        "annual",
        "seasonality",
        "holiday_proximity",
        "correlations",
        "recent_trend",
        "noise",
    ]
    outputs: dict[str, Any] = {}
    for task in progress(tasks, description="Market EDA", unit="stage"):
        if task == "coverage":
            coverage = pd.DataFrame(
                {
                    "symbol": adjusted.columns,
                    "first_valid": [adjusted[c].first_valid_index() for c in adjusted],
                    "last_valid": [adjusted[c].last_valid_index() for c in adjusted],
                    "observations": [int(adjusted[c].notna().sum()) for c in adjusted],
                    "missing_on_spy_calendar": [int(adjusted[c].isna().sum()) for c in adjusted],
                }
            )
            coverage.to_csv(table_dir / "coverage.csv", index=False)
            outputs["coverage"] = "tables/coverage.csv"

        elif task == "normalized_prices":
            normalized = adjusted.divide(adjusted.apply(lambda x: x.dropna().iloc[0])) * 100
            figure, axis = plt.subplots(figsize=(13, 6))
            normalized.plot(ax=axis, linewidth=1.1)
            axis.set(title="Adjusted prices normalized to 100", ylabel="Growth of 100", xlabel="")
            axis.set_yscale("log")
            _save_figure(figure, plot_dir / "01_normalized_prices.png")

        elif task == "event_timeline":
            events = _event_table(panel["session"], spy_return.reset_index(drop=True), events_config)
            events.to_csv(table_dir / "event_windows.csv", index=False)
            figure, axis = plt.subplots(figsize=(14, 6))
            axis.plot(panel["session"], spy / spy.iloc[0] * 100, color="#1f4e79", linewidth=1.2)
            for event in events.to_dict(orient="records"):
                axis.axvline(event["matched_session"], color="#b22222", alpha=0.45, linewidth=0.9)
                axis.annotate(
                    event["name"],
                    (event["matched_session"], 102),
                    xycoords=("data", "axes points"),
                    rotation=90,
                    fontsize=7,
                    va="bottom",
                )
            axis.set(title="SPY growth with prespecified event markers", ylabel="Growth of 100", xlabel="")
            axis.set_yscale("log")
            _save_figure(figure, plot_dir / "02_spy_event_timeline.png")

        elif task == "return_distribution":
            clean = log_returns["SPY"].dropna()
            figure, axes = plt.subplots(1, 2, figsize=(13, 5))
            sns.histplot(clean, bins=100, kde=True, ax=axes[0], color="#386cb0")
            axes[0].set(title="SPY daily log-return distribution", xlabel="Log return")
            sorted_returns = np.sort(clean.to_numpy())
            normal_quantiles = np.sort(np.random.default_rng(17).normal(clean.mean(), clean.std(), len(clean)))
            axes[1].scatter(normal_quantiles, sorted_returns, s=5, alpha=0.5)
            bounds = [min(normal_quantiles.min(), sorted_returns.min()), max(normal_quantiles.max(), sorted_returns.max())]
            axes[1].plot(bounds, bounds, color="black", linewidth=1)
            axes[1].set(title="Empirical versus Gaussian quantiles", xlabel="Gaussian", ylabel="Observed")
            _save_figure(figure, plot_dir / "03_return_distribution.png")

        elif task == "volatility":
            figure, axis = plt.subplots(figsize=(13, 5))
            for window in (20, 60, 252):
                annualized = log_returns["SPY"].rolling(window).std() * np.sqrt(252)
                axis.plot(annualized.index, annualized, label=f"{window} sessions", linewidth=1)
            axis.legend()
            axis.set(title="SPY rolling annualized volatility", ylabel="Volatility", xlabel="")
            _save_figure(figure, plot_dir / "04_rolling_volatility.png")

        elif task == "annual":
            annual = pd.DataFrame(index=sorted(panel["session"].dt.year.unique()))
            annual.index.name = "year"
            grouped = spy_return.groupby(panel["session"].dt.year.to_numpy())
            annual["return"] = grouped.apply(lambda x: (1 + x.dropna()).prod() - 1)
            annual["volatility"] = grouped.std() * np.sqrt(252)
            annual["mean_daily_return"] = grouped.mean()
            annual["worst_day"] = grouped.min()
            annual["best_day"] = grouped.max()
            annual.to_csv(table_dir / "annual_market_statistics.csv")
            figure, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
            annual["return"].plot.bar(ax=axes[0], color=np.where(annual["return"] >= 0, "#2ca25f", "#de2d26"))
            annual["volatility"].plot.bar(ax=axes[1], color="#756bb1")
            axes[0].set(title="SPY calendar-year returns", ylabel="Return")
            axes[1].set(title="SPY annualized daily volatility", ylabel="Volatility", xlabel="Year")
            _save_figure(figure, plot_dir / "05_annual_trends.png")

        elif task == "seasonality":
            seasonal = pd.DataFrame({"return": spy_return, "year": panel["session"].dt.year.to_numpy(), "month": panel["session"].dt.month.to_numpy()})
            monthly = seasonal.groupby(["year", "month"])["return"].apply(lambda x: (1 + x.dropna()).prod() - 1).unstack()
            monthly.to_csv(table_dir / "monthly_returns.csv")
            figure, axis = plt.subplots(figsize=(13, 8))
            sns.heatmap(monthly, center=0, cmap="RdYlGn", ax=axis, cbar_kws={"label": "Return"})
            axis.set(title="SPY monthly return heatmap", xlabel="Month", ylabel="Year")
            _save_figure(figure, plot_dir / "06_monthly_return_heatmap.png")
            weekday = pd.DataFrame({"return": spy_return, "weekday": panel["session"].dt.day_name().to_numpy()}).groupby("weekday")["return"].agg(["mean", "std", "count"])
            weekday.to_csv(table_dir / "weekday_statistics.csv")

        elif task == "holiday_proximity":
            calendar = USFederalHolidayCalendar()
            holidays = calendar.holidays(
                start=panel["session"].min(), end=panel["session"].max(), return_name=True
            )
            observed = pd.DatetimeIndex(panel["session"])
            rows = []
            for holiday_date, holiday_name in holidays.items():
                previous_position = observed.searchsorted(holiday_date, side="left") - 1
                next_position = observed.searchsorted(holiday_date, side="right")
                if previous_position >= 0 and next_position < len(observed):
                    rows.append(
                        {
                            "holiday": holiday_name,
                            "holiday_date": holiday_date,
                            "previous_session": observed[previous_position],
                            "previous_return": spy_return.iloc[previous_position],
                            "next_session": observed[next_position],
                            "next_return": spy_return.iloc[next_position],
                        }
                    )
            holiday_frame = pd.DataFrame(rows)
            holiday_frame.to_csv(table_dir / "federal_holiday_proximity.csv", index=False)
            if not holiday_frame.empty:
                summary = holiday_frame.groupby("holiday")[["previous_return", "next_return"]].mean()
                figure, axis = plt.subplots(figsize=(12, 6))
                summary.plot.bar(ax=axis)
                axis.axhline(0, color="black", linewidth=0.8)
                axis.set(title="Returns around US federal holidays (descriptive)", ylabel="Mean daily return")
                _save_figure(figure, plot_dir / "07_holiday_proximity.png")

        elif task == "correlations":
            correlations = log_returns.corr()
            correlations.to_csv(table_dir / "asset_return_correlations.csv")
            figure, axis = plt.subplots(figsize=(7, 6))
            sns.heatmap(correlations, annot=True, fmt=".2f", center=0, cmap="vlag", ax=axis)
            axis.set(title="Daily log-return correlation")
            _save_figure(figure, plot_dir / "08_asset_correlation_heatmap.png")

        elif task == "recent_trend":
            recent = adjusted.tail(504)
            normalized = recent.divide(recent.iloc[0]) * 100
            figure, axis = plt.subplots(figsize=(13, 5))
            normalized.plot(ax=axis)
            axis.set(title="Most recent 504 sessions, normalized", ylabel="Growth of 100", xlabel="")
            _save_figure(figure, plot_dir / "09_recent_trends.png")

        elif task == "noise":
            spy_log = log_returns["SPY"]
            rolling_mean = spy_log.rolling(252, min_periods=60).mean()
            rolling_std = spy_log.rolling(252, min_periods=60).std()
            zscore = (spy_log - rolling_mean) / rolling_std
            noise = pd.DataFrame(
                {
                    "session": panel["session"],
                    "log_return": spy_log.to_numpy(),
                    "rolling_zscore": zscore.to_numpy(),
                    "absolute_zscore": zscore.abs().to_numpy(),
                }
            ).query("absolute_zscore >= 6").sort_values("absolute_zscore", ascending=False)
            noise.to_csv(table_dir / "extreme_return_diagnostics.csv", index=False)

    summary = {
        "schema_version": 1,
        "created_at_utc": utc_now().isoformat(),
        "market_dataset_id": manifest["dataset_id"],
        "analysis_scope": (
            f"Descriptive EDA through {through}." if through else "Full-sample descriptive EDA."
        ),
        "rows": len(panel),
        "first_session": panel["session"].min().date().isoformat(),
        "last_session": panel["session"].max().date().isoformat(),
        "symbols": manifest["symbols"],
        "plots": sorted(str(path.relative_to(output_dir)) for path in plot_dir.glob("*.png")),
        "tables": sorted(str(path.relative_to(output_dir)) for path in table_dir.glob("*.csv")),
        "notes": [
            "Event markers and holiday tables are descriptive and are not prediction features.",
            "Federal holidays are not identical to the NYSE holiday calendar.",
            "Extreme returns are flagged as noise candidates but are not removed automatically.",
        ],
    }
    atomic_json_dump(summary, output_dir / "eda_manifest.json")
    return summary


def run_feature_eda(
    feature_dataset: Path,
    feature_set: str,
    output_dir: Path,
    development_split: str = "initial_train",
) -> dict[str, Any]:
    frame, manifest = _read_verified_parquet(feature_dataset, "features_and_labels.parquet")
    feature_columns = manifest["feature_sets"][feature_set]
    development = frame.loc[frame["split"].eq(development_split)].copy()
    if development.empty:
        raise ValueError(f"No rows found for split {development_split!r}")
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = output_dir / "plots"
    table_dir = output_dir / "tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    for task in progress(
        ["missingness", "correlation", "target_relationship", "distributions", "temporal_stability"],
        description="Feature EDA",
        unit="stage",
    ):
        if task == "missingness":
            missing = development[feature_columns].isna().mean().sort_values(ascending=False)
            missing.rename("missing_fraction").to_csv(table_dir / "feature_missingness.csv")
            figure, axis = plt.subplots(figsize=(12, max(5, len(missing) * 0.16)))
            missing.sort_values().plot.barh(ax=axis, color="#6baed6")
            axis.set(title=f"Feature missingness: {development_split}", xlabel="Fraction missing")
            _save_figure(figure, plot_dir / "01_feature_missingness.png")

        elif task == "correlation":
            correlations = development[feature_columns].corr()
            correlations.to_csv(table_dir / "feature_correlations.csv")
            figure, axis = plt.subplots(figsize=(16, 14))
            sns.heatmap(correlations, cmap="vlag", center=0, xticklabels=True, yticklabels=True, ax=axis)
            axis.tick_params(labelsize=5)
            axis.set(title=f"Feature correlation matrix: {development_split}")
            _save_figure(figure, plot_dir / "02_feature_correlation_heatmap.png")
            upper = correlations.where(np.triu(np.ones(correlations.shape), k=1).astype(bool))
            pairs = upper.stack().rename("correlation").reset_index()
            pairs["absolute_correlation"] = pairs["correlation"].abs()
            pairs.sort_values("absolute_correlation", ascending=False).head(100).to_csv(
                table_dir / "top_correlated_feature_pairs.csv", index=False
            )

        elif task == "target_relationship":
            target_corr = development[feature_columns].corrwith(development["target_return"])
            target_corr = target_corr.sort_values(key=abs, ascending=False)
            target_corr.rename("pearson_target_correlation").to_csv(
                table_dir / "feature_target_correlations.csv"
            )
            figure, axis = plt.subplots(figsize=(11, 7))
            target_corr.head(25).sort_values().plot.barh(ax=axis, color="#9e9ac8")
            axis.set(title="Top training-period feature/target correlations", xlabel="Pearson correlation")
            _save_figure(figure, plot_dir / "03_feature_target_correlations.png")

        elif task == "distributions":
            variance = development[feature_columns].var().sort_values(ascending=False)
            selected = list(variance.head(min(12, len(variance))).index)
            long = development[selected].melt(var_name="feature", value_name="value").dropna()
            long["standardized_value"] = long.groupby("feature")["value"].transform(
                lambda values: (values - values.median()) / (values.quantile(0.75) - values.quantile(0.25))
                if values.quantile(0.75) > values.quantile(0.25)
                else 0.0
            )
            figure, axis = plt.subplots(figsize=(14, 7))
            sns.boxplot(data=long, x="feature", y="standardized_value", showfliers=False, ax=axis)
            axis.tick_params(axis="x", rotation=65, labelsize=8)
            axis.set(title="Robust-standardized feature distributions", xlabel="", ylabel="(x - median) / IQR")
            _save_figure(figure, plot_dir / "04_feature_distributions.png")

        elif task == "temporal_stability":
            dates = pd.to_datetime(development["signal_session"])
            annual_means = development.assign(year=dates.dt.year).groupby("year")[feature_columns].mean()
            annual_means.to_csv(table_dir / "annual_feature_means.csv")
            top = list(development[feature_columns].corrwith(development["target_return"]).abs().nlargest(8).index)
            rolling = pd.DataFrame(index=development.index)
            for column in top:
                rolling[column] = development[column].rolling(252, min_periods=126).corr(
                    development["target_return"]
                )
            figure, axis = plt.subplots(figsize=(13, 7))
            for column in top:
                axis.plot(dates, rolling[column], label=column, linewidth=0.9)
            axis.axhline(0, color="black", linewidth=0.8)
            axis.legend(fontsize=7, ncol=2)
            axis.set(title="Rolling feature/target correlation in initial training data", ylabel="252-session correlation", xlabel="")
            _save_figure(figure, plot_dir / "05_feature_temporal_stability.png")

    summary = {
        "schema_version": 1,
        "created_at_utc": utc_now().isoformat(),
        "feature_dataset_id": manifest["dataset_id"],
        "feature_set": feature_set,
        "split": development_split,
        "rows": len(development),
        "feature_count": len(feature_columns),
        "scope_warning": "EDA is restricted to the declared development split to prevent final-test-guided feature design.",
        "plots": sorted(str(path.relative_to(output_dir)) for path in plot_dir.glob("*.png")),
        "tables": sorted(str(path.relative_to(output_dir)) for path in table_dir.glob("*.csv")),
    }
    atomic_json_dump(summary, output_dir / "eda_manifest.json")
    return summary

