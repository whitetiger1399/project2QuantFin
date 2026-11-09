"""Check or initialize the repository's cross-platform Git LFS configuration."""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("*.parquet", "*.csv", "*.png", "*.jpg", "*.jpeg", "*.pdf", "*.docx", "*.zip", "*.mp4")


def run(*args: str) -> str:
    result = subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=True)
    return (result.stdout or result.stderr).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help="Run 'git lfs install' for this user/repository.")
    args = parser.parse_args()
    if not shutil.which("git"):
        raise SystemExit("Git is not installed or is not on PATH.")
    try:
        version = run("git", "lfs", "version")
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise SystemExit("Git LFS is not installed. Install it, reopen the terminal, and run this script again.") from exc
    attrs = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    missing = [pattern for pattern in REQUIRED if pattern not in attrs]
    if missing:
        raise SystemExit("Missing Git LFS patterns: " + ", ".join(missing))
    if args.install:
        print(run("git", "lfs", "install"))
    print(version)
    print("Git LFS attributes: OK")
    print("Raw vendor downloads remain ignored; processed datasets, artifacts and reports are eligible for Git LFS.")


if __name__ == "__main__":
    main()
