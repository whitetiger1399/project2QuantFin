"""Build the final DSA5205 report from the verified AI-capability evidence chain."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from quantfin.cross_market.timing import map_release_sessions

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_components import (  # noqa: E402
    NUS_BLUE, MUTED, PALE, PALE_BLUE, TEXT, callout, configure, equation,
    figure, hyperlink, margins, set_widths, shade, table,
)

OUT = ROOT / "reports/Project2_Team16_Report.docx"
FIG = ROOT / "reports/figures_ai_capability"
FIG.mkdir(parents=True, exist_ok=True)
LOGO = ROOT / "assets/nus_logo_full-vertical.jpg"
GITHUB = "https://github.com/whitetiger1399/project2QuantFin"

def evidence_id(name: str, default: str) -> str:
    """Allow a verified rerun to be rendered without editing report source code."""
    return os.environ.get(f"REPORT_{name}", default)


DATASET_ID = evidence_id("DATASET_ID", "ai_capability_panel_20261031T063249Z_928de985ea1dd4f8")
SCREEN_ID = evidence_id("SCREENING_RUN_ID", "cm_ai_capability_screening_20261031T063709Z_72f2f3e05783")
CONFIRM_ID = evidence_id("CONFIRMATION_RUN_ID", "cm_ai_capability_confirmation_20261031T065831Z_c343cf83e423")
FREEZE_ID = evidence_id("FREEZE_ID", "cm_ai_capability_freeze_20261031T071336Z_cb837a5393f8")
FINAL_ID = evidence_id("FINAL_RUN_ID", "cm_ai_capability_final_test_20261031T071400Z_864e226d8bad")
FORWARD_ID = evidence_id("FORWARD_RUN_ID", "cm_ai_capability_2026_forward_20261031T072912Z_885ecbb56a0e")
SELECTED = evidence_id("SELECTED_CONFIG_ID", "cm_extra_trees_05a83581b70b")

DATASET = ROOT / "data/processed/cross_market_ai_capability" / DATASET_ID
RUN_ROOT = ROOT / "artifacts/cross_market_ai_capability/runs"
SCREEN = RUN_ROOT / SCREEN_ID
CONFIRM = RUN_ROOT / CONFIRM_ID
FINAL = RUN_ROOT / FINAL_ID
FREEZE = ROOT / "artifacts/cross_market_ai_capability/freezes" / f"{FREEZE_ID}.json"
FORWARD = ROOT / "artifacts/cross_market_ai_capability_2026/runs" / FORWARD_ID
ANALYSIS = ROOT / "artifacts/cross_market_ai_capability/analysis"
EDA = ANALYSIS / evidence_id("EDA_RUN_ID", "analysis_20261031T063553Z_097995f05f05")
CAP = ANALYSIS / evidence_id("CAPABILITY_ANALYSIS_ID", "ai_capability_analysis_20261031T063601Z_4719ed6d75af")
EPOCH = ANALYSIS / evidence_id("EPOCH_ANALYSIS_ID", "epoch_capability_analysis_20261031T063613Z_f3595944da18")
LADDER = ANALYSIS / evidence_id("LADDER_ANALYSIS_ID", "information_ladder_final_test_20261031T072347Z_d260aa005d7a")
EVIDENCE = ANALYSIS / evidence_id("MODEL_EVIDENCE_ID", "model_evidence_final_test_20261031T072352Z_b18bf0b8f6a6")
STRATEGY = ANALYSIS / evidence_id("STRATEGY_ANALYSIS_ID", "ai_strategy_comparison_20261031T072403Z_a50754ac1b80")
EVENT = ROOT / "artifacts/cross_market_ai_services/analysis" / evidence_id(
    "EVENT_ANALYSIS_ID", "ai_services_analysis_20261031T024215Z_7fe00a9e3329"
)
RAW_INDIA = ROOT / "data/raw/cross_market/yahoo/yahoo_india_core_20261029T124839Z"
RAW_US_SERVICES = ROOT / "data/raw/cross_market/yahoo/yahoo_us_it_services_20261031T023621Z"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_pct(x, n=2):
    return f"{100 * float(x):.{n}f}%"


def selected(frame: pd.DataFrame):
    return frame.loc[frame["config_id"].eq(SELECTED)].iloc[0]


INDIA_ASSETS = ["COFORGE.NS", "HCLTECH.NS", "INFY.NS", "LTM.NS", "MPHASIS.NS",
                "OFSS.NS", "PERSISTENT.NS", "TCS.NS", "TECHM.NS", "WIPRO.NS"]
US_SERVICE_ASSETS = ["ACN", "IBM", "CTSH", "EPAM", "DXC", "CACI", "LDOS", "SAIC", "GLOB", "CNXC", "JKHY"]


def load_raw(root: Path, assets: list[str], column: str = "adjusted_close") -> pd.DataFrame:
    series = {}
    for asset in assets:
        frame = pd.read_parquet(root / f"{asset}.parquet")
        series[asset] = pd.Series(frame[column].to_numpy(), index=pd.to_datetime(frame["session"]), name=asset)
    return pd.concat(series, axis=1).sort_index()


def combined_evaluation():
    """Concatenate the two reported evaluation segments for presentation only."""
    parts = []
    for segment, path in [("2025 frozen final", FINAL), ("2026 forward extension", FORWARD)]:
        frame = pd.read_parquet(path / "strategy_ledgers.parquet")
        frame = frame.loc[frame.config_id.eq(SELECTED)].copy()
        frame["segment"] = segment
        parts.append(frame)
    daily = pd.concat(parts, ignore_index=True).sort_values("decision_date")
    daily["decision_date"] = pd.to_datetime(daily["decision_date"])
    daily = daily.drop_duplicates("decision_date").set_index("decision_date")
    assets = ["COFORGE.NS", "HCLTECH.NS", "INFY.NS", "LTM.NS", "MPHASIS.NS",
              "OFSS.NS", "PERSISTENT.NS", "TCS.NS", "TECHM.NS", "WIPRO.NS"]
    prices = load_raw(RAW_INDIA, assets).ffill()
    first_date = daily.index.min()
    prior = prices.index[prices.index < first_date]
    if prior.empty:
        raise ValueError("A pre-evaluation price is required for the passive-cohort benchmark")
    base = prices.loc[prior[-1]]
    passive_wealth = prices.reindex(daily.index).ffill().div(base).mean(axis=1)
    passive_return = passive_wealth.pct_change()
    passive_return.iloc[0] = passive_wealth.iloc[0] - 1.0
    daily["current_member_buy_hold"] = passive_return
    returns = {
        "Signed model": "net_return",
        "Nifty IT": "benchmark_nifty_it",
        "Nifty 50": "benchmark_nifty50",
        "Current-member buy & hold": "current_member_buy_hold",
    }
    total = pd.Series({name: (1 + daily[col].fillna(0)).prod() - 1 for name, col in returns.items()})
    long_active = daily.long_exposure > 0
    short_active = daily.short_exposure > 0
    counts = {
        "long": int(long_active.sum()),
        "short": int(short_active.sum()),
        "long_only": int((long_active & ~short_active).sum()),
        "short_only": int((short_active & ~long_active).sum()),
        "mixed": int((long_active & short_active).sum()),
        "flat": int(((daily.long_exposure == 0) & (daily.short_exposure == 0)).sum()),
    }
    return daily, total, counts


def compact_equation(doc, pieces, number: int, caption: str):
    """Render a restrained Word-native display equation instead of a large bitmap."""
    t = doc.add_table(rows=1, cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_widths(t, [1.0, 14.0, 1.0])
    tbl_pr = t._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders"); tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = OxmlElement(f"w:{edge}"); node.set(qn("w:val"), "nil"); borders.append(node)
    p = t.cell(0, 1).paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(1)
    for text, mode in pieces:
        r = p.add_run(text); r.font.name = "Cambria Math"; r.font.size = Pt(10.5)
        if mode == "sub": r.font.subscript = True
        elif mode == "sup": r.font.superscript = True
        elif mode == "roman": r.font.italic = False
        else: r.font.italic = True
    p = t.cell(0, 2).paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run(f"({number})"); r.font.name = "Times New Roman"; r.font.size = Pt(9)
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(3)
    r = c.add_run(caption); r.italic = True; r.font.size = Pt(8.2)


def research_period_diagnostics():
    """Stitch OOS ledgers for description only; never treat them as one holdout."""
    stage_paths = [("Screening", SCREEN), ("Confirmation", CONFIRM),
                   ("Canonical final", FINAL), ("Forward extension", FORWARD)]
    parts = []
    for stage, path in stage_paths:
        frame = pd.read_parquet(path / "strategy_ledgers.parquet")
        frame = frame.loc[frame.config_id.eq(SELECTED)].copy()
        frame["stage"] = stage
        parts.append(frame)
    daily = pd.concat(parts, ignore_index=True).sort_values("decision_date")
    daily["decision_date"] = pd.to_datetime(daily["decision_date"])
    daily = daily.drop_duplicates("decision_date").set_index("decision_date")

    # A true passive comparator: equal capital is placed in the ten current
    # constituents on the first test date and shares are held without rebalancing.
    assets = ["COFORGE.NS", "HCLTECH.NS", "INFY.NS", "LTM.NS", "MPHASIS.NS",
              "OFSS.NS", "PERSISTENT.NS", "TCS.NS", "TECHM.NS", "WIPRO.NS"]
    prices = {}
    for asset in assets:
        raw = pd.read_parquet(RAW_INDIA / f"{asset}.parquet")
        prices[asset] = pd.Series(raw.adjusted_close.to_numpy(),
                                  index=pd.to_datetime(raw.session), name=asset)
    prices = pd.concat(prices, axis=1).sort_index().ffill()
    prior = prices.index[prices.index < daily.index.min()]
    if prior.empty:
        raise ValueError("A pre-research-period price is required for the passive benchmark")
    base = prices.loc[prior[-1]]
    passive_wealth = prices.reindex(daily.index).ffill().div(base).mean(axis=1)
    passive_return = passive_wealth.pct_change()
    passive_return.iloc[0] = passive_wealth.iloc[0] - 1.0
    daily["current_member_buy_hold"] = passive_return

    columns = {"Signed model": "net_return", "Nifty IT": "benchmark_nifty_it",
               "Nifty 50": "benchmark_nifty50", "Current-member buy & hold": "current_member_buy_hold"}
    annual_rows = []
    for year, group in daily.groupby(daily.index.year):
        annual_rows.append({"year": int(year), **{
            name: (1 + group[col].fillna(0)).prod() - 1 for name, col in columns.items()}})
    annual = pd.DataFrame(annual_rows).set_index("year")
    total = pd.Series({name: (1 + daily[col].fillna(0)).prod() - 1 for name, col in columns.items()})

    monthly = pd.DataFrame({name: daily[col].resample("ME").apply(
        lambda x: (1 + x.fillna(0)).prod() - 1) for name, col in columns.items()})
    monthly["regime"] = np.select(
        [monthly["Nifty IT"].ge(.03), monthly["Nifty IT"].le(-.03)],
        ["Rising", "Falling"], default="Sideways")
    last_direction = None; reversal = []; prior_direction = []
    for regime in monthly.regime:
        if regime == "Sideways":
            prior_direction.append(last_direction); reversal.append(False)
        else:
            prior_direction.append(last_direction)
            reversal.append(last_direction is not None and regime != last_direction)
            last_direction = regime
    monthly["prior_direction"] = prior_direction
    monthly["reversal"] = reversal
    monthly["reversal_type"] = np.where(
        monthly.reversal, monthly.prior_direction + " → " + monthly.regime, "None")
    regime = monthly.groupby("regime")[list(columns)].agg(["count", "mean", "median"])
    return daily, annual, total, monthly, regime


def build_figures():
    plt.rcParams.update({"font.family": "DejaVu Serif", "axes.titlesize": 11,
                         "axes.labelsize": 9, "figure.facecolor": "white"})

    # Research architecture: tradable forecasting and retrospective analysis are separate lanes.
    fig, ax = plt.subplots(figsize=(10, 5.8), dpi=240)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
    def box(x, y, w, h, title, body, color="#EAF1F5", title_size=9, body_size=7.4):
        from matplotlib.patches import FancyBboxPatch
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.08,rounding_size=.08",
                           facecolor=color, edgecolor="#003D7C", linewidth=1.1)
        ax.add_patch(p); ax.text(x+w/2, y+h-.22, title, ha="center", va="top", weight="bold", fontsize=title_size)
        ax.text(x+w/2, y+h-.53, body, ha="center", va="top", fontsize=body_size, linespacing=1.25)
    source_x=[.15,2.05,3.95,5.85]
    source_titles=["India","Completed U.S. / global","Macro","Dated AI releases"]
    source_bodies=["Own / peers / Nifty 50","Services / S&P 500 / FX","Rates / credit / vintage flags","Timestamp / disclosed scale"]
    for x,title,body in zip(source_x,source_titles,source_bodies): box(x,5.35,1.7,.9,title,body,title_size=7.5,body_size=6.2)
    box(7.85,5.25,1.95,1.1,"08:55 IST gate","Calendar · availability\nvintage status · quality","#FFF4E8",title_size=8.2,body_size=6.6)
    ax.plot([1.0,7.75],[5.05,5.05],color="#6B8796",lw=1)
    for x in [1.0,2.9,4.8,6.7]: ax.plot([x,x],[5.35,5.05],color="#6B8796",lw=1)
    ax.annotate("",xy=(7.85,5.80),xytext=(7.75,5.05),arrowprops=dict(arrowstyle="->",color="#6B8796",lw=1))

    lane_label = dict(fontsize=7.5, weight="bold", color="#003D7C",
                      bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    ax.text(.15,4.55,"TRAINING LANE",**lane_label)
    box(.8,3.55,1.8,.82,"Eligible history","≤1,260 sessions · embargo",title_size=8,body_size=6.4)
    box(3.05,3.55,2.0,.82,"Fit transforms","filter · impute · scale · PCA",title_size=8,body_size=6.4)
    box(5.55,3.55,1.75,.82,"Fit estimator","seed 17 · bounded capacity",title_size=8,body_size=6.4)
    for a,b in [(2.60,3.05),(5.05,5.55)]: ax.annotate("",xy=(b,3.96),xytext=(a,3.96),arrowprops=dict(arrowstyle="->",color="#003D7C",lw=1.1))

    ax.text(.15,3.20,"PREDICTION & EXECUTION LANE",**lane_label)
    box(.35,2.15,1.55,.82,"Current inputs","apply fitted transforms",title_size=8,body_size=6.2)
    box(2.15,2.15,1.35,.82,"Forecast","expected O–C return",title_size=8,body_size=6.2)
    box(3.75,2.15,1.35,.82,"Cost hurdle","±15 bps eligibility",title_size=8,body_size=6.2)
    box(5.35,2.15,1.55,.82,"Signed state","LONG · FLAT · SHORT\ntop/bottom 3 · risk caps","#EDF7F3",title_size=8,body_size=5.9)
    box(7.15,2.15,1.25,.82,"Execution","open → close",title_size=8,body_size=6.2)
    box(8.65,2.15,1.1,.82,"Ledger","gross − costs",title_size=8,body_size=6.2)
    for a,b in [(1.90,2.15),(3.50,3.75),(5.10,5.35),(6.90,7.15),(8.40,8.65)]: ax.annotate("",xy=(b,2.56),xytext=(a,2.56),arrowprops=dict(arrowstyle="->",color="#003D7C",lw=1.1))
    ax.plot([6.4,6.4,1.1],[3.52,3.40,3.40],ls="--",color="#697985",lw=.9)
    ax.annotate("",xy=(1.1,2.99),xytext=(1.1,3.40),arrowprops=dict(arrowstyle="->",linestyle="--",color="#697985",lw=.9))
    ax.plot([9.5,9.5,2.0],[5.23,3.32,3.32],color="#697985",lw=.9)
    ax.annotate("",xy=(2.0,2.99),xytext=(2.0,3.32),arrowprops=dict(arrowstyle="->",color="#697985",lw=.9))

    box(5.15,.75,2.05,.82,"2025 replication","monthly refits · historically inspected","#EDF7F3",title_size=8,body_size=6.1)
    box(7.55,.75,2.1,.82,"2026 extension","one pre-2026 fit · no reselection","#EDF7F3",title_size=8,body_size=6.1)
    ax.annotate("",xy=(6.15,1.57),xytext=(9.2,2.12),arrowprops=dict(arrowstyle="->",color="#2A7F62",lw=1))
    ax.annotate("",xy=(8.6,1.57),xytext=(9.2,2.12),arrowprops=dict(arrowstyle="->",color="#2A7F62",lw=1))
    box(.25,.55,3.95,1.05,"RETROSPECTIVE RESEARCH ONLY","Current-vintage Epoch scores → event/capability tests\nNo connector to historical forecast training","#F1F3F5",title_size=7.5,body_size=6.4)
    ax.text(5,.15,"Target: same-session Nifty IT constituent open-to-close return · simulated INR ledger",ha="center",weight="bold",color="#003D7C",fontsize=9)
    architecture = FIG / "research_architecture.png"; fig.savefig(architecture, bbox_inches="tight"); plt.close(fig)

    # Family comparison across stages.
    rows=[]
    for label, path in [("Screening\n2021–22", SCREEN), ("Confirmation\n2023–24", CONFIRM), ("Final\n2025", FINAL)]:
        df=pd.read_csv(path/"leaderboard.csv")
        for family, g in df.groupby("family"):
            value=g.net_sharpe.max() if g.net_sharpe.notna().any() else np.nan
            rows.append((label, family, value, len(g)))
    fam=pd.DataFrame(rows, columns=["stage","family","sharpe","count"])
    keep=[x for x in ["autoregression","ridge","lasso","elastic_net","pca_ridge","rff_ridge","hist_gradient_boosting","extra_trees"] if x in set(fam.family)]
    stages=["Screening\n2021–22","Confirmation\n2023–24","Final\n2025"]
    matrix=fam[fam.family.isin(keep)].pivot(index="family",columns="stage",values="sharpe").reindex(index=keep,columns=stages)
    counts=fam[fam.family.isin(keep)].pivot(index="family",columns="stage",values="count").reindex(index=keep,columns=stages)
    fig,ax=plt.subplots(figsize=(8.2,4.8),dpi=240)
    image=ax.imshow(matrix.fillna(0),cmap="RdYlGn",vmin=-1.5,vmax=1.5,aspect="auto")
    ax.set_xticks(range(len(stages)),stages,fontsize=8); ax.set_yticks(range(len(keep)),[x.replace("_"," ").title() for x in keep],fontsize=8)
    for i in range(len(keep)):
        for j in range(len(stages)):
            value=matrix.iloc[i,j]; count=counts.iloc[i,j]
            label=(f"{value:+.2f}\n(n={int(count)})" if np.isfinite(value) else (f"no trade\n(n={int(count)})" if np.isfinite(count) else "not run"))
            ax.text(j,i,label,ha="center",va="center",fontsize=7,color="white" if np.isfinite(value) and abs(value)>.75 else "#222")
    ax.set_title("Best family-level net Sharpe and evaluated rows",weight="bold")
    fig.colorbar(image,ax=ax,label="Net Sharpe",fraction=.04,pad=.03); fig.subplots_adjust(left=.29,right=.92,bottom=.15,top=.88)
    family = FIG/"model_family_stages.png"; fig.savefig(family,bbox_inches="tight"); plt.close(fig)

    # Market context: actual adjusted-close paths and development-only correlations.
    india_prices = load_raw(RAW_INDIA, INDIA_ASSETS).loc["2020-01-01":"2026-09-30"].ffill()
    us_prices = load_raw(RAW_US_SERVICES, US_SERVICE_ASSETS).loc["2020-01-01":"2026-09-30"].ffill()
    norm_india = india_prices / india_prices.apply(lambda s: s.dropna().iloc[0]) * 100
    fig, ax = plt.subplots(figsize=(9.6, 4.7), dpi=240)
    palette = plt.cm.tab10(np.linspace(0, 1, len(norm_india.columns)))
    for asset, color in zip(norm_india.columns, palette):
        ax.plot(norm_india.index, norm_india[asset], lw=1.05, color=color, label=asset.replace(".NS", ""))
    ax.axvspan(pd.Timestamp("2025-01-01"), pd.Timestamp("2026-09-30"), color="#DCE8F1", alpha=.45)
    ax.axvline(pd.Timestamp("2025-01-01"), color="#003D7C", ls="--", lw=1.15)
    ax.text(pd.Timestamp("2025-01-08"), ax.get_ylim()[1]*.94, "reported evaluation window", color="#003D7C", fontsize=7.5, va="top")
    ax.set_ylabel("Adjusted close (2020 start = 100)"); ax.set_title("Current Nifty IT cohort: daily price paths and evaluation boundary", weight="bold")
    ax.grid(color="#D9DEE2", lw=.45); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=5, fontsize=7, loc="upper center", bbox_to_anchor=(.5, -.14))
    fig.subplots_adjust(left=.09,right=.98,bottom=.24,top=.88)
    india_trends = FIG/"nifty_it_constituent_trends.png"; fig.savefig(india_trends,bbox_inches="tight"); plt.close(fig)

    selected_india = ["TCS.NS", "INFY.NS", "WIPRO.NS"]
    selected_us = ["ACN", "IBM", "CTSH"]
    mixed = pd.concat([india_prices[selected_india], us_prices[selected_us]], axis=1).loc["2020-01-01":"2026-09-30"].ffill()
    mixed = mixed / mixed.apply(lambda s: s.dropna().iloc[0]) * 100
    fig, ax = plt.subplots(figsize=(9.6, 4.5), dpi=240)
    for asset in selected_india:
        ax.plot(mixed.index, mixed[asset], lw=1.45, label=asset.replace(".NS", "")+" (India)")
    for asset in selected_us:
        ax.plot(mixed.index, mixed[asset], lw=1.35, ls="--", label=asset+" (U.S.)")
    ax.axvline(pd.Timestamp("2025-01-01"), color="#003D7C", ls=":", lw=1.2)
    ax.set_ylabel("Adjusted close (2020 start = 100)"); ax.set_title("Selected Indian and U.S. IT-services price paths", weight="bold")
    ax.grid(color="#D9DEE2", lw=.45); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=3, fontsize=7.5, loc="upper center", bbox_to_anchor=(.5, -.14))
    fig.subplots_adjust(left=.09,right=.98,bottom=.23,top=.88)
    cross_trends = FIG/"india_us_services_trends.png"; fig.savefig(cross_trends,bbox_inches="tight"); plt.close(fig)

    dev_india = india_prices.loc["2020-01-01":"2024-12-31"].pct_change(fill_method=None)
    peer_corr = dev_india.corr()
    fig, ax = plt.subplots(figsize=(8.2, 6.5), dpi=240)
    im = ax.imshow(peer_corr, cmap="RdBu_r", vmin=-1, vmax=1)
    labels = [x.replace(".NS", "") for x in peer_corr.columns]
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right", fontsize=7.2); ax.set_yticks(range(len(labels)), labels, fontsize=7.2)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{peer_corr.iloc[i,j]:.2f}", ha="center", va="center", fontsize=6.2,
                    color="white" if abs(peer_corr.iloc[i,j])>.55 else "#222")
    ax.set_title("Nifty IT peer correlation, 2020–2024 development sample", weight="bold")
    fig.colorbar(im, ax=ax, fraction=.035, pad=.03, label="Pearson correlation")
    fig.subplots_adjust(left=.16,right=.94,bottom=.19,top=.90)
    peer_heatmap = FIG/"india_peer_correlation_heatmap.png"; fig.savefig(peer_heatmap,bbox_inches="tight"); plt.close(fig)

    # Prediction-aligned correlation: completed U.S. close-to-close return maps to
    # the next Indian session, then correlates with Indian same-session O–C return.
    india_oc_full = {}
    for asset in INDIA_ASSETS:
        raw = pd.read_parquet(RAW_INDIA/f"{asset}.parquet")
        india_oc_full[asset] = pd.Series(raw["close"].to_numpy()/raw["open"].replace(0,np.nan).to_numpy()-1,
                                         index=pd.to_datetime(raw["session"]))
    india_oc_full = pd.concat(india_oc_full, axis=1).sort_index()
    india_oc = india_oc_full.loc["2020-01-01":"2024-12-31"]
    indian_sessions = india_oc.index.unique().sort_values()
    aligned_us = {}
    for asset in US_SERVICE_ASSETS:
        s = us_prices[asset].pct_change(fill_method=None).dropna().loc["2020-01-01":"2024-12-31"]
        mapped = {}
        for date, value in s.items():
            pos = indian_sessions.searchsorted(date, side="right")
            if pos < len(indian_sessions): mapped[indian_sessions[pos]] = value
        aligned_us[asset] = pd.Series(mapped)
    aligned_us = pd.concat(aligned_us, axis=1).reindex(indian_sessions)
    cross_corr = pd.DataFrame(index=INDIA_ASSETS, columns=US_SERVICE_ASSETS, dtype=float)
    for india in INDIA_ASSETS:
        for us in US_SERVICE_ASSETS:
            cross_corr.loc[india,us] = india_oc[india].corr(aligned_us[us])
    fig, ax = plt.subplots(figsize=(9.3, 6.3), dpi=240)
    bound = max(.08, float(np.nanmax(np.abs(cross_corr.to_numpy()))))
    im = ax.imshow(cross_corr, cmap="RdBu_r", vmin=-bound, vmax=bound, aspect="auto")
    ax.set_xticks(range(len(US_SERVICE_ASSETS)), US_SERVICE_ASSETS, rotation=45, ha="right", fontsize=7.2)
    ax.set_yticks(range(len(INDIA_ASSETS)), [x.replace(".NS","") for x in INDIA_ASSETS], fontsize=7.2)
    for i in range(len(INDIA_ASSETS)):
        for j in range(len(US_SERVICE_ASSETS)):
            ax.text(j, i, f"{cross_corr.iloc[i,j]:.2f}", ha="center", va="center", fontsize=5.9,
                    color="white" if abs(cross_corr.iloc[i,j])>.65*bound else "#222")
    ax.set_xlabel("Completed U.S. IT-services session"); ax.set_ylabel("Next Indian session O–C return")
    ax.set_title("Prediction-aligned U.S.→India IT-services correlation, 2020–2024", weight="bold")
    fig.colorbar(im, ax=ax, fraction=.035, pad=.03, label="Pearson correlation")
    fig.subplots_adjust(left=.14,right=.95,bottom=.18,top=.88)
    cross_heatmap = FIG/"us_india_predictive_correlation_heatmap.png"; fig.savefig(cross_heatmap,bbox_inches="tight"); plt.close(fig)

    # Frontier events that establish a new running maximum in the mapped Epoch
    # capability index. This avoids annotating every release in the inventory.
    event_frame = pd.read_csv(EPOCH/"epoch_event_capability_returns.csv")
    event_frame["release_date"] = pd.to_datetime(event_frame["release_date"])
    if "first_us_reaction_session" not in event_frame:
        if "public_at_utc" not in event_frame:
            raise ValueError("Event evidence lacks public timestamps required for U.S. reaction-session mapping")
        nse_sessions = pd.DatetimeIndex(india_oc_full.index)
        us_sessions = pd.DatetimeIndex(us_prices.index)
        event_frame["first_us_reaction_session"] = [
            map_release_sessions(value, nse_sessions, us_sessions)["first_us_reaction_session"]
            for value in pd.to_datetime(event_frame["public_at_utc"], utc=True)
        ]
    event_frame = event_frame.loc[event_frame["primary_event"].eq(True) & event_frame["eci"].notna() &
                                  event_frame["release_date"].between("2023-01-01","2025-05-31")].sort_values("release_date")
    event_frame = event_frame.loc[event_frame["eci"].gt(event_frame["eci"].cummax().shift(fill_value=-np.inf))].copy()
    event_frame["short_label"] = event_frame["model_family"].replace({"Claude 3.5 Sonnet":"Claude 3.5", "Claude 3.7 Sonnet":"Claude 3.7", "Gemini 2.5 Pro":"Gemini 2.5"})
    timeline_india = ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"]
    timeline_us = ["ACN", "IBM", "CTSH", "EPAM", "DXC"]
    fig, axes = plt.subplots(2,1,figsize=(9.8,6.2),dpi=240,sharex=True)
    for ax, frame, assets, title in [(axes[0],india_prices,timeline_india,"Indian IT services"),(axes[1],us_prices,timeline_us,"U.S. IT services")]:
        q=frame[assets].loc["2023-01-01":"2025-06-30"].ffill(); q=q/q.apply(lambda s:s.dropna().iloc[0])*100
        for asset in assets: ax.plot(q.index,q[asset],lw=1.05,label=asset.replace(".NS",""))
        for date in event_frame.release_date: ax.axvline(date,color="#A44747",lw=.65,alpha=.55)
        ax.set_ylabel("Index (2023 = 100)"); ax.set_title(title,loc="left",fontsize=9.5,weight="bold"); ax.grid(color="#D9DEE2",lw=.4); ax.spines[["top","right"]].set_visible(False); ax.legend(frameon=False,ncol=5,fontsize=6.8,loc="upper left")
    for k,row in enumerate(event_frame.itertuples()):
        axes[0].text(row.release_date,1.03+(k%2)*.10,f"{row.short_label}\nECI {row.eci:.1f}",transform=axes[0].get_xaxis_transform(),rotation=90,ha="left",va="bottom",fontsize=5.9,color="#7D2626")
    fig.suptitle("Record-improving frontier-model events against IT-services price paths",weight="bold",y=.995)
    fig.subplots_adjust(left=.09,right=.98,bottom=.10,top=.76,hspace=.30)
    event_timeline = FIG/"frontier_record_event_timeline.png"; fig.savefig(event_timeline,bbox_inches="tight"); plt.close(fig)

    response_assets = timeline_us + timeline_india
    responses = pd.DataFrame(index=response_assets, columns=event_frame["short_label"], dtype=float)
    for row in event_frame.itertuples():
        col = row.short_label
        for asset in timeline_us:
            series = us_prices[asset].pct_change(fill_method=None).dropna()
            if not hasattr(row, "first_us_reaction_session") or pd.isna(row.first_us_reaction_session):
                continue
            pos = series.index.searchsorted(pd.Timestamp(row.first_us_reaction_session), side="left")
            if pos < len(series): responses.loc[asset,col] = series.iloc[pos]
        for asset in timeline_india:
            series = india_oc_full[asset].dropna()
            pos = series.index.searchsorted(pd.Timestamp(row.tradable_date), side="left")
            if pos < len(series): responses.loc[asset,col] = series.iloc[pos]
    fig,ax=plt.subplots(figsize=(9.5,5.5),dpi=240); bound=max(.025,float(np.nanmax(np.abs(responses.to_numpy())))); im=ax.imshow(responses*100,cmap="RdBu_r",vmin=-bound*100,vmax=bound*100,aspect="auto")
    ax.set_xticks(range(responses.shape[1]),responses.columns,rotation=45,ha="right",fontsize=7); ax.set_yticks(range(responses.shape[0]),[x.replace(".NS","") for x in responses.index],fontsize=7.4)
    for i in range(responses.shape[0]):
        for j in range(responses.shape[1]):
            v=responses.iloc[i,j]*100; ax.text(j,i,f"{v:+.1f}",ha="center",va="center",fontsize=6,color="white" if abs(v)>.65*bound*100 else "#222")
    ax.axhline(len(timeline_us)-.5,color="#222",lw=1.1); ax.text(-.7,2,"U.S.",rotation=90,va="center",weight="bold",fontsize=8); ax.text(-.7,7,"India",rotation=90,va="center",weight="bold",fontsize=8)
    ax.set_title("One-session response around record-capability frontier events",weight="bold"); fig.colorbar(im,ax=ax,fraction=.035,pad=.03,label="Return (%)")
    fig.subplots_adjust(left=.14,right=.95,bottom=.23,top=.89)
    event_heatmap=FIG/"frontier_event_stock_response_heatmap.png"; fig.savefig(event_heatmap,bbox_inches="tight"); plt.close(fig)

    # 2025 and 2026 wealth/risk panels.
    def wealth_plot(path, title, out):
        d=pd.read_parquet(path/"strategy_ledgers.parquet"); d=d[d.config_id.eq(SELECTED)].sort_values("decision_date").copy(); d.decision_date=pd.to_datetime(d.decision_date)
        curves={"Signed strategy (net)":(1+d.net_return.fillna(0)).cumprod(),"Nifty IT":(1+d.benchmark_nifty_it.fillna(0)).cumprod(),"Nifty 50":(1+d.benchmark_nifty50.fillna(0)).cumprod()}
        fig,ax=plt.subplots(figsize=(9.3,4.4),dpi=240)
        for (name,v),c in zip(curves.items(),["#003D7C","#E97824","#2A9D8F"]): ax.plot(d.decision_date,v,label=name,lw=1.8,color=c)
        ax.set_ylabel("Growth of INR 1"); ax.set_title(title,weight="bold"); ax.grid(color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False); ax.legend(frameon=False,ncol=3,fontsize=8,loc="upper center",bbox_to_anchor=(.5,-.14)); fig.subplots_adjust(bottom=.22,left=.09,right=.98,top=.88); fig.savefig(out,bbox_inches="tight"); plt.close(fig)
    wealth25=FIG/"wealth_2025.png"; wealth26=FIG/"wealth_2026.png"
    wealth_plot(FINAL,"Canonical final evaluation: 2025",wealth25); wealth_plot(FORWARD,"Frozen forward extension: January–September 2026",wealth26)

    evaluation_daily, evaluation_total, evaluation_counts = combined_evaluation()
    fig,ax=plt.subplots(figsize=(9.5,4.5),dpi=240)
    for name,col,color in [("Signed strategy (net)","net_return","#003D7C"),("Nifty IT","benchmark_nifty_it","#E97824"),("Nifty 50","benchmark_nifty50","#2A9D8F"),("Current-member buy & hold","current_member_buy_hold","#7A5195")]:
        ax.plot(evaluation_daily.index,(1+evaluation_daily[col].fillna(0)).cumprod(),label=name,color=color,lw=1.8)
    ax.axvline(pd.Timestamp("2026-01-01"),color="#697985",ls="--",lw=.9); ax.text(pd.Timestamp("2026-01-06"),ax.get_ylim()[1]*.97,"2026 forward segment",va="top",fontsize=7,color="#52606A")
    ax.set_ylabel("Growth of INR 1"); ax.set_title("Cumulative reported evaluation: January 2025–September 2026",weight="bold")
    ax.grid(color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False); ax.legend(frameon=False,ncol=3,fontsize=8)
    fig.subplots_adjust(left=.09,right=.98,bottom=.13,top=.88)
    combined_wealth=FIG/"combined_evaluation_wealth.png"; fig.savefig(combined_wealth,bbox_inches="tight"); plt.close(fig)

    d=evaluation_daily
    monthly_combined=pd.DataFrame({"Strategy":d.net_return.resample("ME").apply(lambda x:(1+x.fillna(0)).prod()-1),"Nifty IT":d.benchmark_nifty_it.resample("ME").apply(lambda x:(1+x.fillna(0)).prod()-1),"Nifty 50":d.benchmark_nifty50.resample("ME").apply(lambda x:(1+x.fillna(0)).prod()-1)})*100
    fig,axes=plt.subplots(2,1,figsize=(9.5,4.9),dpi=240,sharex=False); x=np.arange(len(monthly_combined)); w=.25
    for j,(col,color) in enumerate(zip(monthly_combined.columns,["#003D7C","#E97824","#2A9D8F"])): axes[0].bar(x+(j-1)*w,monthly_combined[col],w,label=col,color=color)
    axes[0].set_xticks(x,[i.strftime("%b\n%y") for i in monthly_combined.index],fontsize=6.7); axes[0].axhline(0,color="#444",lw=.7); axes[0].set_ylabel("Monthly return (%)"); axes[0].legend(frameon=False,ncol=3,fontsize=7.5)
    axes[1].fill_between(d.index,0,d.long_exposure,color="#2A9D8F",alpha=.65,label="Long"); axes[1].fill_between(d.index,0,-d.short_exposure,color="#A44747",alpha=.65,label="Short"); axes[1].axhline(0,color="#444",lw=.6); axes[1].set_ylabel("Signed exposure"); axes[1].legend(frameon=False,ncol=2,fontsize=7.5)
    for ax in axes: ax.grid(axis="y",color="#D9DEE2",lw=.45); ax.spines[["top","right"]].set_visible(False)
    axes[0].set_title("Monthly performance and long/short/flat deployment",weight="bold"); fig.subplots_adjust(hspace=.32,left=.09,right=.98,top=.92,bottom=.10)
    combined_positioning=FIG/"combined_evaluation_positioning.png"; fig.savefig(combined_positioning,bbox_inches="tight"); plt.close(fig)

    # 2026 month and positioning.
    d=pd.read_parquet(FORWARD/"strategy_ledgers.parquet"); d=d[d.config_id.eq(SELECTED)].sort_values("decision_date").copy(); d.decision_date=pd.to_datetime(d.decision_date); d=d.set_index("decision_date")
    monthly=pd.DataFrame({"Strategy":d.net_return.resample("ME").apply(lambda x:(1+x).prod()-1),"Nifty IT":d.benchmark_nifty_it.resample("ME").apply(lambda x:(1+x).prod()-1),"Nifty 50":d.benchmark_nifty50.resample("ME").apply(lambda x:(1+x).prod()-1)})*100
    fig,axes=plt.subplots(2,1,figsize=(9.4,5.7),dpi=240)
    x=np.arange(len(monthly)); w=.25
    for j,(col,c) in enumerate(zip(monthly.columns,["#003D7C","#E97824","#2A9D8F"])): axes[0].bar(x+(j-1)*w,monthly[col],w,label=col,color=c)
    axes[0].set_xticks(x,[i.strftime("%b") for i in monthly.index]); axes[0].axhline(0,color="#444",lw=.7); axes[0].set_ylabel("Monthly return (%)"); axes[0].legend(frameon=False,ncol=3,fontsize=8)
    axes[1].plot(d.index,d.long_exposure,label="Long",color="#2A9D8F",lw=1.2); axes[1].plot(d.index,-d.short_exposure,label="Short",color="#A44747",lw=1.2); axes[1].axhline(0,color="#444",lw=.6); axes[1].set_ylabel("Signed exposure"); axes[1].legend(frameon=False,ncol=2,fontsize=8)
    for ax in axes: ax.grid(axis="y",color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False)
    axes[0].set_title("2026 return path and long/short deployment",weight="bold"); fig.subplots_adjust(hspace=.3,left=.09,right=.98,top=.92,bottom=.1)
    months=FIG/"forward_monthly_positioning.png"; fig.savefig(months,bbox_inches="tight"); plt.close(fig)

    # Group permutation importance, 2025 vs 2026.
    def groups(path):
        q=pd.read_csv(path/"feature_importance_by_refit.csv"); q=q[(q.config_id.eq(SELECTED))&q.feature.str.startswith("GROUP::",na=False)].copy(); q["group"]=q.feature.str.replace("GROUP::","",regex=False); return q.groupby("group").importance.mean()
    a,b=groups(FINAL),groups(FORWARD); imp=pd.concat({"2025":a,"2026 Jan–Sep":b},axis=1).fillna(0); imp=imp.loc[imp.abs().max(axis=1).nlargest(12).index].sort_values("2026 Jan–Sep")
    fig,ax=plt.subplots(figsize=(9.2,5.0),dpi=240); y=np.arange(len(imp)); ax.barh(y-.19,imp["2025"]*1e6,.38,label="2025",color="#8C9AA5"); ax.barh(y+.19,imp["2026 Jan–Sep"]*1e6,.38,label="2026 Jan–Sep",color="#003D7C"); ax.set_yticks(y,[x.replace("_"," ") for x in imp.index],fontsize=7.8); ax.axvline(0,color="#444",lw=.7); ax.set_xlabel("Permutation MSE increase (×10⁻⁶)"); ax.set_title("What the frozen Extra Trees model used",weight="bold"); ax.legend(frameon=False); ax.grid(axis="x",color="#D9DEE2",lw=.5); ax.spines[["top","right","left"]].set_visible(False); fig.subplots_adjust(left=.28,right=.98,bottom=.13,top=.88)
    importance=FIG/"group_importance_2025_2026.png"; fig.savefig(importance,bbox_inches="tight"); plt.close(fig)

    # Information ladder.
    ladder=pd.read_csv(LADDER/"information_ladder_summary.csv")
    fig,axes=plt.subplots(1,2,figsize=(9.6,4.0),dpi=240)
    labels=[x.replace("+ ","+") for x in ladder.information_set]
    axes[0].plot(range(len(ladder)),ladder.oos_r2_asset_mean*100,marker="o",color="#003D7C"); axes[0].axhline(0,color="#444",lw=.7); axes[0].set_ylabel("OOS R² vs asset mean (%)")
    axes[1].plot(range(len(ladder)),ladder.net_sharpe,marker="o",color="#E97824"); axes[1].axhline(0,color="#444",lw=.7); axes[1].set_ylabel("Net Sharpe")
    for ax in axes: ax.set_xticks(range(len(labels)),labels,rotation=55,ha="right",fontsize=7); ax.grid(color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Fixed ridge information ladder in the 2025 final period",weight="bold"); fig.subplots_adjust(left=.09,right=.98,bottom=.39,top=.8,wspace=.25)
    ladderfig=FIG/"information_ladder_2025.png"; fig.savefig(ladderfig,bbox_inches="tight"); plt.close(fig)
    # Complete research-period diagnostic. Screening and confirmation are shown
    # transparently, but this stitched curve is not described as one holdout.
    research_daily, research_annual, research_total, research_monthly, research_regime = research_period_diagnostics()
    curve_map = {"Signed model": "net_return", "Nifty IT": "benchmark_nifty_it",
                 "Nifty 50": "benchmark_nifty50", "Current-member buy & hold": "current_member_buy_hold"}
    fig, ax = plt.subplots(figsize=(9.5, 4.6), dpi=240)
    colors = ["#003D7C", "#E97824", "#2A9D8F", "#6B8796"]
    for (name, col), color in zip(curve_map.items(), colors):
        ax.plot(research_daily.index, (1 + research_daily[col].fillna(0)).cumprod(),
                label=name, color=color, lw=1.65)
    ax.set_xlim(research_daily.index.min(), research_daily.index.max())
    for date, label in [(pd.Timestamp("2023-01-01"), "confirmation"),
                        (pd.Timestamp("2025-01-01"), "canonical final"),
                        (pd.Timestamp("2026-01-01"), "forward extension")]:
        ax.axvline(date, color="#9AA4AB", ls="--", lw=.8)
        ax.text(date, ax.get_ylim()[1] * .96, label, rotation=90, va="top", ha="right", fontsize=7, color="#626A73")
    ax.set_ylabel("Growth of INR 1"); ax.set_title("All available out-of-sample ledgers, 2021–September 2026", weight="bold")
    ax.grid(color="#D9DEE2", lw=.5); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2, fontsize=8, loc="upper left")
    fig.subplots_adjust(left=.09,right=.98,bottom=.13,top=.88)
    stitched = FIG / "stitched_research_period_wealth.png"; fig.savefig(stitched,bbox_inches="tight"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 4.5), dpi=240)
    x=np.arange(len(research_annual)); w=.19
    for j,(name,color) in enumerate(zip(research_annual.columns,colors)):
        ax.bar(x+(j-1.5)*w,research_annual[name]*100,w,label=name,color=color)
    ax.axhline(0,color="#444",lw=.7); ax.set_xticks(x,[str(y) if y<2026 else "2026\nJan–Sep" for y in research_annual.index]); ax.set_ylabel("Calendar-period return (%)")
    ax.set_title("Year-by-year return comparison",weight="bold"); ax.grid(axis="y",color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False); ax.legend(frameon=False,ncol=2,fontsize=8)
    fig.subplots_adjust(left=.09,right=.98,bottom=.15,top=.88)
    annualfig=FIG/"research_period_annual_returns.png"; fig.savefig(annualfig,bbox_inches="tight"); plt.close(fig)

    order=["Rising","Sideways","Falling"]
    means=research_monthly.groupby("regime")[list(curve_map)].mean().reindex(order)*100
    fig,ax=plt.subplots(figsize=(9.4,4.3),dpi=240); x=np.arange(3); w=.19
    for j,(name,color) in enumerate(zip(means.columns,colors)): ax.bar(x+(j-1.5)*w,means[name],w,label=name,color=color)
    ax.axhline(0,color="#444",lw=.7); ax.set_xticks(x,[f"{r}\n(n={int((research_monthly.regime==r).sum())} months)" for r in order]); ax.set_ylabel("Mean monthly return (%)"); ax.set_title("Performance conditional on the Nifty IT monthly regime",weight="bold"); ax.grid(axis="y",color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False); ax.legend(frameon=False,ncol=2,fontsize=8)
    fig.subplots_adjust(left=.09,right=.98,bottom=.18,top=.87)
    regimefig=FIG/"research_period_regime_returns.png"; fig.savefig(regimefig,bbox_inches="tight"); plt.close(fig)

    reversals=research_monthly.loc[research_monthly.reversal]
    rev_means=reversals.groupby("reversal_type")[list(curve_map)].mean()*100
    fig,ax=plt.subplots(figsize=(9.4,4.2),dpi=240); x=np.arange(len(rev_means)); w=.19
    for j,(name,color) in enumerate(zip(rev_means.columns,colors)): ax.bar(x+(j-1.5)*w,rev_means[name],w,label=name,color=color)
    ax.axhline(0,color="#444",lw=.7); ax.set_xticks(x,[f"{r}\n(n={int((reversals.reversal_type==r).sum())})" for r in rev_means.index]); ax.set_ylabel("Mean reversal-month return (%)"); ax.set_title("Response when the directional Nifty IT regime reverses",weight="bold"); ax.grid(axis="y",color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False); ax.legend(frameon=False,ncol=2,fontsize=8)
    fig.subplots_adjust(left=.09,right=.98,bottom=.2,top=.87)
    reversalfig=FIG/"research_period_reversal_returns.png"; fig.savefig(reversalfig,bbox_inches="tight"); plt.close(fig)
    return (architecture, family, india_trends, cross_trends, peer_heatmap, cross_heatmap,
            event_timeline, event_heatmap, combined_wealth, combined_positioning,
            evaluation_daily, evaluation_total, evaluation_counts,
            wealth25, wealth26, months, importance, ladderfig,
            stitched, annualfig, regimefig, reversalfig,
            research_daily, research_annual, research_total, research_monthly, research_regime)


def cover(doc, authors):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run("Cross-Market Forecasting and Signed Trading of Nifty IT Stocks"); r.bold=True; r.font.size=Pt(12); r.font.color.rgb=RGBColor.from_string(NUS_BLUE)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(LOGO),width=Inches(1.55))
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run("Information complexity and signed trading in a temporally aligned retrospective design"); r.italic=True
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run("Data Science in Quantitative Finance DSA5205\nProject2 Teams 16"); r.bold=True
    t=doc.add_table(rows=1,cols=2); t.alignment=WD_TABLE_ALIGNMENT.CENTER; set_widths(t,[10.6,5.1])
    for i,h in enumerate(["AUTHOR","STUDENT ID"]): shade(t.cell(0,i),PALE); p=t.cell(0,i).paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; rr=p.add_run(h); rr.bold=True; rr.font.color.rgb=RGBColor.from_string(MUTED)
    for a in authors:
        row=t.add_row();
        for c in row.cells: margins(c)
        for i,v in enumerate([a["name"],a["student_id"]]): p=row.cells[i].paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run(v)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run("Repository: "); hyperlink(p,GITHUB,GITHUB)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run("Daily market data: Yahoo Finance · Macro context: FRED/ALFRED · AI benchmarks: Epoch AI"); r.italic=True; r.font.color.rgb=RGBColor.from_string(MUTED)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run("October 2026")


def build():
    required=[DATASET/"manifest.json",SCREEN/"manifest.json",CONFIRM/"manifest.json",FINAL/"manifest.json",FORWARD/"manifest.json",FREEZE,LOGO]
    missing=[str(x) for x in required if not x.exists()]
    if missing: raise FileNotFoundError("Missing evidence:\n"+"\n".join(missing))
    authors=sorted(read_json(ROOT/"assets/authors.json"),key=lambda x:x["name"].casefold())
    screen=pd.read_csv(SCREEN/"leaderboard.csv"); confirm=pd.read_csv(CONFIRM/"leaderboard.csv"); final=pd.read_csv(FINAL/"leaderboard.csv"); forward=pd.read_csv(FORWARD/"leaderboard.csv")
    screening_count, confirmation_count = len(screen), len(confirm)
    f25=selected(final); f26=selected(forward); a25=pd.read_csv(FINAL/"annual_performance.csv").iloc[0]; a26=pd.read_csv(FORWARD/"annual_performance.csv").iloc[0]
    i25=read_json(FINAL/"selected_model_inference.json"); i26=read_json(FORWARD/"selected_model_inference.json"); event=read_json(EVENT/"frontier_event_study.json"); cap=read_json(CAP/"capability_effect_summary.json")
    (architecture,family,india_trends,cross_trends,peer_heatmap,cross_heatmap,
     event_timeline,event_heatmap,combined_wealth,combined_positioning,
     evaluation_daily,evaluation_total,evaluation_counts,
     wealth25,wealth26,months,importance,ladderfig,
     stitched,annualfig,regimefig,reversalfig,research_daily,research_annual,
     research_total,research_monthly,research_regime)=build_figures()
    eval_net = evaluation_daily["net_return"].fillna(0)
    eval_annual_return = (1 + evaluation_total["Signed model"]) ** (252 / len(eval_net)) - 1
    eval_sharpe = np.sqrt(252) * eval_net.mean() / eval_net.std(ddof=1)
    eval_wealth = pd.concat([pd.Series([1.0]), (1 + eval_net).cumprod().reset_index(drop=True)], ignore_index=True)
    eval_max_drawdown = float((eval_wealth / eval_wealth.cummax() - 1).min())
    ledger25=pd.read_parquet(FINAL/"strategy_ledgers.parquet"); ledger25=ledger25.loc[ledger25.config_id.eq(SELECTED)]
    ledger26=pd.read_parquet(FORWARD/"strategy_ledgers.parquet"); ledger26=ledger26.loc[ledger26.config_id.eq(SELECTED)]
    gross25=float((1+ledger25.gross_return.fillna(0)).prod()-1); net25=float((1+ledger25.net_return.fillna(0)).prod()-1)
    gross26=float((1+ledger26.gross_return.fillna(0)).prod()-1); net26=float((1+ledger26.net_return.fillna(0)).prod()-1)
    segment_rows = []
    for segment, group in evaluation_daily.groupby("segment", sort=False):
        segment_rows.append((segment,
                             fmt_pct((1+group.net_return.fillna(0)).prod()-1),
                             fmt_pct((1+group.benchmark_nifty_it.fillna(0)).prod()-1),
                             fmt_pct((1+group.benchmark_nifty50.fillna(0)).prod()-1),
                             f"{int((group.long_exposure>0).sum())} / {int((group.short_exposure>0).sum())} / {int(((group.long_exposure==0)&(group.short_exposure==0)).sum())}"))

    doc=Document(); configure(doc); doc.settings.odd_and_even_pages_header_footer = False
    header = doc.sections[0].header.paragraphs[0]
    header.text = "SIGNED CROSS-MARKET FORECASTING OF NIFTY IT STOCKS  |  DSA5205"
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in header.runs:
        run.font.name = "Times New Roman"; run.font.size = Pt(8.4); run.font.bold = True
    doc.core_properties.title="Cross-Market Forecasting and Signed Trading of Nifty IT Stocks"; doc.core_properties.author="; ".join(a["name"] for a in authors)
    cover(doc,authors); doc.add_page_break()

    doc.add_heading("Contents",level=1)
    toc=[
        ("Abstract","Question, design, segment results, and limitations","3"),
        ("1. Research question and hypotheses","Contribution and assigned-paper linkage","3"),
        ("2. Markets, data, and information clock","Universe, sources, labels, benchmarks","4"),
        ("3. Data engineering and exploratory analysis","Cleaning, trends, peer and cross-market evidence","5"),
        ("4. Feature and capability design","Information ladder, AI event timeline, complexity","7"),
        ("5. Models, validation, and trading protocol","Families, Elastic Net, signed decisions, costs","9"),
        ("6. Combined evaluation: Jan 2025–Sep 2026","Cumulative return and long/short/flat behavior","11"),
        ("7. Retrospective research-period diagnostics","Annual returns, regimes, reversals","13"),
        ("8. Interpretation, limitations, conclusion","Evidence-weighted claims","15"),
        ("AI declaration and contributions","Academic-integrity disclosure","16"),
        ("References and Appendix A","Sources, provenance, and exact evidence chain","16"),
        ("Appendices B–C","Assignment crosswalk and deliverable inventory","17"),
    ]
    table(doc,["Section","Purpose","Page"],toc,[6.2,8.7,1.1],8.1)
    callout(doc,"Evidence status","The combined path is a presentation view, not one pristine holdout. The latest run excludes 2025 and 2026 from its mechanical selection routine, but both periods had been inspected during prior research iterations. Results are therefore historical replication and retrospective extension evidence.")
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; hyperlink(p,"Repository and reproducibility artifacts",GITHUB)
    doc.add_page_break()

    doc.add_heading("Abstract",level=1)
    doc.add_paragraph(f"This study forecasts same-session open-to-close returns for ten fixed current Nifty IT constituents from information aligned to the 08:55 IST decision clock. The selected depth-constrained Extra Trees model combines own-stock, peer, U.S. IT-services, broad-market, macro and dated AI context, while current-vintage macro fallbacks remain an identified limitation. The signed strategy applies a 15-bps effective round-trip hurdle and modeled turnover costs. In the 2025 historical replication it earns {fmt_pct(net25)} net with {fmt_pct(float(f25.net_annual_volatility))} annualized volatility, Sharpe {f25.net_sharpe:.2f}, and OOS R² versus the asset mean of {fmt_pct(float(f25.oos_r2_asset_mean))}. In the separate January–September 2026 retrospective extension it earns {fmt_pct(net26)}, with {fmt_pct(float(f26.net_annual_volatility))} volatility and Sharpe {f26.net_sharpe:.2f}. The combined {fmt_pct(evaluation_total['Signed model'])} path is dominated by the declining 2026 segment. Average cross-sectional IC is negative in both segments, and direct event/capability tests do not support a causal claim that stronger frontier models depress Indian IT equities. The evidence supports a conditional defensive-timing hypothesis, not robust stock-selection alpha.")
    callout(doc,"Principal result",f"Across the displayed 2025–September 2026 path, long exposure is active on {evaluation_counts['long']} days, short exposure on {evaluation_counts['short']} days, both sides on {evaluation_counts['mixed']} days, and neither side on {evaluation_counts['flat']} days. Its value is defensive and conditional, not evidence for a deterministic AI-release short rule.")

    doc.add_heading("1. Research question and hypotheses",level=1)
    doc.add_paragraph("The primary question is whether completed U.S. and global information improves the decision to take a long, short, or flat position in current Nifty IT constituents at the Indian open. The secondary question is whether frontier-model releases or capability improvements contain incremental information about the subsequent returns of U.S. IT-services and Indian IT-services firms.")
    table(doc,["Hypothesis","Testable statement","Decision rule"],[
        ("H1: cross-market spillover","U.S. IT-services and broad U.S. signals improve OOS loss or signed returns beyond own history.","Nested information ladder and identical ridge specification."),
        ("H2: peer information","Nifty IT peers and Nifty 50 state improve constituent-level forecasts.","Leave-one-out peer features; no target stock in its peer aggregate."),
        ("H3: AI displacement","Frontier releases or higher capability precede weaker IT-services returns.","Event study, rank tests, time-controlled sensitivity; no causal wording."),
        ("H4: complexity with shrinkage","More predictors can help when temporal validation and regularization control variance.","Model-family comparison and staged selection."),
        ("H5: economic value","Forecast improvements survive turnover costs and investable benchmarks.","Signed open-to-close ledger versus Nifty IT and Nifty 50."),
    ],[2.9,8.3,4.8],7.6)
    doc.add_heading("1.1 Relation to the assigned research",level=2)
    doc.add_paragraph("Chinco, Clark-Joseph, and Ye (2019) motivate many-stock, short-lived predictors with explicit complexity penalties. This study implements sparse and shrinkage baselines, training-only feature selection, and frequent temporal refits. Kelly, Malamud, and Zhou (2024) motivate the possibility that a large feature space improves market timing when complexity is tuned carefully. Here, complexity is tested through nested information sets, PCA, regularized linear models, boosting, and constrained tree ensembles; increasing dimension is treated as an empirical hypothesis rather than a guaranteed benefit.")
    table(doc,["Study","Frequency / target","Complexity control","Adaptation here"],[
        ("Chinco et al. (2019)","Intraday cross-section","Sparse penalized signals","Daily cross-market lags, Lasso/Elastic Net, forward timing"),
        ("Kelly et al. (2024)","Monthly market timing","Large nonlinear feature maps with shrinkage","RFF–Ridge complexity ratios and nested information sets"),
        ("This study","Daily NSE open-to-close","Shrinkage, PCA, shallow ensembles, staged confirmation","Signed Nifty IT timing and stock selection after costs"),
    ],[3.4,3.7,4.2,4.7],7.0)
    figure(doc,architecture,"Figure 1. Research architecture. Each forecast first determines a directional state—long, flat, or short—then ranks constituents within that state. The labels +1, 0 and −1 denote direction, not literal portfolio weights; execution applies the stated top/bottom-three and gross-exposure rules.",6.10)

    doc.add_heading("2. Markets, data, and information clock",level=1)
    doc.add_heading("2.1 Tradable universe and target",level=2)
    doc.add_paragraph("The tradable cohort is fixed to the ten current Nifty IT constituents available in the project reference file: Coforge, HCL Technologies, Infosys, LTIMindtree, Mphasis, Oracle Financial Services Software, Persistent Systems, Tata Consultancy Services, Tech Mahindra, and Wipro. This fixed-cohort design answers a current-universe question and is explicitly conditioned on survivorship; it does not reconstruct historical index membership.")
    compact_equation(doc,[("r","math"),("OC","sup"),("i,t","sub"),(" = C","math"),("i,t","sub"),(" / O","math"),("i,t","sub"),(" − 1","roman")],1,
                     "Constituent response: same-session NSE open-to-close return.")
    compact_equation(doc,[("ℐ","math"),("t","sub"),("08:55","sup"),(" = {x","math"),("j,s","sub"),(" : τ","math"),("j,s","sub"),("available","sup"),(" < 08:55 IST on t}","roman")],2,
                     "Point-in-time information set at the pre-open decision time.")
    doc.add_paragraph("A prediction is formed just before the Indian open. Positions are denominated in INR, enter at the reported NSE open, and are squared off at the close. Completed U.S. sessions are therefore eligible; same-day Indian closes, highs, lows, and volumes are not. The panel begins in July 2016, screening covers 2021–2022, confirmation covers 2023–2024, 2025 is a historical replication, and January–September 2026 is a retrospective extension. Exchange holidays create no target row; invalid or zero opens are quarantined rather than imputed. Public opens are fill proxies, not opening-auction executions.")
    doc.add_heading("2.2 Data sources and frequency",level=2)
    table(doc,["Source block","Frequency and coverage","Research use","Primary limitation"],[
        ("Yahoo Finance OHLCV","Daily; Indian, U.S., ADR, FX and index histories","Returns, gaps, volatility, breadth, tradable benchmarks","Vendor-adjusted public data; not exchange-certified."),
        ("FRED / ALFRED","Daily to monthly, with vintages where available","Fed rates, yields, curve, credit and macro state","Some series require release lags or current-vintage fallback."),
        ("NiftyHistory / project reference","Dated Nifty 50/500 histories; current Nifty IT list","Point-in-time broad-universe filters and fixed target cohort","Nifty IT history is not reconstructed."),
        ("S&P 500 historical components","Dated membership snapshots","Point-in-time U.S. breadth and constituent features","Public reconstruction; ticker changes require mapping."),
        ("Frontier release inventory","Event dates and curated providers","Release-day and decaying event pressure","Small, curated sample; announcement timing uncertainty."),
        ("Epoch AI benchmarks","Current-vintage benchmark records","Ex-post capability study and mapped event context","Never backfilled into historical tradable features."),
    ],[3.4,3.8,5.4,3.4],7.3)
    callout(doc,"Comparator contract","Nifty 50 and Nifty IT are close-to-close index opportunity-cost references, not matched intraday trades. The fixed-cohort passive basket is survivorship-conditioned. The panel also stores an equal-weight cohort open-to-close return for matched intraday diagnostics; zero, asset-mean and autoregressive forecasts are statistical baselines. Cash earns zero in the simulation.")

    doc.add_heading("3. Data engineering and exploratory analysis",level=1)
    doc.add_heading("3.1 Cleaning and reproducibility",level=2)
    table(doc,["Control","Implementation","Why it matters"],[
        ("Immutable snapshots","Each raw and processed snapshot carries timestamp, content hash, manifest, and source inventory.","Allows exact reconstruction and prevents silent data replacement."),
        ("OHLC validation","Impossible envelopes and zero opens are quarantined; INR=X is close-to-close only.","Prevents fabricated intraday features from bad vendor bars."),
        ("Calendar alignment","U.S. observations map to the next eligible Indian decision session.","Preserves the actual time-zone ordering."),
        ("Missingness","No full-sample imputation; training-window medians and exclusion thresholds are refitted.","Prevents future distribution information from entering earlier models."),
        ("Outliers","Winsorization/scaling parameters are learned inside each training window.","Contains unstable tails without contaminating validation."),
        ("Resume and audit","Checkpoints, run states, hashes, and verification scripts survive interruption.","Supports long laptop runs and evidence integrity."),
    ],[3.2,8.0,4.8],7.5)
    doc.add_heading("3.2 Market paths and exploratory findings",level=2)
    doc.add_paragraph("Development-only EDA shows heavy-tailed constituent returns, changing volatility, substantial common movement within the Nifty IT cohort, and modest calendar effects. The price paths below establish the economic setting before presenting correlations or forecasts. The shaded period begins at the frozen 2025 evaluation boundary; it is displayed for context but was not used to tune the selected model.")
    figure(doc,india_trends,"Figure 2. Daily adjusted-close paths for all ten current Nifty IT constituents, normalized at the start of 2020. The dashed boundary marks the reported January 2025–September 2026 evaluation window.",6.05)
    figure(doc,cross_trends,"Figure 3. Selected Indian and U.S. IT-services price paths. Common broad trends coexist with substantial firm-level divergence, motivating stock-level rather than purely index-level forecasts.",6.05)
    table(doc,["Diagnostic","Observed implication","Modeling response"],[
        ("Return tails and volatility clustering","Normal-error intuition is inadequate.","Tree models, robust preprocessing, drawdown and block-bootstrap inference."),
        ("Strong intra-sector common component","Stock forecasts can collapse into market timing.","Leave-one-out peer features and explicit cross-sectional IC reporting."),
        ("U.S.–India timing","Completed U.S. information is available before NSE opens.","One-way alignment through availability timestamps."),
        ("Sparse AI events","Event estimates have low power.","Randomization/HAC tests and conservative interpretation."),
        ("Large broad-universe panels","Dimension can exceed effective temporal sample size.","Shrinkage, PCA, depth/min-leaf constraints and independent confirmation."),
    ],[4.1,6.1,5.8],7.5)
    doc.add_heading("3.3 Peer and cross-market correlation evidence",level=2)
    doc.add_paragraph("Two correlations answer different questions. The peer matrix uses same-day adjusted-close returns during the 2020–2024 development sample and measures common movement inside the Indian cohort. The cross-market matrix respects the information clock: each completed U.S. close-to-close return is mapped to the next Indian session and correlated with that stock's open-to-close return. Correlation is descriptive and is not interpreted as causality.")
    figure(doc,peer_heatmap,"Figure 4. Indian Nifty IT peer correlation. Positive common movement supports leave-one-out peer features, while imperfect correlations preserve a stock-selection problem.",5.65)
    figure(doc,cross_heatmap,"Figure 5. Prediction-aligned U.S. IT-services versus Indian IT-services correlation. Entries use completed U.S. sessions and next-session Indian open-to-close returns, matching the pre-open forecasting clock.",5.75)

    doc.add_heading("4. Feature and capability design",level=1)
    doc.add_heading("4.1 Nested information ladder",level=2)
    table(doc,["Set","Increment","Representative features"],[
        ("F0","Own history","1–21 day lags; momentum; volatility; moving-average distance; RSI; volume z-score; Fourier calendar."),
        ("F1","+ Nifty IT peers","Leave-one-out peer mean, dispersion, breadth, rolling co-movement."),
        ("F2","+ U.S. IT services","ACN, IBM, CTSH, EPAM and peers; sector breadth, dispersion and volatility."),
        ("F3","+ Nifty 50","Domestic breadth, index state, Bank/VIX and cross-sectional context."),
        ("F4","+ S&P 500 aggregate","Broad U.S. risk, sectors, rates, FX and global index state."),
        ("F5","+ S&P 500 constituents","Point-in-time constituent return and breadth features."),
        ("F6","+ AI capability","Release pressure, disclosed scale, generation and capability context."),
        ("F7","+ full context","Macro, global, nonlinear and regime interactions."),
    ],[1.2,4.0,10.8],7.4)
    figure(doc,ladderfig,"Figure 6. Controlled 2025 information ladder using the same ridge family. More information does not monotonically improve OOS loss or net Sharpe; the full context reduces the economic loss but remains negative for ridge.",5.85)
    doc.add_heading("4.2 AI event, parameter, and benchmark features",level=2)
    p=doc.add_paragraph("AI context is represented at three distinct evidentiary levels. Tradable event features use dated frontier releases and decaying pressure measures. Parameter features use disclosed total or active parameter counts only when explicitly reported and never treat missing disclosure as zero capability. Epoch benchmark scores are used for ex-post hypothesis analysis; current-vintage benchmark records are not injected into historical predictions. To avoid a visually uninformative inventory dump, the timeline marks only releases that establish a new running maximum in the mapped Epoch capability index.")
    p.paragraph_format.keep_together = True
    figure(doc,event_timeline,"Figure 7. Record-improving frontier-model events over Indian and U.S. IT-services price paths. Vertical markers provide temporal context; the lines do not show a uniform negative market shock after capability advances.",6.10)

    doc.add_heading("4.3 Capability hypothesis tests",level=2)
    table(doc,["Test","Estimate","p-value","Interpretation"],[
        ("Frontier release: event minus non-event Nifty IT return",fmt_pct(event["event_minus_non_event"]),f"{event['hac_pvalue']:.3f}","Positive, not the hypothesized negative response; statistically inconclusive."),
        ("Randomization test for release-day difference","two-sided",f"{event['two_sided_randomization_pvalue']:.3f}","No decisive event effect."),
        ("Disclosed parameter scale vs direct Nifty IT return",f"ρ = {cap['direct_nifty_it']['rho']:.3f}",f"{cap['direct_nifty_it']['pvalue']:.3f}","Small non-random subset; no negative relationship."),
        ("Epoch capability index vs direct Nifty IT return","ρ = 0.237","0.289","No statistically decisive monotone relationship."),
        ("Time-controlled Epoch capability coefficient","−0.000676","0.363","Sign turns negative after time control, but uncertainty remains large."),
    ],[6.7,3.0,2.0,4.3],7.4)
    figure(doc,event_heatmap,"Figure 8. One-session stock response around record-capability events. U.S. returns use the first completed U.S. session after publication and Indian returns use the first tradable pre-open-aligned session. Mixed signs provide no descriptive support for a uniform displacement shock.",5.25)
    callout(doc,"Hypothesis decision","The predeclared claim that frontier releases or larger models reliably depress Nifty IT is not supported. AI variables remain contextual predictors, not a mandatory short trigger.")

    doc.add_heading("5. Models, validation, and trading protocol",level=1)
    doc.add_heading("5.1 Candidate families and complexity",level=2)
    table(doc,["Family","Role","Capacity control"],[
        ("Zero / asset mean / AR","Forecast baselines","No or minimal trainable capacity."),
        ("Ridge / Lasso / Elastic Net","Dense and sparse shrinkage","Penalty, training-only preselection and scaling."),
        ("PCA + Ridge","Compressed linear structure","Component count and ridge penalty."),
        ("RFF + Ridge","Nonlinear feature-map complexity","Realized feature ratio, 2,048 cap and ridge penalty."),
        ("Histogram boosting","Nonlinear threshold interactions","Learning rate, leaves, depth, iterations."),
        ("Extra Trees","Nonlinear cross-market regimes","Depth, max features, minimum leaf size, trees."),
    ],[4.1,6.0,5.9],7.5)
    doc.add_paragraph("Elastic Net remains part of the completed candidate suite. Its best screening net Sharpe is −0.722, compared with +0.428 for Extra Trees and +0.782 for histogram boosting, so it is not promoted under the configured ranking. The six RFF–Ridge configurations produce small positive forecast R² but no threshold-crossing trades; their Sharpe is undefined rather than zero. Extra Trees later ranks highest in confirmation, although its confirmation Sharpe is only 0.031 and does not by itself establish a strong economic edge. The selected specification uses 250 trees, maximum depth 8, 50% feature subsampling, and minimum leaf size 40.")
    doc.add_heading("5.2 Temporal protocol",level=2)
    table(doc,["Stage","Evaluation dates","Configurations","Role"],[
        ("Screening","2021–2022",f"{screening_count} evaluated configurations; quarterly refits","Compare families and complexity."),
        ("Confirmation","2023–2024",f"{confirmation_count} rows including promoted candidates and controls; quarterly refits","Historical selection stage."),
        ("Freeze","31 Oct 2026","One config and selection rule","Research freeze after historical periods had been inspected."),
        ("Historical replication","2025 calendar year","Selected config; monthly refits","Estimator-OOS evidence, not a pristine research holdout."),
        ("Retrospective extension","1 Jan–30 Sep 2026","Same config, one pre-2026 fit","No reselection within this run; historically inspected."),
    ],[3.1,3.4,5.1,4.4],7.4)
    figure(doc,family,"Figure 9. Best family-level net Sharpe and evaluated-row counts by stage. ‘Not run’ differs from an RFF configuration that generated forecasts but no trades, for which Sharpe is undefined.",5.80)
    callout(doc,"Training contract","Every rolling fit uses at most 1,260 prior trading sessions, a one-session embargo, seed 17, and training-only filtering, imputation, winsorization, scaling, selection and PCA. Screening/confirmation refit quarterly; the 2025 replication refits monthly; the 2026 extension fits once on pre-2026 data.")

    doc.add_heading("5.3 Signed strategy and evaluation",level=2)
    compact_equation(doc,[("s","math"),("i,t","sub"),(" ∈ {−1, 0, +1},   r","roman"),("p,t","sub"),("net","sup"),(" = Σ","math"),("i","sub"),(" w","math"),("i,t","sub"),(" r","math"),("i,t","sub"),("OC","sup"),(" − c × turnover","roman"),("t","sub")],3,
                     "Forecast state and post-cost daily portfolio return.")
    doc.add_paragraph("The active signed rule uses 5 bps commission plus 2.5 bps slippage each way. The effective threshold is therefore max(5 bps configured forecast floor, 15 bps round-trip friction) = 15 bps. Up to three forecasts above +15 bps are long and up to three below −15 bps are short. Absolute stock weight is capped near one-third and total gross exposure at one. Positions enter from cash at the vendor open, exit at the close, and incur two-sided turnover equal to twice gross exposure. The +1/0/−1 states describe direction, not literal unit weights.")
    table(doc,["Layer","Metrics","Purpose"],[
        ("Forecast","RMSE, MAE, OOS R² versus zero and asset mean","Tests statistical improvement under identical dates."),
        ("Direction and rank","Directional accuracy, confusion matrix, Spearman IC","Separates sign skill from cross-sectional ranking."),
        ("Portfolio","Net return, volatility, Sharpe, Sortino, drawdown, Calmar","Measures risk-adjusted economic value."),
        ("Implementation","Turnover, costs, long/short/flat days, exposure","Tests whether the signal is tradable rather than merely accurate."),
        ("Inference","HAC alpha/loss tests and circular block-bootstrap Sharpe interval","Accounts for serial dependence and finite calendar length."),
        ("Interpretability","Grouped OOS permutation importance","Identifies information families used without causal attribution."),
    ],[3.0,6.5,6.5],7.4)
    callout(doc,"Comparator contract","Forecast models and statistical baselines share decision dates, target, information clock, and trading-cost convention. Nifty IT, Nifty 50, and fixed-cohort buy-and-hold are economic opportunity-cost references with close-to-close or passive exposure; their return horizons and costs differ from the open-to-close signed strategy and are reported explicitly.")

    doc.add_heading("6. Combined evaluation: January 2025–September 2026",level=1)
    doc.add_heading("6.1 Cumulative performance and signed decisions",level=2)
    doc.add_paragraph("The reporting view concatenates the 2025 historical-replication ledger and January–September 2026 retrospective extension. It is one performance display, not one untouched test or one estimator-update policy: the vertical boundary records the later pre-2026 fit required to issue extension predictions.")
    table(doc,["Metric","Combined estimate","Interpretation"],[
        ("Signed model cumulative net return",fmt_pct(evaluation_total["Signed model"]),"Compounded after modeled turnover costs across both segments."),
        ("Nifty IT cumulative return",fmt_pct(evaluation_total["Nifty IT"]),"Sector benchmark declines across the combined interval."),
        ("Nifty 50 cumulative return",fmt_pct(evaluation_total["Nifty 50"]),"Broad-market opportunity-cost benchmark."),
        ("Current-member buy-and-hold",fmt_pct(evaluation_total["Current-member buy & hold"]),"Passive fixed-cohort reference initialized from the last pre-evaluation close; survivorship-conditioned."),
        ("Annualized model return / Sharpe",f"{fmt_pct(eval_annual_return)} / {eval_sharpe:.3f}","Descriptive aggregation; the two protocol segments retain separate inference."),
        ("Maximum drawdown",fmt_pct(eval_max_drawdown),"Worst peak-to-trough loss in the displayed path."),
        ("Long-active / short-active / mixed / flat days",f"{evaluation_counts['long']} / {evaluation_counts['short']} / {evaluation_counts['mixed']} / {evaluation_counts['flat']}","Long and short activity counts may overlap on mixed books; flat means zero gross exposure."),
    ],[5.3,4.0,6.7],7.6)
    figure(doc,combined_wealth,"Figure 10. Cumulative January 2025–September 2026 evaluation. The path combines the 2025 frozen final ledger and the later no-reselection 2026 extension; the dashed line marks the refit boundary.",6.10)
    table(doc,["Protocol segment","Model net","Nifty IT","Nifty 50","Long / short / flat days"],segment_rows,[4.2,2.5,2.5,2.5,4.3],7.3)
    table(doc,["Segment","Dates","Net return","Volatility","Sharpe","R² vs mean","Mean IC"],[
        ("2025 replication","249",fmt_pct(net25),fmt_pct(float(f25.net_annual_volatility)),f"{f25.net_sharpe:.3f}",fmt_pct(float(f25.oos_r2_asset_mean)),f"{f25.spearman_ic:.3f}"),
        ("2026 extension","185",fmt_pct(net26),fmt_pct(float(f26.net_annual_volatility)),f"{f26.net_sharpe:.3f}",fmt_pct(float(f26.oos_r2_asset_mean)),f"{f26.spearman_ic:.3f}"),
    ],[3.1,1.4,2.2,2.2,1.8,2.3,2.0],7.1)
    doc.add_paragraph(f"The 2025 policy uses 5 long-active days, 65 short-active days and 179 flat days. Gross return is {fmt_pct(gross25)}, but modeled friction reduces compounded net return to {fmt_pct(net25)}; the arithmetic ledger cost sum is {fmt_pct(float(ledger25.trading_cost.sum()))}. The 2026 extension uses 14 long-active, 79 short-active and 92 flat days; gross return is {fmt_pct(gross26)} and net return {fmt_pct(net26)}. Cost erosion and the negative mean IC show that the primary unresolved question is timing value versus stock-ranking value, not merely whether shorting exists.")

    doc.add_heading("6.2 Monthly behavior, attribution, and uncertainty",level=2)
    figure(doc,combined_positioning,"Figure 11. Monthly returns and signed deployment across the complete reported evaluation. Positive exposure is long, negative exposure is short, and zero exposure is flat.",5.70)
    table(doc,["Attribution question","Evidence","Conclusion"],[
        ("Was the strategy buy-only?",f"{evaluation_counts['short']} active short days and {evaluation_counts['flat']} flat days.","No; the economic rule is genuinely signed."),
        ("Was performance simply long beta?","The largest gain occurs while Nifty IT falls during 2026.","No; downside timing and short exposure dominate."),
        ("Was it an AI-release rule?","Direct AI-event group importance is negligible; the curated calendar ends in May 2025.","No; event variables are context, not a mandatory trigger."),
        ("Did cross-market data matter?","The fitted model relies heavily on U.S. IT-services predictors in 2026.","Incremental value remains unresolved until matched ablation."),
    ],[5.0,6.1,4.9],7.4)
    figure(doc,importance,"Figure 12. Exploratory grouped permutation importance in the two evaluation segments. The historical artifact permutes stock-day rows once; the revised pipeline uses repeated whole-date permutations. Importance measures reliance, not causality or isolated incremental value.",5.85)
    doc.add_paragraph(f"Inference remains segment-aware. The 2025 HAC alpha test is inconclusive (p={i25['alpha_hac_pvalue']:.3f}) and its block-bootstrap Sharpe interval spans negative and positive outcomes. The 2026 extension is stronger (HAC alpha p={i26['alpha_hac_pvalue']:.3f}; Sharpe {f26.net_sharpe:.2f}) but covers only 185 sessions in a pronounced decline. The combined curve is therefore an accurate return summary, not evidence that the same edge is stable in every regime.")
    callout(doc,"Critical limitation","The curated AI-release calendar ends in May 2025. The combined result evaluates the signed cross-market model, not a contemporaneous 2026 frontier-announcement trading rule.")

    doc.add_heading("7. Retrospective research-period diagnostics",level=1)
    doc.add_heading("7.1 Stitched predictions from research stages",level=2)
    doc.add_paragraph("For completeness, the next diagnostic stitches every available out-of-sample ledger for the selected Extra Trees configuration: screening (2021–2022), confirmation (2023–2024), the canonical 2025 final period, and the frozen January–September 2026 extension. It answers the descriptive question ‘what happened across all testing stages?’ It is not a single untouched holdout or an investable historical track record because the first four years participated in screening and model selection.")
    table(doc,["Comparator","2021–Sep 2026 return","Interpretation"],[
        ("Signed model, net",fmt_pct(research_total["Signed model"]),"Positive after modeled costs; return is concentrated in falling regimes and 2026."),
        ("Nifty IT buy-and-hold",fmt_pct(research_total["Nifty IT"]),"Sector index rises overall despite major 2022, 2025 and 2026 declines."),
        ("Nifty 50 buy-and-hold",fmt_pct(research_total["Nifty 50"]),"Broad-market benchmark outperforms the signed model over the full research period."),
        ("Current-member buy-and-hold",fmt_pct(research_total["Current-member buy & hold"]),"Equal capital in ten current constituents, held without rebalancing; survivorship-conditioned."),
    ],[5.0,3.5,7.5],7.5)
    figure(doc,stitched,"Figure 13. Complete research-period wealth comparison. Vertical lines separate screening, confirmation, final evaluation, and extension; the stitched curve is descriptive, not one untouched holdout.",6.05)
    callout(doc,"Why buy-and-hold wins overall","The current-member basket captures the large 2021, 2023, and 2024 sector advances without forecast hurdles or time spent flat. The signed model sacrifices that upside participation to reduce exposure during declines; Nifty 50 also benefits from broader sector diversification.")
    doc.add_heading("7.2 Year-by-year testing-period returns",level=2)
    annual_rows=[]
    reasons={
        2021:"Strong technology rally; conservative thresholds and flat exposure leave most upside uncaptured.",
        2022:"Nifty IT drawdown; signed positions provide material downside protection.",
        2023:"Sector recovery; lagged and defensive signals do not rotate long quickly enough.",
        2024:"Broad technology advance; model remains low-beta and captures little of the rally.",
        2025:"Sector falls; model roughly preserves capital but Nifty 50 diversification wins.",
        2026:"Sharp Nifty IT decline through September; frequent short positions drive the strongest model year.",
    }
    for year,row in research_annual.iterrows():
        annual_rows.append((str(year) if year<2026 else "2026 Jan–Sep",fmt_pct(row["Signed model"]),fmt_pct(row["Nifty IT"]),fmt_pct(row["Nifty 50"]),fmt_pct(row["Current-member buy & hold"]),reasons[int(year)]))
    table(doc,["Period","Model","Nifty IT","Nifty 50","Buy & hold","Reason"],annual_rows,[2.0,2.0,2.0,2.0,2.2,5.8],7.0)
    figure(doc,annualfig,"Figure 14. Calendar-period return comparison. The model behaves defensively: it gives up much of the upside in strong sector years but protects capital in 2022, 2025, and especially 2026.",6.05)
    p=doc.add_paragraph("The yearly pattern explains the full-period ranking. The strategy is not a conventional long-only growth allocation; it is a timing overlay. Its edge, when present, comes from avoiding or shorting weak sector regimes. Consequently, a passive current-member basket dominates across the entire 2021–September 2026 research period even though the signed model performs better during several drawdowns.")
    p.paragraph_format.keep_together = True
    doc.add_heading("7.3 Sideways, trending, and reversal regimes",level=2)
    doc.add_paragraph("Regimes are defined ex post at monthly frequency to describe—not predict—behavior. A month is rising when Nifty IT returns at least +3%, falling when it returns at most −3%, and sideways otherwise. A reversal month is the first directional month opposite the previous directional state; intervening sideways months do not reset the last direction. These labels are never supplied to model fitting and therefore cannot create forecast leakage.")
    regime_rows=[]
    for regime in ["Rising","Sideways","Falling"]:
        g=research_monthly.loc[research_monthly.regime.eq(regime)]
        regime_rows.append((regime,str(len(g)),fmt_pct(g["Signed model"].mean()),fmt_pct(g["Nifty IT"].mean()),fmt_pct(g["Nifty 50"].mean()),fmt_pct(g["Current-member buy & hold"].mean())))
    table(doc,["Monthly regime","Months","Model mean","Nifty IT mean","Nifty 50 mean","Buy & hold mean"],regime_rows,[3.2,1.7,2.6,2.7,2.7,3.1],7.2)
    figure(doc,regimefig,"Figure 15. Mean monthly returns by realized Nifty IT regime. The model is strongest in falling months, modestly positive in sideways months, and nearly flat in rising months.",6.0)
    doc.add_paragraph("In sideways markets the model earns a modest average +0.21% per month while Nifty 50 averages +0.92%. During sustained rises the model averages only +0.03% while Nifty IT gains +7.04% and the current-member basket gains +8.92%. During falling months the signed model averages +1.71% while Nifty IT loses 7.45%. These ex-post associations describe defensive behavior; whether forecast hurdles or lagged features cause the asymmetry remains a mechanism to test.")
    doc.add_heading("7.4 Response to trend reversals",level=2)
    figure(doc,reversalfig,"Figure 16. Mean return in reversal months. The model responds asymmetrically: it performs well when an established rise reverses downward, but it is slow when a decline reverses upward.",5.50)
    rev_rows=[]
    reversals=research_monthly.loc[research_monthly.reversal]
    for typ in ["Rising → Falling","Falling → Rising"]:
        g=reversals.loc[reversals.reversal_type.eq(typ)]
        rev_rows.append((typ,str(len(g)),fmt_pct(g["Signed model"].mean()),fmt_pct((1+g["Signed model"]).prod()-1),fmt_pct((g["Signed model"]>0).mean()),fmt_pct(g["Nifty IT"].mean())))
    table(doc,["Reversal","Months","Model mean","Model compounded","Positive months","Nifty IT mean"],rev_rows,[3.4,1.7,2.6,3.0,2.8,2.5],7.2)
    doc.add_paragraph("The observed reversal response is asymmetric. Across 12 rising-to-falling reversals the model averages +1.94%, is profitable in two-thirds of months, and compounds to +24.83%. Across 11 falling-to-rising reversals it averages −0.15% and compounds to −1.86%. Lagged momentum, tree thresholds and entry hurdles are plausible explanations, but this descriptive analysis does not identify the mechanism. The evidence establishes weaker performance around upward reversals, not why it occurs.")
    callout(doc,"Regime conclusion","The retrospective research-period diagnostic supports a downside-timing interpretation, not a universal return-forecasting claim. Falling and downward-reversal regimes generate the model’s strongest results; persistent rallies and upward reversals create the largest opportunity cost.")
    doc.add_heading("8. Interpretation, limitations, and conclusion",level=1)
    doc.add_heading("8.1 Evidence-weighted interpretation",level=2)
    table(doc,["Claim","Evidence status","Report conclusion"],[
        ("U.S. and global information can help pre-open Nifty IT decisions.","Unresolved incrementally","Extra Trees ranks highest under the configured confirmation metric; matched group ablations are required."),
        ("More features always improve prediction.","Rejected","The fixed ridge ladder deteriorates as raw S&P 500 dimension expands; complexity requires shrinkage and nonlinear capacity control."),
        ("Frontier AI releases reliably cause Nifty IT declines.","Not supported","Event differences are positive and insignificant; capability samples are small and confounded by calendar time."),
        ("The strategy is already production-ready.","Rejected","2025 is flat, data are public end-of-day proxies, and 2026 is a short single-regime extension."),
    ],[5.8,3.2,7.0],7.5)
    doc.add_heading("8.2 Limitations",level=2)
    doc.add_paragraph("The fixed current-member cohort creates survivorship conditioning. Public vendor opens abstract from opening-auction queueing, bid–ask spread variation, taxes, borrow availability, short-sale constraints, market impact, and corporate-action edge cases. S&P and Nifty membership histories are public reconstructions rather than licensed exchange archives. Macro releases may require conservative lags, and some current-vintage fallbacks are not fully point-in-time.")
    doc.add_paragraph("The effective inference sample is the number of serially dependent trading days, not the number of stock-day rows. AI releases are few, parameter disclosure is selective, parameter counts are not comparable across dense and mixture-of-experts architectures, and benchmark progress is multidimensional. The 2026 extension occurs during a sharp sector drawdown and does not include a contemporaneously maintained release calendar after May 2025.")
    doc.add_heading("8.3 Conclusion",level=2)
    doc.add_paragraph("The strongest contribution is a temporally aligned, auditable retrospective design that converts cross-market forecasts into signed positions and reconciled costs. Extra Trees ranks highest under the configured historical confirmation rule, but the 2025 replication has weak forecast and net economic evidence: R² versus the asset mean and mean IC are negative, and costs remove most gross gains. The 2026 extension is strongly positive during a sharp sector decline, making the combined result promising but regime-sensitive and dominated by defensive timing. Direct AI-event and capability hypotheses do not receive statistically decisive support. The next evidentiary steps are strict-vintage sensitivity, matched timing-versus-selection attribution, date-block inference and genuinely future observations after a prospective freeze.")

    doc.add_heading("Team contribution statement",level=1)
    doc.add_paragraph("PRATYUSH SINHA, RAMYANI PALIT, RITIK SRIVASTAVA, and VICTOR LEE CHIA SWEA jointly contributed to research framing, data and feature review, model and validation design, interpretation, report review, and final quality assurance. The repository preserves the shared implementation and evidence trail; any institutionally required individual percentage allocation should be confirmed by the team in the Canvas submission form.")

    doc.add_heading("AI usage declaration",level=1)
    doc.add_paragraph("OpenAI coding and language tools were used to generate implementation ideas, draft and refactor Python scripts, diagnose runtime errors, organize the reproducible experiment pipeline, improve expression, and format portions of the report. All data choices, model specifications, commands, outputs, statistical interpretations, citations, and submitted content were reviewed by the authors. The authors remain responsible for the content and quality of the submitted work.")
    doc.add_heading("Academic integrity",level=1)
    doc.add_paragraph("The submission is prepared with reference to the NUS Plagiarism Policy, the NUS Code of Student Conduct (Section A: Academic Integrity), Academic Integrity Essentials, and the Policy for Use of AI in Teaching and Learning. AI assistance is declared transparently; external data, code, and research sources are attributed.")
    for label,url in [
        ("NUS Plagiarism Policy","https://myportal.nus.edu.sg/studentportal/student-discipline/all/docs/NUS-Plagiarism-Policy.pdf"),
        ("NUS Code of Student Conduct","https://studentconduct.nus.edu.sg/wp-content/uploads/NUS-Code-of-Student-Conduct.pdf"),
        ("Academic Integrity Essentials","https://libguides.nus.edu.sg/new2nus/acadintegrity#s-lib-ctab-22144949-1"),
        ("Policy for Use of AI in Teaching and Learning","http://ctlt.nus.edu.sg/policy-for-use-of-ai-in-teaching-and-learning.pdf")]:
        p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(1); hyperlink(p,label,url)
        for run in p.runs: run.font.size=Pt(8.8)
    doc.add_heading("References",level=1)
    refs=[
        "Chinco, A., Clark-Joseph, A. D., & Ye, M. (2019). Sparse signals in the cross-section of returns. The Journal of Finance, 74(1), 449–492.",
        "Kelly, B., Malamud, S., & Zhou, K. (2024). The virtue of complexity in return prediction. The Journal of Finance, 79(1), 459–503.",
        "National Stock Exchange of India. Nifty indices and constituent reference material.",
        "Yahoo Finance. Historical daily OHLCV and index data used under the project’s public-data protocol.",
        "Federal Reserve Bank of St. Louis. FRED and ALFRED economic data services.",
        "Epoch AI. Benchmark data and model capability records; current-vintage evidence used only for ex-post analysis.",
        "NiftyHistory.in. Public historical Nifty constituent reference files.",
        "fja05680/sp500. Public S&P 500 Historical Components & Changes dataset (GitHub).",
        "Bailey, D. H., & López de Prado, M. (2014). The deflated Sharpe ratio: Correcting for selection bias, backtest overfitting, and non-normality.",
    ]
    for i,x in enumerate(refs,1):
        p=doc.add_paragraph(f"[{i}] {x}"); p.paragraph_format.space_after=Pt(1)
        for run in p.runs: run.font.size=Pt(8.6)
    doc.add_heading("Appendix A. Reproducibility and provenance",level=1)
    table(doc,["Evidence object","Immutable identifier"],[
        ("Processed dataset",DATASET_ID),("Screening run",SCREEN_ID),("Confirmation run",CONFIRM_ID),("Frozen specification",FREEZE_ID),("Canonical final run",FINAL_ID),("2026 forward extension",FORWARD_ID),("Selected configuration",SELECTED),
    ],[5.2,10.8],7.5)
    doc.add_paragraph("The final AI-capability pipeline passed 200 verification checks with zero failures. The 2026 forward extension passed 28 checks with zero failures. Manifests record configuration hashes, parent runs, input snapshots, environment metadata, output hashes, evaluation dates, and the absence of model reselection. Predictions, ledgers, cost sensitivity, refit diagnostics, inference, and plots are retained beside each run.")
    table(doc,["Selected-model parameter","Frozen value"],[
        ("Family","Extra Trees regressor"),("Trees","250"),("Maximum depth","8"),("Maximum features","0.50"),("Minimum samples per leaf","40"),("Feature set","F7_full_context"),("2026 fitting policy","One fit on pre-2026 data; no updates"),
    ],[8.2,7.8],7.7)
    callout(doc,"Reproduction principle","Run identifiers are evidence addresses, not presentation labels. The report builder reads only the listed immutable objects and fails if a required manifest is missing.")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    doc.add_heading("Appendix B. Assignment alignment",level=1)
    table(doc,["Project requirement","Implementation","Report location"],[
        ("Non-trivial market prediction","Nifty IT constituent same-day O–C forecasts from cross-market information.","Sections 1–2"),
        ("Data exploration and cleaning","OHLC audit, missingness, regime, seasonality, event and capability diagnostics.","Section 3"),
        ("Leakage and timing control","08:55 IST availability clock; training-only transforms; temporal alignment.","Sections 2–3"),
        ("Feature engineering and complexity","Nested F0–F7 sets, lags, rolling, Fourier, breadth, macro and nonlinear features.","Section 4"),
        ("Model comparison","Baselines, shrinkage, PCA, boosting and forests through screening/confirmation.","Section 5"),
        ("Out-of-sample evaluation","Combined January 2025–September 2026 display with protocol-separated final and extension segments.","Sections 6–7"),
        ("Economic evaluation","Signed long/short/flat ledger, costs, Nifty IT and Nifty 50 benchmarks.","Sections 5–7"),
        ("Interpretability and inference","Grouped permutation importance, HAC tests and block bootstrap.","Sections 6–8"),
        ("Clear interpretation","Unsupported AI causality rejected; regime dependence and limitations disclosed.","Section 8"),
        ("Reproducibility","Timestamped hashes, manifests, checkpoints, frozen IDs and verification checks.","Appendix A"),
    ],[4.5,7.6,3.9],7.2)
    doc.add_heading("Appendix C. Deliverable inventory",level=1)
    doc.add_paragraph("The repository contains configuration files, ingestion scripts, cleaning and panel builders, EDA and event-study scripts, walk-forward model runners, parallel checkpoint logic, freeze and verification commands, predictions, per-day long/short decisions, performance tables, figures, and the deterministic report builder. Large raw and intermediate artifacts are tracked separately from source-code review through the project’s large-file workflow.")

    # Keep figure images from splitting their captions and update fields on open.
    settings=doc.settings._element
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    upd=OxmlElement("w:updateFields"); upd.set(qn("w:val"),"true"); settings.append(upd)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
