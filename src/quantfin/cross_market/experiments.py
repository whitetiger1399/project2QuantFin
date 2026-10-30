"""Walk-forward model experiments, selection, and cost-aware strategy evaluation."""

from __future__ import annotations

import json
import math
import os
import time
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.base import BaseEstimator
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import ElasticNet, Lasso, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from quantfin.io import atomic_json_dump, atomic_parquet_dump, stable_object_hash
from quantfin.models import NormalizedRidge
from quantfin.progress import progress


def feature_columns(dictionary: pd.DataFrame, feature_set: str) -> list[str]:
    return dictionary.loc[
        dictionary["feature_sets"].fillna("").str.split("|").apply(lambda values: feature_set in values),
        "feature",
    ].tolist()


def _parameter_grid(values: dict[str, Any]) -> list[dict[str, Any]]:
    keys = [key for key, value in values.items() if isinstance(value, list)]
    fixed = {key: value for key, value in values.items() if key not in keys}
    return [{**fixed, **dict(zip(keys, combination))} for combination in product(*(values[key] for key in keys))]


def enumerate_configurations(config: dict[str, Any], profile: str) -> list[dict[str, Any]]:
    profile_config = config["models"]["profiles"][profile]
    permitted = set(profile_config["families"])
    limit = profile_config.get("grid_limit_per_family")
    configurations: list[dict[str, Any]] = []

    # Forecast baselines are fit under the same temporal protocol.
    for baseline in config["models"]["baselines"]:
        if baseline["family"] in permitted:
            configurations.append({**baseline, "feature_set": "F0_own", "experiment": "baseline"})

    # Predeclared one-factor-at-a-time feature progression under identical ridge shrinkage.
    if "ridge" in permitted:
        progression_alpha = float(config["models"]["feature_progression_alpha"])
        for feature_set in profile_config["feature_sets"]:
            configurations.append({
                "family": "ridge", "parameters": {"alpha": progression_alpha},
                "feature_set": feature_set, "experiment": "feature_progression",
            })

        # Two additional F4 penalties tune shrinkage without repeating the
        # F4 alpha already present in the controlled feature progression.
        if profile != "quick":
            for alpha in config["models"]["families"]["ridge"]["alpha"]:
                if float(alpha) == progression_alpha:
                    continue
                configurations.append({
                    "family": "ridge", "parameters": {"alpha": alpha},
                    "feature_set": "F4_full_us", "experiment": "ridge_tuning",
                })

    # Full model-family comparison uses F4, the economic question's complete US information set.
    for family in profile_config["families"]:
        if family in {"zero", "asset_mean", "autoregression", "ridge", "rff_ridge"}:
            continue
        grids = _parameter_grid(config["models"]["families"][family])
        if limit:
            grids = grids[: int(limit)]
        for parameters in grids:
            configurations.append({
                "family": family, "parameters": parameters,
                "feature_set": "F4_full_us", "experiment": "model_family",
            })

    # Kelly–Malamud–Zhou-style approximation complexity with ridge shrinkage.
    if "rff_ridge" in permitted:
        values = config["models"]["families"]["rff_ridge"]
        grids = [
            {
                "complexity_ratio": ratio,
                "maximum_components": values["maximum_components"],
                "gamma_scale": 1.0,
                "penalty": 1.0,
            }
            for ratio in values["complexity_ratio"]
        ]
        grids.extend(
            {
                "complexity_ratio": 2.0,
                "maximum_components": values["maximum_components"],
                "gamma_scale": 1.0,
                "penalty": penalty,
            }
            for penalty in [0.1, 10.0]
        )
        if profile == "quick":
            grids = [row for row in grids if row["complexity_ratio"] in {0.5, 2.0} and row["penalty"] == 1.0]
        for parameters in grids:
            configurations.append({
                "family": "rff_ridge", "parameters": parameters,
                "feature_set": "F2_us_tech", "experiment": "complexity",
            })

    unique: dict[str, dict[str, Any]] = {}
    for item in configurations:
        payload = {key: item[key] for key in ["family", "parameters", "feature_set", "experiment"]}
        item = {**payload, "config_id": f"cm_{item['family']}_{stable_object_hash(payload)[:12]}"}
        unique[item["config_id"]] = item
    return list(unique.values())


