"""Build the compact, sample-matched DSA5205 Project 2 report."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures_ieee"
FIGURES.mkdir(parents=True, exist_ok=True)
RUNS = ROOT / "artifacts" / "runs"
SCREEN = RUNS / "models_screening_8d1f4f8a10e794eb"
CONFIRM = RUNS / "models_confirmation_5d6ed2ce5fa7b6cb"
FINAL = RUNS / "models_final_test_53e047b58e92e27b"
EDA_M = ROOT / "artifacts/eda/market_market_yahoo_20261019T010846Z_2014-12-31_d2cc08ac48"
EDA_F = ROOT / "artifacts/eda/features_features_yahoo_20261019T010846Z_799f619a4f_F2_initial_train"
STATS_PATH = ROOT / "artifacts/statistics/features_yahoo_20261019T010846Z_799f619a4f_F2_initial_train/statistical_tests.json"
FEATURE_MANIFEST = ROOT / "data/processed/features_yahoo_20261019T010846Z_799f619a4f/manifest.json"
GITHUB = "https://github.com/whitetiger1399/project2QuantFin"

NAVY = "17365D"
BLUE = "2F5D73"
TEXT = "111111"
MUTED = "596A72"
LIGHT = "E9ECEF"
MID = "D3D9DD"
WHITE = "FFFFFF"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=55, start=70, bottom=55, end=70) -> None:
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


def repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    node = OxmlElement("w:tblHeader")
    node.set(qn("w:val"), "true")
    tr_pr.append(node)


def add_hyperlink(paragraph, text: str, url: str) -> None:
    rid = paragraph.part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color"); color.set(qn("w:val"), BLUE); rpr.append(color)
    underline = OxmlElement("w:u"); underline.set(qn("w:val"), "single"); rpr.append(underline)
    run.append(rpr)
    node = OxmlElement("w:t"); node.text = text; run.append(node)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_page_field(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run("Project report  •  ")
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    paragraph._p.append(fld)


def add_bottom_rule(paragraph, color=MUTED, width="4") -> None:
    ppr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), width)
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    ppr.append(borders)


def short_name(name: str) -> str:
    replacements = {
        "spy_": "SPY ", "qqq_": "QQQ ", "iwm_": "IWM ", "tlt_": "TLT ", "gld_": "GLD ",
        "log_return": "return", "volatility": "vol", "momentum": "mom", "correlation": "corr",
        "downside_deviation": "downside vol", "price_to_sma": "price/SMA", "return_": "ret ",
    }
    out = name
    for old, new in replacements.items():
        out = out.replace(old, new)
    return out.replace("_", " ")


def plot_correlation_pairs() -> Path:
    raw = pd.read_csv(EDA_F / "tables/feature_correlations.csv", index_col=0)
    values = raw.to_numpy(float)
    names = list(raw.columns)
    pairs = []
    for i in range(1, len(names)):
        for j in range(i):
            value = values[i, j]
            if np.isfinite(value):
                pairs.append((names[i], names[j], value))
    frame = pd.DataFrame(pairs, columns=["a", "b", "correlation"])
    positive = frame.nlargest(12, "correlation").sort_values("correlation")
    negative = frame.nsmallest(12, "correlation").sort_values("correlation", ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.2), dpi=220)
    for ax, subset, title, color in (
        (axes[0], positive, "Strongest positive feature pairs", "#477A8B"),
        (axes[1], negative, "Strongest negative feature pairs", "#9C5A55"),
    ):
        labels = [f"{short_name(a)}  ↔  {short_name(b)}" for a, b in zip(subset.a, subset.b)]
        ax.barh(labels, subset.correlation, color=color)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_xlabel("Pearson correlation", fontsize=8.5)
        ax.tick_params(axis="both", labelsize=7.2)
        ax.grid(axis="x", color="#D7D7D7", linewidth=.55)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        for y, val in enumerate(subset.correlation):
            ax.text(val + (0.012 if val >= 0 else -0.012), y, f"{val:.2f}", va="center",
                    ha="left" if val >= 0 else "right", fontsize=7)
    axes[0].set_xlim(0, 1.08)
    axes[1].set_xlim(min(-1.05, negative.correlation.min() - .08), 0)
    fig.subplots_adjust(left=.22, right=.98, bottom=.12, top=.90, wspace=.78)
    path = FIGURES / "correlation_extremes.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def config_label(row) -> str:
    family = row["family"].replace("_", " ").title()
    try:
        p = eval(row["parameters"], {"__builtins__": {}}, {})
    except Exception:
        p = {}
    if row["family"] in {"random_forest", "extra_trees"}:
        detail = f"d{p.get('max_depth')} / leaf {p.get('min_samples_leaf')}"
    elif row["family"] in {"ridge", "lasso"}:
        detail = f"α={p.get('alpha')}"
    elif row["family"] == "elastic_net":
        detail = f"α={p.get('alpha')} / l1={p.get('l1_ratio')}"
    elif row["family"] == "pca_ridge":
        detail = f"PC={p.get('n_components')} / α={p.get('alpha')}"
    elif row["family"] == "rff_ridge":
        detail = f"RFF={p.get('n_components', p.get('rff_components', '?'))} / α={p.get('alpha')}"
    elif row["family"] == "hist_gradient_boosting":
        detail = f"leaves={p.get('max_leaf_nodes')} / L2={p.get('l2_regularization')}"
    else:
        detail = "baseline"
    return f"{family} ({detail})"


def plot_screening(screen: pd.DataFrame) -> Path:
    top = screen.sort_values("median_annual_net_sharpe", ascending=False).head(15).copy().iloc[::-1]
    labels = [config_label(r) for _, r in top.iterrows()]
    colors = ["#2F5D73" if f == "random_forest" else "#78909C" for f in top.family]
    fig, ax = plt.subplots(figsize=(9.4, 5.4), dpi=220)
    ax.barh(labels, top.median_annual_net_sharpe, color=colors)
    ax.axvline(0, color="#222222", linewidth=.7)
    ax.set_xlabel("Median annual net Sharpe (screening)", fontsize=9)
    ax.tick_params(axis="y", labelsize=8.2)
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="x", color="#D8D8D8", linewidth=.55)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.subplots_adjust(left=.36, right=.98, bottom=.12, top=.97)
    path = FIGURES / "screening_leaderboard_readable.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_complexity(screen: pd.DataFrame) -> Path:
    families = list(dict.fromkeys(screen.family.tolist()))
    cmap = plt.get_cmap("tab10")
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.25), dpi=220)
    for idx, fam in enumerate(families):
        d = screen[screen.family.eq(fam)]
        label = fam.replace("_", " ").title()
        axes[0].scatter(d.median_parameter_to_observation_ratio.clip(lower=1e-5), d.oos_r2_vs_historical_mean,
                        s=25, alpha=.8, color=cmap(idx % 10), label=label)
        axes[1].scatter(d.mean_train_mse, d.mse, s=25, alpha=.8, color=cmap(idx % 10), label=label)
    axes[0].set_xscale("log")
    axes[0].axhline(0, color="#333333", linewidth=.7)
    axes[0].axvline(1, color="#777777", linewidth=.7, linestyle="--")
    axes[0].set_xlabel("Median parameter / observation ratio (log)", fontsize=8.5)
    axes[0].set_ylabel("OOS R² vs historical mean", fontsize=8.5)
    axes[0].set_title("Capacity versus generalization", fontsize=10, fontweight="bold")
    lo = min(screen.mean_train_mse.min(), screen.mse.min())
    hi = max(screen.mean_train_mse.max(), screen.mse.max())
    axes[1].plot([lo, hi], [lo, hi], color="#555555", linestyle="--", linewidth=.8, label="train = OOS")
    axes[1].set_xlabel("Mean training MSE", fontsize=8.5)
    axes[1].set_ylabel("Walk-forward OOS MSE", fontsize=8.5)
    axes[1].set_title("Training–test error map", fontsize=10, fontweight="bold")
    for ax in axes:
        ax.grid(color="#DDDDDD", linewidth=.5); ax.set_axisbelow(True)
        ax.tick_params(labelsize=7.5); ax.spines[["top", "right"]].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=7, frameon=False, bbox_to_anchor=(.5, -.03))
    fig.subplots_adjust(left=.08, right=.98, bottom=.25, top=.88, wspace=.28)
    path = FIGURES / "complexity_generalization_all_models.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_stage(screen: pd.DataFrame, confirm: pd.DataFrame, final: pd.DataFrame) -> Path:
    rows = [d[d.family.eq("random_forest")].iloc[0] for d in (screen, confirm, final)]
    labels = ["Screening\n2015–18", "Confirmation\n2019–21", "Final\n2022–25"]
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.15), dpi=220)
    metrics = [("annualized_net_return", "Annualized net return", 100), ("net_sharpe", "Net Sharpe", 1), ("max_drawdown", "Maximum drawdown", 100)]
    for ax, (key, title, scale) in zip(axes, metrics):
        vals = [r[key] * scale for r in rows]
        ax.bar(labels, vals, color=["#2F5D73", "#7A929C", "#9C5A55"])
        ax.axhline(0, color="#222", linewidth=.7); ax.set_title(title, fontsize=9.5, fontweight="bold")
        ax.tick_params(labelsize=7.5); ax.grid(axis="y", color="#DDD", linewidth=.5); ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        if scale == 100: ax.set_ylabel("Percent", fontsize=8)
    fig.tight_layout()
    path = FIGURES / "stage_stability_compact.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def equation(name: str, tex: str) -> Path:
    path = FIGURES / f"eq_{name}.png"
    fig = plt.figure(figsize=(8.3, .5), dpi=240)
    fig.patch.set_alpha(0)
    fig.text(.5, .5, tex, ha="center", va="center", fontsize=16, color="#111111")
    plt.axis("off")
    fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=.04)
    plt.close(fig)
    return path


def build() -> Path:
    authors = read_json(ROOT / "assets/authors.json")
    if not authors:
        raise ValueError("assets/authors.json must contain at least one author")
    screen = pd.read_csv(SCREEN / "config_metrics.csv")
    confirm = pd.read_csv(CONFIRM / "config_metrics.csv")
    final = pd.read_csv(FINAL / "config_metrics.csv")
    annual = pd.read_csv(FINAL / "annual_returns.csv")
    costs = pd.read_csv(FINAL / "cost_sensitivity.csv")
    stability = pd.read_csv(FINAL / "feature_stability.csv")
    stats = read_json(STATS_PATH)
    features = read_json(FEATURE_MANIFEST)
    verify = read_json(REPORTS / "output_verification.json")
    eval_report = read_json(FINAL / "evaluation_report.json")
    rf_s = screen[screen.family.eq("random_forest")].iloc[0]
    rf_c = confirm[confirm.family.eq("random_forest")].iloc[0]
    rf_f = final[final.family.eq("random_forest")].iloc[0]
    ar_f = final[final.family.eq("autoregression")].iloc[0]

    corr_fig = plot_correlation_pairs()
    screen_fig = plot_screening(screen)
    complexity_fig = plot_complexity(screen)
    stage_fig = plot_stage(screen, confirm, final)
    eq_target = equation("target", r"$y_t=P^{adj}_{t+2}/P^{adj}_{t+1}-1,\qquad \mathrm{available}(y_t)=t+2$")
    eq_net = equation("net", r"$\pi_{t+1}=\mathbf{1}\{\widehat y_t>h\},\qquad r^{net}_{t+2}=\pi_{t+1}y_t-c|\pi_{t+1}-\pi_t|$")

    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin, section.bottom_margin = Cm(1.55), Cm(1.45)
    section.left_margin, section.right_margin = Cm(1.75), Cm(1.75)
    section.header_distance, section.footer_distance = Cm(.62), Cm(.65)
    section.different_first_page_header_footer = True

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"; normal.font.size = Pt(9.4); normal.font.color.rgb = RGBColor.from_string(TEXT)
    normal.paragraph_format.space_after = Pt(4); normal.paragraph_format.line_spacing = 1.02
    for name, size, before, after in (("Title", 17, 4, 8), ("Heading 1", 12, 9, 4), ("Heading 2", 10.5, 7, 3), ("Heading 3", 9.5, 5, 2)):
        style = styles[name]
        style.font.name = "Times New Roman"; style.font.size = Pt(size); style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(TEXT)
        style.paragraph_format.space_before = Pt(before); style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
    cap = styles["Caption"]
    cap.font.name = "Times New Roman"; cap.font.size = Pt(8); cap.font.italic = True; cap.font.color.rgb = RGBColor.from_string(TEXT)
    cap.paragraph_format.space_before = Pt(1); cap.paragraph_format.space_after = Pt(5); cap.paragraph_format.keep_with_next = True

    header = section.header.paragraphs[0]
    header.text = "LEAKAGE-CONTROLLED SPY FORECASTING  |  DSA5205"
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in header.runs:
        run.font.name = "Times New Roman"; run.font.bold = True; run.font.size = Pt(7.2); run.font.color.rgb = RGBColor.from_string(TEXT)
    add_bottom_rule(header, MUTED, "4")
    footer = section.footer.paragraphs[0]
    add_page_field(footer)
    for run in footer.runs:
        run.font.name = "Times New Roman"; run.font.size = Pt(7.2); run.font.color.rgb = RGBColor.from_string(MUTED)

    props = doc.core_properties
    props.title = "Leakage-Controlled Walk-Forward Forecasting and Timing of SPY"
    props.subject = "DSA5205 Project 2"
    props.author = "; ".join(a["name"] for a in authors)

    def paragraph(text="", *, align=None, italic=False, bold=False, size=None, color=None):
        p = doc.add_paragraph()
        if align is not None: p.alignment = align
        r = p.add_run(text); r.italic = italic; r.bold = bold
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = RGBColor.from_string(color)
        return p

    def heading(text: str, level=1):
        return doc.add_heading(text, level=level)

    def bullet(text: str):
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(.45); p.paragraph_format.first_line_indent = Cm(-.2)
        p.add_run(text)
        return p

    def note(label: str, text: str):
        table = doc.add_table(rows=1, cols=1); table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0); set_cell_shading(cell, LIGHT); set_cell_margins(cell, 85, 100, 85, 100)
        p = cell.paragraphs[0]
        r = p.add_run(label + " "); r.bold = True; r.font.size = Pt(8.5)
        p.add_run(text)
        for run in p.runs: run.font.name = "Times New Roman"
        p.paragraph_format.space_after = Pt(0)
        return table

    def table(caption: str, headers, rows, widths=None, font=7.7):
        p = doc.add_paragraph(caption, style="Caption"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        t = doc.add_table(rows=1, cols=len(headers)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = "Table Grid"; t.autofit = False
        for j, h in enumerate(headers):
            c = t.rows[0].cells[j]; c.text = str(h); set_cell_shading(c, LIGHT); set_cell_margins(c); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if widths: c.width = Cm(widths[j])
            for run in c.paragraphs[0].runs: run.font.name = "Times New Roman"; run.font.size = Pt(font); run.bold = True
        repeat_header(t.rows[0])
        for row in rows:
            cells = t.add_row().cells
            for j, value in enumerate(row):
                cells[j].text = str(value); set_cell_margins(cells[j]); cells[j].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                if widths: cells[j].width = Cm(widths[j])
                for p2 in cells[j].paragraphs:
                    for run in p2.runs: run.font.name = "Times New Roman"; run.font.size = Pt(font)
        doc.add_paragraph().paragraph_format.space_after = Pt(0)
        return t

    def figure(path: Path, caption: str, width=6.25):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(1)
        p.add_run().add_picture(str(path), width=Inches(width))
        c = doc.add_paragraph(caption, style="Caption"); c.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def page_break():
        doc.add_page_break()

    # Cover
    p = paragraph("Leakage-Controlled Walk-Forward Forecasting and Timing of SPY", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=10.5, color=BLUE)
    add_bottom_rule(p, BLUE, "6")
    p = paragraph(align=WD_ALIGN_PARAGRAPH.CENTER); p.paragraph_format.space_before = Pt(10)
    p.add_run().add_picture(str(ROOT / "assets/nus_logo_full-vertical.jpg"), width=Inches(1.45))
    paragraph("Daily cross-asset forecasting, chronological model selection and cost-aware backtesting", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=9, color=MUTED)
    paragraph("Data Science in Quantitative Finance DSA5205", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=10)
    p = paragraph(); p.paragraph_format.space_before = Pt(8)
    table("", ["AUTHOR", "STUDENT ID"], [[a["name"].upper(), a["student_id"]] for a in authors], [8.5, 8.5], 8.2)
    paragraph("Dataset: Yahoo Finance daily adjusted OHLCV · SPY, QQQ, IWM, TLT and GLD · 2005–2025", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=8, color=MUTED)
    p = paragraph(align=WD_ALIGN_PARAGRAPH.CENTER); add_hyperlink(p, GITHUB, GITHUB)
    paragraph("Project2 Teams 16 · October 2026", align=WD_ALIGN_PARAGRAPH.CENTER, size=8.5)

    # Contents
    page_break(); heading("Contents", 1)
    toc = [
        ("Foreword", 3), ("1. Abstract", 3), ("2. Introduction and objectives", 3),
        ("3. Data and preparation", 4), ("4. Research design and leakage control", 5),
        ("5. Exploratory and statistical analysis", 6), ("6. Features and models", 8),
        ("7. Walk-forward experiments", 10), ("8. Final holdout results", 12),
        ("9. Interpretation, limitations and conclusion", 15), ("10. AI usage declaration", 16),
        ("References", 16), ("Appendix A. Reproduction and provenance", 17),
        ("Appendix B. Feature and model atlas", 18),
    ]
    for title, page_no in toc:
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(2)
        tab = p.paragraph_format.tab_stops.add_tab_stop(Cm(16.7))
        p.add_run(title); p.add_run("\t" + str(page_no))
    p = paragraph(); p.paragraph_format.space_before = Pt(18); add_bottom_rule(p, BLUE, "5")
    paragraph("Source code and reproducibility materials", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=8, color=BLUE)
    p = paragraph(align=WD_ALIGN_PARAGRAPH.CENTER); add_hyperlink(p, GITHUB, GITHUB)
    paragraph("Raw vendor data are downloaded locally; processed research objects and report artifacts are versioned with Git LFS.", align=WD_ALIGN_PARAGRAPH.CENTER, size=7.8)

    # Main text, continuous flow
    page_break(); heading("Foreword", 1)
    paragraph("This report documents a reproducible investigation of short-horizon SPY forecasting. The emphasis is placed on timing integrity, transparent model selection, cost-aware evaluation and restrained interpretation. Numerical claims are drawn from immutable pipeline outputs and are separated from economic interpretation. The final holdout is treated as an evaluation period rather than a source of model redesign.")

    heading("1. Abstract", 1)
    paragraph(f"Daily adjusted OHLCV observations for SPY, QQQ, IWM, TLT and GLD from 2005–2025 are used to test whether information available after session t can forecast the SPY adjusted-close return from t+1 to t+2. A 99-feature specification combines lagged returns, momentum, trend, volatility, technical, liquidity, calendar and cross-asset state variables. Ten model families are compared through expanding monthly walk-forward refits across screening and confirmation periods before one random-forest configuration is frozen for 2022–2025. The final strategy earns {rf_f.annualized_net_return:.2%} annualized after 5 bp one-way costs, with a {rf_f.net_sharpe:.2f} Sharpe and {rf_f.max_drawdown:.1%} maximum drawdown. SPY earns {rf_f.annualized_benchmark_return:.2%} with a {rf_f.benchmark_sharpe:.2f} Sharpe. OOS R² is {rf_f.oos_r2_vs_historical_mean:.3f}. The evidence supports a reproducible defensive timing experiment but does not support superior forecast accuracy or benchmark outperformance.")

    heading("2. Introduction and objectives", 1)
    paragraph("Short-horizon equity returns contain weak signals relative to noise, while model flexibility creates a material risk of data-snooping and temporal leakage [1, 5–7]. The project therefore evaluates economic performance only after a fixed chain of causal feature construction, chronological selection and frozen final testing.")
    heading("2.1 Objectives", 2)
    bullet("Construct an auditable daily multi-asset dataset and retain genuine extremes for diagnosis.")
    bullet("Compare interpretable baselines, regularized linear models, dimension-reduced models and nonlinear ensembles under identical time splits.")
    bullet("Translate forecasts into an unlevered SPY long-or-cash rule and deduct turnover-based transaction costs.")
    bullet("Report forecast loss, return, risk, exposure, turnover, uncertainty and model complexity without using the final period for tuning.")
    note("Scope note.", "SPY is the only traded asset. QQQ, IWM, TLT and GLD are predictors. Cash earns zero in the reported backtest.")

    heading("3. Data and preparation", 1)
    paragraph("Yahoo Finance is the primary source accessed through yfinance [11]. The immutable snapshot covers 3 January 2005 through 31 December 2025. Stooq is implemented as an optional independent comparison source and is never merged silently. Adjusted close defines returns; raw OHLCV supports range, gap and volume features.")
    table("Table 1. Dataset scope and analytical roles.", ["Asset", "Role", "Economic proxy", "Sessions"], [["SPY", "Traded / target", "US large-cap equity", "5,283"], ["QQQ", "Predictor", "Growth and technology", "5,283"], ["IWM", "Predictor", "Small-cap breadth", "5,283"], ["TLT", "Predictor", "Long-duration Treasury", "5,283"], ["GLD", "Predictor", "Gold and defensive state", "5,283"]], [2.0, 3.0, 8.2, 2.2])
    heading("3.1 Cleaning and quality control", 2)
    bullet("Coerce numeric fields and block invalid OHLC structures, nonpositive prices, negative volume, weekends and missing adjusted closes.")
    bullet("Remove only value-identical duplicate sessions; conflicting duplicates stop processing.")
    bullet("Retain extreme returns and zero-volume observations for analysis; do not winsorize the target.")
    bullet("Align predictors to the observed SPY session calendar without forward or backward filling.")
    note("Data-quality result.", "All five assets contain 5,283 aligned observations with no missing adjusted close on the SPY calendar. The raw audit reports no blocking issue.")
    figure(EDA_M / "plots/01_normalized_prices.png", "Figure 1. Normalized adjusted prices during the initial development period; the plot is descriptive and excludes confirmation and final-test data.", 6.15)

    heading("4. Research design and leakage control", 1)
    heading("4.1 Target, execution and label availability", 2)
    paragraph("Features are observed after the close of t. A position based on that signal becomes executable at the close of t+1. The response is the adjusted-close return from t+1 to t+2 and enters training only after t+2.")
    figure(eq_target, "Equation 1. Two-session-ahead target and label-availability convention.", 5.2)
    figure(eq_net, "Equation 2. Forecast hurdle, long-or-cash position and net return accounting.", 5.8)
    paragraph("The hurdle h equals 0.001 and the base cost c equals 0.0005 per one-way position change. Scaling, imputation, PCA and nonlinear feature maps are fitted within each eligible training sample. Every refit applies the condition label_available_session ≤ refit_origin.")
    heading("4.2 Chronological partitions", 2)
    table("Table 2. Predeclared chronological research stages.", ["Stage", "Dates", "Use", "Configurations × refits"], [["Initial train", "2005–2014", "EDA and diagnostics", "—"], ["Screening", "2015–2018", "Family and parameter comparison", "57 × 48"], ["Confirmation", "2019–2021", "Retest selected families", "4 × 36"], ["Final holdout", "2022–2025", "Frozen evaluation", "3 × 48"]], [2.7, 2.7, 7.3, 3.0])
    note("Leakage-control contract.", "No random split, globally fitted preprocessing, same-close execution, final-period tuning or survivorship-driven symbol selection is permitted. Timing audits and per-refit cutoffs are recorded as artifacts.")

    heading("5. Exploratory and statistical analysis", 1)
    heading("5.1 Correlation structure", 2)
    paragraph("The original 99 × 99 heatmap is unsuitable for a printed report. Figure 2 replaces it with the twelve strongest positive and twelve strongest negative feature pairs, preserving exact labels and values. Strong positive dependence occurs within trend and volatility families. The negative panel shows economically distinct offsets and confirms that correlation structure is not uniformly redundant.")
    figure(corr_fig, "Figure 2. Most positive and most negative feature-pair correlations in the initial training period. Self-correlations and duplicate pairs are excluded.", 6.45)
    paragraph("These views motivate shrinkage, PCA and shallow ensembles. Pairwise correlation remains descriptive; a large coefficient does not establish incremental forecast value.")

    heading("5.2 Financial time-series diagnostics", 2)
    table("Table 3. Initial-training statistical diagnostics.", ["Test", "Reported result", "Interpretation"], [["Mean return, HAC", "p = 0.227", "Zero mean not rejected"], ["Jarque–Bera", "p < 0.001; excess kurtosis 13.44", "Strong non-normality"], ["ADF, log price", "p = 0.954", "Unit root not rejected"], ["ADF, log return", "p < 0.001", "Return stationarity supported"], ["Ljung–Box, returns", "p < 0.001 through lag 20", "Serial dependence"], ["ARCH LM(10)", "p < 0.001", "Volatility clustering"], ["Variance ratio, q=5", "0.792; p < 0.001", "Short-horizon reversal"], ["Variance ratio, q=20", "0.691; p = 0.003", "Departure from random walk"]], [4.1, 5.2, 6.4])
    paragraph("HAC uncertainty is preferred to an IID mean test because daily returns are heteroskedastic [9]. The variance-ratio z-statistic uses a homoskedastic approximation and is treated as descriptive. These tests motivate candidate features but do not authorize strategy claims or final-holdout redesign.")

    heading("6. Features and models", 1)
    heading("6.1 Feature specification", 2)
    paragraph(f"The F2 specification contains {features['feature_counts']['F2']} predictors in eleven causal groups. Mature observations require complete values for every selected feature, which keeps the training population consistent across models.")
    table("Table 4. Feature families and representative transformations.", ["Family", "Representative variables", "Count"], [["Lagged returns", "SPY log-return offsets 0, 1, 2, 3, 4, 9, 14, 19", 8], ["Momentum", "2–252 session cumulative returns", 10], ["Trend", "price/SMA, EMA spread, slope, 50/200 ratio", 10], ["Volatility", "rolling, downside, EWMA, skew, kurtosis", 14], ["Technical", "RSI, Bollinger z, stochastic, MACD", 6], ["Intraday / volume", "gap, range, volume ratios, z-scores, Amihud", 10], ["Interactions", "return×volume, momentum×volatility", 3], ["Calendar", "cyclical weekday/month and month-end", 5], ["Cross-asset", "QQQ/IWM/TLT/GLD momentum, volatility, correlations", 31], ["Drawdown", "60- and 252-session drawdown", 2]], [3.0, 10.5, 2.0])
    heading("6.2 Model families", 2)
    table("Table 5. Candidate model families and complexity controls.", ["Family", "Purpose", "Primary control"], [["Historical mean", "Forecast baseline", "One parameter"], ["Autoregression", "Low-dimensional dynamic baseline", "Four lags"], ["Ridge / lasso / elastic net", "Regularized linear prediction", "Penalty grid"], ["PCA ridge", "Collinearity and dimension control", "5–40 components"], ["Random forest / extra trees", "Nonlinear states and interactions", "Depth 3/6; leaves 50/150"], ["Histogram gradient boosting", "Sequential nonlinear partitions", "3/7 leaves; L2 penalty"], ["RFF ridge", "High-dimensional nonlinear approximation", "64–1,024 components plus ridge"]], [4.1, 7.2, 4.2])
    paragraph("The small predeclared grid limits researcher degrees of freedom. Seed 17, two process workers and one numerical thread per worker provide reproducible execution on Apple Silicon and Intel/AMD systems.")

    heading("7. Walk-forward experiments", 1)
    heading("7.1 Screening", 2)
    paragraph("Each configuration is refitted at month starts on an expanding eligible sample. The primary selection metric is median annual net Sharpe, with at least 98% prediction coverage. Within a 0.05 Sharpe tolerance, lower turnover, fewer trainable parameters and configuration ID provide deterministic tie-breaks.")
    figure(screen_fig, "Figure 3. Fifteen leading screening configurations. Model names and defining parameters are printed directly on the y-axis.", 6.35)
    table("Table 6. Families advanced from screening.", ["Family", "Configuration", "Net return", "Sharpe", "Median annual Sharpe"], [["Random forest", "depth 3; leaf 50; 300 trees", f"{rf_s.annualized_net_return:.2%}", f"{rf_s.net_sharpe:.2f}", f"{rf_s.median_annual_net_sharpe:.2f}"], ["Elastic net", "α=.001; L1 ratio=.8", "1.39%", "0.40", "0.89"]], [2.6, 5.4, 2.5, 2.0, 3.0])

    heading("7.2 Complexity and generalization", 2)
    paragraph("Figure 4 uses every screening configuration rather than the three final baselines. The left panel asks whether additional effective parameters improve genuinely out-of-sample fit. The right panel contrasts training and walk-forward errors against an equality line. Points below zero OOS R² fail to improve on the historical-mean forecast.")
    figure(complexity_fig, "Figure 4. Complexity and generalization across the complete screening grid. The dashed P/T = 1 boundary marks more trainable parameters than observations.", 6.45)
    paragraph("Higher capacity does not produce monotonic OOS improvement. RFF models explicitly probe high P/T regimes while ridge stabilization controls numerical variance. Tree depth and leaf-size constraints remain more informative than nominal tree parameter counts.")

    heading("7.3 Confirmation and model freeze", 2)
    figure(stage_fig, "Figure 5. Random-forest stability across screening, confirmation and the final holdout. Stage results remain separate and are not pooled.", 6.3)
    paragraph(f"Confirmation reduces the selected forest’s annualized net return from {rf_s.annualized_net_return:.2%} to {rf_c.annualized_net_return:.2%}; Sharpe falls from {rf_s.net_sharpe:.2f} to {rf_c.net_sharpe:.2f}. The deterioration is substantive evidence of instability. The configuration nevertheless advances under the predeclared family rule and is serialized as freeze_f98a78b584d0ca42 before final execution.")

    heading("8. Final holdout results", 1)
    heading("8.1 Forecast and portfolio metrics", 2)
    table("Table 7. Frozen final-test results, 2022–2025.", ["Metric", "Random forest", "AR baseline", "SPY"], [["Observations", "1,001", "1,001", "1,001"], ["Directional accuracy", f"{rf_f.directional_accuracy:.2%}", f"{ar_f.directional_accuracy:.2%}", "—"], ["OOS R² vs historical mean", f"{rf_f.oos_r2_vs_historical_mean:.4f}", f"{ar_f.oos_r2_vs_historical_mean:.4f}", "—"], ["Annualized net return", f"{rf_f.annualized_net_return:.2%}", f"{ar_f.annualized_net_return:.2%}", f"{rf_f.annualized_benchmark_return:.2%}"], ["Net Sharpe", f"{rf_f.net_sharpe:.3f}", f"{ar_f.net_sharpe:.3f}", f"{rf_f.benchmark_sharpe:.3f}"], ["Net CAGR", f"{rf_f.net_cagr:.2%}", f"{ar_f.net_cagr:.2%}", "—"], ["Maximum drawdown", f"{rf_f.max_drawdown:.1%}", f"{ar_f.max_drawdown:.1%}", "—"], ["Average exposure", f"{rf_f.average_exposure:.1%}", f"{ar_f.average_exposure:.1%}", "100%"], ["Annualized turnover", f"{rf_f.annualized_turnover:.2f}", f"{ar_f.annualized_turnover:.2f}", "0"]], [5.2, 3.7, 3.3, 2.7])
    paragraph("The frozen forest is profitable after base costs and has a shallower drawdown than SPY. It does not beat SPY on return or Sharpe. Negative OOS R² shows that the economic gating rule does not correspond to superior squared-error forecasts.")
    figure(FINAL / "plots/02_cumulative_wealth.png", "Figure 6. Final-holdout cumulative wealth. Strategy returns are net of 5 bp one-way costs; initial wealth equals one.", 6.35)
    figure(FINAL / "plots/03_drawdown.png", "Figure 7. Final-holdout drawdown paths for the frozen strategy and SPY.", 6.15)

    heading("8.2 Calendar returns and exposure", 2)
    table("Table 8. Annual return decomposition.", ["Year", "Frozen strategy", "SPY"], [[str(int(r.year)), f"{r.strategy:.2%}", f"{r.benchmark:.2%}"] for r in annual.itertuples(index=False)], [4.7, 5.2, 5.2])
    paragraph("The main defensive contribution occurs in 2022, when the strategy earns 17.50% while SPY loses 18.34%. Low average exposure then misses most of the 2023–2025 advance and produces a loss in 2025. The result is regime-dependent rather than a stable return premium.")
    figure(FINAL / "plots/05_rolling_sharpe_exposure.png", "Figure 8. Rolling strategy behavior and realized exposure in the final holdout.", 6.25)

    heading("8.3 Feature interpretation", 2)
    top = stability.head(12)
    table("Table 9. Leading feature importances across final refits.", ["Feature", "Mean importance", "Median"], [[short_name(r.feature), f"{r.mean_absolute:.4f}", f"{r.median:.4f}"] for r in top.itertuples(index=False)], [9.2, 3.4, 3.4])
    paragraph("Volatility-state measures dominate the selected forest, followed by short gold momentum, medium-horizon small-cap momentum and a 14-session SPY return lag. This pattern is consistent with an exposure gate responding to risk state and market breadth. Impurity importance can favor continuous variables and cannot establish causality.")

    heading("8.4 Costs and uncertainty", 2)
    figure(FINAL / "plots/08_cost_sensitivity.png", "Figure 9. Transaction-cost sensitivity with predictions and positions held fixed.", 5.75)
    table("Table 10. Final-holdout transaction-cost scenarios.", ["One-way cost", "Annualized net return", "Sharpe"], [[f"{int(r.one_way_cost_bps)} bp", f"{r.annualized_return:.2%}", f"{r.sharpe:.3f}"] for r in costs.itertuples(index=False)], [4.5, 5.6, 4.2])
    boot = eval_report["block_bootstrap_strategy_minus_spy"]
    paragraph(f"The annualized strategy-minus-SPY mean return is {boot['annualized_mean_return_difference']:.2%}. A {boot['confidence_level']:.0%} moving-block interval using {boot['block_length']} sessions and {boot['repetitions']:,} repetitions is [{boot['confidence_lower']:.2%}, {boot['confidence_upper']:.2%}]. The interval includes zero and remains conditional on the selected strategy [10].")

    heading("9. Interpretation, limitations and conclusion", 1)
    heading("9.1 Limitations", 2)
    bullet("The fixed five-ETF universe and daily frequency restrict external validity.")
    bullet("Adjusted Yahoo data are not exchange-level execution records; bid–ask spread, market impact and taxes are omitted.")
    bullet("Close execution is idealized, the cash leg earns zero and a fixed cost cannot represent every liquidity regime.")
    bullet("Selection across configurations leaves multiple-testing risk. Conditional bootstrap intervals do not remove model-selection bias [5–6].")
    heading("9.2 Conclusion", 2)
    paragraph("The project establishes a defensible leakage-controlled research process. The final random forest is positive after the base transaction cost and reduces drawdown through selective exposure, but it underperforms SPY and fails to improve squared prediction error over the historical-mean baseline. The evidence supports process validity and a regime-sensitive defensive behavior; it does not support a persistent tradable alpha claim.")
    note("Verification status.", f"PASS — {verify['checks_passed']} automated checks cover dataset lineage, hashes, completion, prediction uniqueness, label timing, ledger coverage, cost reconciliation and freeze linkage.")

    heading("10. AI usage declaration", 1)
    paragraph("OpenAI Codex (GPT-6) was used to inspect recorded output manifests, assist with report organization, draft and edit prose, create report-specific visualizations, and generate document-formatting code. Numerical claims were checked against immutable project artifacts. Responsibility for the content, interpretation and quality of the submitted work remains with the listed author or authors. This declaration follows the NUS guidance on academic integrity and transparent use of AI [14–17].")

    heading("References", 1)
    refs = [
        "[1] E. F. Fama, ‘Efficient capital markets: A review of theory and empirical work,’ Journal of Finance, vol. 25, no. 2, pp. 383–417, 1970.",
        "[2] A. W. Lo and A. C. MacKinlay, ‘Stock market prices do not follow random walks,’ Review of Financial Studies, vol. 1, no. 1, pp. 41–66, 1988.",
        "[3] T. J. Moskowitz, Y. H. Ooi, and L. H. Pedersen, ‘Time series momentum,’ Journal of Financial Economics, vol. 104, no. 2, pp. 228–250, 2012.",
        "[4] A. Moreira and T. Muir, ‘Volatility-managed portfolios,’ Journal of Finance, vol. 72, no. 4, pp. 1611–1644, 2017.",
        "[5] H. White, ‘A reality check for data snooping,’ Econometrica, vol. 68, no. 5, pp. 1097–1126, 2000.",
        "[6] D. H. Bailey, J. M. Borwein, M. López de Prado, and Q. J. Zhu, ‘The probability of backtest overfitting,’ Journal of Computational Finance, vol. 20, no. 4, pp. 39–69, 2017.",
        "[7] S. Gu, B. Kelly, and D. Xiu, ‘Empirical asset pricing via machine learning,’ Review of Financial Studies, vol. 33, no. 5, pp. 2223–2273, 2020.",
        "[8] L. Breiman, ‘Random forests,’ Machine Learning, vol. 45, pp. 5–32, 2001.",
        "[9] W. K. Newey and K. D. West, ‘A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix,’ Econometrica, vol. 55, no. 3, pp. 703–708, 1987.",
        "[10] D. N. Politis and J. P. Romano, ‘The stationary bootstrap,’ Journal of the American Statistical Association, vol. 89, no. 428, pp. 1303–1313, 1994.",
        "[11] Yahoo Finance, historical market data for SPY, QQQ, IWM, TLT and GLD, accessed 19 Oct. 2026 through yfinance. https://finance.yahoo.com/.",
        "[12] scikit-learn developers, scikit-learn v1.7.2. https://scikit-learn.org/.",
        "[13] pandas development team, pandas v2.3.3. https://pandas.pydata.org/.",
        "[14] National University of Singapore, NUS Plagiarism Policy. https://myportal.nus.edu.sg/studentportal/student-discipline/all/docs/NUS-Plagiarism-Policy.pdf.",
        "[15] National University of Singapore, Code of Student Conduct, Section A: Academic Integrity. https://studentconduct.nus.edu.sg/wp-content/uploads/NUS-Code-of-Student-Conduct.pdf.",
        "[16] NUS Libraries, Academic Integrity Essentials. https://libguides.nus.edu.sg/new2nus/acadintegrity.",
        "[17] NUS Centre for Teaching, Learning and Technology, Policy for Use of AI in Teaching and Learning, Sections 3–4. http://ctlt.nus.edu.sg/policy-for-use-of-ai-in-teaching-and-learning.pdf.",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref); p.paragraph_format.left_indent = Cm(.45); p.paragraph_format.first_line_indent = Cm(-.45); p.paragraph_format.space_after = Pt(2)
        for r in p.runs: r.font.size = Pt(7.8)

    page_break(); heading("Appendix A. Reproduction and provenance", 1)
    heading("A.1 Canonical identifiers", 2)
    table("Table A1. Immutable report inputs.", ["Object", "Identifier"], [["Feature dataset", "features_yahoo_20261019T010846Z_799f619a4f"], ["Screening", "models_screening_8d1f4f8a10e794eb"], ["Confirmation", "models_confirmation_5d6ed2ce5fa7b6cb"], ["Freeze", "freeze_f98a78b584d0ca42"], ["Final test", "models_final_test_53e047b58e92e27b"]], [4.0, 12.0])
    heading("A.2 Commands", 2)
    commands = ["python scripts/verify_outputs.py", "python reports/build_report.py", "git lfs install", "python scripts/setup_git_lfs.py --install", "git add .gitattributes .gitignore data/processed artifacts reports assets", "git lfs ls-files"]
    for command in commands:
        p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(.45); p.paragraph_format.space_after = Pt(2)
        r = p.add_run(command); r.font.name = "Consolas"; r.font.size = Pt(7.8); r.font.color.rgb = RGBColor.from_string(BLUE)
    heading("A.3 Repository", 2)
    p = paragraph("Complete source code, configurations, manifests and report builder: ")
    add_hyperlink(p, GITHUB, GITHUB)
    paragraph("Raw vendor downloads remain local because redistribution conditions can differ. Processed Parquet, CSV outputs, plots, reports and intermediate artifacts are eligible for Git LFS.")

    heading("Appendix B. Feature and model atlas", 1)
    heading("B.1 Feature timing examples", 2)
    table("Table B1. Representative information sets.", ["Variable", "Construction", "Latest information"], [["SPY return lag 0", "log(Pt/Pt−1)", "close t"], ["SPY momentum 20", "Pt/Pt−20 − 1", "close t"], ["SPY volatility 20", "SD of prior 20 log returns", "close t"], ["QQQ momentum 60", "QQQt/QQQt−60 − 1", "close t"], ["Target", "SPY adjusted return t+1 to t+2", "close t+2"]], [4.0, 7.7, 4.2])
    heading("B.2 Frozen random forest", 2)
    table("Table B2. Final model and compute settings.", ["Setting", "Value"], [["Trees", "300"], ["Maximum depth", "3"], ["Minimum leaf size", "50"], ["Maximum features", "0.5"], ["Refit frequency", "Month start"], ["Training window", "Expanding"], ["Forecast hurdle", "0.001"], ["One-way cost", "5 bp"], ["Random seed", "17"], ["Workers / numerical threads", "2 / 1 each"]], [7.0, 8.7])
    heading("B.3 Contribution statement", 2)
    for author in authors:
        paragraph(f"{author['name']} ({author['student_id']}): research design, data engineering, leakage controls, feature engineering, model implementation, walk-forward evaluation, interpretation and report preparation.")

    output = REPORTS / "Project2_Team16_Report.docx"
    doc.save(output)
    print(output)
    return output


if __name__ == "__main__":
    build()
