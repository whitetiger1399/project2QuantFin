"""Fetch release-aware FRED context and ingest an optional manual VIX file.

This command is plan-only unless --execute is supplied. Set FRED_API_KEY in the
environment. FRED observations use output_type=4 (initial release only).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import certifi

from quantfin.io import atomic_json_dump, make_snapshot_id, sha256_file
from quantfin.progress import progress
from quantfin.research_extension import read_yaml


ROOT = Path(__file__).resolve().parents[1]


class FredApiError(RuntimeError):
    """FRED response error with credentials and request URLs excluded."""


def fetch_json(url: str, timeout: int) -> dict:
    # Framework Python installations on macOS may not inherit the system CA
    # chain. Use certifi's maintained Mozilla bundle while keeping certificate
    # and hostname verification enabled.
    context = ssl.create_default_context(cafile=certifi.where())
    try:
        with urllib.request.urlopen(url, timeout=timeout, context=context) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
            detail = payload.get("error_message") or payload.get("message") or body
        except json.JSONDecodeError:
            detail = body
        # Do not propagate a credential if an upstream message ever echoes it.
        detail = re.sub(r"(?i)(api[_ -]?key[=:\s]+)[A-Za-z0-9]+", r"\1[REDACTED]", str(detail))
        raise FredApiError(f"FRED HTTP {exc.code}: {detail.strip()}") from None


def date_chunks(start: str, end: str, years: int) -> list[tuple[str, str]]:
    """Create adjacent closed real-time periods below FRED's vintage cap."""
    if years < 1:
        raise ValueError("realtime chunk years must be positive")
    cursor = pd.Timestamp(start).normalize()
    final = pd.Timestamp(end).normalize()
    if final < cursor:
        raise ValueError("--end must not precede --start")
    chunks: list[tuple[str, str]] = []
    while cursor <= final:
        chunk_end = min(cursor + pd.DateOffset(years=years) - pd.Timedelta(days=1), final)
        chunks.append((cursor.date().isoformat(), chunk_end.date().isoformat()))
        cursor = chunk_end + pd.Timedelta(days=1)
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/research_extension_2026-10-21.yaml")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--start", default="2005-01-01")
    parser.add_argument("--end", default="2025-12-31")
    parser.add_argument("--vix-csv")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument(
        "--realtime-chunk-years",
        type=int,
        default=5,
        help="Split ALFRED real-time periods to remain below its vintage-date limit",
    )
    parser.add_argument("--output-root", default="data/raw/fred_alfred")
    args = parser.parse_args()
    config = read_yaml(ROOT / args.config)
    if "fred_alfred" in config:
        fred_config = config["fred_alfred"]
        series = fred_config["series"]
        output_type = int(fred_config.get("output_type", 4))
    else:
        fred_config = config["external_data"]
        series = fred_config["fred_series"]
        output_type = 4
    realtime_chunks = date_chunks(args.start, args.end, args.realtime_chunk_years)
    plan = {
        "mode": "execute" if args.execute else "plan_only",
        "source": "FRED/ALFRED API",
        "series": series,
        "realtime_period": [args.start, args.end],
        "observation_period": [args.start, args.end],
        "output_type": output_type,
        "realtime_chunks": realtime_chunks,
        "request_count": len(series) * len(realtime_chunks),
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
    if not re.fullmatch(r"[a-z0-9]{32}", api_key):
        raise EnvironmentError(
            "FRED_API_KEY has an invalid format. Enter only the 32-character lowercase "
            "alphanumeric key, without the account URL, Markdown, quotes, or surrounding spaces."
        )
    snapshot_id = make_snapshot_id("fred_alfred")
    output = ROOT / args.output_root / snapshot_id
    output.mkdir(parents=True, exist_ok=False)
    files = []
    try:
        tasks = [
            (series_id, description, realtime_start, realtime_end)
            for series_id, description in series.items()
            for realtime_start, realtime_end in realtime_chunks
        ]
        observations_by_series: dict[str, list[pd.DataFrame]] = {
            series_id: [] for series_id in series
        }
        availability_mode: dict[str, str] = {
            series_id: "alfred_initial_release" for series_id in series
        }
        current_vintage_fallbacks: dict[str, str] = {}
        for series_id, description, realtime_start, realtime_end in progress(
            tasks, description="FRED/ALFRED download", total=len(tasks), unit="request"
        ):
            if series_id in current_vintage_fallbacks:
                continue
            parameters = {
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "observation_start": args.start,
                "observation_end": args.end,
                "realtime_start": realtime_start,
                "realtime_end": realtime_end,
                "output_type": output_type,
            }
            url = "https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode(parameters)
            try:
                payload = fetch_json(url, args.timeout)
            except FredApiError as exc:
                if "does not exist in ALFRED" not in str(exc):
                    raise FredApiError(
                        f"series={series_id}, realtime={realtime_start}..{realtime_end}: {exc}"
                    ) from None
                # Some non-revisable financial series are published in FRED but
                # have no ALFRED archive. Fetch the current-vintage history once
                # and label it explicitly; never imply it is release-vintage data.
                fallback_parameters = {
                    "series_id": series_id,
                    "api_key": api_key,
                    "file_type": "json",
                    "observation_start": args.start,
                    "observation_end": args.end,
                    "output_type": 1,
                }
                fallback_url = (
                    "https://api.stlouisfed.org/fred/series/observations?"
                    + urllib.parse.urlencode(fallback_parameters)
                )
                payload = fetch_json(fallback_url, args.timeout)
                observations = pd.DataFrame(payload.get("observations", []))
                if observations.empty:
                    raise ValueError(f"FRED current-vintage fallback returned no observations for {series_id}")
                observations["request_realtime_start"] = "CURRENT_FRED"
                observations["request_realtime_end"] = "CURRENT_FRED"
                observations_by_series[series_id] = [observations]
                availability_mode[series_id] = "current_vintage_fallback"
                current_vintage_fallbacks[series_id] = str(exc)
                continue
            observations = pd.DataFrame(payload.get("observations", []))
            if not observations.empty:
                observations["request_realtime_start"] = realtime_start
                observations["request_realtime_end"] = realtime_end
                observations_by_series[series_id].append(observations)

        for series_id, description in series.items():
            chunks = observations_by_series[series_id]
            if not chunks:
                raise ValueError(f"FRED returned no observations for {series_id} across all chunks")
            observations = pd.concat(chunks, ignore_index=True)
            identity_columns = [
                column
                for column in ("realtime_start", "realtime_end", "date", "value")
                if column in observations.columns
            ]
            observations = observations.drop_duplicates(identity_columns).sort_values(identity_columns)
            observations.insert(0, "series_id", series_id)
            observations.insert(1, "description", description)
            destination = output / f"{series_id}.csv"
            observations.to_csv(destination, index=False)
            files.append(
                {
                    "path": destination.name,
                    "sha256": sha256_file(destination),
                    "rows": len(observations),
                    "series_id": series_id,
                    "request_chunks_with_rows": len(chunks),
                    "availability_mode": availability_mode[series_id],
                }
            )
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
            "current_vintage_fallbacks": current_vintage_fallbacks,
            "availability_contract": "realtime_start is the first permitted availability date; a value may enter the Nifty IT signal only if that date and the source release time precede 08:55 Asia/Kolkata.",
            "limitations": [
                "Series marked alfred_initial_release retain initial-release availability information.",
                "Series marked current_vintage_fallback are current FRED histories and require an official effective-date or release-time audit before predictive use.",
            ],
        }
        atomic_json_dump(manifest, output / "manifest.json")
        print(json.dumps({"snapshot_id": snapshot_id, "output_directory": str(output)}, indent=2))
    except BaseException as exc:
        atomic_json_dump({"snapshot_id": snapshot_id, "status": "failed", "error": f"{type(exc).__name__}: {exc}"}, output / "FAILED.json")
        raise


if __name__ == "__main__":
    main()

