#!/usr/bin/env python3
"""Six exploratory hypotheses with frozen input paths, checkpoints and honest missingness."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from quantfin.cross_market.hypotheses import (
    adjust_tests, regression, return_summary, block_indices, headcount_changes,
)
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress

ROOT = Path(__file__).resolve().parents[1]


def path(value):
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


def daily_panel(paths, start, end):
    frames = []
    wanted = ["decision_date", "asset", "target_oc_return", "own__ret_lag_1",
              "nifty50_aggregate__mean", "us_it_services_aggregate__mean",
              "ai_event__frontier_release_today"]
    for folder in paths:
        frames.append(pd.read_parquet(folder / "panel.parquet", columns=wanted))
    panel = pd.concat(frames, ignore_index=True)
    panel["decision_date"] = pd.to_datetime(panel["decision_date"])
    panel = panel.loc[panel.decision_date.between(start, end)]
    keys = ["decision_date", "asset"]
    duplicate_mask = panel.duplicated(keys, keep=False)
    if duplicate_mask.any():
        compared = wanted[2:]
        distinct = panel.loc[duplicate_mask].groupby(keys, dropna=False)[compared].nunique(dropna=False)
        conflicting = distinct.gt(1).any(axis=1)
        if conflicting.any():
            examples = [tuple(value) for value in conflicting.index[conflicting][:5]]
            raise ValueError(
                "Overlapping panel dates/assets disagree on hypothesis inputs; "
                f"examples: {examples}"
            )
        # The historical and forward panels intentionally share the pre-2026
        # training history. Reconcile only byte-equivalent hypothesis inputs;
        # conflicting overlap remains a hard failure above.
        panel = panel.drop_duplicates(keys, keep="first")
    daily = panel.groupby("decision_date")[wanted[2:]].mean().rename(columns={
        "target_oc_return": "india_oc", "own__ret_lag_1": "india_lag",
        "nifty50_aggregate__mean": "market_lag",
        "us_it_services_aggregate__mean": "us_lag",
        "ai_event__frontier_release_today": "event",
    })
    daily["event"] = daily.event.gt(0).astype(float)
    daily["const"] = 1.
    return daily.sort_index()


def run_tests(daily, args):
    rows = []
    def add(h, period, frame, terms, term, sign, minimum=None):
        rows.append({"hypothesis": h, "period": period, "expected_sign": sign,
                     **regression(frame, "india_oc", terms, term, minimum_events=minimum)})
    periods = {"all": daily, **{str(y): g for y, g in daily.groupby(daily.index.year)}}
    for label, group in progress(periods.items(), description="H1-H2 date-level regressions", unit="period"):
        add("H1_US_transmission", label, group, ["us_lag", "india_lag", "market_lag"], "us_lag", 1)
        # Total event association: do not control for the potential U.S. mediator.
        group = group.loc[group.index >= "2023-01-01"]
        add("H2_negative_AI_release", label, group, ["event", "india_lag", "market_lag"],
            "event", -1, {"event": args.minimum_events})
    event_sample = daily.loc[daily.index >= "2023-01-01"].copy()
    event_sample["late"] = (event_sample.index >= pd.Timestamp(args.break_date)).astype(float)
    event_sample["early_event"] = event_sample.event * (1 - event_sample.late)
    event_sample["late_event"] = event_sample.event * event_sample.late
    # Positive interaction means later-minus-earlier response is more positive.
    add("H3_event_attenuation", "fixed_break_" + args.break_date, event_sample,
        ["event", "late", "late_event", "india_lag", "market_lag"], "late_event", 1,
        {"early_event": args.minimum_events, "late_event": args.minimum_events})
    for term in ["early_event", "late_event"]:
        add("H3_period_event_effect", term, event_sample,
            ["early_event", "late_event", "late", "india_lag", "market_lag"], term, -1,
            {"early_event": args.minimum_events, "late_event": args.minimum_events})
    daily = daily.copy()
    daily["late"] = (daily.index >= pd.Timestamp(args.break_date)).astype(float)
    daily["us_late"] = daily.us_lag * daily.late
    add("H1_US_transmission_change", "fixed_break_" + args.break_date, daily,
        ["us_lag", "late", "us_late", "india_lag", "market_lag"], "us_late", -1)
    return rows


def capability_test(daily, source, minimum_events):
    base = {"hypothesis": "H4_capability_shock", "period": "all_ex_post",
            "expected_sign": -1, "pvalue": None, "coefficient": None}
    if source is None:
        return [dict(base, status="missing_capability_table")], pd.DataFrame()
    events = pd.read_csv(source)
    events["tradable_date"] = pd.to_datetime(events["tradable_date"])
    events["release_date"] = pd.to_datetime(events["release_date"])
    # Same-release-date models cannot define a within-day ordering of capability surprises.
    frontier = events.groupby("release_date").eci.max().sort_index().dropna()
    previous = frontier.cummax().shift(1)
    events["previous_frontier"] = events.release_date.map(previous)
    events["capability_increment"] = (events.eci - events.previous_frontier).clip(lower=0)
    events = events.loc[events.tradable_date.isin(daily.index)].copy()
    table = events.groupby("tradable_date").agg(capability_increment=("capability_increment", "max"),
                                                release_count=("event_id", "count"))
    table = table.join(daily[["india_oc", "india_lag", "market_lag"]])
    table["time_years"] = (table.index - pd.Timestamp("2023-01-01")).days / 365.25
    if table.capability_increment.notna().sum() < max(30, minimum_events):
        return [dict(base, status="insufficient_scored_event_dates", n_dates=int(table.capability_increment.notna().sum()))], table
    result = regression(table, "india_oc", ["capability_increment", "time_years", "india_lag", "market_lag"],
                        "capability_increment", covariance="HC3")
    return [{**base, **result}], table


def portfolio_tests(folders, repetitions, block, seed):
    rows, metrics = [], []
    rng = np.random.default_rng(seed)
    for folder in folders:
        manifest = json.loads((folder / "manifest.json").read_text())
        if manifest.get("status") != "complete":
            raise ValueError(f"Incomplete run {folder}")
        ledger = pd.read_parquet(folder / "strategy_ledgers.parquet")
        ledger = ledger.loc[ledger.config_id.eq(manifest["selected_config_id"])].copy()
        ledger["decision_date"] = pd.to_datetime(ledger.decision_date)
        ledger = ledger.sort_values("decision_date")
        if ledger.decision_date.duplicated().any():
            raise ValueError("Selected ledger must contain one portfolio return per date")
        groups = {"all": ledger, **{str(y): g for y, g in ledger.groupby(ledger.decision_date.dt.year)}}
        for period, group in groups.items():
            frame = group.copy()
            frame["const"] = 1.
            frame["excess_nifty50"] = frame.net_return - frame.benchmark_nifty50
            for outcome, h in [("net_return", "H5_positive_net_return"), ("excess_nifty50", "H5_beats_Nifty50")]:
                rows.append({"hypothesis": h, "period": folder.name + ":" + period, "expected_sign": 1,
                             **regression(frame, outcome, [], "const")})
            metrics.append({"run_id": folder.name, "period": period, "basis": "net",
                            **return_summary(group.net_return)})
        x = ledger.net_return.to_numpy()
        draws = []
        for _ in progress(range(repetitions), description=f"H5 bootstrap {manifest['stage']}", unit="draw"):
            sample = x[block_indices(len(x), block, rng)]
            draws.append(return_summary(sample)["sharpe_zero_cash"])
        finite = np.array([v for v in draws if v is not None and np.isfinite(v)])
        for row in metrics:
            if row["run_id"] == folder.name and row["period"] == "all" and len(finite):
                row.update(sharpe_ci_low=float(np.quantile(finite, .025)),
                           sharpe_ci_high=float(np.quantile(finite, .975)))
    return rows, pd.DataFrame(metrics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset", action="append", required=True,
        help="Dataset directory; exact overlapping hypothesis inputs are reconciled, conflicts fail",
    )
    parser.add_argument("--run", action="append", default=[], help="Completed run directory; repeat for screening/confirmation")
    parser.add_argument("--epoch-events", help="Existing epoch_event_capability_returns.csv; retrospective only")
    parser.add_argument("--company-evidence", default="configs/company_adaptation_evidence_2026-11-01.json")
    parser.add_argument("--start", default="2021-01-01")
    parser.add_argument("--end", default="2026-09-30")
    parser.add_argument("--break-date", default="2025-01-01")
    parser.add_argument("--minimum-events", type=int, default=8)
    parser.add_argument("--bootstrap-draws", type=int, default=2000)
    parser.add_argument("--block-sessions", type=int, default=20)
    parser.add_argument("--seed", type=int, default=5205)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume-analysis-id")
    args = parser.parse_args()
    if args.bootstrap_draws < 100 or args.block_sessions < 1 or args.minimum_events < 3:
        parser.error("Use >=100 draws, >=1 block session and >=3 minimum events")
    datasets, runs = [path(p) for p in args.dataset], [path(p) for p in args.run]
    evidence = path(args.company_evidence)
    epoch = path(args.epoch_events) if args.epoch_events else None
    files = [evidence, Path(__file__), ROOT / "src/quantfin/cross_market/hypotheses.py"]
    for d in datasets:
        files += [d / "manifest.json", d / "panel.parquet"]
    for r in runs:
        files += [r / "manifest.json", r / "strategy_ledgers.parquet"]
    if epoch:
        files.append(epoch)
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in files}
    settings = {k: v for k, v in vars(args).items() if k not in {"execute", "resume_analysis_id"}}
    content_hash = stable_object_hash({"settings": settings, "inputs": hashes})[:16]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.resume_analysis_id or f"hypotheses_{stamp}_{content_hash}"
    if Path(run_id).name != run_id:
        parser.error("Resume ID must be a directory name")
    output = ROOT / "artifacts/research_hypotheses" / run_id
    plan = {"analysis_id": run_id, "content_hash": content_hash, "directory": str(output),
            "classification": "exploratory_after_prior_result_inspection", "settings": settings,
            "input_hashes": hashes, "created_at_utc": datetime.now(timezone.utc).isoformat()}
    print(json.dumps({**plan, "status": "starting" if args.execute else "plan_only"}, indent=2), flush=True)
    if not args.execute:
        return
    if args.resume_analysis_id:
        previous = json.loads((output / "run_state.json").read_text())
        if previous["content_hash"] != content_hash:
            raise ValueError("Resume inputs/code/settings changed; create a fresh analysis")
    else:
        output.mkdir(parents=True, exist_ok=False)
    atomic_json_dump({**plan, "status": "running"}, output / "run_state.json")
    # Restart is safe: only this analysis directory is rewritten; source runs are read-only.
    daily = daily_panel(datasets, pd.Timestamp(args.start), pd.Timestamp(args.end))
    if daily.empty:
        raise ValueError("No dates in the requested interval")
    rows = run_tests(daily, args)
    h4, event_table = capability_test(daily, epoch, args.minimum_events)
    rows.extend(h4)
    checkpoint = output / "portfolio_checkpoint.json"
    if args.resume_analysis_id and checkpoint.exists():
        saved = json.loads(checkpoint.read_text())
        if saved["content_hash"] != content_hash:
            raise ValueError("Checkpoint hash does not match")
        if stable_object_hash(saved["payload"]) != saved["payload_hash"]:
            raise ValueError("Portfolio checkpoint content is corrupt")
        h5 = saved["payload"]["tests"]
        performance = pd.DataFrame(saved["payload"]["performance"])
        print("Reusing verified portfolio inference checkpoint", flush=True)
    else:
        h5, performance = portfolio_tests(runs, args.bootstrap_draws, args.block_sessions, args.seed)
        payload = {"tests": h5, "performance": json.loads(performance.to_json(orient="records"))}
        atomic_json_dump({"content_hash": content_hash, "payload": payload,
                          "payload_hash": stable_object_hash(payload)}, checkpoint)
    rows.extend(h5)
    company = json.loads(evidence.read_text())
    changes = headcount_changes(company["observations"])
    tests = adjust_tests(rows)
    tests.to_csv(output / "hypothesis_tests.csv", index=False)
    performance.to_csv(output / "portfolio_periods.csv", index=False)
    changes.to_csv(output / "company_headcount_changes.csv", index=False)
    event_table.to_csv(output / "capability_event_dates.csv")
    daily.to_csv(output / "daily_analysis_inputs.csv")
    counts = daily.groupby(daily.index.year).agg(sessions=("event", "size"), event_sessions=("event", "sum"))
    counts.to_csv(output / "event_coverage_by_year.csv")
    plots = output / "plots"
    plots.mkdir(exist_ok=True)
    for h, title in progress([("H1_US_transmission", "U.S. services association with next Indian intraday return"),
                              ("H2_negative_AI_release", "AI release association with Indian intraday return")],
                             description="Rendering hypothesis evidence", unit="plot"):
        table = tests.loc[tests.hypothesis.eq(h) & tests.status.eq("estimated")]
        if table.empty:
            continue
        fig, ax = plt.subplots(figsize=(9, 4.5))
        y = np.arange(len(table))
        ax.errorbar(table.coefficient, y, xerr=np.vstack([table.coefficient-table.ci_low, table.ci_high-table.coefficient]), fmt="o", color="#12385b", capsize=4)
        ax.set_yticks(y, table.period); ax.axvline(0, color="grey", lw=1)
        ax.set_title(title); ax.set_xlabel("Regression coefficient; pointwise 95% HAC interval\nHolm-adjusted p-values in hypothesis_tests.csv")
        fig.tight_layout(); fig.savefig(plots / f"{h}.png", dpi=220); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for company_name, group in changes.groupby("company"):
        group = group.sort_values("period_end")
        ax.plot(group.period_end, 100 * group.headcount / group.headcount.iloc[0], marker="o", label=company_name)
    ax.set_title("Reported workforce: within-company indexed change")
    ax.set_ylabel("First available observation = 100"); ax.legend(); fig.autofmt_xdate()
    fig.tight_layout(); fig.savefig(plots / "H6_headcount.png", dpi=220); plt.close(fig)
    notes = ["# Exploratory hypothesis evidence", "",
             "These are new analyses of previously examined history, not new independent confirmation.",
             "H1 is conditional association, not causation. H2 uses conservatively mapped tradable dates, not exact announcement timestamps.",
             "H3 attenuation requires a negative earlier effect as well as a positive interaction; a positive interaction alone is insufficient.",
             "H4 uses retrospectively compiled capability scores and cannot be used as a historical trading signal.",
             "H5 uses existing frozen ledgers. Benchmark returns have different overnight exposure. No models or policies are selected here.",
             "H6 is descriptive: a few quarterly workforce totals cannot identify an AI treatment effect or support a workforce t-test.",
             "Sparse/constant designs are reported as not estimable. A nonsignificant result does not establish no effect.",
             "All regression p-values are corrected together with Holm; displayed intervals are pointwise, not simultaneous.",
             f"Market panel coverage: {daily.index.min().date()} to {daily.index.max().date()}.",
             "Overnight gap decomposition remains pending a verified same-session adjusted OHLC outcome dataset; lagged gap features are not substituted.",
             "Use company publications only as retrospective discussion; their release dates may follow the test endpoint.", "", "## Company evidence sources", ""]
    notes += [f"- [{s['title']}]({s['url']}) — {s['interpretation']}" for s in company["sources"]]
    (output / "interpretation.md").write_text("\n".join(notes) + "\n")
    products = {str(p.relative_to(output)): sha256_file(p) for p in output.rglob("*")
                if p.is_file() and p.name not in {"manifest.json", "run_state.json"}}
    atomic_json_dump({**plan, "status": "complete", "files": products,
                      "completed_at_utc": datetime.now(timezone.utc).isoformat()}, output / "manifest.json")
    atomic_json_dump({**plan, "status": "complete"}, output / "run_state.json")
    print(json.dumps({"analysis_id": run_id, "status": "complete", "directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()
