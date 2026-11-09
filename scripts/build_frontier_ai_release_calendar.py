#!/usr/bin/env python3
"""Parse the supplied AI inventory and build a curated, immutable event calendar.

The inventory CSV is lossless with respect to simple scalar fields in the Lua
``articles`` table.  The trading calendar is deliberately driven by a reviewed
whitelist and official-provider dates, never by ex-post market returns.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


ROOT = Path(__file__).resolve().parents[1]
ENTRY = re.compile(r'^\s*(?:\["(?P<quoted>[^"]+)"\]|(?P<plain>[A-Za-z0-9_.-]+))\s*=\s*\{\s*$')
FIELD = re.compile(r'^\s*(?P<key>[A-Za-z0-9_]+)\s*=\s*"(?P<value>(?:[^"\\]|\\.)*)"\s*,?\s*$')


def _path(value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def _parse_articles(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_articles = False
    depth = 0
    current: dict[str, str] | None = None
    records: list[dict[str, str]] = []
    for line_number, line in enumerate(progress(lines, description="Parsing AI inventory", unit="line"), start=1):
        if not in_articles:
            if re.match(r"^\s*articles\s*=\s*\{", line):
                in_articles = True
                depth = 1
            continue
        if current is None:
            match = ENTRY.match(line)
            if match:
                current = {
                    "article_name": match.group("quoted") or match.group("plain"),
                    "source_line": str(line_number),
                }
                depth = 2
                continue
            if line.strip() == "},":
                break
        else:
            field = FIELD.match(line)
            if field:
                current[field.group("key")] = bytes(field.group("value"), "utf-8").decode("unicode_escape")
            if line.strip() in {"},", "}"}:
                records.append(current)
                current = None
                depth = 1
    if current is not None:
        records.append(current)
    if not records:
        raise ValueError(f"No articles parsed from {path}")
    return records


def _curated(
    events: list[dict[str, Any]],
    inventory: pd.DataFrame,
    policy: dict[str, Any],
) -> pd.DataFrame:
    indexed = inventory.set_index("article_name", drop=False)
    coverage_start = pd.Timestamp(policy["coverage_start"])
    coverage_end = pd.Timestamp(policy["coverage_end"])
    if coverage_start > coverage_end:
        raise ValueError("coverage_start must not be after coverage_end")
    allowed_providers = set(policy.get("primary_providers", [])) | set(
        policy.get("robustness_providers", [])
    )
    rows: list[dict[str, Any]] = []
    for event in progress(events, description="Validating frontier calendar", unit="event"):
        name = str(event.get("inventory_name", "")).strip()
        source: dict[str, Any] = {}
        if name and name in indexed.index:
            matched = indexed.loc[name]
            if isinstance(matched, pd.DataFrame):
                matched = matched.iloc[0]
            source = matched.to_dict()
        release_date = pd.Timestamp(event["release_date"])
        if not coverage_start <= release_date <= coverage_end:
            raise ValueError(
                f"Event is outside [{coverage_start.date()}, {coverage_end.date()}]: "
                f"{event['event_id']}"
            )
        if event["provider"] not in allowed_providers:
            raise ValueError(f"Provider is outside the declared universe: {event['provider']}")
        if not str(event.get("source_url", "")).startswith("https://"):
            raise ValueError(f"Official HTTPS source is required: {event['event_id']}")
        rows.append({
            **event,
            "release_date": str(release_date.date()),
            "time_precision": "date_only",
            "public_at_utc": f"{release_date.date()}T23:59:59+00:00",
            "tradability_rule": "first NSE 08:55 IST decision strictly after public_at_utc",
            "inventory_match": bool(source),
            "inventory_release_date": source.get("release_date", ""),
            "inventory_developer": source.get("developer", ""),
            "selection_used_returns": False,
        })
    result = pd.DataFrame(rows).sort_values(["release_date", "event_id"]).reset_index(drop=True)
    if result["event_id"].duplicated().any():
        raise ValueError("Duplicate event_id values in whitelist")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/frontier_ai_release_whitelist.yaml")
    parser.add_argument("--output-root", default="data/raw/cross_market/frontier_ai_events")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    config_path = _path(args.config)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    source_path = _path(config["inventory_source"])
    payload_hash = stable_object_hash({
        "source_sha256": sha256_file(source_path),
        "config_sha256": sha256_file(config_path),
    })[:16]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_id = f"frontier_ai_events_{stamp}_{payload_hash}"
    output = _path(args.output_root) / snapshot_id
    plan = {
        "action": "build_frontier_ai_release_calendar",
        "mode": "execute" if args.execute else "plan_only",
        "snapshot_id": snapshot_id,
        "content_hash": payload_hash,
        "inventory": str(source_path),
        "whitelist": str(config_path),
        "output": str(output),
    }
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    output.mkdir(parents=True, exist_ok=False)
    try:
        records = _parse_articles(source_path)
        keys = sorted({key for row in records for key in row}, key=lambda key: (key != "article_name", key))
        inventory = pd.DataFrame(records).reindex(columns=keys)
        inventory.to_csv(output / "model_publishing_inventory.csv", index=False, quoting=csv.QUOTE_MINIMAL)
        events = _curated(config["events"], inventory, config["policy"])
        events.to_csv(output / "frontier_ai_releases.csv", index=False)
        files = []
        for name in ["model_publishing_inventory.csv", "frontier_ai_releases.csv"]:
            files.append({"path": name, "sha256": sha256_file(output / name)})
        manifest = {
            "schema_version": 1,
            **plan,
            "status": "complete",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "inventory_source_url": config.get("inventory_source_url"),
            "inventory_sha256": sha256_file(source_path),
            "whitelist_sha256": sha256_file(config_path),
            "inventory_records": len(inventory),
            "curated_events": len(events),
            "primary_events": int(events["primary_event"].sum()),
            "coverage_start": config["policy"]["coverage_start"],
            "coverage_end": config["policy"]["coverage_end"],
            "release_scope": config["policy"]["release_scope"],
            "files": files,
        }
        atomic_json_dump(manifest, output / "manifest.json")
    except BaseException as exc:
        atomic_json_dump({**plan, "status": "failed", "error": repr(exc)}, output / "state.json")
        raise
    print(json.dumps({**plan, "status": "complete"}, indent=2))


if __name__ == "__main__":
    main()
