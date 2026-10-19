"""Build the DSA5205 Project 2 academic report from immutable run outputs."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)
SCREEN = ROOT / "artifacts/runs/models_screening_8d1f4f8a10e794eb"
CONFIRM = ROOT / "artifacts/runs/models_confirmation_5d6ed2ce5fa7b6cb"
FINAL = ROOT / "artifacts/runs/models_final_test_53e047b58e92e27b"
MARKET_EDA = ROOT / "artifacts/eda/market_market_yahoo_20261019T010846Z_2014-12-31_d2cc08ac48"
FEATURE_EDA = ROOT / "artifacts/eda/features_features_yahoo_20261019T010846Z_799f619a4f_F2_initial_train"
STATS = ROOT / "artifacts/statistics/features_yahoo_20261019T010846Z_799f619a4f_F2_initial_train/statistical_tests.json"
FEATURE_MANIFEST = ROOT / "data/processed/features_yahoo_20261019T010846Z_799f619a4f/manifest.json"
VERIFY = OUT / "output_verification.json"

NAVY = "14223C"
BLUE = "1F4E79"
ORANGE = "EF7C00"
PALE = "EAF0F6"
MID = "60758A"
WHITE = "FFFFFF"
GRAY = "F2F3F5"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def shade(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def margins(section, top=1.45, bottom=1.35, left=1.75, right=1.55):
    section.top_margin = Cm(top)
    section.bottom_margin = Cm(bottom)
    section.left_margin = Cm(left)
    section.right_margin = Cm(right)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("PROJECT 2 TEAMS 16   ·   ")
    run.font.name = "Times New Roman"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string(MID)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    paragraph._p.append(fld)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_cell_margins(cell, top=90, start=90, bottom=90, end=90):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def make_equation(name: str, tex: str):
    path = FIG / f"equation_{name}.png"
    fig = plt.figure(figsize=(9, 0.62), dpi=220)
    fig.patch.set_alpha(0)
    fig.text(0.5, 0.51, tex, ha="center", va="center", fontsize=18, color="#14223C")
    plt.axis("off")
    fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return path


def make_summary_figure(screen: pd.DataFrame, confirm: pd.DataFrame, final: pd.DataFrame):
    def rf(frame):
        return frame.loc[frame.family.eq("random_forest")].iloc[0]
    rows = [rf(screen), rf(confirm), rf(final)]
    labels = ["Screening\n2015–2018", "Confirmation\n2019–2021", "Final holdout\n2022–2025"]
    returns = [r.annualized_net_return * 100 for r in rows]
    sharpes = [r.net_sharpe for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.4), dpi=190)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#DDE3E9", linewidth=.7)
        ax.set_axisbelow(True)
    axes[0].bar(labels, returns, color=["#1F4E79", "#7997B5", "#EF7C00"])
    axes[0].axhline(0, color="#14223C", lw=.8)
    axes[0].set_ylabel("Annualized net return (%)")
    axes[1].bar(labels, sharpes, color=["#1F4E79", "#7997B5", "#EF7C00"])
    axes[1].axhline(0, color="#14223C", lw=.8)
    axes[1].set_ylabel("Net Sharpe ratio")
    fig.tight_layout()
    path = FIG / "stage_stability.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def make_feature_figure(stability: pd.DataFrame):
    d = stability.head(12).sort_values("mean_absolute")
    labels = [x.replace("spy_", "SPY ").replace("iwm_", "IWM ").replace("gld_", "GLD ").replace("_", " ") for x in d.feature]
    fig, ax = plt.subplots(figsize=(8.8, 5.1), dpi=190)
    ax.barh(labels, d.mean_absolute, color="#1F4E79")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color="#DDE3E9", linewidth=.7)
    ax.set_axisbelow(True)
    ax.set_xlabel("Mean impurity importance across refits")
    fig.tight_layout()
    path = FIG / "feature_importance.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    rid = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color"); color.set(qn("w:val"), BLUE); rpr.append(color)
    underline = OxmlElement("w:u"); underline.set(qn("w:val"), "single"); rpr.append(underline)
    run.append(rpr)
    text_node = OxmlElement("w:t"); text_node.text = text; run.append(text_node)
    link.append(run); paragraph._p.append(link)


def build():
    screen = pd.read_csv(SCREEN / "config_metrics.csv")
    confirm = pd.read_csv(CONFIRM / "config_metrics.csv")
    final = pd.read_csv(FINAL / "config_metrics.csv")
    annual = pd.read_csv(FINAL / "annual_returns.csv")
    cost = pd.read_csv(FINAL / "cost_sensitivity.csv")
    stability = pd.read_csv(FINAL / "feature_stability.csv")
    stats = load(STATS)
    features = load(FEATURE_MANIFEST)
    verification = load(VERIFY)
    authors = load(ROOT / "assets/authors.json")
    report_eval = load(FINAL / "evaluation_report.json")
    rf_s = screen.loc[screen.family.eq("random_forest")].iloc[0]
    rf_c = confirm.loc[confirm.family.eq("random_forest")].iloc[0]
    rf_f = final.loc[final.family.eq("random_forest")].iloc[0]
    ar_f = final.loc[final.family.eq("autoregression")].iloc[0]

    eq_target = make_equation("target", r"$y_t = P^{adj}_{t+2}/P^{adj}_{t+1}-1$")
    eq_timing = make_equation("timing", r"$\mathrm{label\_available}(t)=t+2\leq s_j$")
    eq_strategy = make_equation("strategy", r"$\pi_{t+1}=\mathbf{1}\{\widehat{y}_t>h\},\quad r^{net}_{t+2}=\pi_{t+1}y_t-c|\pi_{t+1}-\pi_t|$")
    eq_ridge = make_equation("ridge", r"$\widehat{\beta}=\arg\min_{\beta}\sum_{i\in\mathcal{T}_j}(y_i-x_i^{\top}\beta)^2+\lambda\|\beta\|_2^2$")
    stage_fig = make_summary_figure(screen, confirm, final)
    feature_fig = make_feature_figure(stability)

    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    margins(sec)
    sec.different_first_page_header_footer = True
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"; normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor.from_string(NAVY)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08
    for name, size, color in (("Title", 25, NAVY), ("Heading 1", 19, NAVY), ("Heading 2", 13, BLUE), ("Heading 3", 11, ORANGE)):
        s = styles[name]; s.font.name = "Times New Roman"; s.font.size = Pt(size); s.font.bold = True
        s.font.color.rgb = RGBColor.from_string(color); s.paragraph_format.space_before = Pt(4); s.paragraph_format.space_after = Pt(7)
    for name in ("Caption",):
        s = styles[name]; s.font.name = "Times New Roman"; s.font.size = Pt(8); s.font.italic = True
        s.font.color.rgb = RGBColor.from_string(MID)
    if "Source Note" not in styles:
        s = styles.add_style("Source Note", WD_STYLE_TYPE.PARAGRAPH)
        s.font.name = "Times New Roman"; s.font.size = Pt(7.5); s.font.color.rgb = RGBColor.from_string(MID)
        s.paragraph_format.space_after = Pt(4)
    header = sec.header.paragraphs[0]
    header.text = "DSA5205  ·  DATA SCIENCE IN QUANTITATIVE FINANCE  ·  PROJECT 2"
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for r in header.runs:
        r.font.name="Times New Roman"; r.font.size=Pt(8); r.font.color.rgb=RGBColor.from_string(MID)
    ppr = header._p.get_or_add_pPr(); border = OxmlElement("w:pBdr"); bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single"); bot.set(qn("w:sz"), "10"); bot.set(qn("w:color"), ORANGE); border.append(bot); ppr.append(border)
    add_page_number(sec.footer.paragraphs[0])
    props = doc.core_properties
    props.title = "Leakage-Controlled Walk-Forward Forecasting and Timing of SPY"
    props.subject = "DSA5205 Project 2"
    props.author = "; ".join(a["name"] for a in authors)

    def page(title=None, eyebrow=None):
        if len(doc.paragraphs) > 0:
            doc.add_page_break()
        if eyebrow:
            p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(2)
            r=p.add_run(eyebrow.upper()); r.bold=True; r.font.size=Pt(8); r.font.color.rgb=RGBColor.from_string(ORANGE)
        if title:
            doc.add_heading(title, level=1)

    def body(text, bold_prefix=None):
        p=doc.add_paragraph()
        if bold_prefix and text.startswith(bold_prefix):
            r=p.add_run(bold_prefix); r.bold=True; p.add_run(text[len(bold_prefix):])
        else: p.add_run(text)
        return p

    def bullet(text):
        p=doc.add_paragraph(style="List Bullet"); p.add_run(text); return p

    def callout(title, text):
        t=doc.add_table(rows=1, cols=1); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
        c=t.cell(0,0); c.width=Inches(6.5); shade(c, PALE); set_cell_margins(c,140,160,140,160)
        p=c.paragraphs[0]; r=p.add_run(title.upper()+"\n"); r.bold=True; r.font.color.rgb=RGBColor.from_string(ORANGE); r.font.size=Pt(8)
        p.add_run(text)

    def table(headers, rows, widths=None, font=8.2):
        t=doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
        t.style="Table Grid"
        for j,h in enumerate(headers):
            c=t.rows[0].cells[j]; c.text=str(h); shade(c,NAVY); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for r in c.paragraphs[0].runs: r.bold=True; r.font.color.rgb=RGBColor.from_string(WHITE); r.font.size=Pt(font)
            if widths: c.width=Cm(widths[j])
            set_cell_margins(c)
        set_repeat_table_header(t.rows[0])
        for i,row in enumerate(rows):
            cells=t.add_row().cells
            for j,val in enumerate(row):
                cells[j].text=str(val); shade(cells[j], WHITE if i%2==0 else GRAY); set_cell_margins(cells[j])
                for p in cells[j].paragraphs:
                    for r in p.runs: r.font.name="Times New Roman"; r.font.size=Pt(font)
                if widths: cells[j].width=Cm(widths[j])
        return t

    def picture(path, width=6.25, caption=None, source=None):
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(2)
        p.add_run().add_picture(str(path), width=Inches(width))
        if caption:
            q=doc.add_paragraph(caption, style="Caption"); q.alignment=WD_ALIGN_PARAGRAPH.CENTER
        if source:
            q=doc.add_paragraph(source, style="Source Note"); q.alignment=WD_ALIGN_PARAGRAPH.CENTER

    # 1 Cover
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(12)
    p.add_run().add_picture(str(ROOT/"assets/nus_logo_full-vertical.jpg"), width=Inches(1.35))
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(28)
    r=p.add_run("DSA5205"); r.bold=True; r.font.size=Pt(12); r.font.color.rgb=RGBColor.from_string(ORANGE)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("DATA SCIENCE IN QUANTITATIVE FINANCE"); r.bold=True; r.font.size=Pt(13); r.font.color.rgb=RGBColor.from_string(NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(20)
    r=p.add_run("Leakage-Controlled Walk-Forward\nForecasting and Timing of SPY"); r.bold=True; r.font.name="Times New Roman"; r.font.size=Pt(25); r.font.color.rgb=RGBColor.from_string(NAVY)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(10)
    r=p.add_run("PROJECT 2  ·  FINAL REPORT"); r.bold=True; r.font.size=Pt(10); r.font.color.rgb=RGBColor.from_string(ORANGE)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(32)
    add_hyperlink(p,"Project2 Teams 16","https://canvas.nus.edu.sg/groups/233255")
    for a in authors:
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(f"{a['name']}  ·  {a['student_id']}\n{a['email']}")
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(22)
    p.add_run("National University of Singapore\n19 October 2026").font.size=Pt(10)

    # 2
    page("Abstract and decision summary", "Executive synthesis")
    body("This study asks whether information available after the close of session t can forecast the SPY adjusted-close return from t+1 to t+2 and support a long-or-cash strategy after realistic transaction costs. Daily adjusted OHLCV data for SPY, QQQ, IWM, TLT and GLD span 2005–2025. Ninety-nine lagged, trailing and cross-asset features feed ten predeclared model families under expanding monthly walk-forward refits.")
    callout("Primary result", f"The frozen random forest earned {rf_f.annualized_net_return:.2%} annualized after 5 bp one-way costs with a {rf_f.net_sharpe:.2f} Sharpe and {rf_f.max_drawdown:.1%} maximum drawdown in 2022–2025. Buy-and-hold SPY earned {rf_f.annualized_benchmark_return:.2%} with a {rf_f.benchmark_sharpe:.2f} Sharpe. OOS R² was {rf_f.oos_r2_vs_historical_mean:.3f}; the evidence does not support superior forecasting accuracy or benchmark outperformance.")
    doc.add_heading("What survives scrutiny",level=2)
    bullet("Every one of 41 automated lineage, completion, uniqueness, timing and accounting checks passed.")
    bullet("The strategy was positive after the base cost and reduced final-period drawdown relative to SPY, largely through 8.6% average exposure.")
    bullet("Performance was unstable across stages and became negative at 20 bp. The bootstrap interval for annualized active return includes zero.")
    doc.add_heading("Research posture",level=2)
    body("The result is best interpreted as a reproducible low-exposure timing experiment rather than evidence of a deployable alpha. All final-holdout statements use the configuration frozen after confirmation.")

    # 3
    page("Research question, scope and contribution", "1 · Introduction")
    doc.add_heading("Question",level=2)
    body("Can daily price, volume, calendar and cross-asset state variables predict a two-session-ahead SPY return strongly enough to form a profitable long-or-cash strategy after costs?")
    doc.add_heading("Economic hypothesis",level=2)
    body("Short-horizon return continuation or reversal, volatility-state persistence and cross-asset risk transmission may create weak conditional signals. TLT and GLD proxy defensive conditions; QQQ and IWM distinguish growth and breadth. Because such relations are small and time-varying, the analysis uses strong regularization, shallow trees and strictly chronological evaluation [1–4].")
    doc.add_heading("Contribution",level=2)
    bullet("A precise signal, entry and label-availability convention that can be audited at every refit.")
    bullet("A three-stage screening, confirmation and untouched final-test protocol with a frozen model specification.")
    bullet("A cost-aware portfolio translation and separate forecast, economic and risk evaluation.")
    bullet("Hash-addressed datasets, configurations, checkpoints and output verification for exact provenance.")
    callout("Scope", "SPY is the only traded asset. QQQ, IWM, TLT and GLD are predictors. The strategy is unlevered, long or cash, and evaluated at daily frequency.")

    # 4
    page("Data, market and provenance", "2 · Data")
    body("Yahoo Finance is the primary lawful-access source used through yfinance [11]. The immutable snapshot was downloaded on 19 October 2026 for 3 January 2005 through 31 December 2025. Stooq is implemented only as an optional independent comparison and is never silently merged. Raw vendor files remain excluded from Git because redistribution terms can differ; processed research objects and manifests can be stored through Git LFS.")
    table(["Asset","Role","Economic information","Valid sessions"],[["SPY","Traded / target","US large-cap equity market","5,283"],["QQQ","Predictor","Growth / technology risk","5,283"],["IWM","Predictor","Small-cap breadth","5,283"],["TLT","Predictor","Long-duration Treasury state","5,283"],["GLD","Predictor","Gold / defensive state","5,283"]],[2.1,2.1,7.4,2.4])
    doc.add_heading("Identifiers and hashes",level=2)
    table(["Object","Identifier"],[["Raw snapshot","yahoo_20261019T010846Z"],["Market panel","market_yahoo_20261019T010846Z"],["Feature dataset","features_yahoo_20261019T010846Z_799f619a4f"],["Feature manifest SHA-256",features["feature_protocol_sha256"][:24]+"…"]],[4.2,10.0])
    body("Adjusted close defines returns; raw OHLCV supports intraday, range and volume variables. The SPY observed-session calendar is the research calendar. No price is forward-filled.")

    # 5
    page("Cleaning, coverage and exploratory evidence", "2 · Data")
    picture(MARKET_EDA/"plots/01_normalized_prices.png",5.8,"Figure 1. Normalized prices in the initial development period.","Source: authors’ calculations from the immutable Yahoo snapshot; initial train only.")
    doc.add_heading("Conservative cleaning",level=2)
    bullet("Numeric coercion and structural OHLC tests; block nonpositive prices, negative volume, weekends and missing adjusted closes.")
    bullet("Remove only value-identical duplicate sessions; conflicting duplicates stop the pipeline.")
    bullet("Retain genuine extreme returns and zero-volume observations for diagnosis rather than winsorizing outcomes.")
    bullet("Align predictors to observed SPY sessions without forward or backward filling.")
    callout("Audit outcome", "All five assets had 5,283 aligned observations and no missing adjusted closes on the SPY calendar. The raw-data audit reported no blocking issue.")

    # 6
    page("Prediction target and causal timing", "3 · Research design")
    body("Features are computed after the close of t. The position is assumed executable at the close of t+1. The label is the following adjusted-close return and becomes available only after t+2.")
    picture(eq_target,5.3,"Equation 1. Two-session-ahead return target.")
    picture(eq_timing,4.7,"Equation 2. Eligibility rule at refit origin sⱼ.")
    picture(eq_strategy,6.0,"Equation 3. Forecast-to-position rule and net return accounting.")
    body("The hurdle h is 0.001 and c is 0.0005 per one-way position change. Scaling, imputation and dimensionality reduction are fitted inside each training sample. The feature table intentionally contains future labels, so every refit filters rows using Equation 2.")
    callout("Leakage controls", "No random split, no global preprocessing fit, no contemporaneous execution, no final-holdout tuning, and no survivorship-based symbol selection. The timing audit and per-refit label cutoffs are independently verified.")

    # 7
    page("Feature architecture", "4 · Feature engineering")
    body(f"The F2 specification contains {features['feature_counts']['F2']} predictors organized into eleven causal groups. All rolling features use current or prior observations available at signal time.")
    table(["Group","Examples","Count"],[["Returns","log-return lags 0, 1, 2, 3, 4, 9, 14, 19",8],["Momentum","2–252 session cumulative returns",10],["Trend","price/SMA, EMA spread, slopes, 50/200 ratio",10],["Volatility","rolling, downside, EWMA, higher moments",14],["Technical","RSI, Bollinger z, stochastic, MACD",6],["Liquidity / range","volume ratios, z-scores, Amihud, gaps",10],["Interactions","return×volume, momentum×volatility",3],["Calendar","cyclical weekday/month, month-end",5],["Cross-asset","QQQ/IWM/TLT/GLD states and correlations",31],["Drawdown","60- and 252-session drawdown",2]],[3.0,9.3,1.5],7.8)
    body("Long windows deliberately trade sample size for state information. Mature rows require every selected feature, preventing varying feature availability from changing the training population across model families.")

    # 8
    page("Exploration and dependence structure", "4 · Feature engineering")
    picture(FEATURE_EDA/"plots/02_feature_correlation_heatmap.png",5.55,"Figure 2. Correlation structure of F2 features.","Source: authors’ calculations; initial train only.")
    body("Momentum windows, volatility estimates and related trend transforms form correlated blocks. This motivates regularized linear models, PCA ridge, tree ensembles and explicit complexity reporting. Correlation is descriptive: redundant predictors may destabilize coefficients even when predictive loss changes little.")
    doc.add_heading("Exploration boundary",level=2)
    body("Market and feature EDA used the initial training period ending 31 December 2014. Event markers and holiday summaries were descriptive overlays. Neither confirmation nor final outcomes were used to invent features, thresholds or model families.")

    # 9
    page("Statistical diagnostics", "5 · Diagnostics")
    table(["Diagnostic","Result","Interpretation"],[["Mean return, HAC","p = 0.227","No rejection of zero mean"],["Jarque–Bera","p < 0.001; excess kurtosis 13.44","Strong non-normality"],["ADF: log price","p = 0.954","Unit root not rejected"],["ADF: log return","p < 0.001","Return stationarity supported"],["Ljung–Box returns","p < 0.001 through lag 20","Serial dependence present"],["ARCH LM(10)","p < 0.001","Volatility clustering present"],["Variance ratio q=5","0.792; p < 0.001","Short-horizon mean reversion signal"],["Variance ratio q=20","0.691; p = 0.003","Longer-horizon departure from RW"]],[3.6,3.4,7.0],7.7)
    body("These initial-training diagnostics support modeling conditional mean and variance structure but do not establish an exploitable or causal relation. The variance-ratio z-test uses a homoskedastic approximation; strategy comparison therefore uses block bootstrap uncertainty.")

    # 10
    page("Model families and preprocessing", "6 · Models")
    table(["Family","Purpose","Complexity control"],[["Historical mean","Forecast baseline","1 parameter"],["Autoregression","Low-dimensional time-series baseline","4 parameters"],["Ridge / lasso / elastic net","Regularized linear prediction","Penalty grid"],["PCA ridge","Collinearity and dimension control","5–40 components"],["Random forest / extra trees","Nonlinear interactions","Depth 3/6; leaf 50/150"],["Histogram gradient boosting","Smooth nonlinear partitions","3/7 leaves; L2 penalty"],["RFF ridge","Controlled high-dimensional nonlinear map","64–1,024 components"]],[4.0,6.0,4.3],7.8)
    picture(eq_ridge,5.6,"Equation 4. Ridge objective fitted only on eligible training rows.")
    body("All model families share identical splits, labels and cost rules. The small predeclared grid reduces researcher degrees of freedom. Random seed 17 and two workers with one numerical thread each balance repeatability with Apple Silicon and Intel/AMD portability.")

    # 11
    page("Walk-forward validation and model selection", "7 · Validation")
    table(["Stage","Dates","Role","Configs × refits"],[["Initial train","2005–2014","EDA and statistical diagnostics","—"],["Screening","2015–2018","Compare families and hyperparameters","57 × 48 = 2,736"],["Confirmation","2019–2021","Retest two distinct families plus baselines","4 × 36 = 144"],["Final holdout","2022–2025","Single frozen specification plus baselines","3 × 48 = 144"]],[3.0,3.0,6.5,2.8],7.8)
    body("At each month start, the training window expands and only labels available by the refit origin are admitted. Forecasts continue daily until the next refit. Selection maximizes median annual net Sharpe, requires at least 98% coverage and uses lower turnover, fewer parameters and configuration ID as deterministic tie-breakers within a 0.05 Sharpe tolerance.")
    callout("Freeze rule", "The final random-forest configuration was serialized in freeze_f98a78b584d0ca42 before final-test execution. Final evaluation loaded that immutable object and did not reopen the screening grid.")

    # 12
    page("Screening results", "8 · Empirical results")
    picture(SCREEN/"plots/01_leaderboard.png",6.15,"Figure 3. Screening leaderboard across predeclared configurations.","Metric: median annual net Sharpe, 2015–2018; 5 bp one-way cost.")
    table(["Selected family","Configuration","Net return","Sharpe","Median annual Sharpe"],[["Random forest","depth 3; leaf 50; 300 trees",f"{rf_s.annualized_net_return:.2%}",f"{rf_s.net_sharpe:.2f}",f"{rf_s.median_annual_net_sharpe:.2f}"],["Elastic net","α=.001; L1 ratio=.8","1.39%","0.40","0.89"]],[3.0,5.2,2.0,1.7,2.7],7.7)
    body("The random forest and elastic net advanced as distinct families. Screening SPY returned 7.72% annually with a 0.57 Sharpe. Positive screening results are selection inputs, not unbiased performance estimates.")

    # 13
    page("Confirmation and stability", "8 · Empirical results")
    picture(stage_fig,6.15,"Figure 4. Selected random-forest performance across chronological stages.","Source: authors’ calculations. Stage metrics are not pooled.")
    table(["Stage","Net return","Net Sharpe","Max drawdown","OOS R²"],[["Screening",f"{rf_s.annualized_net_return:.2%}",f"{rf_s.net_sharpe:.2f}",f"{rf_s.max_drawdown:.1%}",f"{rf_s.oos_r2_vs_historical_mean:.3f}"],["Confirmation",f"{rf_c.annualized_net_return:.2%}",f"{rf_c.net_sharpe:.2f}",f"{rf_c.max_drawdown:.1%}",f"{rf_c.oos_r2_vs_historical_mean:.3f}"],["Final",f"{rf_f.annualized_net_return:.2%}",f"{rf_f.net_sharpe:.2f}",f"{rf_f.max_drawdown:.1%}",f"{rf_f.oos_r2_vs_historical_mean:.3f}"]],[3.2,2.5,2.4,2.7,2.3],8)
    body("Confirmation sharply reduced the apparent edge: annualized net return fell to 0.14%, the Sharpe to 0.01 and OOS R² to −0.009. The configuration advanced under the predeclared family-selection rule, but the deterioration is substantive evidence of instability.")

    # 14
    page("Final holdout: forecast and portfolio metrics", "8 · Empirical results")
    table(["Metric","Frozen random forest","AR baseline","SPY benchmark"],[["Observations","1,001","1,001","1,001"],["Directional accuracy",f"{rf_f.directional_accuracy:.2%}",f"{ar_f.directional_accuracy:.2%}","—"],["OOS R² vs historical mean",f"{rf_f.oos_r2_vs_historical_mean:.4f}",f"{ar_f.oos_r2_vs_historical_mean:.4f}","—"],["Annualized net return",f"{rf_f.annualized_net_return:.2%}",f"{ar_f.annualized_net_return:.2%}",f"{rf_f.annualized_benchmark_return:.2%}"],["Net Sharpe",f"{rf_f.net_sharpe:.3f}",f"{ar_f.net_sharpe:.3f}",f"{rf_f.benchmark_sharpe:.3f}"],["Net CAGR",f"{rf_f.net_cagr:.2%}",f"{ar_f.net_cagr:.2%}","—"],["Maximum drawdown",f"{rf_f.max_drawdown:.1%}",f"{ar_f.max_drawdown:.1%}","—"],["Average exposure",f"{rf_f.average_exposure:.1%}",f"{ar_f.average_exposure:.1%}","100%"],["Annualized turnover",f"{rf_f.annualized_turnover:.2f}",f"{ar_f.annualized_turnover:.2f}","0"]],[4.8,3.4,3.2,3.1],7.8)
    callout("Inference", "The strategy was profitable after base costs and had a shallower drawdown, but did not beat SPY on return or Sharpe. Negative predictive R² means probability-of-sign and portfolio gating did not translate into superior squared-error forecasts.")

    # 15
    page("Final holdout: cumulative wealth", "8 · Empirical results")
    picture(FINAL/"plots/02_cumulative_wealth.png",6.25,"Figure 5. Cumulative wealth of the frozen strategy and SPY, 2022–2025.","Strategy returns are net of 5 bp one-way costs; initial wealth = 1.")
    body("The frozen strategy finished near 1.10 while SPY finished near 1.55. The stair-step strategy path reflects infrequent exposure. Cash is modeled as a zero return and no risk-free interest is credited, which is conservative for the 2022–2025 period.")

    # 16
    page("Risk path and calendar decomposition", "8 · Empirical results")
    picture(FINAL/"plots/03_drawdown.png",5.75,"Figure 6. Drawdown paths in the final holdout.","Source: strategy ledger and SPY adjusted-close returns.")
    table(["Year","Strategy","SPY"],[[str(int(r.year)),f"{r.strategy:.2%}",f"{r.benchmark:.2%}"] for r in annual.itertuples(index=False)],[4.5,4.0,4.0],8.5)
    body("The model’s main economic contribution occurred in 2022, when it earned 17.50% while SPY lost 18.34%. It then missed most of the 2023–2025 equity advance and lost 8.57% in 2025. This asymmetric pattern explains lower drawdown alongside large benchmark underperformance.")

    # 17
    page("Complexity, fit and generalization", "9 · Interpretation")
    picture(FINAL/"plots/07_training_vs_oos_error.png",5.8,"Figure 7. Training versus out-of-sample error across final configurations.","Source: expanding-window refits; logarithmic scales where shown.")
    table(["Quantity","Frozen random forest"],[["Median train observations","4,508"],["Median trainable parameters","1,312"],["Parameter / observation ratio","0.292"],["Mean train MSE",f"{rf_f.mean_train_mse:.6f}"],["Final OOS MSE",f"{rf_f.mse:.6f}"],["Train–test MSE gap",f"{rf_f.train_test_mse_gap:.6f}"]],[7.0,6.2],8.5)
    body("The shallow forest stays below one parameter per training observation, but parameter count alone understates tree flexibility. Depth and minimum-leaf constraints are the operative regularizers. High-dimensional RFF variants in screening explicitly probe P/T regimes up to and above one; their ridge penalty protects numerical stability, while chronological loss determines whether extra capacity generalizes.")

    # 18
    page("Feature interpretation", "9 · Interpretation")
    picture(feature_fig,6.05,"Figure 8. Leading random-forest feature importances across final refits.","Impurity importance is descriptive and can favor continuous variables; it is not causal attribution.")
    body("Volatility-state variables dominate the selected forest, followed by short gold momentum, medium-horizon small-cap momentum and a 14-session SPY return lag. This pattern is economically consistent with an exposure gate reacting to risk state and cross-asset breadth. It does not identify a structural causal mechanism, and correlated features can divide or exchange importance across refits.")

    # 19
    page("Costs, uncertainty and robustness", "10 · Robustness")
    picture(FINAL/"plots/08_cost_sensitivity.png",5.85,"Figure 9. Final-holdout cost sensitivity.","Only the cost assumption varies; predictions and positions are held fixed.")
    table(["One-way cost","Annualized return","Sharpe"],[[f"{int(r.one_way_cost_bps)} bp",f"{r.annualized_return:.2%}",f"{r.sharpe:.3f}"] for r in cost.itertuples(index=False)],[4.2,4.4,3.8],8.3)
    boot=report_eval["block_bootstrap_strategy_minus_spy"]
    callout("Block-bootstrap uncertainty", f"The estimated annualized strategy-minus-SPY mean return was {boot['annualized_mean_return_difference']:.2%}. A {boot['confidence_level']:.0%} moving-block interval with {boot['block_length']} sessions and {boot['repetitions']:,} repetitions was [{boot['confidence_lower']:.2%}, {boot['confidence_upper']:.2%}]. The interval includes zero and is conditional on the selected strategy.")

    # 20
    page("Limitations, conclusion and reproducibility", "11 · Conclusion")
    doc.add_heading("Limitations",level=2)
    bullet("The asset universe is small and fixed; results may not generalize to other markets or frequencies.")
    bullet("Yahoo adjusted data are convenient but are not exchange-level execution data; spread, market impact and taxes are not modeled.")
    bullet("Close-to-close execution is idealized, cash earns zero, and the fixed 5 bp cost is only a scenario.")
    bullet("Model selection creates residual multiple-testing risk; the bootstrap interval does not remove selection bias.")
    doc.add_heading("Conclusion",level=2)
    body("The project demonstrates a sound leakage-controlled research process, but the empirical evidence is modest. The frozen random forest delivered positive net performance and defensive behavior in the final period, while failing to outperform SPY and failing to improve squared forecast error over a historical-mean baseline. The defensible conclusion is process validity with economically weak, regime-dependent evidence.")
    doc.add_heading("Reproducibility record",level=2)
    table(["Control","Recorded value"],[["Verification",f"PASS — {verification['checks_passed']} checks"],["Screening run","models_screening_8d1f4f8a10e794eb"],["Confirmation run","models_confirmation_5d6ed2ce5fa7b6cb"],["Final run","models_final_test_53e047b58e92e27b"],["Freeze","freeze_f98a78b584d0ca42"],["Seed / compute","17; 2 workers; 1 numeric thread each"]],[4.5,9.0],7.7)

    # 21
    page("Reproduction commands and contribution note", "Appendix A")
    body("Run from the repository root in an activated environment. The run IDs below reproduce the report inputs without refitting completed checkpoints.")
    cmds=["python scripts/verify_outputs.py","python reports/build_report.py","python /Users/whitetiger/.codex/plugins/cache/openai-primary-runtime/documents/26.601.10930/skills/documents/render_docx.py reports/Project2_Team16_Report.docx --output_dir reports/_rendered --emit_pdf","git lfs install","git add .gitattributes .gitignore data/processed artifacts reports assets","git lfs ls-files"]
    for c in cmds:
        p=doc.add_paragraph(); p.style="Intense Quote"; r=p.add_run(c); r.font.name="Courier New"; r.font.size=Pt(8)
    doc.add_heading("Contribution note",level=2)
    for a in authors:
        body(f"{a['name']} ({a['student_id']}): research design, data engineering, leakage controls, feature engineering, model implementation, walk-forward evaluation, interpretation and report preparation.")
    body("The repository records executable code, exact source hashes, dataset manifests and run manifests. Team members should update assets/authors.json and this contribution note if the final roster or allocation differs.")

    # 22
    page("References", "References")
    refs=[
      "[1] Fama, E. F. (1970). Efficient capital markets: A review of theory and empirical work. Journal of Finance, 25(2), 383–417.",
      "[2] Lo, A. W., & MacKinlay, A. C. (1988). Stock market prices do not follow random walks. Review of Financial Studies, 1(1), 41–66.",
      "[3] Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. Journal of Financial Economics, 104(2), 228–250.",
      "[4] Moreira, A., & Muir, T. (2017). Volatility-managed portfolios. Journal of Finance, 72(4), 1611–1644.",
      "[5] White, H. (2000). A reality check for data snooping. Econometrica, 68(5), 1097–1126.",
      "[6] Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2014). The probability of backtest overfitting. Journal of Computational Finance, 20(4), 39–69.",
      "[7] Gu, S., Kelly, B., & Xiu, D. (2020). Empirical asset pricing via machine learning. Review of Financial Studies, 33(5), 2223–2273.",
      "[8] Breiman, L. (2001). Random forests. Machine Learning, 45, 5–32.",
      "[9] Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. Econometrica, 55(3), 703–708.",
      "[10] Politis, D. N., & Romano, J. P. (1994). The stationary bootstrap. Journal of the American Statistical Association, 89(428), 1303–1313.",
      "[11] Yahoo Finance. Historical market data for SPY, QQQ, IWM, TLT and GLD, accessed 19 October 2026 through yfinance. https://finance.yahoo.com/",
      "[12] scikit-learn developers. scikit-learn: Machine learning in Python, version 1.7.2. https://scikit-learn.org/",
      "[13] pandas development team. pandas, version 2.3.3. https://pandas.pydata.org/",
    ]
    for ref in refs:
        p=doc.add_paragraph(ref); p.paragraph_format.left_indent=Cm(.55); p.paragraph_format.first_line_indent=Cm(-.55); p.paragraph_format.space_after=Pt(5); p.runs[0].font.size=Pt(8.5)
    body("All empirical figures and tables are authors’ calculations from the immutable objects identified in Section 2. Software versions and platform metadata are stored in each run manifest.")

    out=OUT/"Project2_Team16_Report.docx"
    doc.save(out)
    print(out)


if __name__ == "__main__":
    # The compact academic layout is maintained in a separate module so the
    # earlier page-oriented draft remains available for provenance.
    from build_report_ieee import build as build_compact_report
    build_compact_report()
