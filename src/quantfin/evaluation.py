"""Forecast, portfolio, benchmark, and uncertainty metrics."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _drawdown(returns: pd.Series) -> tuple[pd.Series, float]:
    wealth = (1 + returns.fillna(0)).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    return drawdown, float(drawdown.min())


def strategy_returns(
    predictions: pd.DataFrame,
    *,
    forecast_hurdle: float,
    one_way_cost_bps: float,
) -> pd.DataFrame:
    frame = predictions.sort_values("signal_session").copy()
    frame["position"] = (frame["prediction"] > forecast_hurdle).astype(float)
    frame["turnover"] = frame["position"].diff().abs()
    if not frame.empty:
        frame.loc[frame.index[0], "turnover"] = frame.loc[frame.index[0], "position"]
    cost_rate = one_way_cost_bps / 10_000
    frame["trading_cost"] = frame["turnover"] * cost_rate
    frame["gross_strategy_return"] = frame["position"] * frame["target_return"]
    frame["net_strategy_return"] = frame["gross_strategy_return"] - frame["trading_cost"]
    if not frame.empty:
        final_liquidation = frame.loc[frame.index[-1], "position"]
        frame.loc[frame.index[-1], "turnover"] += final_liquidation
        frame.loc[frame.index[-1], "net_strategy_return"] -= final_liquidation * cost_rate
        frame.loc[frame.index[-1], "trading_cost"] += final_liquidation * cost_rate
    frame["strategy_wealth"] = (1 + frame["net_strategy_return"]).cumprod()
    frame["benchmark_wealth"] = (1 + frame["target_return"]).cumprod()
    frame["strategy_drawdown"], _ = _drawdown(frame["net_strategy_return"])
    frame["benchmark_drawdown"], _ = _drawdown(frame["target_return"])
    return frame


def _annualized_metrics(returns: pd.Series, annualization: int) -> dict[str, float]:
    clean = returns.dropna()
    if clean.empty:
        return {"annualized_mean": np.nan, "annualized_volatility": np.nan, "sharpe": np.nan, "cagr": np.nan, "max_drawdown": np.nan}
    mean = clean.mean() * annualization
    volatility = clean.std(ddof=1) * np.sqrt(annualization)
    sharpe = mean / volatility if volatility > 0 else np.nan
    years = len(clean) / annualization
    terminal = float((1 + clean).prod())
    cagr = terminal ** (1 / years) - 1 if years > 0 and terminal > 0 else np.nan
    _, maximum_drawdown = _drawdown(clean)
    return {
        "annualized_mean": float(mean),
        "annualized_volatility": float(volatility),
        "sharpe": float(sharpe),
        "cagr": float(cagr),
        "max_drawdown": maximum_drawdown,
    }


def evaluate_predictions(
    predictions: pd.DataFrame,
    configurations: dict[str, dict[str, Any]],
    *,
    forecast_hurdle: float,
    one_way_cost_bps: float,
    annualization: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline = predictions.loc[
        predictions["family"].eq("historical_mean"), ["signal_session", "prediction"]
    ].rename(columns={"prediction": "historical_mean_prediction"})
    results = []
    ledgers = []
    for config_id, group in predictions.groupby("config_id", sort=False):
        ledger = strategy_returns(
            group,
            forecast_hurdle=forecast_hurdle,
            one_way_cost_bps=one_way_cost_bps,
        )
        ledger["config_id"] = config_id
        ledgers.append(ledger)
        merged = ledger.merge(baseline, on="signal_session", how="left", validate="one_to_one")
        error = merged["target_return"] - merged["prediction"]
        baseline_error = merged["target_return"] - merged["historical_mean_prediction"]
        denominator = float(np.square(baseline_error.dropna()).sum())
        oos_r2 = 1 - float(np.square(error.dropna()).sum()) / denominator if denominator > 0 else np.nan
        performance = _annualized_metrics(ledger["net_strategy_return"], annualization)
        benchmark = _annualized_metrics(ledger["target_return"], annualization)
        annual_sharpes = ledger.assign(
            year=pd.to_datetime(ledger["signal_session"]).dt.year
        ).groupby("year")["net_strategy_return"].apply(
            lambda x: x.mean() / x.std(ddof=1) * np.sqrt(annualization) if x.std(ddof=1) > 0 else np.nan
        )
        config = configurations[config_id]
        results.append(
            {
                "config_id": config_id,
                "family": config["family"],
                "parameters": str(config["parameters"]),
                "observations": len(ledger),
                "prediction_coverage": float(ledger["prediction"].notna().mean()),
                "mse": float(np.square(error).mean()),
                "mae": float(error.abs().mean()),
                "oos_r2_vs_historical_mean": oos_r2,
                "directional_accuracy": float(
                    (np.sign(ledger["prediction"]) == np.sign(ledger["target_return"])).mean()
                ),
                "annualized_net_return": performance["annualized_mean"],
                "annualized_net_volatility": performance["annualized_volatility"],
                "net_sharpe": performance["sharpe"],
                "net_cagr": performance["cagr"],
                "max_drawdown": performance["max_drawdown"],
                "median_annual_net_sharpe": float(annual_sharpes.median()),
                "annualized_benchmark_return": benchmark["annualized_mean"],
                "benchmark_sharpe": benchmark["sharpe"],
                "average_exposure": float(ledger["position"].mean()),
                "annualized_turnover": float(ledger["turnover"].mean() * annualization),
                "total_trading_cost": float(ledger["trading_cost"].sum()),
                "mean_fit_seconds": float(ledger["fit_seconds"].mean()),
                "mean_train_mse": float(ledger["train_mse"].mean()),
                "train_test_mse_gap": float(np.square(error).mean() - ledger["train_mse"].mean()),
                "median_train_observations": float(ledger["n_train"].median()),
                "median_trainable_parameters": float(ledger["trainable_parameters"].median()),
                "median_parameter_to_observation_ratio": float(
                    (ledger["trainable_parameters"] / ledger["n_train"]).median()
                ),
            }
        )
    return pd.DataFrame(results), pd.concat(ledgers, ignore_index=True)


def block_bootstrap_difference(
    strategy: pd.Series,
    benchmark: pd.Series,
    *,
    repetitions: int,
    block_length: int,
    confidence_level: float,
    seed: int,
    annualization: int,
) -> dict[str, float]:
    paired = pd.concat([strategy, benchmark], axis=1).dropna().to_numpy()
    n = len(paired)
    if n < block_length * 2:
        raise ValueError("Insufficient returns for requested block bootstrap")
    rng = np.random.default_rng(seed)
    differences = []
    for _ in range(repetitions):
        sampled = []
        while len(sampled) < n:
            start = rng.integers(0, n - block_length + 1)
            sampled.extend(paired[start : start + block_length])
        sample = np.asarray(sampled[:n])
        differences.append((sample[:, 0].mean() - sample[:, 1].mean()) * annualization)
    alpha = 1 - confidence_level
    return {
        "annualized_mean_return_difference": float((paired[:, 0].mean() - paired[:, 1].mean()) * annualization),
        "confidence_lower": float(np.quantile(differences, alpha / 2)),
        "confidence_upper": float(np.quantile(differences, 1 - alpha / 2)),
        "repetitions": repetitions,
        "block_length": block_length,
        "confidence_level": confidence_level,
    }

