"""Command-line entry points for the staged data pipeline."""

from __future__ import annotations

import argparse
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
from quantfin.errors import SourceFetchError
from quantfin.features import audit_feature_timing, build_feature_dataset
from quantfin.io import read_manifest, resolve_snapshot


def _latest_dataset(root: Path, prefix: str) -> Path:
    candidates = sorted(
        path for path in root.glob(f"{prefix}*") if (path / "manifest.json").is_file()
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

