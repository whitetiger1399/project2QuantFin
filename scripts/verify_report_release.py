#!/usr/bin/env python3
"""Failing integrity and publication checks for a versioned report release."""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "reports"))
from report_release import resolve, sha256_file  # noqa: E402


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def csv_scalar(root: Path, specification: dict):
    path = resolve(root, specification["artifact"])
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for key, expected in specification.get("selector", {}).items():
        rows = [row for row in rows if str(row[key]) == str(expected)]
    if len(rows) != 1:
        raise ValueError(f"Expected one selected row in {path}; found {len(rows)}")
    value = rows[0][specification["column"]]
    try:
        return float(value)
    except ValueError:
        return value


def claim_value(root: Path, name: str, specification: dict, resolved_claims: dict):
    kind = specification.get("kind")
    if kind == "csv_scalar":
        return csv_scalar(root, specification)
    if kind == "configuration_parameter":
        configuration = json.loads(csv_scalar(root, specification))
        return configuration["parameters"][specification["parameter"]]
    if kind == "compound":
        values = [resolved_claims[item] for item in specification["inputs"]]
        result = 1.0
        for value in values:
            result *= 1.0 + float(value)
        return result - 1.0
    if kind == "zero_crossing_linear_interpolation":
        path = resolve(root, specification["artifact"])
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        for key, expected in specification.get("selector", {}).items():
            rows = [row for row in rows if str(row[key]) == str(expected)]
        points = sorted((float(row[specification["x_column"]]), float(row[specification["y_column"]])) for row in rows)
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            if y0 == 0:
                return x0
            if y0 * y1 <= 0 and y1 != y0:
                return x0 + (0 - y0) * (x1 - x0) / (y1 - y0)
        raise ValueError(f"No zero crossing in {path} for claim {name}")
    raise ValueError(f"Unknown claim kind for {name}: {kind}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-registry", type=Path, required=True)
    args = parser.parse_args()
    registry_path = args.release_registry if args.release_registry.is_absolute() else ROOT / args.release_registry
    registry = load(registry_path)
    ids = registry["ids"]
    outputs = {key: resolve(ROOT, value) for key, value in registry["outputs"].items()}
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    evidence = {
        "dataset": ROOT / "data/processed/cross_market_ai_capability" / ids["DATASET_ID"] / "manifest.json",
        "forward_dataset": ROOT / "data/processed/cross_market_ai_capability_2026" / ids["FORWARD_DATASET_ID"] / "manifest.json",
        "screening": ROOT / "artifacts/cross_market_ai_capability/runs" / ids["SCREENING_RUN_ID"] / "manifest.json",
        "confirmation": ROOT / "artifacts/cross_market_ai_capability/runs" / ids["CONFIRMATION_RUN_ID"] / "manifest.json",
        "freeze": ROOT / "artifacts/cross_market_ai_capability/freezes" / f"{ids['FREEZE_ID']}.json",
        "final": ROOT / "artifacts/cross_market_ai_capability/runs" / ids["FINAL_RUN_ID"] / "manifest.json",
        "forward": ROOT / "artifacts/cross_market_ai_capability_2026/runs" / ids["FORWARD_RUN_ID"] / "manifest.json",
        "paired": ROOT / "artifacts/cross_market_ai_capability/analysis" / ids["PAIRED_STRATEGY_ANALYSIS_ID"] / "manifest.json",
        "strict_vintage": ROOT / "artifacts/cross_market_ai_capability/analysis" / ids["STRICT_VINTAGE_ANALYSIS_ID"] / "manifest.json",
    }
    manifests = {}
    for name, path in evidence.items():
        check(f"{name}_manifest_exists", path.is_file(), str(path))
        if path.is_file():
            manifests[name] = load(path)
            if name != "freeze":
                check(f"{name}_complete", manifests[name].get("status") == "complete", manifests[name].get("status", "missing"))
    identity_fields = {
        "dataset": ("dataset_id", "DATASET_ID"), "forward_dataset": ("dataset_id", "FORWARD_DATASET_ID"),
        "screening": ("run_id", "SCREENING_RUN_ID"), "confirmation": ("run_id", "CONFIRMATION_RUN_ID"),
        "freeze": ("freeze_id", "FREEZE_ID"), "final": ("run_id", "FINAL_RUN_ID"),
        "forward": ("run_id", "FORWARD_RUN_ID"),
        "paired": ("analysis_id", "PAIRED_STRATEGY_ANALYSIS_ID"),
        "strict_vintage": ("analysis_id", "STRICT_VINTAGE_ANALYSIS_ID"),
    }
    for name, (field, registry_key) in identity_fields.items():
        if name in manifests:
            check(f"{name}_identity", manifests[name].get(field) == ids[registry_key], str(manifests[name].get(field)))
    selected = ids["SELECTED_CONFIG_ID"]
    for name in ("freeze", "final", "forward"):
        if name in manifests:
            check(f"{name}_selected_config", manifests[name].get("selected_config_id") == selected,
                  str(manifests[name].get("selected_config_id")))
    parent_expectations = [
        ("screening", "dataset_id", "DATASET_ID"),
        ("confirmation", "dataset_id", "DATASET_ID"),
        ("confirmation", "screening_run_id", "SCREENING_RUN_ID"),
        ("freeze", "confirmation_run_id", "CONFIRMATION_RUN_ID"),
        ("final", "dataset_id", "DATASET_ID"),
        ("final", "confirmation_run_id", "CONFIRMATION_RUN_ID"),
        ("final", "freeze_id", "FREEZE_ID"),
        ("forward", "dataset_id", "FORWARD_DATASET_ID"),
        ("forward", "source_confirmation_run_id", "CONFIRMATION_RUN_ID"),
        ("forward", "source_freeze_id", "FREEZE_ID"),
    ]
    for child, field, registry_key in parent_expectations:
        if child in manifests:
            actual = manifests[child].get(field)
            check(f"{child}_parent:{field}", actual == ids[registry_key], str(actual))
    manifest_hash_expectations = [
        ("screening", "dataset_manifest_sha256", "dataset"),
        ("confirmation", "dataset_manifest_sha256", "dataset"),
        ("final", "dataset_manifest_sha256", "dataset"),
        ("freeze", "confirmation_manifest_sha256", "confirmation"),
    ]
    for child, field, parent in manifest_hash_expectations:
        if child in manifests and parent in evidence and evidence[parent].is_file():
            actual = manifests[child].get(field)
            expected = sha256_file(evidence[parent])
            check(f"{child}_parent_hash:{field}", actual == expected, f"{actual} vs {expected}")
    if "forward" in manifests:
        source_identity = manifests["forward"].get("source_identity", {})
        for field, parent in [("dataset_manifest_sha256", "forward_dataset"), ("confirmation_manifest_sha256", "confirmation"), ("freeze_sha256", "freeze")]:
            expected = sha256_file(evidence[parent]) if evidence[parent].is_file() else "missing"
            check(f"forward_source_hash:{field}", source_identity.get(field) == expected,
                  f"{source_identity.get(field)} vs {expected}")
    if "paired" in manifests:
        for relative, digest in manifests["paired"].get("identity", {}).get("sources", {}).items():
            path = ROOT / relative
            check(f"paired_source_hash:{relative}", path.is_file() and sha256_file(path) == digest, str(path))
        paired_dir = evidence["paired"].parent
        for relative, digest in manifests["paired"].get("files", {}).items():
            path = paired_dir / relative
            check(f"paired_output_hash:{relative}", path.is_file() and sha256_file(path) == digest, str(path))
    if "strict_vintage" in manifests:
        strict = manifests["strict_vintage"]
        check("strict_vintage_exact_selected_parameters", strict.get("selected_parameters_match_exactly") is True,
              str(strict.get("selected_parameters_match_exactly")))
        check("strict_vintage_excluded_60_flags", strict.get("fallback_flagged_features_excluded") == 60,
              str(strict.get("fallback_flagged_features_excluded")))
        check("strict_vintage_retained_zero_flags", strict.get("fallback_flagged_features_retained") == 0,
              str(strict.get("fallback_flagged_features_retained")))
        strict_dir = evidence["strict_vintage"].parent
        for relative, digest in strict.get("files", {}).items():
            path = strict_dir / relative
            check(f"strict_vintage_output_hash:{relative}", path.is_file() and sha256_file(path) == digest, str(path))

    pack_manifest_path = outputs["figure_pack"] / "manifest.json"
    check("figure_pack_manifest_exists", pack_manifest_path.is_file(), str(pack_manifest_path))
    if pack_manifest_path.is_file():
        pack = load(pack_manifest_path)
        check("figure_pack_complete", pack.get("status") == "complete", str(pack.get("status")))
        check("figure_pack_selected_config", pack.get("canonical_config") == selected, str(pack.get("canonical_config")))
        for relative, digest in pack.get("inputs", {}).items():
            path = ROOT / relative
            check(f"figure_input_hash:{relative}", path.is_file() and sha256_file(path) == digest, str(path))
        for relative, digest in pack.get("files", {}).items():
            path = outputs["figure_pack"] / relative
            check(f"figure_hash:{relative}", path.is_file() and sha256_file(path) == digest, str(path))

    for name in ("docx", "pdf"):
        check(f"{name}_exists", outputs[name].is_file(), str(outputs[name]))
    page_count = None
    if outputs["pdf"].is_file():
        info = subprocess.run(["pdfinfo", str(outputs["pdf"])], text=True, capture_output=True, check=True).stdout
        page_count = int(re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE).group(1))
        check("page_count_15_to_25", 15 <= page_count <= 25, str(page_count))
        page_two = subprocess.run(["pdftotext", "-f", "2", "-l", "2", "-layout", str(outputs["pdf"]), "-"],
                                  text=True, capture_output=True, check=True).stdout
        check("toc_has_no_page_zero", not re.search(r"\.{3,}\s*0\s*$", page_two, re.MULTILINE), page_two[:500])
    if outputs["docx"].is_file():
        document = Document(outputs["docx"])
        cover_text = " ".join(p.text for p in document.paragraphs[:20]).casefold()
        check("docx_submission_cover", "cross-market forecasting" in cover_text and "traceable research report" not in cover_text and "version 2" not in cover_text, "Course-facing cover without internal revision label")
    toc = load(outputs["toc_pages"]) if outputs["toc_pages"].is_file() else {}
    check("toc_page_map_nonzero", bool(toc) and all(int(value) > 0 for value in toc.values()), f"{len(toc)} headings")

    resolved_claims = {}
    for name, specification in registry.get("claims", {}).items():
        try:
            actual = claim_value(ROOT, name, specification, resolved_claims)
            expected = specification["expected"]
            if isinstance(expected, (int, float)) and not isinstance(expected, bool):
                tolerance = float(specification.get("tolerance", 0))
                passed = math.isclose(float(actual), float(expected), rel_tol=0, abs_tol=tolerance)
            else:
                passed = actual == expected
            resolved_claims[name] = actual
            check(f"claim:{name}", passed, f"actual={actual!r}; expected={expected!r}")
        except Exception as exc:
            check(f"claim:{name}", False, f"{type(exc).__name__}: {exc}")

    try:
        git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip())
    except Exception:
        git_head, dirty = "unavailable", None
    result = {
        "release_id": registry["release_id"],
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if all(item["passed"] for item in checks) else "fail",
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_failed": sum(not item["passed"] for item in checks),
        "page_count": page_count,
        "git_head": git_head,
        "git_dirty": dirty,
        "files": {name: sha256_file(outputs[name]) for name in ("docx", "pdf") if outputs[name].is_file()},
        "checks": checks,
    }
    outputs["verification"].parent.mkdir(parents=True, exist_ok=True)
    outputs["verification"].write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
