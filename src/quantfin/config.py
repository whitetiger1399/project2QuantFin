"""Configuration loading and project-relative path resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def find_project_root(start: Path | None = None) -> Path:
    """Find the nearest parent containing pyproject.toml and configs/."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "configs").is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not locate the project root. Run the command inside project2QuantFin "
        "or pass a config path located below the project root."
    )


def load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).expanduser().resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a YAML mapping in {config_path}")
    return loaded


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    raw: Path
    processed: Path
    artifacts: Path

    @classmethod
    def from_protocol(cls, protocol: dict[str, Any], root: Path) -> "ProjectPaths":
        configured = protocol.get("paths", {})

        def resolve(key: str, default: str) -> Path:
            value = Path(configured.get(key, default))
            return value if value.is_absolute() else root / value

        return cls(
            root=root,
            raw=resolve("raw_dir", "data/raw"),
            processed=resolve("processed_dir", "data/processed"),
            artifacts=resolve("artifacts_dir", "artifacts"),
        )


def load_protocol(path: str | Path) -> tuple[dict[str, Any], ProjectPaths]:
    config_path = Path(path).expanduser().resolve()
    protocol = load_yaml(config_path)
    root = find_project_root(config_path.parent)
    return protocol, ProjectPaths.from_protocol(protocol, root)

