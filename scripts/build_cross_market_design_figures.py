#!/usr/bin/env python3
"""Build compact report diagrams for the cross-market Nifty IT research design."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from textwrap import fill

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from quantfin.cross_market.common import environment_record, load_research_config, root_path
from quantfin.io import atomic_json_dump, sha256_file, stable_object_hash
from quantfin.progress import progress


NAVY = "#003D7C"
ORANGE = "#EF7C00"
TEAL = "#2A9D8F"
PALE_BLUE = "#EAF2F8"
PALE_ORANGE = "#FFF1E2"
PALE_TEAL = "#E8F6F3"
INK = "#17202A"
MUTED = "#5D6D7E"
LINE = "#AAB7B8"


def _box(ax, xy, width, height, title, body, *, face=PALE_BLUE, edge=NAVY, title_size=10, body_size=8.2):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.4, edgecolor=edge, facecolor=face,
        transform=ax.transAxes, clip_on=False,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height - 0.045, title, ha="center", va="top", fontsize=title_size, fontweight="bold", color=edge, transform=ax.transAxes)
    wrapped = "\n".join(fill(line, 31) for line in body.splitlines())
    ax.text(x + width / 2, y + height - 0.085, wrapped, ha="center", va="top", fontsize=body_size, color=INK, linespacing=1.22, transform=ax.transAxes)
    return patch


def _arrow(ax, start, end, *, color=LINE, width=1.5, style="-|>"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=13, linewidth=width, color=color, transform=ax.transAxes, clip_on=False))


def _header(ax, title, subtitle):
    ax.text(0.02, 0.965, title, ha="left", va="top", fontsize=17, fontweight="bold", color=NAVY, transform=ax.transAxes)
    ax.text(0.02, 0.918, subtitle, ha="left", va="top", fontsize=9.5, color=MUTED, transform=ax.transAxes)
    ax.plot([0.02, 0.98], [0.89, 0.89], color=ORANGE, linewidth=2.0, transform=ax.transAxes, clip_on=False)


def _finish(fig, output: Path):
    fig.savefig(output, dpi=240, bbox_inches="tight", facecolor="white")
    fig.savefig(output.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def research_architecture(output: Path):
    fig, ax = plt.subplots(figsize=(14, 8)); ax.set_axis_off()
    _header(ax, "Cross-market information architecture", "Observed information is aligned to 08:55 IST; arrows denote predictive inputs, not causal claims.")
    _box(ax, (0.02, 0.61), .19, .21, "India market", "10 fixed current Nifty IT constituents; Nifty IT, Nifty 50, Bank, India VIX, ETFs and USD/INR", face=PALE_ORANGE, edge=ORANGE)
    _box(ax, (0.02, 0.35), .19, .21, "United States", "20 liquid technology stocks; INFY/WIT ADRs; SPY, QQQ and sector/risk proxies; PIT S&P 500", face=PALE_BLUE, edge=NAVY)
    _box(ax, (0.02, 0.09), .19, .21, "Global and macro", "Completed overseas sessions; FRED/ALFRED rates, curves, credit spreads, FX and volatility", face=PALE_TEAL, edge=TEAL)

    _box(ax, (0.27, 0.34), .18, .31, "Availability and quality gate", "Immutable snapshots and hashes\nOHLC quarantine\nStrict source session < decision date\nRelease/vintage lags\nTraining-only transformations", face="#F8F9F9", edge=MUTED, body_size=8.5)
    for y in [.715, .455, .195]: _arrow(ax, (.21, y), (.27, .495))

    ladder = [
        ("F0", "Own history + calendar"), ("F1", "+ India context"), ("F2", "+ US technology + ADRs"),
        ("F3", "+ broad/global context"), ("F4", "+ PIT S&P 500 detail"), ("F5", "+ macro + nonlinear robustness"),
    ]
    y0 = .735
    for index, (label, body) in enumerate(ladder):
        y = y0 - index * .115
        _box(ax, (.50, y), .20, .098, label, body, face=PALE_BLUE if index < 5 else PALE_ORANGE, edge=NAVY if index < 5 else ORANGE, title_size=9.2, body_size=7.2)
    _arrow(ax, (.45, .495), (.50, .495))

    _box(ax, (.76, .62), .22, .20, "Daily pooled forecast", "Target for stock i on NSE day t:\n yᵢ,ₜ = Closeᵢ,ₜ / Openᵢ,ₜ − 1\nTen-stock cross-section; stock fixed effects", face=PALE_TEAL, edge=TEAL)
    _box(ax, (.76, .36), .22, .20, "Shrinkage and nonlinear models", "Baselines; Ridge; LASSO; Elastic Net; PCA-Ridge; trees; boosting; random Fourier feature Ridge", face=PALE_BLUE, edge=NAVY)
    _box(ax, (.76, .10), .22, .20, "Trading and evaluation", "Rank forecasts; long top-k above costs; open→close execution; compare ITBEES, NIFTYBEES and equal-weight cohort", face=PALE_ORANGE, edge=ORANGE)
    _arrow(ax, (.70, .495), (.76, .72)); _arrow(ax, (.87, .62), (.87, .56)); _arrow(ax, (.87, .36), (.87, .30))
    ax.text(.50, .035, "Primary question: does progressively richer pre-open information improve daily Indian IT forecasts and post-cost performance?", ha="center", va="center", fontsize=10, color=INK, fontweight="bold", transform=ax.transAxes)
    _finish(fig, output)


def experiment_design(output: Path):
    fig, ax = plt.subplots(figsize=(14, 8)); ax.set_axis_off()
    _header(ax, "Experiment design and selection funnel", "Three controlled comparisons isolate information, model family and functional complexity before the final holdout is opened.")
    lane_y = [.67, .43, .19]
    lane_titles = ["A  Incremental information", "B  Model-family comparison", "C  Virtue-of-complexity test"]
    lane_bodies = [
        "F0 → F1 → F2 → F3 → F4 → F5\nSame Ridge shrinkage; attribute changes to information set",
        "F4 held fixed\nRidge, sparse linear models, PCA-Ridge, RF, Extra Trees and HGB",
        "F2 held fixed\nRFF/input ratios 0.5, 1, 2, 5, 10, 15 with Ridge shrinkage",
    ]
    lane_colors = [(PALE_ORANGE, ORANGE), (PALE_BLUE, NAVY), (PALE_TEAL, TEAL)]
    for y, title, body, colors in zip(lane_y, lane_titles, lane_bodies, lane_colors):
        _box(ax, (.03, y), .35, .16, title, body, face=colors[0], edge=colors[1], title_size=10, body_size=8.5)
        _arrow(ax, (.38, y + .08), (.45, y + .08))

    _box(ax, (.45, .57), .19, .25, "Screening", "2021–2022\n36 configurations\n8 quarterly refits\nDaily OOS predictions\nPost-cost ranking", face=PALE_BLUE, edge=NAVY)
    _box(ax, (.68, .57), .14, .25, "Confirmation", "2023–2024\n≤10 candidates\nQuarterly refits\nSame metrics", face=PALE_TEAL, edge=TEAL)
    _box(ax, (.85, .57), .13, .25, "Freeze one", "One model\nOne feature set\nOne strategy rule\nHashed record", face=PALE_ORANGE, edge=ORANGE)
    _arrow(ax, (.64, .695), (.68, .695)); _arrow(ax, (.82, .695), (.85, .695))

    _box(ax, (.45, .20), .53, .23, "Final holdout: 2025–29 October 2026", "Monthly refits for the frozen model only • Forecast baselines retained for comparison • Net costs, OOS R², IC, Sharpe, drawdown, turnover, alpha, cost sensitivity and grouped permutation importance", face="#F8F9F9", edge=MUTED, title_size=11, body_size=9)
    _arrow(ax, (.915, .57), (.82, .43))
    ax.text(.03, .075, "Integrity controls", fontsize=10.5, fontweight="bold", color=NAVY, transform=ax.transAxes)
    ax.text(.03, .035, "Chronological splits • one-session embargo • training-only imputation/scaling/selection • no final-test retuning • explicit transaction costs", fontsize=9.2, color=INK, transform=ax.transAxes)
    _finish(fig, output)


def timing_design(output: Path):
    fig, ax = plt.subplots(figsize=(14, 6.8)); ax.set_axis_off()
    _header(ax, "Leakage-safe daily information clock", "Every feature must be observable before the 08:55 IST decision; the target is realized only after execution.")
    y = .53
    ax.plot([.06, .95], [y, y], color=LINE, linewidth=2.2, transform=ax.transAxes)
    events = [
        (.10, "Prior India close", "NSE t−1\nprices and volume", NAVY),
        (.29, "Completed US close", "US t−1\ntech, ADRs, S&P 500", TEAL),
        (.48, "08:55 IST", "Decision timestamp\nfeatures locked", ORANGE),
        (.66, "09:15 IST", "Enter selected stocks\nat reported NSE open", NAVY),
        (.86, "15:30 IST", "Exit at NSE close\ntarget becomes known", TEAL),
    ]
    for x, title, body, color in events:
        ax.scatter([x], [y], s=150, color=color, edgecolor="white", linewidth=1.5, transform=ax.transAxes, zorder=3)
        above = x not in {.29, .66}
        yy = .68 if above else .28
        ax.text(x, yy + .07, title, ha="center", va="center", fontsize=10, fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(x, yy, body, ha="center", va="top", fontsize=8.5, color=INK, linespacing=1.25, transform=ax.transAxes)
        ax.plot([x, x], [y, yy + (.01 if above else .13)], color=color, linewidth=1.0, linestyle="--", transform=ax.transAxes)
    _box(ax, (.06, .025), .40, .15, "Allowed at 08:55", "Latest completed sessions and known calendar\nReleased or vintage-adjusted macro data", face=PALE_TEAL, edge=TEAL, body_size=8.2)
    _box(ax, (.54, .025), .40, .15, "Forbidden at 08:55", "Same-day NSE OHLC or unfinished Asian sessions\nInformation released after the decision", face="#FDEDEC", edge="#9B2226", body_size=8.2)
    _finish(fig, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/cross_market_research.yaml")
    parser.add_argument("--output-root", default="artifacts/cross_market/report_figures")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    config = load_research_config(args.config)
    code_hash = sha256_file(Path(__file__))
    content_hash = stable_object_hash({"action": "cross_market_design_figures", "config": sha256_file(root_path(args.config)), "code": code_hash})[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    figure_id = f"design_figures_{stamp}_{content_hash}"
    output = root_path(args.output_root) / figure_id
    plan = {"action": "build_cross_market_design_figures", "figure_id": figure_id, "content_hash": content_hash, "directory": str(output)}
    if args.plan_only:
        print(json.dumps(plan, indent=2)); return
    print(json.dumps({**plan, "status": "starting"}, indent=2), flush=True)
    output.mkdir(parents=True, exist_ok=False)
    jobs = [
        ("10_research_architecture.png", research_architecture),
        ("11_experiment_design.png", experiment_design),
        ("12_information_clock.png", timing_design),
    ]
    for filename, builder in progress(jobs, description="Building design figures", total=len(jobs), unit="figure"):
        builder(output / filename)
    record = {
        "schema_version": 1, **plan, "status": "complete", "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": sha256_file(root_path(args.config)), "script_sha256": code_hash,
        "files": {path.name: sha256_file(path) for path in sorted(output.glob("*")) if path.is_file()},
        "environment": environment_record(),
    }
    atomic_json_dump(record, output / "manifest.json")
    print(json.dumps({"figure_id": figure_id, "status": "complete", "directory": str(output)}, indent=2))


if __name__ == "__main__":
    main()