def stage_dates(config: dict[str, Any], stage: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    key = {"screening": "screening", "confirmation": "confirmation", "final_test": "final_test"}[stage]
    start, end = config["sample"]["splits"][key]
    return pd.Timestamp(start), pd.Timestamp(end)


def forecast_blocks(
    dates: pd.DatetimeIndex,
    start: pd.Timestamp,
    end: pd.Timestamp,
    refit_frequency: str,
) -> list[pd.DatetimeIndex]:
    selected = dates[(dates >= start) & (dates <= end)]
    period = {"month_start": "M", "quarter_start": "Q"}[refit_frequency]
    return [pd.DatetimeIndex(values) for _, values in pd.Series(selected, index=selected).groupby(selected.to_period(period))]


def _viable_columns(train: pd.DataFrame, columns: list[str], config: dict[str, Any]) -> list[str]:
    values = train[columns].replace([np.inf, -np.inf], np.nan)
    missing = values.isna().mean()
    allowed = missing[missing <= float(config["cleaning"]["maximum_feature_missing_fraction"])].index
    variance = values[allowed].var(skipna=True)
    threshold = float(config["cleaning"]["minimum_feature_variance"])
    return variance[variance > threshold].index.tolist()


def _winsorize(train: pd.DataFrame, test: pd.DataFrame, quantiles: list[float]) -> tuple[pd.DataFrame, pd.DataFrame]:
    lower = train.quantile(float(quantiles[0]))
    upper = train.quantile(float(quantiles[1]))
    return train.clip(lower=lower, upper=upper, axis=1), test.clip(lower=lower, upper=upper, axis=1)


def _build_estimator(configuration: dict[str, Any], input_count: int, rows: int, config: dict[str, Any]) -> tuple[BaseEstimator, int]:
    family = configuration["family"]
    parameters = configuration["parameters"]
    seed = int(config["validation"]["random_seed"])
    n_jobs = int(config["validation"]["n_jobs"])
    scaled = [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    if family == "autoregression":
        return Pipeline([*scaled, ("model", Ridge(alpha=float(parameters.get("alpha", 0.0)), solver="svd"))]), input_count + 1
    if family == "ridge":
        return Pipeline([*scaled, ("model", NormalizedRidge(float(parameters["alpha"]))) ]), input_count + 1
    if family == "lasso":
        selected = min(int(parameters["preselect_k"]), input_count)
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("selector", SelectKBest(score_func=f_regression, k=selected)),
            ("scaler", StandardScaler()),
            ("model", Lasso(
                alpha=float(parameters["alpha"]), max_iter=int(parameters["max_iter"]),
                tol=float(parameters["tolerance"]), selection="random", random_state=seed,
            )),
        ]), selected + 1
    if family == "elastic_net":
        selected = min(int(parameters["preselect_k"]), input_count)
        return Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("selector", SelectKBest(score_func=f_regression, k=selected)),
            ("scaler", StandardScaler()),
            ("model", ElasticNet(
                alpha=float(parameters["alpha"]), l1_ratio=float(parameters["l1_ratio"]),
                max_iter=int(parameters["max_iter"]), tol=float(parameters["tolerance"]),
                selection="random", random_state=seed,
            )),
        ]), selected + 1
    if family == "pca_ridge":
        components = min(int(parameters["n_components"]), input_count, rows - 1)
        return Pipeline([*scaled, ("pca", PCA(n_components=max(1, components), svd_solver="randomized", random_state=seed)), ("model", NormalizedRidge(float(parameters["alpha"]))) ]), components + 1
    if family in {"random_forest", "extra_trees"}:
        cls = RandomForestRegressor if family == "random_forest" else ExtraTreesRegressor
        model = cls(
            n_estimators=int(parameters["n_estimators"]), max_depth=parameters["max_depth"],
            min_samples_leaf=int(parameters["min_samples_leaf"]), max_features=parameters["max_features"],
            n_jobs=n_jobs, random_state=seed,
        )
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", model)]), int(parameters["n_estimators"]) * 2 ** (parameters["max_depth"] or 10)
    if family == "hist_gradient_boosting":
        model = HistGradientBoostingRegressor(
            max_leaf_nodes=int(parameters["max_leaf_nodes"]), learning_rate=float(parameters["learning_rate"]),
            max_iter=int(parameters["max_iter"]), min_samples_leaf=int(parameters["min_samples_leaf"]),
            l2_regularization=float(parameters["l2_regularization"]), early_stopping=False, random_state=seed,
        )
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", model)]), int(parameters["max_leaf_nodes"]) * int(parameters["max_iter"])
    if family == "rff_ridge":
        components = min(
            int(parameters.get("maximum_components", 10_000)),
            max(8, int(math.ceil(float(parameters["complexity_ratio"]) * input_count))),
        )
        gamma = float(parameters["gamma_scale"]) / max(1, input_count)
        model = Pipeline([
            *scaled,
            ("rff", RBFSampler(gamma=gamma, n_components=components, random_state=seed)),
            (
                "model",
                Ridge(
                    alpha=float(parameters["penalty"]) * rows,
                    solver="lsqr",
                    tol=1e-6,
                    max_iter=5_000,
                ),
            ),
        ])
        return model, components + 1
    raise ValueError(f"Unsupported fitted model family: {family}")


