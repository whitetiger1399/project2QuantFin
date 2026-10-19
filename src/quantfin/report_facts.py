"""Resolve report facts by immutable identifiers rather than table row order."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


V1_PATHS = {
    "screening": "artifacts/runs/models_screening_8d1f4f8a10e794eb",
    "confirmation": "artifacts/runs/models_confirmation_5d6ed2ce5fa7b6cb",
    "final_test": "artifacts/runs/models_final_test_53e047b58e92e27b",
    "freeze": "artifacts/freezes/freeze_f98a78b584d0ca42.json",
}


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _unique_metric(directory: Path, config_id: str) -> dict[str, Any]:
    metrics = pd.read_csv(directory / "config_metrics.csv")
    match = metrics.loc[metrics["config_id"].eq(config_id)]
    if len(match) != 1:
        raise ValueError(
            f"Expected exactly one metrics row for {config_id} in {directory}; found {len(match)}"
        )
    record = match.iloc[0].to_dict()
    return {
        key: value.item() if isinstance(value, np.generic) else value
        for key, value in record.items()
    }


def load_v1_report_facts(root: Path) -> dict[str, Any]:
    """Load the exact selected configurations and metrics used by the v1 report."""
    root = root.resolve()
    runs = {name: root / relative for name, relative in V1_PATHS.items() if name != "freeze"}
    screening_selection = _read_json(runs["screening"] / "selection.json")
    confirmation_selection = _read_json(runs["confirmation"] / "selection.json")
    freeze = _read_json(root / V1_PATHS["freeze"])

    screening_by_family = {
        item["family"]: item["config_id"]
        for item in screening_selection["selected_configurations"]
    }
    final_config_id = freeze["selected_configurations"][0]["config_id"]
    confirmation_config_id = confirmation_selection["selected_configurations"][0]["config_id"]
    if final_config_id != confirmation_config_id:
        raise ValueError("The frozen final configuration does not match confirmation selection")

    final_metrics = pd.read_csv(runs["final_test"] / "config_metrics.csv")
    ar_ids = final_metrics.loc[final_metrics["family"].eq("autoregression"), "config_id"].tolist()
    if len(ar_ids) != 1:
        raise ValueError(f"Expected one final autoregression row; found {len(ar_ids)}")

    final_ledger = pd.read_parquet(runs["final_test"] / "strategy_ledgers.parquet")
    benchmark = final_ledger.loc[final_ledger["config_id"].eq(final_config_id), "target_return"].dropna()
    benchmark_volatility = float(benchmark.std(ddof=1) * np.sqrt(252))
    protocol = yaml.safe_load((root / "configs/protocol.yaml").read_text(encoding="utf-8"))

    return {
        "schema_version": 1,
        "screening_random_forest": _unique_metric(
            runs["screening"], screening_by_family["random_forest"]
        ),
        "screening_elastic_net": _unique_metric(
            runs["screening"], screening_by_family["elastic_net"]
        ),
        "confirmation_random_forest": _unique_metric(
            runs["confirmation"], confirmation_config_id
        ),
        "final_random_forest": _unique_metric(runs["final_test"], final_config_id),
        "final_autoregression": _unique_metric(runs["final_test"], ar_ids[0]),
        "benchmark_annualized_volatility": benchmark_volatility,
        "protocol_splits": protocol["splits"],
        "selected_ids": {
            "screening_random_forest": screening_by_family["random_forest"],
            "screening_elastic_net": screening_by_family["elastic_net"],
            "confirmation_random_forest": confirmation_config_id,
            "final_random_forest": final_config_id,
            "final_autoregression": ar_ids[0],
        },
    }

