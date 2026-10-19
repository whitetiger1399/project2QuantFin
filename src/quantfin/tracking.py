"""Content-addressed local run tracking with resumable checkpoints."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from quantfin.io import atomic_json_dump, package_versions, read_manifest, stable_object_hash, utc_now


def _git_revision(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


@dataclass(frozen=True)
class RunTracker:
    run_id: str
    directory: Path
    manifest_path: Path

    @classmethod
    def create_or_resume(
        cls,
        *,
        artifacts_root: Path,
        project_root: Path,
        command: str,
        inputs: dict[str, Any],
        resume: bool,
    ) -> "RunTracker":
        payload = {"command": command, "inputs": inputs}
        run_id = f"{command}_{stable_object_hash(payload)[:16]}"
        directory = artifacts_root / "runs" / run_id
        manifest_path = directory / "run_manifest.json"
        if manifest_path.exists():
            if not resume:
                raise FileExistsError(
                    f"Run already exists: {run_id}. Pass --resume to reuse checkpoints."
                )
            existing = read_manifest(manifest_path)
            if existing.get("input_hash") != stable_object_hash(inputs):
                raise ValueError(f"Run input hash mismatch: {run_id}")
            return cls(run_id, directory, manifest_path)

        directory.mkdir(parents=True, exist_ok=False)
        atomic_json_dump(
            {
                "schema_version": 1,
                "run_id": run_id,
                "command": command,
                "status": "running",
                "created_at_utc": utc_now().isoformat(),
                "updated_at_utc": utc_now().isoformat(),
                "input_hash": stable_object_hash(inputs),
                "inputs": inputs,
                "environment": {
                    "python": sys.version,
                    "executable": sys.executable,
                    "platform": platform.platform(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "pid": os.getpid(),
                    "git_revision": _git_revision(project_root),
                    "packages": package_versions(
                        [
                            "numpy",
                            "pandas",
                            "pyarrow",
                            "scikit-learn",
                            "scipy",
                            "statsmodels",
                            "matplotlib",
                            "seaborn",
                            "threadpoolctl",
                        ]
                    ),
                },
            },
            manifest_path,
        )
        return cls(run_id, directory, manifest_path)

    def update(self, **values: Any) -> None:
        manifest = read_manifest(self.manifest_path)
        manifest.update(values)
        manifest["updated_at_utc"] = utc_now().isoformat()
        atomic_json_dump(manifest, self.manifest_path)

    def complete(self, **outputs: Any) -> None:
        self.update(status="complete", completed_at_utc=utc_now().isoformat(), outputs=outputs)

    def fail(self, exc: BaseException) -> None:
        self.update(
            status="failed",
            failed_at_utc=utc_now().isoformat(),
            error_type=type(exc).__name__,
            error=str(exc),
        )