def _select_model_columns(configuration: dict[str, Any], columns: list[str]) -> list[str]:
    if configuration["family"] == "autoregression":
        selected = [column for column in columns if column.startswith("asset__") or (column.startswith("own__") and "ret_lag_" in column)]
        return selected
    return columns


def _extract_importance(estimator: BaseEstimator, columns: list[str], family: str) -> pd.DataFrame:
    if not hasattr(estimator, "named_steps") or "model" not in estimator.named_steps:
        return pd.DataFrame()
    model = estimator.named_steps["model"]
    values: np.ndarray | None = None
    measure = ""
    if family in {"autoregression", "ridge", "lasso", "elastic_net"} and hasattr(model, "coef_"):
        values = np.asarray(model.coef_).ravel(); measure = "standardized_coefficient"
    elif family == "pca_ridge" and hasattr(model, "coef_"):
        values = estimator.named_steps["pca"].components_.T @ np.asarray(model.coef_).ravel(); measure = "projected_coefficient"
    elif family in {"random_forest", "extra_trees"} and hasattr(model, "feature_importances_"):
        values = np.asarray(model.feature_importances_); measure = "impurity_importance"
    selected_columns = columns
    if "selector" in estimator.named_steps:
        selected_columns = list(np.asarray(columns)[estimator.named_steps["selector"].get_support()])
    if values is None or len(values) != len(selected_columns):
        return pd.DataFrame()
    result = pd.DataFrame({"feature": selected_columns, "importance": values, "measure": measure})
    return result.reindex(result["importance"].abs().sort_values(ascending=False).index).head(50)


