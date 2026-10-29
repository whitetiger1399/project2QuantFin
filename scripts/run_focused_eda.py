"""Generate a compact, finance-specific EDA package for the research report."""

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
from scipy import stats
from statsmodels.tsa.stattools import acf

from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.research_extension import load_feature_dataset, read_yaml


ROOT = Path(__file__).resolve().parents[1]
COLORS = ["#123B5D", "#1E7898", "#E0A458", "#A23B72", "#4F6D44"]


def save(fig: plt.Figure, output: Path, name: str) -> None:
    fig.savefig(output / name, dpi=260, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/research_extension_2026-10-21.yaml")
    parser.add_argument("--report-inputs", default="configs/report_inputs_2026-10-21.yaml")
    parser.add_argument("--top-features", type=int, default=12)
    parser.add_argument("--rolling-window", type=int, default=252)
    parser.add_argument("--output-root", default="artifacts/research/focused_eda")
    args = parser.parse_args()
    config_path = ROOT / args.config
    config = read_yaml(config_path)
    report_inputs = read_yaml(ROOT / args.report_inputs)
    frame, feature_manifest, features, feature_dir = load_feature_dataset(ROOT, config["feature_dataset_id"], config["feature_set"])
    initial = frame.loc[
        frame["signal_session"].between(pd.Timestamp("2006-01-01"), pd.Timestamp("2014-12-31"))
        & frame["target_return"].notna()
    ].copy()
    correlations = initial[features].corrwith(initial["target_return"]).dropna().sort_values(key=np.abs, ascending=False)
    selected = correlations.head(args.top_features).index.tolist()
    identity = {"config_sha256": sha256_file(config_path), "feature_manifest_sha256": sha256_file(feature_dir / "manifest.json"), "top_features": args.top_features, "rolling_window": args.rolling_window}
    eda_id = "focused_eda_" + stable_object_hash(identity)[:16]
    output = ROOT / args.output_root / eda_id
    output.mkdir(parents=True, exist_ok=True)

    missing = pd.DataFrame({
        "feature": features,
        "missing_count": [int(frame[x].isna().sum()) for x in features],
        "missing_fraction": [float(frame[x].isna().mean()) for x in features],
        "first_valid_session": [frame.loc[frame[x].notna(), "signal_session"].min() for x in features],
        "last_valid_session": [frame.loc[frame[x].notna(), "signal_session"].max() for x in features],
    }).sort_values(["missing_fraction", "feature"], ascending=[False, True])
    missing.to_csv(output / "feature_coverage.csv", index=False)
    correlations.rename("initial_train_correlation").to_csv(output / "initial_train_feature_target_correlations.csv")

    sns.set_theme(style="whitegrid", font_scale=1.0)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5))
    target = frame["target_return"].dropna()
    sns.ecdfplot(target, ax=axes[0], color=COLORS[0], linewidth=2)
    axes[0].axvline(0, color="#555555", linewidth=.8)
    axes[0].set(title="Empirical distribution of next-session return", xlabel="Return")
    stats.probplot(target, dist="norm", plot=axes[1])
    axes[1].get_lines()[0].set_markerfacecolor(COLORS[1])
    axes[1].set_title("Normal Q–Q diagnostic")
    save(fig, output, "01_target_ecdf_qq.png")

    lag_count = 40
    acf_rows = []
    for transform, series in [("return", target), ("absolute_return", target.abs()), ("squared_return", target.pow(2))]:
        values = acf(series, nlags=lag_count, fft=True, missing="drop")
        acf_rows.extend({"transform": transform, "lag": lag, "acf": float(value)} for lag, value in enumerate(values))
    acf_frame = pd.DataFrame(acf_rows)
    acf_frame.to_csv(output / "return_dependence.csv", index=False)
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 8), sharex=True)
    for axis, (name, group), color in zip(axes, acf_frame.groupby("transform", sort=False), COLORS):
        axis.bar(group["lag"], group["acf"], color=color, width=.8)
        axis.axhline(0, color="#555", linewidth=.8)
        axis.set_ylabel(name.replace("_", " "))
    axes[-1].set_xlabel("Trading-session lag")
    fig.suptitle("Serial dependence in returns and volatility proxies")
    save(fig, output, "02_return_dependence_acf.png")

    corr = initial[selected].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    fig, ax = plt.subplots(figsize=(9.5, 8))
    sns.heatmap(corr, mask=mask, cmap="vlag", center=0, vmin=-1, vmax=1, annot=True, fmt=".2f", square=True, cbar_kws={"shrink": .75}, ax=ax)
    ax.set_title("Initial-training correlation among selected features")
    ax.tick_params(axis="x", labelrotation=55, labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    save(fig, output, "03_selected_feature_correlation.png")

    rolling_rows = []
    ordered = frame.loc[frame["target_return"].notna(), ["signal_session", "target_return", *selected]].sort_values("signal_session")
    for feature in selected:
        values = ordered[feature].rolling(args.rolling_window, min_periods=args.rolling_window // 2).corr(ordered["target_return"])
        rolling_rows.append(pd.DataFrame({"signal_session": ordered["signal_session"], "feature": feature, "rolling_ic": values}))
    rolling = pd.concat(rolling_rows, ignore_index=True)
    rolling.to_csv(output / "rolling_information_coefficients.csv", index=False)
    fig, ax = plt.subplots(figsize=(12, 6.5))
    for feature, group in rolling.groupby("feature"):
        ax.plot(group["signal_session"], group["rolling_ic"], linewidth=1, alpha=.75, label=feature)
    ax.axhline(0, color="#444", linewidth=.8)
    ax.set(title=f"Rolling {args.rolling_window}-session feature information coefficients", ylabel="Pearson correlation", xlabel="Signal session")
    ax.legend(ncol=2, fontsize=7, frameon=False, loc="upper left")
    save(fig, output, "04_rolling_information_coefficients.png")

    run_rows = []
    for role in ["canonical", "retrospective_comparison"]:
        for stage in ["screening", "confirmation"]:
            run_id = report_inputs[role][f"{stage}_run_id"]
            directory = ROOT / "artifacts/runs" / run_id
            ledger = pd.read_parquet(directory / "strategy_ledgers.parquet")
            ledger["pnl_session"] = pd.to_datetime(ledger["pnl_session"])
            yearly = ledger.assign(year=ledger["pnl_session"].dt.year).groupby(["family", "config_id", "year"], as_index=False).agg(
                net_mean=("net_strategy_return", "mean"),
                net_std=("net_strategy_return", "std"),
                exposure=("position", "mean"),
                observations=("position", "size"),
            )
            yearly["net_sharpe"] = yearly["net_mean"] / yearly["net_std"] * np.sqrt(252)
            yearly["run_id"] = run_id
            yearly["role"] = role
            yearly["stage"] = stage
            run_rows.append(yearly)
    model_year = pd.concat(run_rows, ignore_index=True)
    model_year.to_csv(output / "model_year_stability.csv", index=False)
    retrospective = model_year.loc[model_year["role"].eq("retrospective_comparison")].copy()
    leaders = retrospective.groupby(["family", "config_id"], as_index=False)["net_sharpe"].median().nlargest(12, "net_sharpe")
    selected_ids = leaders["config_id"]
    heat = retrospective.loc[retrospective["config_id"].isin(selected_ids)].copy()
    heat["label"] = heat["family"] + " | " + heat["config_id"].str[-8:]
    pivot = heat.pivot_table(index="label", columns="year", values="net_sharpe", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(10.5, max(5, .45 * len(pivot))))
    sns.heatmap(pivot, cmap="vlag", center=0, annot=True, fmt=".2f", ax=ax)
    ax.set(title="Annual net Sharpe stability for leading retrospective configurations", xlabel="P&L year", ylabel="Model configuration")
    save(fig, output, "05_model_year_stability.png")

    split_stats = frame.loc[frame["target_return"].notna()].groupby("split")["target_return"].agg(["count", "mean", "std", "skew", "min", "max"])
    split_stats.to_csv(output / "target_by_split.csv")
    manifest = {
        "schema_version": 1,
        "eda_id": eda_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "complete",
        "identity": identity,
        "selected_features_chosen_on_initial_train_only": selected,
        "figures": sorted(path.name for path in output.glob("*.png")),
        "tables": sorted(path.name for path in output.glob("*.csv")),
        "interpretation_rule": "Figures are diagnostic evidence; event labels do not establish causality.",
    }
    atomic_json_dump(manifest, output / "manifest.json")
    print(json.dumps({**manifest, "output_directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()

