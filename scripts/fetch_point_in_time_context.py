"""Fetch release-aware FRED context and ingest an optional manual VIX file.

This command is plan-only unless --execute is supplied. Set FRED_API_KEY in the
environment. FRED observations are requested with all-vintage output_type=4.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from quantfin.io import atomic_json_dump, make_snapshot_id, sha256_file
from quantfin.research_extension import read_yaml


ROOT = Path(__file__).resolve().parents[1]


def fetch_json(url: str, timeout: int) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/research_extension_2026-10-21.yaml")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--start", default="2005-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--vix-csv")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--output-root", default="data/raw/fred_alfred")
    args = parser.parse_args()
    config = read_yaml(ROOT / args.config)
    series = config["external_data"]["fred_series"]
    plan = {
        "mode": "execute" if args.execute else "plan_only",
        "source": "FRED/ALFRED API",
        "series": series,
        "realtime_period": [args.start, args.end],
        "observation_period": [args.start, args.end],
        "output_type": 4,
        "requires_environment_variable": "FRED_API_KEY",
        "optional_vix_csv": args.vix_csv,
        "licensing_note": "Raw files retain source metadata and are for the declared academic analysis; review source terms before redistribution.",
    }
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise EnvironmentError("FRED_API_KEY is required only when --execute is supplied")
    snapshot_id = make_snapshot_id("fred_alfred")
    output = ROOT / args.output_root / snapshot_id
    output.mkdir(parents=True, exist_ok=False)
    files = []
    try:
        for series_id, description in series.items():
            parameters = {
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "observation_start": args.start,
                "observation_end": args.end,
                "realtime_start": args.start,
                "realtime_end": args.end,
                "output_type": 4,
            }
            url = "https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode(parameters)
            payload = fetch_json(url, args.timeout)
            observations = pd.DataFrame(payload.get("observations", []))
            if observations.empty:
                raise ValueError(f"FRED returned no observations for {series_id}")
            observations.insert(0, "series_id", series_id)
            observations.insert(1, "description", description)
            destination = output / f"{series_id}.csv"
            observations.to_csv(destination, index=False)
            files.append({"path": destination.name, "sha256": sha256_file(destination), "rows": len(observations), "series_id": series_id})
        if args.vix_csv:
            source = Path(args.vix_csv).expanduser().resolve()
            if not source.is_file():
                raise FileNotFoundError(source)
            destination = output / "vix_history.csv"
            shutil.copy2(source, destination)
            files.append({"path": destination.name, "sha256": sha256_file(destination), "rows": len(pd.read_csv(destination)), "series_id": "VIX"})
        manifest = {
            "schema_version": 1,
            "snapshot_id": snapshot_id,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "complete",
            "source": "Federal Reserve Economic Data API with real-time periods",
            "request_policy": plan,
            "files": files,
            "availability_contract": "realtime_start is the first permitted availability date; same-day values are used only at the after-close decision time.",
        }
        atomic_json_dump(manifest, output / "manifest.json")
        print(json.dumps({"snapshot_id": snapshot_id, "output_directory": str(output)}, indent=2))
    except BaseException as exc:
        atomic_json_dump({"snapshot_id": snapshot_id, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}, output / "FAILED.json")
        raise


if __name__ == "__main__":
    main()

