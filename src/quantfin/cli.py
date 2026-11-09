"""Command-line entry points for the staged data pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quantfin.config import load_protocol, load_yaml
from quantfin.data.cleaning import (
    audit_corporate_actions,
    audit_yahoo_snapshot,
    clean_yahoo_snapshot,
)
from quantfin.data.stooq import fetch_stooq_snapshot
from quantfin.data.verification import compare_yahoo_stooq, record_skipped_verification
from quantfin.data.yahoo import fetch_yahoo_snapshot
from quantfin.eda import run_feature_eda, run_market_eda
from quantfin.errors import SourceFetchError
from quantfin.features import audit_feature_timing, build_feature_dataset
from quantfin.freeze import create_freeze
from quantfin.io import read_manifest, resolve_snapshot, sha256_file, stable_object_hash
from quantfin.modeling import run_walk_forward, select_models, walk_forward_plan
from quantfin.reporting import plot_model_run
from quantfin.statistics import run_statistical_tests


def _latest_dataset(root: Path, prefix: str) -> Path:
    candidates = sorted(
        [path for path in root.glob(f"{prefix}*") if (path / "manifest.json").is_file()],
        key=lambda path: (path / "manifest.json").stat().st_mtime,
    )
    if not candidates:
        raise FileNotFoundError(f"No datasets beginning with {prefix!r} under {root}")
    return candidates[-1]


def _dataset(root: Path, dataset_id: str | None, prefix: str) -> Path:
    if dataset_id:
        path = root / dataset_id
        if not (path / "manifest.json").is_file():
            raise FileNotFoundError(f"Dataset does not exist or lacks a manifest: {path}")
        return path
    return _latest_dataset(root, prefix)


def _run_directory(artifacts_root: Path, run_id: str | None, prefix: str | None = None) -> Path:
    root = artifacts_root / "runs"
    if run_id:
        path = root / run_id
        if not (path / "run_manifest.json").is_file():
            raise FileNotFoundError(f"Run does not exist: {path}")
        return path
    candidates = sorted(
        [
            path
            for path in root.glob(f"{prefix or '*'}*")
            if (path / "run_manifest.json").is_file()
        ],
        key=lambda path: (path / "run_manifest.json").stat().st_mtime,
    )
    if not candidates:
        raise FileNotFoundError(f"No matching runs found under {root}")
    return candidates[-1]


def _window(value: str) -> int | None:
    if value.lower() == "expanding":
        return None
    observations = int(value)
    if observations < 60:
        raise argparse.ArgumentTypeError("Rolling window must contain at least 60 observations")
    return observations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quantfin",
        description="Project 2 reproducible market-data pipeline",
    )
    parser.add_argument(
        "--protocol",
        default="configs/protocol.yaml",
        help="Path to the research protocol YAML (default: configs/protocol.yaml)",
    )
    parser.add_argument("--debug", action="store_true", help="Show Python tracebacks for debugging")
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch", help="Create an immutable raw source snapshot")
    fetch.add_argument("--source", choices=["yahoo", "stooq"], required=True)

    audit = commands.add_parser("audit-data", help="Audit a raw Yahoo snapshot")
    audit.add_argument("--snapshot-id", help="Yahoo snapshot ID; defaults to latest complete")

    actions = commands.add_parser("audit-actions", help="Export corporate-action diagnostics")
    actions.add_argument("--snapshot-id", help="Yahoo snapshot ID; defaults to latest complete")

    clean = commands.add_parser("clean", help="Clean a raw Yahoo snapshot")
    clean.add_argument("--snapshot-id", help="Yahoo snapshot ID; defaults to latest complete")

    verify = commands.add_parser("verify-sources", help="Compare Yahoo and Stooq overlap")
    verify.add_argument("--yahoo-snapshot-id", help="Defaults to latest complete Yahoo snapshot")
    verify.add_argument("--stooq-snapshot-id", help="Defaults to latest complete Stooq snapshot")

    features = commands.add_parser("build-features", help="Build causal features and delayed labels")
    features.add_argument("--features-config", default="configs/features.yaml")
    features.add_argument("--market-dataset-id", help="Defaults to latest market_* dataset")

    timing = commands.add_parser("check-timing", help="Audit feature/label ordering")
    timing.add_argument("--feature-dataset-id", help="Defaults to latest features_* dataset")

    inspect = commands.add_parser("show-manifest", help="Print the manifest path and summary")
    inspect.add_argument("--kind", choices=["yahoo", "stooq", "market", "features"], required=True)
    inspect.add_argument("--id", help="Specific snapshot/dataset ID; defaults to latest")

    market_eda = commands.add_parser("eda-market", help="Create market-data EDA tables and plots")
    market_eda.add_argument("--market-dataset-id", help="Defaults to latest market_* dataset")
    market_eda.add_argument("--events-config", default="configs/events.yaml")
    market_eda.add_argument(
        "--through",
        default="2014-12-31",
        help="Inclusive EDA cutoff; use 2025-12-31 only after the final-test freeze",
    )

    feature_eda = commands.add_parser("eda-features", help="Create training-only feature EDA")
    feature_eda.add_argument("--feature-dataset-id", help="Defaults to latest features_* dataset")
    feature_eda.add_argument("--feature-set", default="F2")
    feature_eda.add_argument("--split", default="initial_train")

    statistics = commands.add_parser("stat-tests", help="Run finance-oriented statistical diagnostics")
    statistics.add_argument("--market-dataset-id", help="Defaults to latest market_* dataset")
    statistics.add_argument("--feature-dataset-id", help="Defaults to latest features_* dataset")
    statistics.add_argument("--feature-set", default="F2")
    statistics.add_argument("--split", default="initial_train")

    models = commands.add_parser("run-models", help="Run resumable monthly-refit walk-forward models")
    models.add_argument("--models-config", default="configs/models.yaml")
    models.add_argument("--feature-dataset-id", help="Defaults to latest features_* dataset")
    models.add_argument("--feature-set", help="Override the configured feature set, e.g. F0/F1/F2")
    models.add_argument("--stage", choices=["screening", "confirmation", "final_test"], required=True)
    models.add_argument("--profile", choices=["quick", "standard", "deep"], default="standard")
    models.add_argument("--window", type=_window, default=None, help="expanding or rolling observations, e.g. 1260")
    models.add_argument("--selection", help="Selection JSON from the preceding stage")
    models.add_argument("--freeze", help="Required protocol freeze JSON for final_test")
    models.add_argument("--resume", action="store_true")
    models.add_argument("--plan-only", action="store_true", help="Print fit counts without creating a run")

    status = commands.add_parser("run-status", help="Show a model run and checkpoint completion")
    status.add_argument("--run-id", help="Defaults to the most recently updated model run")

    selection = commands.add_parser("select-models", help="Apply the predeclared rule to a completed run")
    selection.add_argument("--models-config", default="configs/models.yaml")
    selection.add_argument("--run-id", help="Defaults to latest model run")
    selection.add_argument("--top", type=int, help="Number of distinct model families to retain")

    plots = commands.add_parser("plot-run", help="Create performance, complexity, and interpretation plots")
    plots.add_argument("--models-config", default="configs/models.yaml")
    plots.add_argument("--run-id", help="Defaults to latest completed model run")
    plots.add_argument("--top-n", type=int, default=8)

    freeze = commands.add_parser("freeze", help="Freeze the confirmed strategy before final testing")
    freeze.add_argument("--models-config", default="configs/models.yaml")
    freeze.add_argument("--feature-dataset-id", help="Defaults to latest features_* dataset")
    freeze.add_argument("--feature-set", default="F2")
    freeze.add_argument("--window", type=_window, default=None, help="expanding or rolling observations")
    freeze.add_argument("--selection", required=True, help="Selection JSON from confirmation run")
    return parser


def _run(args: argparse.Namespace) -> int:
    protocol, paths = load_protocol(args.protocol)

    if args.command == "fetch":
        destination = (
            fetch_yahoo_snapshot(protocol, paths.raw)
            if args.source == "yahoo"
            else fetch_stooq_snapshot(protocol, paths.raw)
        )
        print(f"Created raw snapshot: {destination}")
        return 0

    if args.command == "audit-data":
        snapshot = resolve_snapshot(paths.raw, "yahoo", args.snapshot_id)
        report = audit_yahoo_snapshot(snapshot, protocol, paths.artifacts)
        print(f"Created quality report: {report}")
        return 0

    if args.command == "audit-actions":
        snapshot = resolve_snapshot(paths.raw, "yahoo", args.snapshot_id)
        report = audit_corporate_actions(snapshot, paths.artifacts)
        print(f"Created corporate-action report: {report}")
        return 0

    if args.command == "clean":
        snapshot = resolve_snapshot(paths.raw, "yahoo", args.snapshot_id)
        destination = clean_yahoo_snapshot(snapshot, protocol, paths.processed)
        print(f"Created processed market dataset: {destination}")
        return 0

    if args.command == "verify-sources":
        yahoo = resolve_snapshot(paths.raw, "yahoo", args.yahoo_snapshot_id)
        try:
            stooq = resolve_snapshot(paths.raw, "stooq", args.stooq_snapshot_id)
        except FileNotFoundError as exc:
            report = record_skipped_verification(yahoo, str(exc), paths.artifacts)
            print("SKIPPED: Optional Stooq verification is unavailable.")
            print(f"Recorded reason: {report}")
            print("Continue with: python -m quantfin clean")
            return 0
        report = compare_yahoo_stooq(yahoo, stooq, protocol, paths.artifacts)
        print(f"Created cross-source report: {report}")
        return 0

    if args.command == "build-features":
        feature_config = load_yaml(args.features_config)
        market_dataset = _dataset(paths.processed, args.market_dataset_id, "market_")
        destination = build_feature_dataset(
            market_dataset, protocol, feature_config, paths.processed
        )
        print(f"Created feature dataset: {destination}")
        return 0

    if args.command == "check-timing":
        feature_dataset = _dataset(paths.processed, args.feature_dataset_id, "features_")
        report = audit_feature_timing(feature_dataset, paths.artifacts)
        print(f"Created timing report: {report}")
        return 0

    if args.command == "show-manifest":
        if args.kind in {"yahoo", "stooq"}:
            path = resolve_snapshot(paths.raw, args.kind, args.id)
        else:
            path = _dataset(paths.processed, args.id, f"{args.kind}_")
        manifest_path = path / "manifest.json"
        manifest = read_manifest(manifest_path)
        print(f"Manifest: {manifest_path}")
        for key in ("snapshot_id", "dataset_id", "source", "status", "created_at_utc", "retrieved_at_utc"):
            if key in manifest:
                print(f"{key}: {manifest[key]}")
        return 0

    if args.command == "eda-market":
        market_dataset = _dataset(paths.processed, args.market_dataset_id, "market_")
        events = load_yaml(args.events_config)
        output = paths.artifacts / "eda" / (
            f"market_{market_dataset.name}_{args.through}_{stable_object_hash(events)[:10]}"
        )
        summary = run_market_eda(market_dataset, events, output, args.through)
        print(f"Created market EDA: {output / 'eda_manifest.json'}")
        print(f"Plots: {len(summary['plots'])}; tables: {len(summary['tables'])}")
        return 0

    if args.command == "eda-features":
        feature_dataset = _dataset(paths.processed, args.feature_dataset_id, "features_")
        output = paths.artifacts / "eda" / (
            f"features_{feature_dataset.name}_{args.feature_set}_{args.split}"
        )
        summary = run_feature_eda(feature_dataset, args.feature_set, output, args.split)
        print(f"Created feature EDA: {output / 'eda_manifest.json'}")
        print(f"Plots: {len(summary['plots'])}; tables: {len(summary['tables'])}")
        return 0

    if args.command == "stat-tests":
        market_dataset = _dataset(paths.processed, args.market_dataset_id, "market_")
        feature_dataset = _dataset(paths.processed, args.feature_dataset_id, "features_")
        output = paths.artifacts / "statistics" / (
            f"{feature_dataset.name}_{args.feature_set}_{args.split}"
        )
        run_statistical_tests(
            market_dataset,
            feature_dataset,
            args.feature_set,
            output,
            args.split,
        )
        print(f"Created statistical diagnostics: {output / 'statistical_tests.json'}")
        return 0

    if args.command == "run-models":
        feature_dataset = _dataset(paths.processed, args.feature_dataset_id, "features_")
        model_config = load_yaml(args.models_config)
        selection_path = Path(args.selection).expanduser().resolve() if args.selection else None
        if args.plan_only:
            plan = walk_forward_plan(
                feature_dataset=feature_dataset,
                protocol=protocol,
                model_config=model_config,
                feature_set_override=args.feature_set,
                profile=args.profile,
                stage=args.stage,
                selection_path=selection_path,
                window_observations=args.window,
            )
            print(json.dumps(plan, indent=2, sort_keys=True))
            return 0
        tracker = run_walk_forward(
            feature_dataset=feature_dataset,
            protocol=protocol,
            model_config=model_config,
            feature_set_override=args.feature_set,
            profile=args.profile,
            stage=args.stage,
            window_observations=args.window,
            selection_path=selection_path,
            freeze_path=Path(args.freeze).expanduser().resolve() if args.freeze else None,
            artifacts_root=paths.artifacts,
            project_root=paths.root,
            resume=args.resume,
        )
        print(f"Completed run: {tracker.run_id}")
        print(f"Run directory: {tracker.directory}")
        return 0

    if args.command == "run-status":
        run_directory = _run_directory(paths.artifacts, args.run_id, "models_")
        manifest = read_manifest(run_directory / "run_manifest.json")
        checkpoint_paths = [
            path for path in run_directory.glob("checkpoints/*/*.parquet")
            if not path.stem.endswith("_features")
        ]
        complete = 0
        invalid = 0
        for path in checkpoint_paths:
            metadata_path = path.with_suffix(".json")
            if metadata_path.is_file() and read_manifest(metadata_path).get(
                "checkpoint_sha256"
            ) == sha256_file(path):
                complete += 1
            else:
                invalid += 1
        planned = int(manifest.get("total_planned_fits", 0))
        print(f"run_id: {manifest['run_id']}")
        print(f"status: {manifest.get('status')}")
        print(f"updated_at_utc: {manifest.get('updated_at_utc')}")
        print(f"checkpoints: {complete}/{planned}")
        print(f"invalid_checkpoints_to_rebuild: {invalid}")
        print(f"percent: {(100 * complete / planned) if planned else 0:.1f}")
        print(f"directory: {run_directory}")
        return 0

    if args.command == "freeze":
        feature_dataset = _dataset(paths.processed, args.feature_dataset_id, "features_")
        model_config = load_yaml(args.models_config)
        destination = create_freeze(
            selection_path=Path(args.selection).expanduser().resolve(),
            feature_dataset=feature_dataset,
            protocol=protocol,
            model_config=model_config,
            feature_set=args.feature_set,
            window_observations=args.window,
            freezes_root=paths.artifacts / "freezes",
        )
        print(f"Created final-test freeze: {destination}")
        return 0

    if args.command == "select-models":
        model_config = load_yaml(args.models_config)
        run_directory = _run_directory(paths.artifacts, args.run_id, "models_")
        selection_path = select_models(run_directory, model_config, args.top)
        print(f"Created selection: {selection_path}")
        return 0

    if args.command == "plot-run":
        model_config = load_yaml(args.models_config)
        run_directory = _run_directory(paths.artifacts, args.run_id, "models_")
        report = plot_model_run(run_directory, model_config, args.top_n)
        print(f"Created model report: {report}")
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _run(args)
    except SourceFetchError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        if exc.source.lower() == "stooq":
            print(
                "Stooq is optional. Continue the core pipeline with: python -m quantfin audit-data",
                file=sys.stderr,
            )
        return 3
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (FileExistsError, ValueError, KeyError) as exc:
        if args.debug:
            raise
        print(f"ERROR: {exc}", file=sys.stderr)
        print("Re-run with --debug before the subcommand to show a traceback.", file=sys.stderr)
        return 4

