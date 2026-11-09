#!/usr/bin/env python3
"""Confirm that the report release verifier fails closed under single mutations."""
from __future__ import annotations

import copy
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "reports/releases/project2_team16_v2_2026-11-01/release_registry.json"
VERIFIER = ROOT / "scripts/verify_report_release.py"


def execute(name: str, registry: dict, root: Path) -> dict:
    registry["outputs"]["verification"] = str((root / f"{name}_verification.json").relative_to(ROOT)) if root.is_relative_to(ROOT) else str(root / f"{name}_verification.json")
    path = root / f"{name}_registry.json"
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    result = subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(VERIFIER), "--release-registry", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        raise AssertionError(f"Negative control {name} was incorrectly accepted")
    output = json.loads((root / f"{name}_verification.json").read_text(encoding="utf-8"))
    return {"name": name, "exit_code": result.returncode, "failed_checks": [item["check"] for item in output["checks"] if not item["passed"]]}


def main() -> None:
    base = json.loads(REGISTRY.read_text(encoding="utf-8"))
    results = []
    with tempfile.TemporaryDirectory(prefix="report_release_negative_") as folder:
        root = Path(folder)

        mutated = copy.deepcopy(base)
        mutated["ids"]["FREEZE_ID"] = "NONEXISTENT_FREEZE_NEGATIVE_CONTROL"
        results.append(execute("wrong_freeze", mutated, root))

        mutated = copy.deepcopy(base)
        mutated["ids"]["SELECTED_CONFIG_ID"] = "NONEXISTENT_CONFIG_NEGATIVE_CONTROL"
        results.append(execute("wrong_config", mutated, root))

        mutated = copy.deepcopy(base)
        mutated["claims"]["return_2025_net"]["expected"] = 0.99
        results.append(execute("altered_claim", mutated, root))

        source_pack = ROOT / base["outputs"]["figure_pack"]
        copied_pack = root / "figure_pack"
        copied_pack.mkdir()
        for source in source_pack.iterdir():
            if source.name != "manifest.json":
                (copied_pack / source.name).symlink_to(source)
        manifest = json.loads((source_pack / "manifest.json").read_text(encoding="utf-8"))
        first_input = sorted(manifest["inputs"])[0]
        manifest["inputs"][first_input] = "0" * 64
        (copied_pack / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        mutated = copy.deepcopy(base)
        mutated["outputs"]["figure_pack"] = str(copied_pack)
        results.append(execute("stale_figure_input", mutated, root))

    summary = {"status": "pass", "controls": results}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