def _fit_block(
    configuration: dict[str, Any],
    panel: pd.DataFrame,
    dictionary: pd.DataFrame,
    block: pd.DatetimeIndex,
    config: dict[str, Any],
    training_scheme: str,
    explain: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    started = time.monotonic()
    all_dates = pd.DatetimeIndex(sorted(panel["decision_date"].unique()))
    block_start = block.min()
    prior = all_dates[all_dates < block_start]
    embargo = int(config["validation"]["embargo_sessions"])
    if embargo:
        prior = prior[:-embargo]
    if training_scheme == "rolling":
        prior = prior[-int(config["validation"]["rolling_window_sessions"]):]
    train = panel.loc[panel["decision_date"].isin(prior)].copy()
    test = panel.loc[panel["decision_date"].isin(block)].copy()
    if len(train) < int(config["validation"]["minimum_training_rows"]):
        raise ValueError(f"Insufficient training rows before {block_start.date()}: {len(train)}")
    family = configuration["family"]
    base = feature_columns(dictionary, configuration["feature_set"])
    base = _select_model_columns(configuration, base)
    columns = _viable_columns(train, base, config)
    if not columns and family not in {"zero", "asset_mean"}:
        raise ValueError(f"No viable features for {configuration['config_id']} at {block_start.date()}")
    y_train = train["target_oc_return"].to_numpy(dtype=float)
    complexity = 1
    importance = pd.DataFrame()
    if family == "zero":
        prediction = np.zeros(len(test))
    elif family == "asset_mean":
        means = train.groupby("asset")["target_oc_return"].mean()
        prediction = test["asset"].map(means).fillna(train["target_oc_return"].mean()).to_numpy()
        complexity = len(means) + 1
    else:
        x_train, x_test = _winsorize(train[columns], test[columns], config["cleaning"]["feature_winsor_quantiles"])
        estimator, complexity = _build_estimator(configuration, len(columns), len(train), config)
        estimator.fit(x_train, y_train)
        prediction = estimator.predict(x_test)
        importance = _extract_importance(estimator, columns, family)
        if explain:
            rng = np.random.default_rng(int(config["validation"]["random_seed"]))
            baseline_mse = float(np.mean(np.square(test["target_oc_return"].to_numpy() - prediction)))
            grouped_rows: list[dict[str, Any]] = []
            for feature_family in sorted({column.split("__", 1)[0] for column in columns}):
                family_columns = [column for column in columns if column.split("__", 1)[0] == feature_family]
                permuted = x_test.copy()
                order = rng.permutation(len(permuted))
                permuted.loc[:, family_columns] = permuted[family_columns].to_numpy()[order]
                permuted_prediction = estimator.predict(permuted)
                permuted_mse = float(np.mean(np.square(test["target_oc_return"].to_numpy() - permuted_prediction)))
                grouped_rows.append({
                    "feature": f"GROUP::{feature_family}",
                    "importance": permuted_mse - baseline_mse,
                    "measure": "oos_group_permutation_mse_increase",
                })
            importance = pd.concat([importance, pd.DataFrame(grouped_rows)], ignore_index=True)
    result = test[["decision_date", "asset", "target_oc_return", "benchmark_nifty_it_cc_return", "benchmark_nifty50_cc_return", "benchmark_cohort_ew_oc_return"]].copy()
    result["prediction"] = prediction
    result["config_id"] = configuration["config_id"]
    result["feature_set"] = configuration["feature_set"]
    result["family"] = family
    diagnostics = {
        "block_start": str(block_start.date()), "block_end": str(block.max().date()),
        "training_start": str(prior.min().date()), "training_end": str(prior.max().date()),
        "training_rows": len(train), "training_dates": len(prior), "test_rows": len(test),
        "input_features": len(columns), "trainable_parameters_proxy": complexity,
        "parameter_to_observation_ratio": complexity / len(train),
        "parameter_to_feature_ratio": complexity / max(1, len(columns)),
        "runtime_seconds": time.monotonic() - started,
    }
    if not importance.empty:
        importance["block_start"] = str(block_start.date())
        importance["config_id"] = configuration["config_id"]
    return result, diagnostics, importance


def _checkpoint_paths(root: Path, config_id: str, block: pd.DatetimeIndex) -> tuple[Path, Path, Path]:
    directory = root / config_id
    key = str(block.min().date())
    return directory / f"{key}.parquet", directory / f"{key}.json", directory / f"{key}_importance.csv"


def _strategy_ledger(predictions: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    settings = config["strategy"]["primary"]
    round_trip_cost = 2.0 * (float(settings["one_way_cost_bps"]) + float(settings["slippage_bps"])) / 10_000.0
    hurdle = max(float(settings["forecast_hurdle"]), round_trip_cost)
    top_k = int(settings["top_k"])
    rows: list[dict[str, Any]] = []
    for date, group in predictions.groupby("decision_date"):
        eligible = group.loc[group["prediction"] > hurdle].nlargest(top_k, "prediction")
        if eligible.empty:
            gross = net = turnover = 0.0
            holdings = ""
        else:
            weight = min(1.0 / len(eligible), float(settings["maximum_weight"]))
            gross_exposure = weight * len(eligible)
            gross = float((eligible["target_oc_return"] * weight).sum())
            turnover = 2.0 * gross_exposure
            net = gross - turnover * (float(settings["one_way_cost_bps"]) + float(settings["slippage_bps"])) / 10_000.0
            holdings = "|".join(eligible["asset"].tolist())
        first = group.iloc[0]
        rows.append({
            "decision_date": date, "gross_return": gross, "net_return": net, "turnover": turnover,
            "holdings": holdings, "benchmark_nifty_it": first["benchmark_nifty_it_cc_return"],
            "benchmark_nifty50": first["benchmark_nifty50_cc_return"],
            "benchmark_cohort": first["benchmark_cohort_ew_oc_return"],
        })
    return pd.DataFrame(rows).sort_values("decision_date")


def _annualized_metrics(returns: pd.Series, annualization: int) -> dict[str, float]:
    values = returns.dropna().astype(float)
    if values.empty:
        return {key: float("nan") for key in ["annual_return", "annual_volatility", "sharpe", "sortino", "maximum_drawdown", "calmar"]}
    wealth = (1.0 + values).cumprod()
    years = len(values) / annualization
    annual_return = float(wealth.iloc[-1] ** (1 / years) - 1) if wealth.iloc[-1] > 0 and years > 0 else float("nan")
    volatility = float(values.std(ddof=1) * np.sqrt(annualization))
    downside = float(values.where(values.lt(0), 0).std(ddof=1) * np.sqrt(annualization))
    drawdown = wealth / wealth.cummax() - 1.0
    maximum_drawdown = float(drawdown.min())
    return {
        "annual_return": annual_return, "annual_volatility": volatility,
        "sharpe": float(values.mean() / values.std(ddof=1) * np.sqrt(annualization)) if values.std(ddof=1) > 0 else float("nan"),
        "sortino": float(values.mean() * annualization / downside) if downside > 0 else float("nan"),
        "maximum_drawdown": maximum_drawdown,
        "calmar": float(annual_return / abs(maximum_drawdown)) if maximum_drawdown < 0 else float("nan"),
    }


def evaluate_predictions(predictions: pd.DataFrame, diagnostics: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    annualization = int(config["validation"]["annualization_sessions"])
    baseline = predictions.loc[predictions["family"].eq("asset_mean"), ["decision_date", "asset", "prediction"]].rename(columns={"prediction": "asset_mean_prediction"})
    rows: list[dict[str, Any]] = []
    ledgers: list[pd.DataFrame] = []
    for config_id, group in predictions.groupby("config_id"):
        configuration = group.iloc[0]
        ledger = _strategy_ledger(group, config)
        ledger["config_id"] = config_id
        ledgers.append(ledger)
        errors = group["target_oc_return"] - group["prediction"]
        merged = group.merge(baseline, on=["decision_date", "asset"], how="left")
        denominator_zero = float(np.square(group["target_oc_return"]).sum())
        denominator_mean = float(np.square(merged["target_oc_return"] - merged["asset_mean_prediction"]).sum())
        daily_ic = group.groupby("decision_date").apply(
            lambda value: value["prediction"].corr(value["target_oc_return"], method="spearman"), include_groups=False
        )
        metrics = _annualized_metrics(ledger["net_return"], annualization)
        benchmark_metrics = _annualized_metrics(ledger["benchmark_nifty50"], annualization)
        diag = diagnostics.loc[diagnostics["config_id"].eq(config_id)]
        rows.append({
            "config_id": config_id, "family": configuration["family"], "feature_set": configuration["feature_set"],
            "observations": len(group), "prediction_coverage": float(group["prediction"].notna().mean()),
            "rmse": float(np.sqrt(np.mean(np.square(errors)))), "mae": float(np.mean(np.abs(errors))),
            "oos_r2_zero": 1.0 - float(np.square(errors).sum()) / denominator_zero if denominator_zero else float("nan"),
            "oos_r2_asset_mean": 1.0 - float(np.square(errors).sum()) / denominator_mean if denominator_mean and np.isfinite(denominator_mean) else float("nan"),
            "spearman_ic": float(daily_ic.mean()), "directional_accuracy": float((np.sign(group["prediction"]) == np.sign(group["target_oc_return"])).mean()),
            "net_annual_return": metrics["annual_return"], "net_annual_volatility": metrics["annual_volatility"],
            "net_sharpe": metrics["sharpe"], "net_sortino": metrics["sortino"],
            "maximum_drawdown": metrics["maximum_drawdown"], "calmar": metrics["calmar"],
            "mean_daily_turnover": float(ledger["turnover"].mean()),
            "nifty50_sharpe": benchmark_metrics["sharpe"],
            "mean_input_features": float(diag["input_features"].mean()),
            "mean_trainable_parameters_proxy": float(diag["trainable_parameters_proxy"].mean()),
            "mean_parameter_to_observation_ratio": float(diag["parameter_to_observation_ratio"].mean()),
            "mean_runtime_seconds_per_refit": float(diag["runtime_seconds"].mean()),
        })
    leaderboard = pd.DataFrame(rows)
    leaderboard = leaderboard.sort_values(
        ["net_sharpe", "oos_r2_asset_mean", "spearman_ic", "mean_daily_turnover", "mean_trainable_parameters_proxy"],
        ascending=[False, False, False, True, True], na_position="last",
    ).reset_index(drop=True)
    leaderboard.insert(0, "rank", np.arange(1, len(leaderboard) + 1))
    return leaderboard, pd.concat(ledgers, ignore_index=True)


def run_walk_forward(
    panel: pd.DataFrame,
    dictionary: pd.DataFrame,
    configurations: list[dict[str, Any]],
    config: dict[str, Any],
    stage: str,
    run_directory: Path,
    *,
    training_scheme: str = "rolling",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    start, end = stage_dates(config, stage)
    dates = pd.DatetimeIndex(sorted(panel["decision_date"].unique()))
    refit_frequency = config["validation"]["refit_frequency_by_stage"][stage]
    blocks = forecast_blocks(dates, start, end, refit_frequency)
    checkpoints = run_directory / "checkpoints"
    tasks = [(configuration, block) for configuration in configurations for block in blocks]
    prediction_frames: list[pd.DataFrame] = []
    diagnostic_rows: list[dict[str, Any]] = []
    importance_frames: list[pd.DataFrame] = []
    for configuration, block in progress(tasks, description=f"{stage} walk-forward", total=len(tasks), unit="refit"):
        parquet_path, json_path, importance_path = _checkpoint_paths(checkpoints, configuration["config_id"], block)
        if parquet_path.is_file() and json_path.is_file():
            prediction_frames.append(pd.read_parquet(parquet_path))
            with json_path.open("r", encoding="utf-8") as handle:
                diagnostic_rows.append(json.load(handle))
            if importance_path.is_file():
                importance_frames.append(pd.read_csv(importance_path))
            continue
        prediction, diagnostics, importance = _fit_block(
            configuration, panel, dictionary, block, config, training_scheme, explain=stage == "final_test"
        )
        diagnostics["config_id"] = configuration["config_id"]
        diagnostics["family"] = configuration["family"]
        diagnostics["feature_set"] = configuration["feature_set"]
        atomic_parquet_dump(prediction, parquet_path)
        atomic_json_dump(diagnostics, json_path)
        if not importance.empty:
            importance_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_importance = importance_path.with_suffix(".csv.tmp")
            importance.to_csv(temporary_importance, index=False)
            os.replace(temporary_importance, importance_path)
            importance_frames.append(importance)
        prediction_frames.append(prediction); diagnostic_rows.append(diagnostics)
    predictions = pd.concat(prediction_frames, ignore_index=True)
    diagnostics = pd.DataFrame(diagnostic_rows)
    importance = pd.concat(importance_frames, ignore_index=True) if importance_frames else pd.DataFrame()
    leaderboard, ledgers = evaluate_predictions(predictions, diagnostics, config)
    return predictions, diagnostics, importance, leaderboard.merge(
        pd.DataFrame({"config_id": [c["config_id"] for c in configurations], "configuration": [json.dumps(c, sort_keys=True) for c in configurations]}),
        on="config_id", how="left",
    ), ledgers


def cost_sensitivity(predictions: pd.DataFrame, config: dict[str, Any], config_id: str) -> pd.DataFrame:
    selected = predictions.loc[predictions["config_id"].eq(config_id)]
    base = json.loads(json.dumps(config))
    rows: list[dict[str, Any]] = []
    for top_k, cost, hurdle in product(
        config["strategy"]["robustness"]["top_k"],
        config["strategy"]["robustness"]["round_trip_cost_bps"],
        config["strategy"]["robustness"]["forecast_hurdle"],
    ):
        base["strategy"]["primary"]["top_k"] = top_k
        base["strategy"]["primary"]["one_way_cost_bps"] = cost / 2
        base["strategy"]["primary"]["slippage_bps"] = 0
        base["strategy"]["primary"]["forecast_hurdle"] = hurdle
        ledger = _strategy_ledger(selected, base)
        metrics = _annualized_metrics(ledger["net_return"], int(config["validation"]["annualization_sessions"]))
        rows.append({"top_k": top_k, "round_trip_cost_bps": cost, "forecast_hurdle": hurdle, **metrics, "mean_turnover": ledger["turnover"].mean()})
    return pd.DataFrame(rows)


def inferential_tests(
    predictions: pd.DataFrame,
    ledgers: pd.DataFrame,
    selected_config_id: str,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    """HAC forecast comparisons, CAPM-style alpha, block bootstrap, and annual stability."""
    baseline = predictions.loc[predictions["family"].eq("asset_mean"), ["decision_date", "asset", "prediction"]].rename(
        columns={"prediction": "baseline_prediction"}
    )
    comparison_rows: list[dict[str, Any]] = []
    for config_id, group in predictions.groupby("config_id"):
        merged = group.merge(baseline, on=["decision_date", "asset"], how="left")
        merged["loss_difference"] = np.square(merged["target_oc_return"] - merged["baseline_prediction"]) - np.square(
            merged["target_oc_return"] - merged["prediction"]
        )
        daily = merged.groupby("decision_date")["loss_difference"].mean().dropna()
        if len(daily) > 20:
            fit = sm.OLS(daily.to_numpy(), np.ones((len(daily), 1))).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
            statistic, pvalue = float(fit.tvalues[0]), float(fit.pvalues[0])
        else:
            statistic = pvalue = float("nan")
        comparison_rows.append({
            "config_id": config_id, "mean_squared_loss_improvement_vs_asset_mean": float(daily.mean()),
            "hac_t_statistic": statistic, "hac_pvalue": pvalue,
        })
    comparisons = pd.DataFrame(comparison_rows)
    if not comparisons.empty:
        comparisons["fdr_bh_pvalue"] = _bh(comparisons["hac_pvalue"].fillna(1).to_numpy())

    ledger = ledgers.loc[ledgers["config_id"].eq(selected_config_id)].sort_values("decision_date").copy()
    regression = ledger[["net_return", "benchmark_nifty50"]].dropna()
    if len(regression) > 20:
        model = sm.OLS(regression["net_return"], sm.add_constant(regression["benchmark_nifty50"])).fit(
            cov_type="HAC", cov_kwds={"maxlags": 5}
        )
        alpha = {
            "daily_alpha": float(model.params["const"]), "annualized_alpha": float(model.params["const"] * 252),
            "alpha_hac_t_statistic": float(model.tvalues["const"]), "alpha_hac_pvalue": float(model.pvalues["const"]),
            "nifty50_beta": float(model.params["benchmark_nifty50"]), "regression_observations": int(model.nobs),
        }
    else:
        alpha = {}

    returns = ledger["net_return"].fillna(0).to_numpy()
    repetitions = 1000
    block = 20
    rng = np.random.default_rng(int(config["validation"]["random_seed"]) + 101)
    sharpes: list[float] = []
    if len(returns) >= block:
        for _ in range(repetitions):
            starts = rng.integers(0, len(returns), size=math.ceil(len(returns) / block))
            sample = np.concatenate([np.take(returns, np.arange(start, start + block) % len(returns)) for start in starts])[: len(returns)]
            std = np.std(sample, ddof=1)
            sharpes.append(float(np.mean(sample) / std * np.sqrt(252)) if std > 0 else np.nan)
    bootstrap = {
        "method": "circular_block_bootstrap", "repetitions": repetitions, "block_length_sessions": block,
        "net_sharpe_95_ci": [float(np.nanquantile(sharpes, .025)), float(np.nanquantile(sharpes, .975))] if sharpes else [None, None],
        **alpha,
    }
    annual = ledger.assign(year=pd.to_datetime(ledger["decision_date"]).dt.year).groupby("year").agg(
        strategy_net_return=("net_return", lambda s: float((1 + s).prod() - 1)),
        nifty_it_return=("benchmark_nifty_it", lambda s: float((1 + s.fillna(0)).prod() - 1)),
        nifty50_return=("benchmark_nifty50", lambda s: float((1 + s.fillna(0)).prod() - 1)),
        mean_turnover=("turnover", "mean"),
    ).reset_index()
    return comparisons, bootstrap, annual


def _bh(values: np.ndarray) -> np.ndarray:
    count = len(values); order = np.argsort(values); ranked = values[order]
    adjusted = np.minimum.accumulate((ranked * count / np.arange(1, count + 1))[::-1])[::-1]
    output = np.empty(count); output[order] = np.clip(adjusted, 0, 1)
    return output


def set_thread_limits(config: dict[str, Any]) -> None:
    threads = str(config["validation"]["numeric_threads_per_worker"])
    for variable in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"]:
        os.environ.setdefault(variable, threads)
