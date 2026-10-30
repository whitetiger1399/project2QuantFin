"""Build the DSA5205 cross-market Project 2 report (DOCX only).

The report is evidence-driven: completed screening results are reported as
screening evidence, while confirmation and final holdout sections remain
explicitly marked as pending until their immutable artifacts exist.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUT = REPORTS / "Project2_Team16_Report.docx"
FIG_OUT = REPORTS / "figures_cross_market"
FIG_OUT.mkdir(parents=True, exist_ok=True)

DATASET_ID = "cross_market_panel_20261030T044550Z_e8964cacce4208c3"
ANALYSIS_ID = "analysis_20261030T044648Z_26ceef2429b3"
RUN_ID = "cm_screening_20261030T093727Z_0e77ef60dd73"
DATASET = ROOT / "data/processed/cross_market" / DATASET_ID
EDA = ROOT / "artifacts/cross_market/analysis" / ANALYSIS_ID
RUN = ROOT / "artifacts/cross_market/runs" / RUN_ID
DESIGN = ROOT / "artifacts/cross_market/report_figures/design_figures_20261030T104226Z_d63b02e71159"
LOGO = ROOT / "assets/NUS_logo_full-horizontal.jpg"
GITHUB = "https://github.com/whitetiger1399/project2QuantFin"

NAVY = "17365D"
BLUE = "2F5D73"
TEAL = "2A9D8F"
ORANGE = "E97824"
RED = "A44747"
TEXT = "151515"
MUTED = "5B6770"
LIGHT = "EEF2F4"
PALE_BLUE = "EAF1F5"
PALE_ORANGE = "FCEFE5"
WHITE = "FFFFFF"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def set_repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    node = OxmlElement("w:tblHeader")
    node.set(qn("w:val"), "true")
    tr_pr.append(node)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:cantSplit")) is None:
        tr_pr.append(OxmlElement("w:cantSplit"))


def set_cell_shading(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=70, start=85, bottom=70, end=85):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{name}"))
        if node is None:
            node = OxmlElement(f"w:{name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_widths(table, widths_cm):
    table.autofit = False
    total_twips = int(sum(widths_cm) * 567)
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(total_twips))
    tbl_w.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_cm:
        node = OxmlElement("w:gridCol")
        node.set(qn("w:w"), str(int(width * 567)))
        grid.append(node)
    for row in table.rows:
        for cell, width in zip(row.cells, widths_cm):
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(int(width * 567)))
            tc_w.set(qn("w:type"), "dxa")
            cell.width = Cm(width)


def add_hyperlink(paragraph, text: str, url: str):
    rid = paragraph.part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color"); color.set(qn("w:val"), BLUE); props.append(color)
    underline = OxmlElement("w:u"); underline.set(qn("w:val"), "single"); props.append(underline)
    run.append(props)
    node = OxmlElement("w:t"); node.text = text; run.append(node)
    link.append(run)
    paragraph._p.append(link)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run("DSA5205 Project 2  |  Team 16  |  ")
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    paragraph._p.append(fld)


def keep_with_next(paragraph):
    paragraph.paragraph_format.keep_with_next = True


def add_caption(doc, text: str):
    p = doc.add_paragraph(style="Caption")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run(text)
    return p


def add_figure(doc, path: Path, caption: str, width=6.55):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Inches(width))
    add_caption(doc, caption)


def add_callout(doc, label: str, text: str, fill=PALE_BLUE):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_widths(table, [16.1])
    cell = table.cell(0, 0)
    set_cell_shading(cell, fill)
    set_cell_margins(cell, top=100, start=130, bottom=100, end=130)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(label + "  ")
    r.bold = True; r.font.color.rgb = RGBColor.from_string(NAVY)
    p.add_run(text)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_table(doc, headers, rows, widths, font_size=8.0, header_fill=NAVY):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    set_table_widths(table, widths)
    hdr = table.rows[0]
    set_repeat_header(hdr)
    for i, value in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_shading(cell, header_fill)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(str(value)); r.bold = True; r.font.color.rgb = RGBColor.from_string(WHITE); r.font.size = Pt(font_size)
    for ridx, values in enumerate(rows):
        row = table.add_row()
        prevent_row_split(row)
        if ridx % 2:
            for cell in row.cells: set_cell_shading(cell, "F7F9FA")
        for i, value in enumerate(values):
            cell = row.cells[i]
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(value)); r.font.size = Pt(font_size); r.font.color.rgb = RGBColor.from_string(TEXT)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def friendly_family(value: str) -> str:
    return {
        "extra_trees": "Extra Trees", "random_forest": "Random Forest",
        "hist_gradient_boosting": "Histogram GB", "pca_ridge": "PCA + Ridge",
        "elastic_net": "Elastic Net", "rff_ridge": "RFF + Ridge",
        "autoregression": "Autoregression", "asset_mean": "Asset mean",
    }.get(value, value.replace("_", " ").title())


def make_result_figures(lb: pd.DataFrame):
    plt.rcParams.update({"font.family": "DejaVu Serif", "axes.titlesize": 11, "axes.labelsize": 9})

    # One configuration per model family keeps labels readable and avoids a chart dump.
    family_best = (lb.dropna(subset=["net_sharpe"]).sort_values("rank")
                   .groupby("family", as_index=False).first().sort_values("net_sharpe"))
    fig, ax = plt.subplots(figsize=(8.8, 4.8), dpi=220)
    colors = ["#A44747" if x < 0 else "#2A9D8F" for x in family_best.net_sharpe]
    ax.barh([friendly_family(x) for x in family_best.family], family_best.net_sharpe, color=colors)
    ax.axvline(0, color="#333", lw=.8)
    ax.set_xlabel("Annualized net Sharpe (screening, 2021-2022)")
    ax.set_title("Best configuration within each model family", fontweight="bold")
    ax.grid(axis="x", color="#D9DEE2", lw=.6); ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    for y, v in enumerate(family_best.net_sharpe):
        ax.text(v + (.04 if v >= 0 else -.04), y, f"{v:.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=8)
    fig.subplots_adjust(left=.26, right=.96, bottom=.15, top=.88)
    leaderboard = FIG_OUT / "screening_family_leaderboard.png"
    fig.savefig(leaderboard, bbox_inches="tight", facecolor="white"); plt.close(fig)

    ledgers = pd.read_parquet(RUN / "strategy_ledgers.parquet")
    chosen = ledgers[ledgers.config_id.eq("cm_extra_trees_8ef7eb6a91c8")].sort_values("decision_date").copy()
    chosen["decision_date"] = pd.to_datetime(chosen.decision_date)
    # Use arrays here: constructing with Series plus a new DatetimeIndex would
    # align on the old integer index and silently produce an all-NaN chart.
    wealth = pd.DataFrame({
        "Selected strategy (net)": (1 + chosen.net_return.fillna(0)).cumprod().to_numpy(),
        "Nifty IT buy-and-hold proxy": (1 + chosen.benchmark_nifty_it.fillna(0)).cumprod().to_numpy(),
        "Nifty 50 buy-and-hold": (1 + chosen.benchmark_nifty50.fillna(0)).cumprod().to_numpy(),
        "Equal-weight fixed cohort": (1 + chosen.benchmark_cohort.fillna(0)).cumprod().to_numpy(),
    }, index=chosen.decision_date.to_numpy())
    fig, ax = plt.subplots(figsize=(8.8, 4.7), dpi=220)
    colors = ["#17365D", "#E97824", "#2A9D8F", "#786F8A"]
    for col, color in zip(wealth.columns, colors): ax.plot(wealth.index, wealth[col], label=col, lw=1.7, color=color)
    ax.set_ylabel("Growth of INR 1")
    ax.set_title("Screening-period wealth: selected strategy and benchmarks", fontweight="bold")
    ax.grid(color="#D9DEE2", lw=.55); ax.set_axisbelow(True); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(ncol=2, fontsize=7.8, frameon=False, loc="upper center", bbox_to_anchor=(.5, -.13))
    fig.subplots_adjust(left=.09, right=.98, bottom=.25, top=.88)
    wealth_path = FIG_OUT / "screening_wealth_readable.png"
    fig.savefig(wealth_path, bbox_inches="tight", facecolor="white"); plt.close(fig)

    rff = lb[lb.family.eq("rff_ridge")].copy()
    parsed = rff.configuration.map(json.loads)
    rff["ratio"] = parsed.map(lambda x: x["parameters"]["complexity_ratio"])
    rff["penalty"] = parsed.map(lambda x: x["parameters"]["penalty"])
    fig, ax = plt.subplots(figsize=(8.8, 4.4), dpi=220)
    for penalty, data in rff.sort_values("ratio").groupby("penalty"):
        ax.plot(data.ratio, 100 * data.oos_r2_asset_mean, marker="o", lw=1.6, label=f"Ridge penalty {penalty:g}")
    ax.axhline(0, color="#444", lw=.8)
    ax.set_xscale("log"); ax.set_xticks([.5, 1, 2, 5, 10, 15]); ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel("Random Fourier features / input features")
    ax.set_ylabel("OOS R² vs asset-mean forecast (%)")
    ax.set_title("Complexity experiment: forecast accuracy, not trading Sharpe", fontweight="bold")
    ax.grid(color="#D9DEE2", lw=.55); ax.set_axisbelow(True); ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8)
    complexity = FIG_OUT / "rff_complexity_oos_r2.png"
    fig.savefig(complexity, bbox_inches="tight", facecolor="white"); plt.close(fig)

    importance = pd.read_csv(RUN / "feature_importance_by_refit.csv")
    importance = importance[importance.config_id.eq("cm_extra_trees_8ef7eb6a91c8")]
    top = importance.groupby("feature").importance.mean().nlargest(15).sort_values()
    def shorten(x):
        x = x.replace("sp500_raw__", "S&P500 · ").replace("us_context__", "US context · ")
        x = x.replace("india_core__", "India · ").replace("us_tech__", "US tech · ").replace("global__", "Global · ")
        return x.replace("__", " · ").replace("_", " ")
    fig, ax = plt.subplots(figsize=(8.8, 5.5), dpi=220)
    ax.barh([shorten(x) for x in top.index], top.values, color="#2F5D73")
    ax.set_xlabel("Mean impurity importance across quarterly refits")
    ax.set_title("Screening leader: most-used predictors", fontweight="bold")
    ax.grid(axis="x", color="#D9DEE2", lw=.55); ax.set_axisbelow(True); ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=7.6)
    fig.subplots_adjust(left=.38, right=.97, bottom=.12, top=.9)
    feature = FIG_OUT / "screening_feature_importance.png"
    fig.savefig(feature, bbox_inches="tight", facecolor="white"); plt.close(fig)
    return leaderboard, wealth_path, complexity, feature


def equation(path: Path, latex: str, width=10.5, height=1.0):
    fig = plt.figure(figsize=(width, height), dpi=220)
    fig.text(.5, .5, latex, ha="center", va="center", fontsize=16, color="#17365D")
    fig.savefig(path, bbox_inches="tight", transparent=True, pad_inches=.08)
    plt.close(fig)


def configure_document(doc: Document):
    section = doc.sections[0]
    section.page_width = Cm(21.0); section.page_height = Cm(29.7)
    section.top_margin = Cm(1.65); section.bottom_margin = Cm(1.6)
    section.left_margin = Cm(2.2); section.right_margin = Cm(2.2)
    section.header_distance = Cm(.7); section.footer_distance = Cm(.75)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"; normal.font.size = Pt(9.5); normal.font.color.rgb = RGBColor.from_string(TEXT)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.line_spacing = 1.06
    normal.paragraph_format.space_after = Pt(3.5)

    for name, size, before, after, color in [
        ("Title", 20, 0, 7, NAVY), ("Subtitle", 11, 0, 6, MUTED),
        ("Heading 1", 13.2, 9, 4, NAVY), ("Heading 2", 10.7, 7, 3, BLUE),
        ("Heading 3", 9.7, 5, 2, NAVY), ("Caption", 8.1, 1, 5, MUTED),
    ]:
        s = doc.styles[name]
        s.font.name = "Times New Roman"; s.font.size = Pt(size); s.font.color.rgb = RGBColor.from_string(color)
        s._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        s.paragraph_format.space_before = Pt(before); s.paragraph_format.space_after = Pt(after)
        if name.startswith("Heading") or name == "Title": s.font.bold = True
        if name.startswith("Heading"): s.paragraph_format.keep_with_next = True
    doc.styles["Caption"].font.italic = True

    header = section.header.paragraphs[0]
    header.text = "CROSS-MARKET PRE-OPEN FORECASTING OF NIFTY IT STOCKS"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.runs[0].font.name = "Times New Roman"; header.runs[0].font.size = Pt(7.5); header.runs[0].font.color.rgb = RGBColor.from_string(MUTED)
    add_page_number(section.footer.paragraphs[0])
    for r in section.footer.paragraphs[0].runs:
        r.font.name = "Times New Roman"; r.font.size = Pt(7.5); r.font.color.rgb = RGBColor.from_string(MUTED)


def build():
    required = [DATASET / "manifest.json", EDA / "manifest.json", RUN / "manifest.json", LOGO]
    missing = [str(p) for p in required if not p.exists()]
    if missing: raise FileNotFoundError("Missing report evidence:\n" + "\n".join(missing))
    dataset_manifest = read_json(DATASET / "manifest.json")
    eda_manifest = read_json(EDA / "manifest.json")
    run_manifest = read_json(RUN / "manifest.json")
    authors = sorted(x["name"] for x in read_json(ROOT / "assets/authors.json"))
    lb = pd.read_csv(RUN / "leaderboard.csv")
    selected = lb[lb.config_id.eq(run_manifest["selected_config_id"])].iloc[0]
    inference = read_json(RUN / "selected_model_inference.json")
    leaderboard_fig, wealth_fig, complexity_fig, feature_fig = make_result_figures(lb)

    eq_target = FIG_OUT / "eq_target.png"
    eq_info = FIG_OUT / "eq_information_set.png"
    eq_strategy = FIG_OUT / "eq_strategy.png"
    equation(eq_target, r"$y_{i,t}=\frac{P^{close}_{i,t}}{P^{open}_{i,t}}-1$")
    equation(eq_info, r"$\mathcal{I}_{t}^{08{:}55}=\{x_{j,s}:\;\tau^{available}_{j,s}<08{:}55\;\mathrm{IST\ on\ day}\ t\}$")
    equation(eq_strategy, r"$w_{i,t}\propto\max(\widehat y_{i,t}-h_t,0),\quad \sum_i w_{i,t}\leq1,\quad r^{net}_{p,t}=\sum_i w_{i,t}y_{i,t}-c\,\mathrm{turnover}_t$")

    doc = Document()
    configure_document(doc)
    props = doc.core_properties
    props.title = "Cross-Market Pre-Open Forecasting of Nifty IT Stocks"
    props.subject = "DSA5205 Project 2"
    props.author = "; ".join(authors)

    # Cover page: compact academic title block.
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(LOGO), width=Inches(3.0))
    p.paragraph_format.space_after = Pt(14)
    title = doc.add_paragraph(style="Title"); title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("Cross-Market Pre-Open Forecasting\nof Nifty IT Stocks")
    sub = doc.add_paragraph(style="Subtitle"); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run("Information progression, shrinkage, and model complexity under leakage-controlled daily evaluation")
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Data Science in Quantitative Finance · DSA5205\nProject2 Teams 16")
    r.bold = True; r.font.size = Pt(11); r.font.color.rgb = RGBColor.from_string(NAVY)
    p.paragraph_format.space_after = Pt(11)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for idx, name in enumerate(authors):
        r = p.add_run(name + ("\n" if idx < len(authors)-1 else "")); r.font.size = Pt(10)
    p.paragraph_format.space_after = Pt(10)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Repository: "); add_hyperlink(p, GITHUB, GITHUB)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Report evidence date: 30 October 2026").italic = True
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(13)
    r = p.add_run("SCREENING RESULTS INCLUDED · CONFIRMATION AND FINAL HOLDOUT PENDING")
    r.bold = True; r.font.size = Pt(8.5); r.font.color.rgb = RGBColor.from_string(ORANGE)
    doc.add_page_break()

    doc.add_heading("Foreword", level=1)
    doc.add_paragraph(
        "This report studies whether information already available before the Indian cash-market open improves forecasts of same-day open-to-close returns for a fixed cohort of current Nifty IT constituents. The design separates economic intuition from statistical evidence: market timing is explicit, every feature is availability-lagged, model selection is confined to dated validation stages, and trading performance is reported after costs. The completed screening stage is documented here; no confirmation or final-holdout claim is made before those artifacts are produced."
    )
    doc.add_heading("Abstract", level=1)
    doc.add_paragraph(
        "Daily stock-level returns are forecast at 08:55 IST for ten current Nifty IT constituents and traded from the reported NSE open to close. A 2016-2026 panel combines India market state, a limited U.S. technology basket, Indian ADRs, broad U.S. and global context, point-in-time S&P 500 membership, and macro-financial series. The processed panel contains 25,380 stock-days, 2,538 decision dates, and 3,333 candidate features. Predeclared feature sets F0-F5 test incremental information gain; model families span baselines, shrinkage, dimension reduction, tree ensembles, boosting, and random Fourier features with ridge regularization. In 2021-2022 screening, the depth-constrained Extra Trees configuration on F4 produced a 0.849 net Sharpe, 3.13% annual net return, -3.11% maximum drawdown, and 0.83% out-of-sample R² versus an asset-mean forecast. Its bootstrap Sharpe interval [-0.257, 1.723] and non-significant HAC alpha require caution. Confirmation and untouched final testing remain pending."
    )
    add_callout(doc, "Evidence status", f"Dataset {DATASET_ID}; EDA {ANALYSIS_ID}; completed screening {RUN_ID} (hash 0e77ef60dd73). Confirmation, model freeze, and final holdout are intentionally not populated.", PALE_ORANGE)

    doc.add_heading("1. Research question and contribution", level=1)
    doc.add_paragraph(
        "The primary question is whether completed U.S. and global sessions contain incremental information for the cross-section of Indian technology stocks after controlling for each stock's own history and the Indian market state. The strategy is intentionally practical: one decision per Indian trading day, a known information cutoff, executable open-to-close positions, explicit costs, and a Nifty 50 buy-and-hold comparison."
    )
    add_table(doc, ["Hypothesis", "Predeclared comparison", "Interpretation"], [
        ("H1 · Cross-market gain", "F2/F3 versus F0/F1", "U.S. technology and global context improve OOS forecasts."),
        ("H2 · Breadth gain", "F4 versus F2", "Point-in-time S&P 500 information adds useful breadth."),
        ("H3 · Complexity", "RFF ratios 0.5-15 with ridge", "More nonlinear features help only with adequate shrinkage."),
        ("H4 · Economic value", "Net strategy versus Nifty 50 and Nifty IT", "Forecast gains survive turnover and costs."),
    ], [2.8, 4.1, 9.2], 7.8)
    doc.add_paragraph(
        "Chinco, Clark-Joseph, and Ye (2019) motivate a large cross-asset feature pool with regularization because predictive links can be sparse and short-lived. Kelly, Malamud, and Zhou (2024) motivate the controlled complexity experiment: random nonlinear features can improve return prediction when shrinkage contains estimation noise. These ideas are adapted to daily cross-market timing rather than copied at their original minute or monthly horizons."
    )
    add_figure(doc, DESIGN / "10_research_architecture.png", "Figure 1. Research architecture. Information sets expand from Nifty IT history to Indian, U.S. technology, global, and point-in-time broad-U.S. predictors; the target remains the same NSE open-to-close return.")

    doc.add_heading("2. Markets, assets, and information timing", level=1)
    doc.add_heading("2.1 Traded cohort and benchmark", level=2)
    assets = dataset_manifest["evidence_summary"]["assets"]
    doc.add_paragraph(
        "The tradable universe is a frozen cohort of the ten constituents listed in the current Nifty IT file on 30 October 2026: " + ", ".join(x.replace(".NS", "") for x in assets) + ". This supports complete stock-level tracking but is not a historical reconstruction of the Nifty IT index. Results therefore condition on current membership and carry survivorship risk. Nifty 50 buy-and-hold is the main real-world benchmark; a Nifty IT proxy and the equal-weight fixed cohort are diagnostic comparators."
    )
    add_table(doc, ["Market block", "Primary instruments or source", "Role at 08:55 IST"], [
        ("India target/state", "10 Nifty IT stocks; Nifty 50, Bank, India VIX, NIFTYBEES", "Own lags, market and sector state"),
        ("Limited U.S. technology", "20 U.S. technology leaders", "Completed prior U.S. session"),
        ("Indian ADRs", "INFY and WIT ADRs", "Overnight India-linked price discovery"),
        ("Broad U.S.", "SPY, QQQ, sector ETFs; PIT S&P 500 constituents", "Market breadth and cross-sectional state"),
        ("Global", "Selected Asian/global indices and USD/INR", "Completed-session risk context"),
        ("Macro-financial", "FRED/ALFRED rates, curves, spreads, volatility", "Release-lagged state variables"),
    ], [3.0, 7.2, 5.9], 7.7)
    add_figure(doc, DESIGN / "12_information_clock.png", "Figure 2. Information clock. The 08:55 IST forecast uses only observations whose market session or release was complete and available before the decision; execution follows at the 09:15 NSE open.")
    add_figure(doc, eq_target, "Equation 1. Stock-level target: same-day open-to-close return.", width=5.5)
    add_figure(doc, eq_info, "Equation 2. Availability-time information set. Calendar date alone never determines feature eligibility.", width=6.1)

    doc.add_heading("3. Data engineering and quality control", level=1)
    doc.add_paragraph(
        "Raw snapshots are immutable and identified by timestamp. The panel builder reads the latest completed snapshots, applies symbol-specific cleaning, records quarantined rows, constructs availability-aware features, and writes a content-addressed dataset manifest. The raw audit passed with warnings. INR=X is restricted to close-to-close use because its Yahoo OHLC envelope is unreliable; the NIFTYBEES open-to-close anomaly on 7 July 2009 is quarantined; optional broad-universe rows with impossible OHLC values are excluded."
    )
    add_table(doc, ["Item", "Value", "Meaning"], [
        ("Observation unit", "25,380 stock-days", "10 assets × 2,538 decision dates"),
        ("Decision span", "21 Jul 2016-29 Oct 2026", "Daily frequency; Indian sessions"),
        ("Candidate features", "3,333", "Nested F0-F5 information sets"),
        ("Quarantined rows", str(dataset_manifest["evidence_summary"]["quarantined_row_count"]), "Invalid/impossible source rows removed"),
        ("Macro fallbacks", str(len(dataset_manifest["evidence_summary"]["macro_current_vintage_fallbacks"])), "Current-vintage series flagged, not silently treated as PIT"),
    ], [3.2, 3.5, 9.4], 8)
    add_callout(doc, "Leakage controls", "Feature availability precedes 08:55 IST; rolling statistics use past values only; scaling, imputation, screening, and selection are fitted inside each training window; S&P 500 aggregates use dated membership; the final period is not accessed during screening.")

    doc.add_heading("4. Feature engineering and information progression", level=1)
    add_table(doc, ["Set", "Increment", "Examples", "Purpose"], [
        ("F0", "Own stock + calendar", "1/2/5/10/21-day returns; ranges; volatility; weekday/Fourier", "Forecast baseline"),
        ("F1", "+ India", "Nifty 50, Bank, India VIX, cross-sectional breadth", "Domestic state"),
        ("F2", "+ U.S. tech + ADR", "Lagged U.S. tech returns, momentum, volatility; INFY/WIT ADRs", "Focused spillover"),
        ("F3", "+ Global context", "SPY/QQQ/sectors, global indices, FX", "Risk-on/off state"),
        ("F4", "+ PIT S&P 500", "Dated-member raw signals and robust breadth aggregates", "Broad information complexity"),
        ("F5", "+ Macro/nonlinear", "Rates, curves, spreads, regimes, interactions", "Robustness and state dependence"),
    ], [1.0, 3.1, 7.2, 4.8], 7.5)
    doc.add_paragraph(
        "Price features include log and simple returns, rolling mean and volatility, downside variation, open-gap and range statistics, price-to-moving-average ratios, momentum, cross-sectional dispersion, and trend-shift indicators. Calendar seasonality is encoded with sine/cosine Fourier pairs rather than unordered month labels. Higher-order and interaction features are kept within predeclared F5 or generated through random Fourier mappings; ridge, Lasso, Elastic Net, depth constraints, minimum leaf size, PCA, and training-only preselection control variance."
    )

    doc.add_heading("5. Exploratory and statistical analysis", level=1)
    doc.add_paragraph(
        "EDA is descriptive and precedes model selection. It evaluates target tails, time-varying volatility, correlation structure, lead-lag patterns, missingness, stationarity, autocorrelation, heteroskedasticity, and seasonality. Event and lead-lag overlays are not treated as causal evidence. No sourced retrospective event markers were available in the completed EDA artifact, so an event-attribution chart is deliberately excluded."
    )
    add_figure(doc, EDA / "figures/02_target_distributions.png", "Figure 3. Open-to-close return distributions for the frozen Nifty IT cohort. Heavy tails and asset heterogeneity motivate robust evaluation rather than Gaussian-error assumptions.")
    add_figure(doc, EDA / "figures/03_rolling_return_volatility.png", "Figure 4. Rolling return and volatility. Time variation supports walk-forward refitting and regime-aware robustness checks.")
    add_figure(doc, EDA / "figures/05_cross_asset_correlation.png", "Figure 5. Cross-asset target correlation. Shared sector exposure is visible, but imperfect co-movement preserves a cross-sectional ranking problem.")
    add_figure(doc, EDA / "figures/06_us_india_lead_lag.png", "Figure 6. U.S.-India lead-lag correlations. These diagnostics guide candidate lags; they do not establish causal transmission.")

    doc.add_heading("6. Models, validation, and trading rule", level=1)
    add_figure(doc, DESIGN / "11_experiment_design.png", "Figure 7. Experiment design. Feature progression, model-family comparison, and controlled nonlinear complexity are evaluated inside time-ordered walk-forward stages.")
    add_table(doc, ["Family", "Role", "Overfitting control"], [
        ("Zero / asset mean / AR", "Forecast baselines", "Minimal degrees of freedom"),
        ("Ridge / Lasso / Elastic Net", "Linear shrinkage and sparse links", "Penalty; training-only preprocessing"),
        ("PCA + Ridge", "Compressed high-dimensional linear model", "Components and ridge penalty"),
        ("Random Forest / Extra Trees", "Nonlinear interactions", "Depth, leaf size, feature subsampling"),
        ("Histogram boosting", "Sequential nonlinear correction", "Learning rate, leaves, L2"),
        ("RFF + Ridge", "Kelly et al.-style complexity path", "Fixed ratios, cap 4,096, ridge shrinkage"),
    ], [4.1, 6.0, 6.0], 7.7)
    add_table(doc, ["Stage", "Dates", "Refit design", "Permitted use"], [
        ("Initial training", "21 Jul 2016-31 Dec 2020", "Past data only", "Fit first screening model"),
        ("Screening", "2021-2022", "Quarterly refit, daily OOS forecast", "Compare 36 predeclared configurations"),
        ("Confirmation", "2023-2024", "Quarterly refit", "Confirm family/feature conclusions"),
        ("Final holdout", "2025-29 Oct 2026", "Monthly refit, frozen setup", "One-time final estimate"),
    ], [3.1, 3.4, 5.2, 4.4], 7.7)
    add_figure(doc, eq_strategy, "Equation 3. Long-only top-three forecast-to-position rule with forecast hurdle and turnover cost.", width=6.3)
    doc.add_paragraph(
        "The standard cost assumption is 5 bps commission plus 2.5 bps slippage per side (15 bps round trip), with 0/10/20/40 bps robustness cases. A position is opened only when the predicted return clears the hurdle and estimated round-trip cost. Individual stock weight is capped at 50%. The primary selection metric is post-cost net Sharpe; OOS R², information coefficient, turnover, drawdown, and complexity are tie-break diagnostics."
    )

    doc.add_heading("7. Completed screening results", level=1)
    add_callout(doc, "Screening conclusion", "The depth-six Extra Trees model on F4 is the provisional candidate because it produced the highest post-cost screening Sharpe with materially lower capacity and turnover than the unconstrained forest. It is not the final selected model until confirmation and freeze are completed.", PALE_ORANGE)
    add_table(doc, ["Metric", "Screening estimate", "Interpretation"], [
        ("Net annual return", f"{100*selected.net_annual_return:.2f}%", "After standard transaction costs"),
        ("Net Sharpe", f"{selected.net_sharpe:.3f}", "Primary screening selection metric"),
        ("Maximum drawdown", f"{100*selected.maximum_drawdown:.2f}%", "Screening path risk"),
        ("OOS R² vs asset mean", f"{100*selected.oos_r2_asset_mean:.2f}%", "Small positive forecast improvement"),
        ("Directional accuracy", f"{100*selected.directional_accuracy:.2f}%", "Stock-day sign accuracy"),
        ("Mean daily turnover", f"{100*selected.mean_daily_turnover:.2f}%", "Low activity after hurdle"),
        ("Mean refit runtime", f"{selected.mean_runtime_seconds_per_refit:.1f} s", "Quarterly screening refit"),
    ], [4.2, 3.4, 8.5], 8)
    add_figure(doc, leaderboard_fig, "Figure 8. Best configuration per model family. Only tree ensembles produced positive post-cost screening Sharpe among actively trading families; family comparisons remain validation evidence.")
    add_figure(doc, wealth_fig, "Figure 9. Screening wealth paths. The selected strategy is low-turnover and comparatively stable, but its 2021-2022 gain is far smaller than the Nifty IT rally and must not be extrapolated.")
    add_figure(doc, feature_fig, "Figure 10. Mean Extra Trees impurity importance across quarterly refits. The leader uses a mix of U.S. breadth, sector, global, and Indian-state variables; impurity importance is associative and can favor continuous predictors.")
    add_figure(doc, complexity_fig, "Figure 11. Random Fourier complexity path. Forecast R² remains slightly positive, but all tested RFF forecasts failed the trading hurdle and generated no positions; trading Sharpe is therefore undefined, not zero.")
    doc.add_paragraph(
        f"The selected configuration uses 300 trees, maximum depth 6, max_features=0.33, and minimum leaf size 50. Its mean parameter proxy is {selected.mean_trainable_parameters_proxy:,.0f}, or {selected.mean_parameter_to_observation_ratio:.2f} parameters per training observation. The unconstrained Extra Trees variant improved forecast R² to 1.11% but increased the proxy ratio to 25.20, turnover to 20.77%, and reduced net Sharpe to 0.192. This is the clearest screening evidence that complexity without sufficient structural constraint can weaken economic performance."
    )
    doc.add_paragraph(
        f"Uncertainty is substantial. The circular block-bootstrap 95% interval for net Sharpe is [{inference['net_sharpe_95_ci'][0]:.3f}, {inference['net_sharpe_95_ci'][1]:.3f}]. Annualized alpha versus Nifty 50 is {100*inference['annualized_alpha']:.2f}% with HAC p={inference['alpha_hac_pvalue']:.3f}. The loss-differential HAC test versus the asset-mean forecast has p=0.075 before multiple-testing adjustment and 0.192 after Benjamini-Hochberg correction. Screening evidence is therefore suggestive rather than statistically decisive. Constant-input Spearman warnings arise for constant baseline predictions and do not invalidate the fitted nonconstant models."
    )

    doc.add_heading("8. What remains before a final claim", level=1)
    add_table(doc, ["Gate", "Required action", "Current status"], [
        ("Confirmation", "Run promoted family representatives on 2023-2024 only", "Pending"),
        ("Model freeze", "Freeze feature set, model, hyperparameters, rule, and costs", "Pending"),
        ("Final holdout", "Run one untouched 2025-2026 evaluation with monthly refits", "Pending"),
        ("Robustness", "Report cost curve, subperiods, turnover, IC stability, and bootstrap intervals", "Pending final model"),
        ("Report finalization", "Replace interim wording with frozen-run facts; regenerate DOCX/PDF", "Pending"),
    ], [3.0, 9.3, 3.8], 7.9)
    doc.add_paragraph(
        "The final report must distinguish selection evidence from final evidence. No model change is permitted after inspecting the final holdout. Any post-holdout revision becomes a new research cycle with a newly reserved test period."
    )

    doc.add_heading("9. Limitations and interim conclusion", level=1)
    doc.add_paragraph(
        "The fixed current-member cohort creates survivorship conditioning; Yahoo price fields and public membership histories are not exchange-certified; some macro series use current-vintage fallbacks; open-price execution omits auction queueing and stock-specific market impact; and the two-year screening sample is short for inference. Cross-market associations may reflect common global risk rather than direct transmission. These limitations constrain interpretation but do not compromise the internal timing protocol."
    )
    doc.add_paragraph(
        "The completed evidence supports a disciplined next step, not a finished investment claim. Broad U.S. information improved the best screening model, while depth constraint and low turnover mattered more than unconstrained capacity. The complexity experiment also demonstrates that positive forecast R² need not translate into trades when predicted returns do not clear costs. Confirmation and the untouched final holdout will determine whether these patterns persist."
    )

    doc.add_heading("AI tool declaration", level=1)
    doc.add_paragraph(
        "OpenAI Codex was used to assist with code drafting, debugging, figure generation, report structuring, language refinement, and document formatting. All empirical claims in this report are tied to repository artifacts and remain the responsibility of the listed authors. AI-generated suggestions were reviewed against the project requirements, data manifests, and completed run outputs."
    )

    doc.add_heading("References", level=1)
    refs = [
        "Chinco, A. M., Clark-Joseph, A. D., & Ye, M. (2019). Sparse signals in the cross-section of returns. The Journal of Finance, 74(1), 449-492. https://doi.org/10.1111/jofi.12733",
        "Gu, S., Kelly, B. T., & Xiu, D. (2020). Empirical asset pricing via machine learning. Review of Financial Studies, 33(5), 2223-2273.",
        "Kelly, B. T., Malamud, S., & Zhou, K. (2024). The virtue of complexity in return prediction. The Journal of Finance, 79(1), 459-501. https://doi.org/10.1111/jofi.13298",
        "National University of Singapore. NUS Plagiarism Policy. https://myportal.nus.edu.sg/studentportal/student-discipline/all/docs/NUS-Plagiarism-Policy.pdf",
        "National University of Singapore. Code of Student Conduct, Section A: Academic Integrity. https://studentconduct.nus.edu.sg/wp-content/uploads/NUS-Code-of-Student-Conduct.pdf",
        "NUS Libraries. Academic Integrity Essentials. https://libguides.nus.edu.sg/new2nus/acadintegrity",
        "NUS Centre for Teaching, Learning and Technology. Policy for Use of AI in Teaching and Learning, Sections 3-4. http://ctlt.nus.edu.sg/policy-for-use-of-ai-in-teaching-and-learning.pdf",
        "Project repository and reproducibility artifacts. " + GITHUB,
        "Yahoo Finance market data; FRED/ALFRED macro-financial data; public historical constituent files cited in the repository data manifests.",
    ]
    for idx, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(.6); p.paragraph_format.first_line_indent = Cm(-.6)
        p.add_run(f"[{idx}] ").bold = True; p.add_run(ref)

    doc.add_heading("Appendix A. Reproducibility and provenance", level=1)
    add_table(doc, ["Artifact", "Identifier"], [
        ("Processed dataset", DATASET_ID),
        ("EDA run", ANALYSIS_ID),
        ("Screening run", RUN_ID),
        ("Screening content hash", run_manifest["content_hash"]),
        ("Configuration count", str(run_manifest["configuration_count"])),
        ("Completed refits", f"{run_manifest['checkpoint_count']}/{run_manifest['expected_checkpoint_count']}"),
        ("Selected screening configuration", run_manifest["selected_config_id"]),
        ("Environment", f"Python 3.10.10; scikit-learn 1.7.2; macOS arm64"),
    ], [5.4, 10.7], 7.6)
    doc.add_paragraph(
        "Exact commands, configuration hashes, source snapshots, run states, checkpoints, and environment versions are stored under configs/, data/processed/cross_market/, and artifacts/cross_market/. The repository README is the operational entry point."
    )

    doc.add_heading("Appendix B. Assignment-alignment checklist", level=1)
    add_table(doc, ["Project requirement", "Implemented evidence"], [
        ("Markets, assets, frequency, timing", "Sections 2-3; Figures 1-2"),
        ("Labels and leakage-safe features", "Equations 1-2; Sections 3-4"),
        ("Buy-and-hold and forecast baselines", "Sections 2 and 6; Figure 9"),
        ("Model choice and overfitting control", "Section 6; Figures 7 and 11"),
        ("Time-respecting split and selection", "Section 6; stage table"),
        ("Trades, costs, and constraints", "Equation 3; Section 6"),
        ("OOS return, Sharpe, drawdown, benchmarks", "Section 7; Figures 8-9"),
        ("Interpretation and reproducibility", "Sections 7-9; Appendix A"),
    ], [6.4, 9.7], 7.8)

    doc.save(OUT)
    print(json.dumps({
        "output": str(OUT), "authors": authors, "dataset_id": DATASET_ID,
        "analysis_id": ANALYSIS_ID, "screening_run_id": RUN_ID,
        "screening_status": run_manifest["status"], "selected_screening_config": run_manifest["selected_config_id"],
        "pdf_modified": False,
    }, indent=2))


if __name__ == "__main__":
    build()
