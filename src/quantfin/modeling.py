"""Resumable monthly-refit walk-forward model execution."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from threadpoolctl import threadpool_limits

from quantfin.evaluation import evaluate_predictions
from quantfin.freeze import validate_freeze
from quantfin.io import (
    atomic_json_dump,
    atomic_parquet_dump,
    read_manifest,
    sha256_file,
    stable_object_hash,
    utc_now,
)
from quantfin.models import (
    build_estimator,
    enumerate_model_configs,
    extract_feature_diagnostics,
    model_complexity,
)
from quantfin.progress import progress
from quantfin.tracking import RunTracker


def _source_hashes(project_root: Path) -> dict[str, str]:
    sources = sorted((project_root / "src" / "quantfin").rglob("*.py"))
    return {str(path.relative_to(project_root)): sha256_file(path) for path in sources}


def _load_feature_dataset(feature_dataset: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    manifest = read_manifest(feature_dataset / "manifest.json")
    path = feature_dataset / manifest["file"]["path"]
    if sha256_file(path) != manifest["file"]["sha256"]:
        raise ValueError(f"Feature dataset hash mismatch: {path}")
    frame = pd.read_parquet(path)
    for column in ["signal_session", "entry_session", "label_end_session", "label_available_session"]:
        frame[column] = pd.to_datetime(frame[column])
    return frame.sort_values("signal_session").reset_index(drop=True), manifest


def _monthly_blocks(evaluation: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.DataFrame]]:
    blocks = []
    for _, block in evaluation.groupby(evaluation["signal_session"].dt.to_period("M"), sort=True):
        blocks.append((block["signal_session"].min(), block.copy()))
    return blocks


def _load_selection(
    path: Path,
    *,
    expected_source_stage: str | None = None,
    feature_dataset_id: str | None = None,
    feature_set: str | None = None,
    window_observations: int | None = None,
) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    configurations = value.get("selected_configurations")
    if not isinstance(configurations, list) or not configurations:
        raise ValueError(f"Selection contains no configurations: {path}")
    context = value.get("source_context", {})
    expected = {
        "stage": expected_source_stage,
        "feature_dataset_id": feature_dataset_id,
        "feature_set": feature_set,
        "window_observations": window_observations,
    }
    mismatches = [
        key for key, expected_value in expected.items()
        if expected_value is not None and context.get(key) != expected_value
    ]
    # None is meaningful for an expanding window, so check it separately.
    if window_observations is None and context.get("window_observations", "missing") is not None:
        mismatches.append("window_observations")
    if mismatches:
        raise ValueError(f"Selection lineage mismatch for {sorted(set(mismatches))}: {path}")
    return configurations


def _load_checkpoint(path: Path) -> pd.DataFrame | None:
    """Return a verified checkpoint, or None when a partial checkpoint must be rebuilt."""
    metadata_path = path.with_suffix(".json")
    if not path.exists() and not metadata_path.exists():
        return None
    if not path.exists() or not metadata_path.exists():
        return None
    metadata = read_manifest(metadata_path)
    if metadata.get("checkpoint_sha256") != sha256_file(path):
        return None
    return pd.read_parquet(path)


def _add_baselines(configurations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    existing = {item["family"] for item in configurations}
    result = list(configurations)
    for family in ["historical_mean", "autoregression"]:
        if family not in existing:
            payload = {"family": family, "parameters": {}}
            result.append({**payload, "config_id": f"{family}_{stable_object_hash(payload)[:10]}"})
    return result


def walk_forward_plan(
    *,
    feature_dataset: Path,
    protocol: dict[str, Any],
    model_config: dict[str, Any],
    feature_set_override: str | None,
    profile: str,
    stage: str,
    selection_path: Path | None,
    window_observations: int | None,
) -> dict[str, Any]:
    """Describe the requested computation without fitting or writing artifacts."""
    if stage not in {"screening", "confirmation", "final_test"}:
        raise ValueError(f"Unsupported walk-forward stage: {stage}")
    if stage != "screening" and selection_path is None:
        raise ValueError(f"{stage} requires --selection from the preceding completed stage")
    frame, feature_manifest = _load_feature_dataset(feature_dataset)
    feature_set = feature_set_override or model_config["research"]["feature_set"]
    if feature_set not in feature_manifest["feature_sets"]:
        raise ValueError(f"Unknown feature set {feature_set!r}")
    configurations = (
        _add_baselines(
            _load_selection(
                selection_path,
                expected_source_stage="screening" if stage == "confirmation" else "confirmation",
                feature_dataset_id=feature_manifest["dataset_id"],
                feature_set=feature_set,
                window_observations=window_observations,
            )
        )
        if selection_path
        else enumerate_model_configs(model_config, profile)
    )
    bounds = protocol["splits"][stage]
    evaluation = frame.loc[
        frame["signal_session"].between(
            pd.Timestamp(bounds["start"]), pd.Timestamp(bounds["end"]), inclusive="both"
        )
        & frame["target_return"].notna()
    ]
    blocks = _monthly_blocks(evaluation)
    families = pd.Series([item["family"] for item in configurations]).value_counts().to_dict()
    return {
        "stage": stage,
        "profile": profile,
        "feature_set": feature_set,
        "training_window": "expanding" if window_observations is None else window_observations,
        "input_features": len(feature_manifest["feature_sets"][feature_set]),
        "evaluation_rows": len(evaluation),
        "monthly_refits_per_configuration": len(blocks),
        "configuration_count": len(configurations),
        "total_planned_fits": len(configurations) * len(blocks),
        "configurations_by_family": families,
        "first_refit": blocks[0][0].date().isoformat() if blocks else None,
        "last_refit": blocks[-1][0].date().isoformat() if blocks else None,
    }


def run_walk_forward(
    *,
    feature_dataset: Path,
    protocol: dict[str, Any],
    model_config: dict[str, Any],
    feature_set_override: str | None,
    profile: str,
    stage: str,
    window_observations: int | None,
    selection_path: Path | None,
    freeze_path: Path | None,
    artifacts_root: Path,
    project_root: Path,
    resume: bool,
) -> RunTracker:
    if stage not in {"screening", "confirmation", "final_test"}:
        raise ValueError(f"Unsupported walk-forward stage: {stage}")
    if stage != "screening" and selection_path is None:
        raise ValueError(f"{stage} requires --selection from the preceding completed stage")
    if stage == "final_test" and freeze_path is None:
        raise ValueError("final_test requires --freeze created after confirmation selection")

    frame, feature_manifest = _load_feature_dataset(feature_dataset)
    feature_set = feature_set_override or model_config["research"]["feature_set"]
    if feature_set not in feature_manifest["feature_sets"]:
        raise ValueError(f"Unknown feature set {feature_set!r}")
    feature_columns = feature_manifest["feature_sets"][feature_set]
    freeze = None
    if stage == "final_test":
        freeze = validate_freeze(
            freeze_path,
            selection_path=selection_path,
            feature_manifest=feature_manifest,
            feature_manifest_path=feature_dataset / "manifest.json",
            protocol=protocol,
            model_config=model_config,
            feature_set=feature_set,
            window_observations=window_observations,
        )
    if selection_path:
        configurations = _add_baselines(
            _load_selection(
                selection_path,
                expected_source_stage="screening" if stage == "confirmation" else "confirmation",
                feature_dataset_id=feature_manifest["dataset_id"],
                feature_set=feature_set,
                window_observations=window_observations,
            )
        )
        selection_hash = sha256_file(selection_path)
    else:
        configurations = enumerate_model_configs(model_config, profile)
        selection_hash = None

    split_bounds = protocol["splits"][stage]
    evaluation = frame.loc[
        frame["signal_session"].between(
            pd.Timestamp(split_bounds["start"]), pd.Timestamp(split_bounds["end"]), inclusive="both"
        )
        & frame["target_return"].notna()
    ].copy()
    if evaluation.empty:
        raise ValueError(f"No mature evaluation rows for stage {stage}")
    blocks = _monthly_blocks(evaluation)
    research = model_config["research"]
    compute = model_config["compute"]
    inputs = {
        "feature_dataset_id": feature_manifest["dataset_id"],
        "feature_manifest_sha256": sha256_file(feature_dataset / "manifest.json"),
        "feature_set": feature_set,
        "profile": profile,
        "stage": stage,
        "window_observations": window_observations,
        "selection_sha256": selection_hash,
        "freeze_sha256": sha256_file(freeze_path) if freeze_path else None,
        "freeze_id": freeze.get("freeze_id") if freeze else None,
        "configurations": configurations,
        "research": research,
        "protocol_sha256": stable_object_hash(protocol),
        "model_config_sha256": stable_object_hash(model_config),
        "source_hashes": _source_hashes(project_root),
    }
    tracker = RunTracker.create_or_resume(
        artifacts_root=artifacts_root,
        project_root=project_root,
        command=f"models_{stage}",
        inputs=inputs,
        resume=resume,
    )
    tracker.update(
        status="running",
        configuration_count=len(configurations),
        refit_count_per_configuration=len(blocks),
        total_planned_fits=len(configurations) * len(blocks),
    )
    atomic_json_dump(
        {item["config_id"]: item for item in configurations},
        tracker.directory / "configurations.json",
    )

    all_predictions: list[pd.DataFrame] = []
    jobs = [(configuration, origin, block) for configuration in configurations for origin, block in blocks]
    try:
        for configuration, origin, block in progress(
            jobs,
            description=f"Walk-forward {stage}",
            total=len(jobs),
            unit="fit",
        ):
            config_id = configuration["config_id"]
            checkpoint_dir = tracker.directory / "checkpoints" / config_id
            checkpoint_path = checkpoint_dir / f"{origin.date().isoformat()}.parquet"
            saved_checkpoint = _load_checkpoint(checkpoint_path)
            if saved_checkpoint is not None:
                all_predictions.append(saved_checkpoint)
                continue

            eligible = frame.loc[
                frame["target_return"].notna()
                & frame["label_available_session"].le(origin)
                & frame["signal_session"].ge(pd.Timestamp(protocol["splits"]["initial_train"]["start"]))
            ].copy()
            if window_observations is not None:
                eligible = eligible.tail(window_observations)
            if len(eligible) < 60:
                raise ValueError(
                    f"Only {len(eligible)} eligible training rows at {origin.date()} for {config_id}"
                )

            estimator, feature_override = build_estimator(
                configuration,
                random_seed=int(research["random_seed"]),
                n_jobs=int(compute["n_jobs"]),
                input_feature_count=len(feature_columns),
            )
            used_features = feature_override or feature_columns
            X_train = eligible[used_features]
            y_train = eligible["target_return"].astype(float)
            X_evaluation = block[used_features]
            started = time.perf_counter()
            with threadpool_limits(limits=int(compute["numerical_threads_per_worker"])):
                estimator.fit(X_train, y_train)
                prediction = estimator.predict(X_evaluation)
                training_prediction = estimator.predict(X_train)
            fit_seconds = time.perf_counter() - started
            complexity = model_complexity(estimator, configuration, len(used_features))
            checkpoint = block[
                [
                    "signal_session",
                    "entry_session",
                    "label_end_session",
                    "label_available_session",
                    "target_return",
                    "split",
                ]
            ].copy()
            checkpoint["prediction"] = prediction
            checkpoint["config_id"] = config_id
            checkpoint["family"] = configuration["family"]
            checkpoint["refit_origin"] = origin
            checkpoint["n_train"] = len(eligible)
            checkpoint["n_input_features"] = len(used_features)
            checkpoint["train_start"] = eligible["signal_session"].min()
            checkpoint["train_last_signal"] = eligible["signal_session"].max()
            checkpoint["train_last_label_available"] = eligible["label_available_session"].max()
            checkpoint["train_mse"] = mean_squared_error(y_train, training_prediction)
            checkpoint["fit_seconds"] = fit_seconds
            checkpoint["trainable_parameters"] = complexity.get("trainable_parameters")
            checkpoint["approximation_features"] = complexity.get(
                "approximation_features", complexity.get("trainable_parameters")
            )
            checkpoint["parameter_to_observation_ratio"] = (
                checkpoint["trainable_parameters"] / checkpoint["n_train"]
            )
            atomic_parquet_dump(checkpoint.reset_index(drop=True), checkpoint_path)
            atomic_json_dump(
                {
                    "config_id": config_id,
                    "configuration": configuration,
                    "refit_origin": origin.isoformat(),
                    "fit_seconds": fit_seconds,
                    "n_train": len(eligible),
                    "features": used_features,
                    "complexity": complexity,
                    "checkpoint_sha256": sha256_file(checkpoint_path),
                },
                checkpoint_path.with_suffix(".json"),
            )
            diagnostics = extract_feature_diagnostics(estimator, configuration, used_features)
            if diagnostics:
                diagnostics_frame = pd.DataFrame(diagnostics)
                diagnostics_frame["config_id"] = config_id
                diagnostics_frame["refit_origin"] = origin
                atomic_parquet_dump(
                    diagnostics_frame,
                    checkpoint_path.with_name(f"{checkpoint_path.stem}_features.parquet"),
                )
            all_predictions.append(checkpoint)

        predictions = pd.concat(all_predictions, ignore_index=True).sort_values(
            ["config_id", "signal_session"]
        )
        prediction_path = tracker.directory / "predictions.parquet"
        atomic_parquet_dump(predictions, prediction_path)
        configuration_map = {item["config_id"]: item for item in configurations}
        metrics, ledgers = evaluate_predictions(
            predictions,
            configuration_map,
            forecast_hurdle=float(research["forecast_hurdle"]),
            one_way_cost_bps=float(research["one_way_cost_bps"]),
            annualization=int(research["annualization_sessions"]),
        )
        metrics_path = tracker.directory / "config_metrics.csv"
        metrics.to_csv(metrics_path, index=False)
        ledger_path = tracker.directory / "strategy_ledgers.parquet"
        atomic_parquet_dump(ledgers, ledger_path)
        tracker.complete(
            predictions=str(prediction_path),
            predictions_sha256=sha256_file(prediction_path),
            metrics=str(metrics_path),
            ledgers=str(ledger_path),
            completed_fits=len(jobs),
        )
        return tracker
    except BaseException as exc:
        tracker.fail(exc)
        raise


def select_models(
    run_directory: Path,
    model_config: dict[str, Any],
    top: int | None = None,
) -> Path:
    manifest = read_manifest(run_directory / "run_manifest.json")
    if manifest.get("status") != "complete":
        raise ValueError(f"Cannot select from incomplete run: {run_directory}")
    metrics = pd.read_csv(run_directory / "config_metrics.csv")
    with (run_directory / "configurations.json").open("r", encoding="utf-8") as handle:
        configurations = json.load(handle)
    selection = model_config["selection"]
    primary = model_config["research"]["primary_selection_metric"]
    candidates = metrics.loc[
        metrics["prediction_coverage"].ge(float(selection["minimum_prediction_coverage"]))
        & ~metrics["family"].isin(["historical_mean", "autoregression"])
        & metrics[primary].notna()
    ].copy()
    if candidates.empty:
        raise ValueError("No non-baseline model satisfies the selection requirements")
    count = int(top or selection["top_families"])
    tolerance = float(model_config["research"].get("tie_sharpe_tolerance", 0.0))
    remaining = candidates.copy()
    chosen_rows: list[pd.Series] = []
    while len(chosen_rows) < count and not remaining.empty:
        best_value = float(remaining[primary].max())
        near_best = remaining.loc[remaining[primary].ge(best_value - tolerance)].sort_values(
            ["annualized_turnover", "median_trainable_parameters", "config_id"],
            ascending=[True, True, True],
        )
        winner = near_best.iloc[0]
        chosen_rows.append(winner)
        if selection.get("require_distinct_families", True):
            remaining = remaining.loc[~remaining["family"].eq(winner["family"])]
        else:
            remaining = remaining.loc[~remaining["config_id"].eq(winner["config_id"])]
    chosen = pd.DataFrame(chosen_rows)
    selected_configurations = [configurations[config_id] for config_id in chosen["config_id"]]
    path = run_directory / "selection.json"
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing model selection: {path}")
    atomic_json_dump(
        {
            "schema_version": 1,
            "created_at_utc": utc_now().isoformat(),
            "source_run_id": manifest["run_id"],
            "source_run_manifest_sha256": sha256_file(run_directory / "run_manifest.json"),
            "source_context": {
                "stage": manifest["inputs"]["stage"],
                "feature_dataset_id": manifest["inputs"]["feature_dataset_id"],
                "feature_set": manifest["inputs"]["feature_set"],
                "window_observations": manifest["inputs"]["window_observations"],
            },
            "selection_rule": {
                "primary_metric": primary,
                "minimum_prediction_coverage": selection["minimum_prediction_coverage"],
                "distinct_families": selection.get("require_distinct_families", True),
                "primary_metric_tolerance": tolerance,
                "tie_breaks_within_tolerance": [
                    "lower turnover",
                    "fewer trainable parameters",
                    "config_id",
                ],
            },
            "selected_metrics": chosen.to_dict(orient="records"),
            "selected_configurations": selected_configurations,
        },
        path,
    )
    return path

