"""Protocol freeze artifacts that gate access to the final test stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from quantfin.io import atomic_json_dump, read_manifest, sha256_file, stable_object_hash, utc_now


def create_freeze(
    *,
    selection_path: Path,
    feature_dataset: Path,
    protocol: dict[str, Any],
    model_config: dict[str, Any],
    feature_set: str,
    window_observations: int | None,
    freezes_root: Path,
) -> Path:
    selection = read_manifest(selection_path)
    feature_manifest = read_manifest(feature_dataset / "manifest.json")
    expected_context = {
        "stage": "confirmation",
        "feature_dataset_id": feature_manifest["dataset_id"],
        "feature_set": feature_set,
        "window_observations": window_observations,
    }
    actual_context = selection.get("source_context", {})
    mismatches = [
        key for key, expected_value in expected_context.items()
        if actual_context.get(key, "missing") != expected_value
    ]
    if mismatches:
        raise ValueError(
            f"Confirmation selection does not match freeze inputs for: {mismatches}"
        )
    payload = {
        "selection_sha256": sha256_file(selection_path),
        "source_run_id": selection["source_run_id"],
        "feature_dataset_id": feature_manifest["dataset_id"],
        "feature_manifest_sha256": sha256_file(feature_dataset / "manifest.json"),
        "protocol_sha256": stable_object_hash(protocol),
        "model_config_sha256": stable_object_hash(model_config),
        "feature_set": feature_set,
        "window_observations": window_observations,
        "selected_configurations": selection["selected_configurations"],
        "final_test_bounds": protocol["splits"]["final_test"],
        "forecast_hurdle": model_config["research"]["forecast_hurdle"],
        "one_way_cost_bps": model_config["research"]["one_way_cost_bps"],
    }
    freeze_id = f"freeze_{stable_object_hash(payload)[:16]}"
    destination = freezes_root / f"{freeze_id}.json"
    if destination.exists():
        raise FileExistsError(f"Freeze already exists: {destination}")
    atomic_json_dump(
        {
            "schema_version": 1,
            "freeze_id": freeze_id,
            "created_at_utc": utc_now().isoformat(),
            "status": "frozen",
            **payload,
            "rule": (
                "Any feature, model, threshold, cost, window, or selection change after this point "
                "creates a new analysis whose final period is no longer an untouched holdout."
            ),
        },
        destination,
    )
    return destination


def validate_freeze(
    freeze_path: Path,
    *,
    selection_path: Path,
    feature_manifest: dict[str, Any],
    feature_manifest_path: Path,
    protocol: dict[str, Any],
    model_config: dict[str, Any],
    feature_set: str,
    window_observations: int | None,
) -> dict[str, Any]:
    freeze = read_manifest(freeze_path)
    comparisons = {
        "status": freeze.get("status") == "frozen",
        "selection": freeze.get("selection_sha256") == sha256_file(selection_path),
        "feature_dataset": freeze.get("feature_dataset_id") == feature_manifest["dataset_id"],
        "feature_manifest": freeze.get("feature_manifest_sha256") == sha256_file(feature_manifest_path),
        "protocol": freeze.get("protocol_sha256") == stable_object_hash(protocol),
        "model_config": freeze.get("model_config_sha256") == stable_object_hash(model_config),
        "feature_set": freeze.get("feature_set") == feature_set,
        "window": freeze.get("window_observations") == window_observations,
    }
    failed = [name for name, valid in comparisons.items() if not valid]
    if failed:
        raise ValueError(f"Final-test freeze validation failed for: {failed}")
    return freeze

