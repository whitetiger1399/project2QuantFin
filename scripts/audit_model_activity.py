"""Create explicit activity, invalid-metric, and signal/P&L boundary audits."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from quantfin.io import atomic_json_dump, stable_object_hash
from quantfin.research_extension import activity_tables


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", action="append", required=True, help="Repeat for every run to audit")
    parser.add_argument("--forecast-hurdle", type=float, default=0.001)
    parser.add_argument("--one-way-cost-bps", type=float, default=5.0)
    parser.add_argument("--minimum-active-sessions", type=int, default=20)
    parser.add_argument("--minimum-round-trips", type=int, default=3)
    parser.add_argument("--output-root", default="artifacts/research/activity_audits")
    args = parser.parse_args()

    summary_parts: list[pd.DataFrame] = []
    yearly_parts: list[pd.DataFrame] = []
    boundary_parts: list[pd.DataFrame] = []
    for run_id in args.run_id:
        directory = ROOT / "artifacts" / "runs" / run_id
        manifest_path = directory / "run_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "complete":
            raise ValueError(f"Run is not complete: {run_id}")
        predictions = pd.read_parquet(directory / "predictions.parquet")
        for column in ["signal_session", "entry_session", "label_end_session", "label_available_session"]:
            predictions[column] = pd.to_datetime(predictions[column])
        summary, yearly, ledger = activity_tables(
            predictions,
            forecast_hurdle=args.forecast_hurdle,
            one_way_cost_bps=args.one_way_cost_bps,
        )
        summary.insert(0, "stage", manifest["inputs"]["stage"])
        summary.insert(0, "run_id", run_id)
        summary["activity_gate_pass"] = (
            summary["active_sessions"].ge(args.minimum_active_sessions)
            & summary["completed_round_trips"].ge(args.minimum_round_trips)
            & summary["metric_status"].eq("valid")
        )
        yearly.insert(0, "stage", manifest["inputs"]["stage"])
        yearly.insert(0, "run_id", run_id)
        boundary = ledger.loc[
            ledger["signal_session"].dt.year.ne(ledger["pnl_session"].dt.year),
            ["config_id", "family", "signal_session", "trade_entry_session", "pnl_session", "target_return", "position", "net_strategy_return"],
        ].copy()
        boundary.insert(0, "stage", manifest["inputs"]["stage"])
        boundary.insert(0, "run_id", run_id)
        summary_parts.append(summary)
        yearly_parts.append(yearly)
        boundary_parts.append(boundary)

    summary_all = pd.concat(summary_parts, ignore_index=True)
    yearly_all = pd.concat(yearly_parts, ignore_index=True)
    boundary_all = pd.concat(boundary_parts, ignore_index=True)
    identity = {
        "run_ids": args.run_id,
        "forecast_hurdle": args.forecast_hurdle,
        "one_way_cost_bps": args.one_way_cost_bps,
        "minimum_active_sessions": args.minimum_active_sessions,
        "minimum_round_trips": args.minimum_round_trips,
    }
    audit_id = "activity_" + stable_object_hash(identity)[:16]
    output = ROOT / args.output_root / audit_id
    output.mkdir(parents=True, exist_ok=True)
    summary_all.to_csv(output / "activity_summary.csv", index=False)
    yearly_all.to_csv(output / "activity_by_year.csv", index=False)
    boundary_all.to_csv(output / "signal_pnl_boundary_rows.csv", index=False)
    manifest = {
        "schema_version": 1,
        "audit_id": audit_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "complete",
        "identity": identity,
        "rows": {"summary": len(summary_all), "yearly": len(yearly_all), "boundary": len(boundary_all)},
        "failed_activity_gate": int((~summary_all["activity_gate_pass"]).sum()),
        "invalid_metric_rows": int(summary_all["metric_status"].ne("valid").sum()),
    }
    atomic_json_dump(manifest, output / "manifest.json")
    print(json.dumps({**manifest, "output_directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()

