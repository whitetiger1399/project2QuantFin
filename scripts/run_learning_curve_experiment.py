"""Run chronological MLP-epoch or boosting-round experiments with resume support."""

from __future__ import annotations

import argparse
import json
import time
import warnings
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from tqdm import tqdm

from quantfin.io import atomic_json_dump, atomic_parquet_dump, sha256_file, stable_object_hash
from quantfin.research_extension import activity_tables, deterministic_run_id, environment_record, evenly_spaced, load_feature_dataset, monthly_blocks, read_yaml


ROOT = Path(__file__).resolve().parents[1]


def configurations(config: dict[str, Any], family: str) -> list[dict[str, Any]]:
    learning = config["learning_curves"]
    if family == "mlp":
        return [
            {"family": family, "width": width, "alpha": alpha, "seed": seed}
            for width, alpha, seed in product(learning["mlp"]["hidden_widths"], learning["mlp"]["alpha"], learning["seeds"])
        ]
    boosting = learning["hist_gradient_boosting"]
    return [
        {"family": family, "max_leaf_nodes": leaves, "learning_rate": rate, "l2_regularization": l2, "seed": seed}
        for leaves, rate, l2, seed in product(boosting["max_leaf_nodes"], boosting["learning_rate"], boosting["l2_regularization"], learning["seeds"])
    ]


