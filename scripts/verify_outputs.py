"""Verify canonical Project 2 research artifacts before report generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

from quantfin.io import atomic_json_dump
from quantfin.report_facts import load_v1_report_facts


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
RUNS = {
    "screening": ROOT / "artifacts/runs/models_screening_8d1f4f8a10e794eb",
    "confirmation": ROOT / "artifacts/runs/models_confirmation_5d6ed2ce5fa7b6cb",
    "final_test": ROOT / "artifacts/runs/models_final_test_53e047b58e92e27b",
}
FEATURES = ROOT / "data/processed/features_yahoo_20261019T010846Z_799f619a4f"
MARKET = ROOT / "data/processed/market_yahoo_20261019T010846Z"
FREEZE = ROOT / "artifacts/freezes/freeze_f98a78b584d0ca42.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def check(condition: bool, message: str, checks: list[dict]) -> None:
    checks.append({"check": message, "status": "pass" if condition else "fail"})
    if not condition:
        raise AssertionError(message)


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    checks: list[dict] = []
    feature_manifest = read_json(FEATURES / "manifest.json")
    market_manifest = read_json(MARKET / "manifest.json")
    freeze = read_json(FREEZE)
    protocol = yaml.safe_load((ROOT / "configs/protocol.yaml").read_text())
    models = yaml.safe_load((ROOT / "configs/models.yaml").read_text())
    report_facts = load_v1_report_facts(ROOT)

    check(feature_manifest["source_market_dataset_id"] == market_manifest["dataset_id"], "feature lineage matches market dataset", checks)
    feature_path = FEATURES / feature_manifest["file"]["path"]
    check(digest(feature_path) == feature_manifest["file"]["sha256"], "feature parquet hash matches manifest", checks)
    check(feature_manifest["feature_counts"]["F2"] == 99, "F2 contains 99 declared features", checks)
    check(feature_manifest["rows"] == 5283 and feature_manifest["rows_with_mature_labels"] == 5281, "feature row counts match timing audit", checks)

    timing = read_json(ROOT / "artifacts/timing_audits/features_yahoo_20261019T010846Z_799f619a4f/timing_report.json")
    check(timing["status"] == "pass" and not timing["blocking_issues"], "timing audit passed without blockers", checks)
    quality = read_json(ROOT / "artifacts/data_audits/yahoo_20261019T010846Z/quality_report.json")
    check(not quality["blocking_issues"], "raw-data quality audit has no blocking issues", checks)

    run_summaries = {}
    for stage, directory in RUNS.items():
        manifest = read_json(directory / "run_manifest.json")
        metrics = pd.read_csv(directory / "config_metrics.csv")
        predictions = pd.read_parquet(directory / "predictions.parquet")
        ledgers = pd.read_parquet(directory / "strategy_ledgers.parquet")
        check(manifest["status"] == "complete", f"{stage} run is complete", checks)
        check(manifest["outputs"]["completed_fits"] == manifest["total_planned_fits"], f"{stage} completed all planned fits", checks)
        check(digest(directory / "predictions.parquet") == manifest["outputs"]["predictions_sha256"], f"{stage} predictions hash matches", checks)
        checkpoints = [p for p in directory.glob("checkpoints/*/*.parquet") if not p.stem.endswith("_features")]
        check(len(checkpoints) == manifest["total_planned_fits"], f"{stage} checkpoint count matches plan", checks)
        check(not predictions.duplicated(["config_id", "signal_session"]).any(), f"{stage} predictions are unique by model and session", checks)
        check(predictions["prediction"].notna().all(), f"{stage} predictions contain no missing values", checks)
        check((pd.to_datetime(predictions["train_last_label_available"]) <= pd.to_datetime(predictions["refit_origin"])).all(), f"{stage} fit cutoffs use only available labels", checks)
        check(len(ledgers) == len(predictions), f"{stage} ledger covers every prediction", checks)
        accounting_error = (ledgers["gross_strategy_return"] - ledgers["trading_cost"] - ledgers["net_strategy_return"]).abs().max()
        check(float(accounting_error) < 1e-12, f"{stage} net-return accounting reconciles", checks)
        run_summaries[stage] = {
            "run_id": manifest["run_id"],
            "configurations": int(manifest["configuration_count"]),
            "fits": int(manifest["total_planned_fits"]),
            "observations_per_configuration": int(metrics["observations"].iloc[0]),
            "prediction_rows": len(predictions),
        }

    confirmation_selection = read_json(RUNS["confirmation"] / "selection.json")
    final_manifest = read_json(RUNS["final_test"] / "run_manifest.json")
    check(freeze["status"] == "frozen", "final protocol is frozen", checks)
    check(freeze["selection_sha256"] == digest(RUNS["confirmation"] / "selection.json"), "freeze binds confirmation selection", checks)
    check(final_manifest["inputs"]["freeze_id"] == freeze["freeze_id"], "final run uses declared freeze", checks)
    check(final_manifest["inputs"]["feature_dataset_id"] == feature_manifest["dataset_id"], "final run uses verified feature dataset", checks)
    check(final_manifest["inputs"]["configurations"][0] == confirmation_selection["selected_configurations"][0], "final champion matches confirmation selection", checks)
    check(protocol["splits"]["final_test"] == freeze["final_test_bounds"], "freeze final dates match protocol", checks)
    check(float(models["research"]["one_way_cost_bps"]) == float(freeze["one_way_cost_bps"]), "final costs match model configuration", checks)
    check(protocol["splits"]["warmup"]["end"] == "2005-12-31", "2005 is identified as warm-up", checks)
    check(protocol["splits"]["initial_train"]["start"] == "2006-01-01", "initial model training begins in 2006", checks)

    screening_selection = read_json(RUNS["screening"] / "selection.json")
    selected_screen_ids = {item["family"]: item["config_id"] for item in screening_selection["selected_configurations"]}
    check(report_facts["selected_ids"]["screening_random_forest"] == selected_screen_ids["random_forest"], "report resolves selected screening forest by config ID", checks)
    check(report_facts["selected_ids"]["screening_elastic_net"] == selected_screen_ids["elastic_net"], "report resolves selected screening elastic net by config ID", checks)
    check(report_facts["selected_ids"]["final_random_forest"] == confirmation_selection["selected_configurations"][0]["config_id"], "report final forest matches confirmation selection", checks)

    final_metrics = pd.read_csv(RUNS["final_test"] / "config_metrics.csv")
    champion = final_metrics.loc[final_metrics["family"].eq("random_forest")].iloc[0]
    check(champion["prediction_coverage"] == 1.0, "final champion has complete prediction coverage", checks)

    result = {
        "status": "pass",
        "checks_passed": len(checks),
        "checks": checks,
        "run_summaries": run_summaries,
        "canonical_ids": {
            "feature_dataset": feature_manifest["dataset_id"],
            "freeze": freeze["freeze_id"],
            "final_run": final_manifest["run_id"],
        },
        "final_champion": {
            "config_id": champion["config_id"],
            "annualized_net_return": float(champion["annualized_net_return"]),
            "annualized_net_volatility": float(champion["annualized_net_volatility"]),
            "net_sharpe": float(champion["net_sharpe"]),
            "net_cagr": float(champion["net_cagr"]),
            "max_drawdown": float(champion["max_drawdown"]),
            "average_exposure": float(champion["average_exposure"]),
            "annualized_turnover": float(champion["annualized_turnover"]),
            "oos_r2_vs_historical_mean": float(champion["oos_r2_vs_historical_mean"]),
            "benchmark_return": float(champion["annualized_benchmark_return"]),
            "benchmark_sharpe": float(champion["benchmark_sharpe"]),
        },
        "report_facts": report_facts,
    }
    atomic_json_dump(result, REPORTS / "output_verification.json")
    atomic_json_dump(report_facts, REPORTS / "report_facts.json")
    pd.DataFrame(checks).to_csv(REPORTS / "output_verification.csv", index=False)
    print(json.dumps({"status": result["status"], "checks_passed": len(checks), "final_run": final_manifest["run_id"]}, indent=2))


if __name__ == "__main__":
    main()
