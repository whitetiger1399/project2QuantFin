"""Evaluate activity, sizing, risk controls, uncertainty, and CAPM attribution."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from quantfin.io import atomic_json_dump, atomic_parquet_dump, stable_object_hash
from quantfin.research_extension import annualized_metrics, completed_round_trips


ROOT = Path(__file__).resolve().parents[1]


def ledger_with_position(frame: pd.DataFrame, position: pd.Series, cost_bps: float) -> pd.DataFrame:
    ledger = frame.sort_values("signal_session").copy()
    ledger["position"] = position.reindex(ledger.index).fillna(0).clip(0, 1)
    ledger["turnover"] = ledger["position"].diff().abs().fillna(ledger["position"])
    cost = cost_bps / 10_000
    ledger["trading_cost"] = ledger["turnover"] * cost
    ledger["gross_strategy_return"] = ledger["position"] * ledger["target_return"]
    ledger["net_strategy_return"] = ledger["gross_strategy_return"] - ledger["trading_cost"]
    if len(ledger):
        liquidation = float(ledger["position"].iloc[-1])
        ledger.loc[ledger.index[-1], "turnover"] += liquidation
        ledger.loc[ledger.index[-1], "trading_cost"] += liquidation * cost
        ledger.loc[ledger.index[-1], "net_strategy_return"] -= liquidation * cost
    return ledger


def block_interval(values: np.ndarray, block: int, repetitions: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    draws = []
    for _ in range(repetitions):
        sample = []
        while len(sample) < n:
            start = int(rng.integers(0, n - block + 1))
            sample.extend(values[start:start + block])
        draws.append(float(np.mean(sample[:n]) * 252))
    return float(np.quantile(draws, .025)), float(np.quantile(draws, .975))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", required=True, help="Path to predictions.parquet")
    parser.add_argument("--config-id", action="append", help="Repeat; defaults to every configuration")
    parser.add_argument("--forecast-hurdle", type=float, default=.001)
    parser.add_argument("--one-way-cost-bps", type=float, default=5)
    parser.add_argument("--volatility-target", type=float, default=.10)
    parser.add_argument("--bootstrap-repetitions", type=int, default=2000)
    parser.add_argument("--output-root", default="artifacts/research/strategy_robustness")
    args = parser.parse_args()
    prediction_path = (ROOT / args.predictions).resolve()
    data = pd.read_parquet(prediction_path)
    data["signal_session"] = pd.to_datetime(data["signal_session"])
    if args.config_id:
        data = data.loc[data["config_id"].isin(args.config_id)]
    if data.empty:
        raise ValueError("No predictions match the requested configurations")
    identity = {"prediction_path": str(prediction_path.relative_to(ROOT)), "config_ids": args.config_id, "hurdle": args.forecast_hurdle, "cost_bps": args.one_way_cost_bps, "volatility_target": args.volatility_target, "bootstrap_repetitions": args.bootstrap_repetitions}
    output = ROOT / args.output_root / ("robustness_" + stable_object_hash(identity)[:16])
    output.mkdir(parents=True, exist_ok=True)
    metric_rows = []
    bootstrap_rows = []
    capm_rows = []
    all_ledgers = []
    for config_id, group in data.groupby("config_id", sort=False):
        group = group.sort_values("signal_session").copy()
        past_vol = group["target_return"].rolling(20, min_periods=20).std().shift(1) * np.sqrt(252)
        risk_scalar = (args.volatility_target / past_vol).clip(upper=1).fillna(0)
        positions = {
            "binary_hurdle": group["prediction"].gt(args.forecast_hurdle).astype(float),
            "continuous_capped": (group["prediction"].clip(lower=0) / args.forecast_hurdle * risk_scalar).clip(0, 1),
            "volatility_managed_spy": risk_scalar,
            "buy_and_hold_spy": pd.Series(1.0, index=group.index),
            "cash": pd.Series(0.0, index=group.index),
        }
        reference_returns = None
        for rule, position in positions.items():
            rule_frame = group.copy()
            if rule in {"volatility_managed_spy", "buy_and_hold_spy", "cash"}:
                rule_frame["prediction"] = 0.0
            ledger = ledger_with_position(rule_frame, position, args.one_way_cost_bps if rule != "cash" else 0)
            ledger["config_id"] = config_id
            ledger["sizing_rule"] = rule
            all_ledgers.append(ledger)
            measures = annualized_metrics(ledger["net_strategy_return"])
            metric_rows.append({"config_id": config_id, "family": group["family"].iloc[0], "sizing_rule": rule, "average_exposure": float(ledger["position"].mean()), "active_sessions": int(ledger["position"].gt(0).sum()), "completed_round_trips": completed_round_trips(ledger["position"]), "annualized_turnover": float(ledger["turnover"].mean() * 252), **measures})
            if rule == "buy_and_hold_spy":
                reference_returns = ledger["net_strategy_return"].to_numpy()
            if rule in {"binary_hurdle", "continuous_capped"}:
                excess = ledger["net_strategy_return"].to_numpy() - group["target_return"].to_numpy()
                for block in [10, 20, 60]:
                    lower, upper = block_interval(excess, block, args.bootstrap_repetitions, 29 + block)
                    bootstrap_rows.append({"config_id": config_id, "sizing_rule": rule, "comparison": "strategy_minus_spy", "block_length": block, "annualized_mean_difference": float(excess.mean() * 252), "confidence_lower": lower, "confidence_upper": upper})
                x = sm.add_constant(group["target_return"].to_numpy())
                model = sm.OLS(ledger["net_strategy_return"].to_numpy(), x).fit(cov_type="HAC", cov_kwds={"maxlags": 20})
                capm_rows.append({"config_id": config_id, "sizing_rule": rule, "daily_alpha": float(model.params[0]), "annualized_alpha": float(model.params[0] * 252), "alpha_hac_se_annualized": float(model.bse[0] * 252), "beta": float(model.params[1]), "beta_hac_se": float(model.bse[1]), "observations": len(group)})
    pd.DataFrame(metric_rows).to_csv(output / "sizing_and_risk_metrics.csv", index=False)
    pd.DataFrame(bootstrap_rows).to_csv(output / "paired_block_bootstrap.csv", index=False)
    pd.DataFrame(capm_rows).to_csv(output / "capm_hac_attribution.csv", index=False)
    atomic_parquet_dump(pd.concat(all_ledgers, ignore_index=True), output / "strategy_ledgers.parquet")
    atomic_json_dump({"schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(), "status": "complete", "identity": identity, "cash_return_convention": 0.0, "continuous_rule": "clip(max(forecast,0)/hurdle * min(target_vol/past_20d_vol,1),0,1)", "interpretation": "CAPM and event results are descriptive associations, not causal estimates."}, output / "manifest.json")
    print(json.dumps({"status": "complete", "output_directory": str(output), "configurations": data["config_id"].nunique()}, indent=2))


if __name__ == "__main__":
    main()

