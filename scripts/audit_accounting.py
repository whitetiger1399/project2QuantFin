"""Independently audit the canonical model run's trade accounting."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = "models_final_test_53e047b58e92e27b"
DEFAULT_FREEZE = "freeze_f98a78b584d0ca42"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def atomic_csv_dump(frame: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    os.close(fd)
    try:
        frame.to_csv(temporary, index=False)
        os.replace(temporary, destination)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def drawdown_with_initial_capital(returns: pd.Series) -> tuple[pd.Series, float]:
    values = returns.fillna(0.0).to_numpy(dtype=float)
    wealth = np.concatenate(([1.0], np.cumprod(1.0 + values)))
    peaks = np.maximum.accumulate(wealth)
    drawdowns = wealth / peaks - 1.0
    result = pd.Series(drawdowns[1:], index=returns.index, dtype=float)
    return result, float(drawdowns.min())


def corrected_ledger(
    predictions: pd.DataFrame, forecast_hurdle: float, one_way_cost_bps: float
) -> pd.DataFrame:
    frame = predictions.sort_values(["signal_session", "config_id"]).copy()
    if frame["config_id"].nunique() != 1:
        raise ValueError("corrected_ledger requires one configuration")
    frame["position"] = frame["prediction"].gt(forecast_hurdle).astype(float)
    frame["turnover"] = frame["position"].diff().abs()
    if not frame.empty:
        frame.loc[frame.index[0], "turnover"] = frame.loc[frame.index[0], "position"]
        frame.loc[frame.index[-1], "turnover"] += frame.loc[frame.index[-1], "position"]
    cost_rate = one_way_cost_bps / 10_000.0
    frame["trading_cost"] = frame["turnover"] * cost_rate
    frame["gross_strategy_return"] = frame["position"] * frame["target_return"]
    frame["net_strategy_return"] = frame["gross_strategy_return"] - frame["trading_cost"]
    frame["strategy_wealth"] = (1.0 + frame["net_strategy_return"]).cumprod()
    frame["benchmark_wealth"] = (1.0 + frame["target_return"]).cumprod()
    frame["strategy_drawdown"], _ = drawdown_with_initial_capital(frame["net_strategy_return"])
    frame["benchmark_drawdown"], _ = drawdown_with_initial_capital(frame["target_return"])
    frame["trade_entry_session"] = pd.to_datetime(frame["entry_session"])
    frame["pnl_session"] = pd.to_datetime(frame["label_end_session"])
    frame["signal_year"] = pd.to_datetime(frame["signal_session"]).dt.year
    frame["pnl_year"] = frame["pnl_session"].dt.year
    return frame


def annualized(returns: pd.Series, periods: int = 252) -> dict[str, float]:
    clean = returns.dropna().astype(float)
    mean = float(clean.mean() * periods)
    volatility = float(clean.std(ddof=1) * np.sqrt(periods))
    terminal = float((1.0 + clean).prod())
    years = len(clean) / periods
    _, maximum_drawdown = drawdown_with_initial_capital(clean)
    return {
        "observations": int(len(clean)),
        "annualized_mean": mean,
        "annualized_volatility": volatility,
        "sharpe": mean / volatility if volatility > 0 else float("nan"),
        "cagr": terminal ** (1.0 / years) - 1.0 if years > 0 and terminal > 0 else float("nan"),
        "max_drawdown": maximum_drawdown,
    }


def fixture_results() -> list[dict[str, Any]]:
    first_loss = pd.Series([-0.10, 0.05])
    drawdown, maximum = drawdown_with_initial_capital(first_loss)
    cases = [
        {
            "name": "first_observation_loss_uses_initial_capital_peak",
            "pass": bool(np.isclose(drawdown.iloc[0], -0.10) and np.isclose(maximum, -0.10)),
            "observed": {"first_drawdown": float(drawdown.iloc[0]), "maximum_drawdown": maximum},
        }
    ]
    fixture = pd.DataFrame(
        {
            "signal_session": pd.to_datetime(["2020-12-30", "2020-12-31"]),
            "entry_session": pd.to_datetime(["2020-12-31", "2021-01-04"]),
            "label_end_session": pd.to_datetime(["2021-01-04", "2021-01-05"]),
            "prediction": [0.01, -0.01],
            "target_return": [0.02, -0.03],
            "config_id": ["fixture", "fixture"],
        }
    )
    ledger = corrected_ledger(fixture, forecast_hurdle=0.0, one_way_cost_bps=5.0)
    cases.append(
        {
            "name": "entry_exit_cost_and_pnl_year_boundary",
            "pass": bool(
                np.allclose(ledger["turnover"], [1.0, 1.0])
                and np.allclose(ledger["trading_cost"], [0.0005, 0.0005])
                and ledger["pnl_year"].tolist() == [2021, 2021]
            ),
            "observed": {
                "turnover": ledger["turnover"].tolist(),
                "trading_cost": ledger["trading_cost"].tolist(),
                "pnl_year": ledger["pnl_year"].tolist(),
            },
        }
    )
    return cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=DEFAULT_RUN)
    parser.add_argument("--freeze-id", default=DEFAULT_FREEZE)
    parser.add_argument("--forecast-hurdle", type=float)
    parser.add_argument("--one-way-cost-bps", type=float)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()

    run_dir = ROOT / "artifacts/runs" / args.run_id
    freeze_path = ROOT / "artifacts/freezes" / f"{args.freeze_id}.json"
    if args.plan_only:
        print(json.dumps({
            "action": "audit_accounting",
            "run": str(run_dir.relative_to(ROOT)),
            "freeze": str(freeze_path.relative_to(ROOT)),
            "canonical_run_is_read_only": True,
        }, indent=2))
        return

    freeze = read_json(freeze_path)
    run_manifest = read_json(run_dir / "run_manifest.json")
    config_id = freeze["selected_configurations"][0]["config_id"]
    hurdle = float(args.forecast_hurdle if args.forecast_hurdle is not None else freeze["forecast_hurdle"])
    costs = float(args.one_way_cost_bps if args.one_way_cost_bps is not None else freeze["one_way_cost_bps"])
    predictions = pd.read_parquet(run_dir / "predictions.parquet")
    selected = predictions.loc[predictions["config_id"].eq(config_id)].copy()
    if selected.empty:
        raise ValueError(f"No predictions found for frozen configuration {config_id}")
    ledger = corrected_ledger(selected, hurdle, costs)

    legacy_all = pd.read_parquet(run_dir / "strategy_ledgers.parquet")
    legacy = legacy_all.loc[legacy_all["config_id"].eq(config_id)].sort_values("signal_session")
    corrected = ledger.sort_values("signal_session")
    if len(legacy) != len(corrected):
        raise AssertionError("Legacy and corrected ledgers contain different row counts")
    comparisons = {}
    for column in ["position", "turnover", "trading_cost", "gross_strategy_return", "net_strategy_return", "strategy_drawdown", "benchmark_drawdown"]:
        difference = np.abs(legacy[column].to_numpy(float) - corrected[column].to_numpy(float))
        comparisons[column] = {
            "maximum_absolute_difference": float(np.nanmax(difference)),
            "different_rows_at_1e_12": int(np.sum(difference > 1e-12)),
        }

    annual = (
        ledger.assign(year=ledger["pnl_year"])
        .groupby("year", as_index=False)
        .agg(
            strategy=("net_strategy_return", lambda x: float((1.0 + x).prod() - 1.0)),
            benchmark=("target_return", lambda x: float((1.0 + x).prod() - 1.0)),
            observations=("target_return", "size"),
        )
    )
    fixtures = fixture_results()
    source_fingerprints = {
        "predictions_sha256": sha256_file(run_dir / "predictions.parquet"),
        "legacy_ledger_sha256": sha256_file(run_dir / "strategy_ledgers.parquet"),
        "freeze_sha256": sha256_file(freeze_path),
    }
    identity = {
        "run_id": args.run_id,
        "config_id": config_id,
        "forecast_hurdle": hurdle,
        "one_way_cost_bps": costs,
        **source_fingerprints,
    }
    audit_id = "accounting_" + stable_object_hash(identity)[:16]
    output = ROOT / "artifacts/research/accounting_audits" / audit_id
    report = {
        "schema_version": 1,
        "audit_id": audit_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass_with_findings" if all(case["pass"] for case in fixtures) else "fail",
        "source": identity,
        "source_run_status": run_manifest["status"],
        "accounting_contract": {
            "trade_entry_column": "entry_session",
            "pnl_date_column": "label_end_session",
            "drawdown_peak_includes_initial_wealth": True,
            "initial_and_final_turnover_charged": True,
        },
        "fixture_results": fixtures,
        "strategy_metrics_by_pnl_date": annualized(ledger["net_strategy_return"]),
        "benchmark_metrics_by_pnl_date": annualized(ledger["target_return"]),
        "year_boundary_rows": int((ledger["signal_year"] != ledger["pnl_year"]).sum()),
        "recorded_ledger_comparison": comparisons,
        "interpretation": "Differences are audit findings. The canonical run remains immutable; corrected outputs are stored only in this audit directory.",
    }
    atomic_parquet_dump(ledger, output / "corrected_strategy_ledger.parquet")
    atomic_csv_dump(annual, output / "annual_returns_by_pnl_session.csv")
    atomic_json_dump(report, output / "audit_report.json")
    print(output)


if __name__ == "__main__":
    main()

