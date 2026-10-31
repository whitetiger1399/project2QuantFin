#!/usr/bin/env python3
"""Augment an immutable AI-services panel with disclosed model-scale features."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from quantfin.cross_market.common import load_research_config, root_path
from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


def _source_dataset(config: dict[str, Any], dataset_id: str) -> Path:
    path = root_path(config["capability_data"]["source_processed_root"]) / dataset_id
    if not (path / "manifest.json").is_file():
        raise FileNotFoundError(path)
    return path


def _event_mapping(
    events: pd.DataFrame,
    catalog: dict[str, Any],
    dates: pd.DatetimeIndex,
) -> pd.DataFrame:
    cutoffs = pd.Series(
        dates.tz_localize("Asia/Kolkata") + pd.Timedelta(hours=8, minutes=55), index=dates
    ).dt.tz_convert("UTC")
    events = events.copy()
    events["public_at_utc"] = pd.to_datetime(events["public_at_utc"], utc=True, errors="raise")
    events["primary_event"] = events["primary_event"].astype(str).str.lower().isin({"true", "1", "yes"})
    events = events.sort_values(["public_at_utc", "event_id"]).reset_index(drop=True)
    events["provider_generation_index"] = events.groupby("provider").cumcount() + 1
    events["global_generation_index"] = np.arange(1, len(events) + 1)
    direct_dates: list[pd.Timestamp] = []
    post_us_dates: list[pd.Timestamp] = []
    for value in events["public_at_utc"]:
        eligible = cutoffs.index[cutoffs.gt(value)]
        direct = eligible[0] if len(eligible) else pd.NaT
        later = dates[dates > direct] if pd.notna(direct) else pd.DatetimeIndex([])
        direct_dates.append(direct)
        post_us_dates.append(later[0] if len(later) else pd.NaT)
    events["tradable_date"] = direct_dates
    events["post_us_reaction_date"] = post_us_dates
    records = catalog.get("records", {})
    events["total_parameters_b"] = events["event_id"].map(
        lambda value: records.get(value, {}).get("total_parameters_b")
    )
    events["active_parameters_b"] = events["event_id"].map(
        lambda value: records.get(value, {}).get("active_parameters_b")
    )
    events["parameter_architecture"] = events["event_id"].map(
        lambda value: records.get(value, {}).get("architecture", "undisclosed")
    )
    events["parameter_source_url"] = events["event_id"].map(
        lambda value: records.get(value, {}).get("source_url", "")
    )
    events["parameter_disclosed"] = events["total_parameters_b"].notna()
    events["log1p_total_parameters_b"] = np.log1p(events["total_parameters_b"])
    events["log1p_active_parameters_b"] = np.log1p(events["active_parameters_b"])
    events["provider_parameter_log_change"] = np.nan
    for _, indices in events.groupby("provider").groups.items():
        prior: float | None = None
        for index in indices:
            value = events.at[index, "total_parameters_b"]
            if pd.notna(value):
                current = float(np.log1p(value))
                events.at[index, "provider_parameter_log_change"] = current - prior if prior is not None else np.nan
                prior = current
    return events


def _daily_features(mapping: pd.DataFrame, dates: pd.DatetimeIndex, half_lives: list[int]) -> pd.DataFrame:
    result = pd.DataFrame(index=dates)
    pulse_columns = [
        "release_count_today", "primary_release_count_today", "parameter_disclosed_count_today",
        "total_parameters_b_today", "active_parameters_b_today", "log1p_total_parameters_b_today",
        "log1p_active_parameters_b_today", "provider_generation_index_today",
        "global_generation_index_today", "provider_parameter_log_change_today",
    ]
    for column in pulse_columns:
        result[f"ai_capability__{column}"] = 0.0
    for row in progress(mapping.dropna(subset=["tradable_date"]).itertuples(index=False),
                        description="Mapping disclosed model scale", total=int(mapping["tradable_date"].notna().sum()), unit="event"):
        date = pd.Timestamp(row.tradable_date)
        result.loc[date, "ai_capability__release_count_today"] += 1.0
        result.loc[date, "ai_capability__primary_release_count_today"] += float(bool(row.primary_event))
        result.loc[date, "ai_capability__parameter_disclosed_count_today"] += float(bool(row.parameter_disclosed))
        values = {
            "total_parameters_b_today": row.total_parameters_b,
            "active_parameters_b_today": row.active_parameters_b,
            "log1p_total_parameters_b_today": row.log1p_total_parameters_b,
            "log1p_active_parameters_b_today": row.log1p_active_parameters_b,
            "provider_generation_index_today": row.provider_generation_index,
            "global_generation_index_today": row.global_generation_index,
            "provider_parameter_log_change_today": row.provider_parameter_log_change,
        }
        for name, value in values.items():
            if pd.notna(value):
                column = f"ai_capability__{name}"
                if name == "provider_parameter_log_change_today":
                    result.loc[date, column] += float(value)
                else:
                    result.loc[date, column] = max(result.loc[date, column], float(value))
    disclosed = result["ai_capability__parameter_disclosed_count_today"].gt(0)
    total_today = result["ai_capability__total_parameters_b_today"].where(disclosed)
    result["ai_capability__latest_disclosed_total_parameters_b"] = total_today.ffill()
    result["ai_capability__expanding_max_total_parameters_b"] = total_today.cummax().ffill()
    result["ai_capability__cumulative_parameter_disclosures"] = disclosed.astype(float).cumsum()
    disclosed_dates = result.index[disclosed]
    for date in dates:
        previous = disclosed_dates[disclosed_dates <= date]
        result.loc[date, "ai_capability__days_since_parameter_disclosure"] = (
            (date - previous[-1]).days if len(previous) else np.nan
        )
    for half_life in half_lives:
        for source, label in [
            ("ai_capability__release_count_today", "release_pressure"),
            ("ai_capability__log1p_total_parameters_b_today", "parameter_pressure"),
            ("ai_capability__provider_generation_index_today", "generation_pressure"),
        ]:
            result[f"ai_capability__{label}_{half_life}"] = result[source].ewm(
                halflife=half_life, adjust=False
            ).mean()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_ai_capability_research.yaml")
    parser.add_argument("--source-dataset-id", required=True)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    source = _source_dataset(config, args.source_dataset_id)
    source_manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    catalog_path = root_path(config["capability_data"]["parameter_catalog"])
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    event_snapshot_id = source_manifest["snapshot_manifests"]["frontier_ai_events"]["snapshot_id"]
    event_snapshot = root_path(config["raw_data"]["frontier_ai_events_root"]) / event_snapshot_id
    events_path = event_snapshot / "frontier_ai_releases.csv"
    content_hash = stable_object_hash({
        "source_manifest": sha256_file(source / "manifest.json"),
        "parameter_catalog": sha256_file(catalog_path),
        "events": sha256_file(events_path),
        "config": config,
        "script": sha256_file(Path(__file__)),
    })[:16]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dataset_id = f"{config['tracking']['dataset_prefix']}_{stamp}_{content_hash}"
    output = root_path(config["outputs"]["processed_root"]) / dataset_id
    plan = {"action": "build_ai_capability_panel", "dataset_id": dataset_id,
            "content_hash": content_hash, "source_dataset_id": source.name,
            "event_snapshot_id": event_snapshot_id, "output": str(output)}
    if args.plan_only:
        print(json.dumps(plan, indent=2)); return
    output.mkdir(parents=True, exist_ok=False)
    panel = pd.read_parquet(source / "panel.parquet")
    dictionary = pd.read_csv(source / "feature_dictionary.csv")
    dates = pd.DatetimeIndex(sorted(pd.to_datetime(panel["decision_date"]).unique()))
    mapping = _event_mapping(pd.read_csv(events_path), catalog, dates)
    features = _daily_features(mapping, dates, list(config["capability_data"]["pressure_half_lives_sessions"]))
    service = panel.drop_duplicates("decision_date").set_index("decision_date")["us_it_services_aggregate__mean"]
    features["ai_capability_interaction__parameter_pressure_63_x_us_services"] = (
        features["ai_capability__parameter_pressure_63"] * service.reindex(features.index)
    )
    features["ai_capability_interaction__generation_pressure_63_x_us_services"] = (
        features["ai_capability__generation_pressure_63"] * service.reindex(features.index)
    )
    panel = panel.merge(features.reset_index(names="decision_date"), on="decision_date", how="left", validate="many_to_one")
    new_rows = []
    for column in features:
        family = column.split("__", 1)[0]
        sets = [name for name, families in config["feature_sets"].items() if family in families]
        new_rows.append({"feature": column, "family": family, "feature_sets": "|".join(sets),
                         "known_at_0855_ist": True,
                         "alignment": "first NSE 08:55 cutoff after official release; state carried forward",
                         "current_vintage_fallback": False})
    dictionary = pd.concat([dictionary, pd.DataFrame(new_rows)], ignore_index=True)
    # The source panel was built under the AI-services ladder, whose sixth rung
    # was named F6_ai_events. Rebuild every membership from the capability
    # configuration so F6_ai_capability is cumulative rather than containing
    # only the newly appended columns.
    dictionary["feature_sets"] = dictionary["family"].map(
        lambda family: "|".join(
            name for name, families in config["feature_sets"].items() if family in families
        )
    )
    dictionary = dictionary.sort_values(["family", "feature"]).reset_index(drop=True)
    unassigned = dictionary.loc[dictionary["feature_sets"].eq(""), ["feature", "family"]]
    if not unassigned.empty:
        raise ValueError(
            "Capability feature dictionary contains unassigned families: "
            f"{sorted(unassigned['family'].unique().tolist())}"
        )
    atomic_parquet_dump(panel, output / "panel.parquet")
    dictionary.to_csv(output / "feature_dictionary.csv", index=False)
    mapping.to_csv(output / "capability_event_mapping.csv", index=False)
    evidence = {
        "source_dataset_id": source.name, "events": len(mapping),
        "events_with_disclosed_total_parameters": int(mapping["parameter_disclosed"].sum()),
        "disclosure_fraction": float(mapping["parameter_disclosed"].mean()),
        "capability_features": len(features.columns),
        "guardrail": "Parameter count is a sparse scale proxy; undisclosed values are not imputed.",
    }
    atomic_json_dump(evidence, output / "capability_evidence.json")
    files = ["panel.parquet", "feature_dictionary.csv", "capability_event_mapping.csv", "capability_evidence.json"]
    manifest = {"schema_version": 1, **plan, "status": "complete", "source_hash": content_hash,
                "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                "files": {name: sha256_file(output / name) for name in files},
                "evidence_summary": evidence,
                "source_dataset_manifest_sha256": sha256_file(source / "manifest.json"),
                "config_sha256": sha256_file(root_path(args.config)),
                "snapshot_manifests": source_manifest.get("snapshot_manifests", {})}
    atomic_json_dump(manifest, output / "manifest.json")
    print(json.dumps({"dataset_id": dataset_id, "status": "complete", "directory": str(output), **evidence}, indent=2))


if __name__ == "__main__":
    main()