def fit_mlp(
    specification: dict[str, Any], x_inner: np.ndarray, y_inner: np.ndarray,
    x_validation: np.ndarray, y_validation: np.ndarray, x_full: np.ndarray,
    y_full: np.ndarray, x_eval: np.ndarray, config: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, list[dict[str, float]], int]:
    settings = config["learning_curves"]["mlp"]
    checkpoints = [int(x) for x in settings["epoch_checkpoints"]]
    model = MLPRegressor(
        hidden_layer_sizes=(int(specification["width"]),), activation="relu", solver="adam",
        alpha=float(specification["alpha"]), learning_rate_init=float(settings["learning_rate_init"]),
        max_iter=1, warm_start=True, shuffle=False, random_state=int(specification["seed"]),
    )
    curve = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        for epoch in range(1, max(checkpoints) + 1):
            model.fit(x_inner, y_inner)
            if epoch in checkpoints:
                curve.append({"iteration": epoch, "inner_train_mse": mean_squared_error(y_inner, model.predict(x_inner)), "validation_mse": mean_squared_error(y_validation, model.predict(x_validation))})
    best_epoch = int(min(curve, key=lambda row: row["validation_mse"])["iteration"])
    final = MLPRegressor(
        hidden_layer_sizes=(int(specification["width"]),), activation="relu", solver="adam",
        alpha=float(specification["alpha"]), learning_rate_init=float(settings["learning_rate_init"]),
        max_iter=best_epoch, shuffle=False, random_state=int(specification["seed"]), tol=0.0,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        final.fit(x_full, y_full)
    return final.predict(x_full), final.predict(x_eval), curve, best_epoch


def fit_boosting(
    specification: dict[str, Any], x_inner: np.ndarray, y_inner: np.ndarray,
    x_validation: np.ndarray, y_validation: np.ndarray, x_full: np.ndarray,
    y_full: np.ndarray, x_eval: np.ndarray, config: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, list[dict[str, float]], int]:
    settings = config["learning_curves"]["hist_gradient_boosting"]
    curve = []
    for rounds in settings["max_iter"]:
        model = HistGradientBoostingRegressor(
            max_leaf_nodes=int(specification["max_leaf_nodes"]), learning_rate=float(specification["learning_rate"]),
            l2_regularization=float(specification["l2_regularization"]), max_iter=int(rounds),
            min_samples_leaf=20, early_stopping=False, random_state=int(specification["seed"]),
        )
        model.fit(x_inner, y_inner)
        curve.append({"iteration": int(rounds), "inner_train_mse": mean_squared_error(y_inner, model.predict(x_inner)), "validation_mse": mean_squared_error(y_validation, model.predict(x_validation))})
    best_rounds = int(min(curve, key=lambda row: row["validation_mse"])["iteration"])
    final = HistGradientBoostingRegressor(
        max_leaf_nodes=int(specification["max_leaf_nodes"]), learning_rate=float(specification["learning_rate"]),
        l2_regularization=float(specification["l2_regularization"]), max_iter=best_rounds,
        min_samples_leaf=20, early_stopping=False, random_state=int(specification["seed"]),
    )
    final.fit(x_full, y_full)
    return final.predict(x_full), final.predict(x_eval), curve, best_rounds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/research_extension_2026-10-21.yaml")
    parser.add_argument("--family", choices=["mlp", "boosting"], required=True)
    parser.add_argument("--origin-limit", type=int, help="Evenly spaced refits for a pilot")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-hours", type=float)
    parser.add_argument("--output-root", default="artifacts/research/learning_curve_runs")
    args = parser.parse_args()
    config_path = ROOT / args.config
    config = read_yaml(config_path)
    frame, manifest, feature_columns, feature_dir = load_feature_dataset(ROOT, config["feature_dataset_id"], config["feature_set"])
    bounds = config["evaluation"]
    evaluation = frame.loc[frame["signal_session"].between(pd.Timestamp(bounds["start"]), pd.Timestamp(bounds["end"])) & frame["target_return"].notna()].copy()
    blocks = monthly_blocks(evaluation)
    if args.origin_limit:
        blocks = evenly_spaced(blocks, args.origin_limit)
    specs = configurations(config, args.family)
    tasks = [(specification, origin, block) for specification in specs for origin, block in blocks]
    identity = {"config_sha256": sha256_file(config_path), "feature_manifest_sha256": sha256_file(feature_dir / "manifest.json"), "family": args.family, "origin_limit": args.origin_limit, "origins": [origin.isoformat() for origin, _ in blocks]}
    run_id = deterministic_run_id(f"learning_{args.family}", identity)
    run_dir = ROOT / args.output_root / run_id
    plan = {"mode": "execute" if args.execute else "plan_only", "run_id": run_id, "family": args.family, "configurations": len(specs), "refit_origins": len(blocks), "planned_refits": len(tasks), "research_status": config["research_status"], "output_directory": str(run_dir)}
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    if run_dir.exists() and not args.resume:
        raise FileExistsError(f"Run exists; pass --resume: {run_dir}")
    checkpoint_dir = run_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = {"schema_version": 1, "run_id": run_id, "status": "running", "created_at_utc": datetime.now(timezone.utc).isoformat(), "identity": identity, "plan": plan, "environment": environment_record()}
    atomic_json_dump(run_manifest, run_dir / "run_manifest.json")
    start = time.perf_counter()
    max_hours = float(args.max_hours or config["compute"]["maximum_hours"])
    window = int(config["learning_curves"]["training_window_observations"])
    validation_fraction = float(config["learning_curves"]["validation_fraction"])
    completed = 0
    curves = []
    bar = tqdm(tasks, desc=f"Learning curves {args.family}", unit="refit")
    for specification, origin, block in bar:
        if (time.perf_counter() - start) / 3600 >= max_hours:
            run_manifest.update(status="budget_stop", completed_refits=completed, updated_at_utc=datetime.now(timezone.utc).isoformat())
            atomic_json_dump(run_manifest, run_dir / "run_manifest.json")
            bar.close()
            print(json.dumps({"run_id": run_id, "status": "budget_stop", "resume": True}, indent=2))
            return
        config_id = f"{args.family}_curve_" + stable_object_hash(specification)[:12]
        task_id = stable_object_hash({"configuration": specification, "origin": origin.isoformat()})[:20]
        checkpoint = checkpoint_dir / f"{task_id}.parquet"
        curve_path = checkpoint_dir / f"{task_id}_curve.csv"
        meta_path = checkpoint_dir / f"{task_id}.json"
        if args.resume and checkpoint.is_file() and curve_path.is_file() and meta_path.is_file():
            completed += 1
            continue
        eligible = frame.loc[frame["target_return"].notna() & frame["label_available_session"].le(origin) & frame["signal_session"].ge(pd.Timestamp(bounds["initial_train_start"]))].tail(window)
        if len(eligible) < int(config["learning_curves"]["minimum_training_rows"]):
            raise ValueError(f"Insufficient eligible rows at {origin.date()}: {len(eligible)}")
        split = int(len(eligible) * (1.0 - validation_fraction))
        inner, validation = eligible.iloc[:split], eligible.iloc[split:]
        imputer = SimpleImputer(strategy="median")
        scaler = StandardScaler()
        x_inner = scaler.fit_transform(imputer.fit_transform(inner[feature_columns]))
        x_validation = scaler.transform(imputer.transform(validation[feature_columns]))
        # Refit preprocessing on all eligible history only after the epoch/round choice.
        final_imputer = SimpleImputer(strategy="median")
        final_scaler = StandardScaler()
        x_full = final_scaler.fit_transform(final_imputer.fit_transform(eligible[feature_columns]))
        x_eval = final_scaler.transform(final_imputer.transform(block[feature_columns]))
        y_inner = inner["target_return"].to_numpy(float)
        y_validation = validation["target_return"].to_numpy(float)
        y_full = eligible["target_return"].to_numpy(float)
        fit_started = time.perf_counter()
        with threadpool_limits(limits=int(config["compute"]["numerical_threads"])):
            if args.family == "mlp":
                train_prediction, prediction, curve, selected_iteration = fit_mlp(specification, x_inner, y_inner, x_validation, y_validation, x_full, y_full, x_eval, config)
            else:
                train_prediction, prediction, curve, selected_iteration = fit_boosting(specification, x_inner, y_inner, x_validation, y_validation, x_full, y_full, x_eval, config)
        seconds = time.perf_counter() - fit_started
        curve_frame = pd.DataFrame(curve)
        curve_frame["config_id"] = config_id
        curve_frame["refit_origin"] = origin
        curve_frame["selected_iteration"] = selected_iteration
        curve_frame.to_csv(curve_path, index=False)
        curves.append(curve_frame)
        output = block[["signal_session", "entry_session", "label_end_session", "label_available_session", "target_return", "split"]].copy()
        output["prediction"] = prediction
        output["baseline_prediction"] = float(y_full.mean())
        output["config_id"] = config_id
        output["family"] = f"{args.family}_learning_curve"
        output["refit_origin"] = origin
        output["n_train"] = len(eligible)
        output["selected_iteration"] = selected_iteration
        output["train_mse"] = mean_squared_error(y_full, train_prediction)
        output["fit_seconds"] = seconds
        output["train_last_label_available"] = eligible["label_available_session"].max()
        for key, value in specification.items():
            if key != "family":
                output[key] = value
        atomic_parquet_dump(output, checkpoint)
        atomic_json_dump({"task_id": task_id, "configuration": specification, "origin": origin.isoformat(), "selected_iteration": selected_iteration, "fit_seconds": seconds, "checkpoint_sha256": sha256_file(checkpoint)}, meta_path)
        completed += 1
        bar.set_postfix(selected=selected_iteration, seconds=f"{seconds:.1f}")
        run_manifest.update(completed_refits=completed, updated_at_utc=datetime.now(timezone.utc).isoformat())
        atomic_json_dump(run_manifest, run_dir / "run_manifest.json")
    bar.close()
    predictions = pd.concat([pd.read_parquet(path) for path in checkpoint_dir.glob("*.parquet")], ignore_index=True).sort_values(["config_id", "signal_session"])
    atomic_parquet_dump(predictions, run_dir / "predictions.parquet")
    curves_all = pd.concat([pd.read_csv(path) for path in checkpoint_dir.glob("*_curve.csv")], ignore_index=True)
    curves_all.to_csv(run_dir / "learning_curves.csv", index=False)
    metrics, annual, ledgers = activity_tables(predictions, forecast_hurdle=float(bounds["forecast_hurdle"]), one_way_cost_bps=float(bounds["one_way_cost_bps"]), annualization=int(bounds["annualization_sessions"]))
    metrics.to_csv(run_dir / "config_metrics.csv", index=False)
    annual.to_csv(run_dir / "activity_by_year.csv", index=False)
    atomic_parquet_dump(ledgers, run_dir / "strategy_ledgers.parquet")
    figure_data = curves_all.groupby(["iteration"], as_index=False).agg(train_mse=("inner_train_mse", "median"), validation_mse=("validation_mse", "median"))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(figure_data["iteration"], figure_data["train_mse"], marker="o", label="inner training")
    ax.plot(figure_data["iteration"], figure_data["validation_mse"], marker="o", label="past-only validation")
    ax.set(xlabel="Epochs" if args.family == "mlp" else "Boosting rounds", ylabel="Median MSE", title=f"{args.family.upper()} chronological learning curve")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(run_dir / "learning_curve.png", dpi=240)
    plt.close(fig)
    run_manifest.update(status="complete", completed_at_utc=datetime.now(timezone.utc).isoformat(), completed_refits=len(tasks), elapsed_seconds=time.perf_counter() - start, outputs={"predictions": "predictions.parquet", "metrics": "config_metrics.csv", "learning_curves": "learning_curves.csv", "figure": "learning_curve.png"})
    atomic_json_dump(run_manifest, run_dir / "run_manifest.json")
    print(json.dumps({"run_id": run_id, "status": "complete", "output_directory": str(run_dir)}, indent=2))


if __name__ == "__main__":
    main()

