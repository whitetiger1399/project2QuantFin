"""Build the final DSA5205 cross-market report (DOCX only)."""
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
OUT = REPORTS / "Project2_Team16_Report.docx"
FIG = REPORTS / "figures_cross_market"
FIG.mkdir(parents=True, exist_ok=True)

DATASET_ID = "cross_market_panel_20261030T044550Z_e8964cacce4208c3"
ANALYSIS_ID = "analysis_20261030T044648Z_26ceef2429b3"
SCREENING_ID = "cm_screening_20261030T093727Z_0e77ef60dd73"
CONFIRMATION_ID = "cm_confirmation_20261030T111633Z_8bb9c211fb41"
FREEZE_ID = "cm_freeze_20261030T115423Z_7c6b1efba4dc"
SOURCE_FINAL_ID = "cm_final_test_20261030T115442Z_120878a67dbc"
FINAL_ID = "cm_final_slice_2025_20261031T002503Z_059ae5d8d47c"
SELECTED_ID = "cm_elastic_net_329a4ccca456"

DATASET = ROOT / "data/processed/cross_market" / DATASET_ID
EDA = ROOT / "artifacts/cross_market/analysis" / ANALYSIS_ID
RUNS = ROOT / "artifacts/cross_market/runs"
SCREENING = RUNS / SCREENING_ID
CONFIRMATION = RUNS / CONFIRMATION_ID
SOURCE_FINAL = RUNS / SOURCE_FINAL_ID
FINAL = RUNS / FINAL_ID
FREEZE = ROOT / "artifacts/cross_market/freezes" / f"{FREEZE_ID}.json"
DESIGN = ROOT / "artifacts/cross_market/report_figures/design_figures_20261030T104226Z_d63b02e71159"
LOGO = ROOT / "assets/nus_logo_full-vertical.jpg"
GITHUB = "https://github.com/whitetiger1399/project2QuantFin"

NUS_BLUE = "003D7C"
TEXT = "171717"
MUTED = "626A73"
PALE = "EFEFEF"
PALE_BLUE = "EAF1F5"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def shade(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr(); node = tc_pr.find(qn("w:shd"))
    if node is None: node = OxmlElement("w:shd"); tc_pr.append(node)
    node.set(qn("w:fill"), fill)


def margins(cell, top=65, start=80, bottom=65, end=80):
    tc_pr = cell._tc.get_or_add_tcPr(); tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None: tc_mar = OxmlElement("w:tcMar"); tc_pr.append(tc_mar)
    for name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{name}"))
        if node is None: node = OxmlElement(f"w:{name}"); tc_mar.append(node)
        node.set(qn("w:w"), str(value)); node.set(qn("w:type"), "dxa")


def repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr(); node = OxmlElement("w:tblHeader"); node.set(qn("w:val"), "true"); tr_pr.append(node)


def no_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:cantSplit")) is None: tr_pr.append(OxmlElement("w:cantSplit"))


def set_widths(table, widths_cm):
    table.autofit = False; total = int(sum(widths_cm) * 567); tbl_pr = table._tbl.tblPr; tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None: tbl_w = OxmlElement("w:tblW"); tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(total)); tbl_w.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid): grid.remove(child)
    for width in widths_cm:
        node = OxmlElement("w:gridCol"); node.set(qn("w:w"), str(int(width * 567))); grid.append(node)
    for row in table.rows:
        for cell, width in zip(row.cells, widths_cm):
            tc_pr = cell._tc.get_or_add_tcPr(); tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None: tc_w = OxmlElement("w:tcW"); tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(int(width * 567))); tc_w.set(qn("w:type"), "dxa")


def hyperlink(paragraph, text: str, url: str):
    rid = paragraph.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    link = OxmlElement("w:hyperlink"); link.set(qn("r:id"), rid); run = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color"); color.set(qn("w:val"), "4F81BD"); rpr.append(color); underline = OxmlElement("w:u"); underline.set(qn("w:val"), "single"); rpr.append(underline)
    run.append(rpr); node = OxmlElement("w:t"); node.text = text; run.append(node); link.append(run); paragraph._p.append(link)


def page_field(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER; paragraph.add_run("Project report  •  "); fld = OxmlElement("w:fldSimple"); fld.set(qn("w:instr"), "PAGE"); paragraph._p.append(fld)


def table(doc, headers, rows, widths, size=8.0):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; set_widths(t, widths); repeat_header(t.rows[0])
    for i, value in enumerate(headers):
        c = t.rows[0].cells[i]; shade(c, PALE); margins(c); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER; p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(str(value)); r.bold = True; r.font.size = Pt(size)
    for values in rows:
        row = t.add_row(); no_split(row)
        for i, value in enumerate(values):
            c = row.cells[i]; margins(c); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER; p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(0); p.add_run(str(value)).font.size = Pt(size)
    doc.add_paragraph().paragraph_format.space_after = Pt(0); return t


def callout(doc, label: str, text: str):
    t = doc.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER; set_widths(t, [16.1]); c = t.cell(0, 0); shade(c, PALE_BLUE); margins(c, 95, 125, 95, 125)
    p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0); r = p.add_run(label + "  "); r.bold = True; r.font.color.rgb = RGBColor.from_string(NUS_BLUE); p.add_run(text); doc.add_paragraph().paragraph_format.space_after = Pt(0)


def figure(doc, path: Path, caption_text: str, width=6.55):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(2); p.paragraph_format.keep_with_next = True; p.add_run().add_picture(str(path), width=Inches(width))
    c = doc.add_paragraph(style="Caption"); c.add_run(caption_text)


def equation(path: Path, latex: str, width=10.0):
    fig = plt.figure(figsize=(width, 1.0), dpi=240); fig.text(.5, .5, latex, ha="center", va="center", fontsize=16, color="#003D7C"); fig.savefig(path, bbox_inches="tight", transparent=True, pad_inches=.06); plt.close(fig)


def short_feature(x: str):
    for old, new in (("sp500_raw__", "S&P500 · "), ("us_context__", "US context · "), ("india_core__", "India · "), ("us_tech__", "US tech · "), ("global__", "Global · "), ("adr__", "ADR · "), ("own__", "Own · ")): x = x.replace(old, new)
    return x.replace("__", " · ").replace("_", " ")


def build_figures(screen_lb, confirm_lb, final_lb):
    plt.rcParams.update({"font.family": "DejaVu Serif", "axes.titlesize": 11, "axes.labelsize": 9})
    names = {"elastic_net":"Elastic Net","extra_trees":"Extra Trees","random_forest":"Random Forest","hist_gradient_boosting":"Histogram GB","pca_ridge":"PCA + Ridge","lasso":"Lasso","ridge":"Ridge","autoregression":"Autoregression"}
    best = confirm_lb.dropna(subset=["net_sharpe"]).sort_values("rank").groupby("family", as_index=False).first().sort_values("net_sharpe")
    fig, ax = plt.subplots(figsize=(8.8, 4.6), dpi=240); vals = best.net_sharpe; ax.barh([names.get(x, x) for x in best.family], vals, color=["#A44747" if x < 0 else "#2A9D8F" for x in vals]); ax.axvline(0, color="#333", lw=.8); ax.set_xlabel("Annualized net Sharpe (confirmation, 2023–2024)"); ax.set_title("Confirmation-stage model comparison", fontweight="bold"); ax.grid(axis="x", color="#D9DEE2", lw=.6); ax.set_axisbelow(True); ax.spines[["top","right","left"]].set_visible(False)
    for y,v in enumerate(vals): ax.text(v+(.04 if v>=0 else -.04),y,f"{v:.2f}",va="center",ha="left" if v>=0 else "right",fontsize=8)
    fig.subplots_adjust(left=.28,right=.96,bottom=.15,top=.88); leaderboard=FIG/"confirmation_family_leaderboard.png"; fig.savefig(leaderboard,bbox_inches="tight",facecolor="white"); plt.close(fig)

    stages=[]
    for label, frame in (("Screening\n2021–22",screen_lb),("Confirmation\n2023–24",confirm_lb),("Final evaluation\n2025",final_lb)): stages.append((label,frame[frame.config_id.eq(SELECTED_ID)].iloc[0]))
    fig, axes = plt.subplots(1,3,figsize=(9.2,3.4),dpi=240)
    for ax,key,title,scale in zip(axes,["net_annual_return","net_sharpe","maximum_drawdown"],["Annualized net return","Net Sharpe","Maximum drawdown"],[100,1,100]):
        values=[float(r[key])*scale for _,r in stages]; bars=ax.bar([s for s,_ in stages],values,color=["#8C9AA5","#2A9D8F","#003D7C"]); ax.axhline(0,color="#333",lw=.7); ax.set_title(title,fontweight="bold",fontsize=9.5); ax.grid(axis="y",color="#D9DEE2",lw=.5); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False); ax.tick_params(labelsize=7.1); ax.bar_label(bars,labels=[f"{v:.2f}"+("%" if scale==100 else "") for v in values],fontsize=7.2,padding=2)
    fig.suptitle("Frozen Elastic Net across research stages",fontweight="bold",fontsize=11); fig.subplots_adjust(left=.07,right=.98,bottom=.2,top=.8,wspace=.32); stability=FIG/"frozen_model_stage_stability.png"; fig.savefig(stability,bbox_inches="tight",facecolor="white"); plt.close(fig)

    ledgers=pd.read_parquet(FINAL/"strategy_ledgers.parquet"); d=ledgers[ledgers.config_id.eq(SELECTED_ID)].sort_values("decision_date").copy(); d["decision_date"]=pd.to_datetime(d.decision_date)
    wealth=pd.DataFrame({"Frozen Elastic Net (net)":(1+d.net_return.fillna(0)).cumprod().to_numpy(),"Nifty IT buy-and-hold proxy":(1+d.benchmark_nifty_it.fillna(0)).cumprod().to_numpy(),"Nifty 50 buy-and-hold":(1+d.benchmark_nifty50.fillna(0)).cumprod().to_numpy()},index=d.decision_date.to_numpy())
    fig,ax=plt.subplots(figsize=(8.8,4.4),dpi=240)
    for col,color in zip(wealth.columns,["#003D7C","#E97824","#2A9D8F"]): ax.plot(wealth.index,wealth[col],label=col,lw=1.8,color=color)
    ax.set_ylabel("Growth of INR 1"); ax.set_title("Complete-calendar-year 2025 wealth",fontweight="bold"); ax.grid(color="#D9DEE2",lw=.55); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False); ax.legend(ncol=3,fontsize=7.5,frameon=False,loc="upper center",bbox_to_anchor=(.5,-.14)); fig.subplots_adjust(left=.09,right=.98,bottom=.24,top=.88); wealth_path=FIG/"final_holdout_wealth.png"; fig.savefig(wealth_path,bbox_inches="tight",facecolor="white"); plt.close(fig)

    imp=pd.read_csv(FINAL/"feature_importance_by_refit.csv"); imp=imp[(imp.config_id.eq(SELECTED_ID))&(imp.measure.eq("standardized_coefficient"))]; top=imp.groupby("feature").importance.apply(lambda x:x.abs().mean()).nlargest(15).sort_values()
    fig,ax=plt.subplots(figsize=(8.8,5.1),dpi=240); ax.barh([short_feature(x) for x in top.index],top.values,color="#2F5D73"); ax.set_xlabel("Mean absolute standardized coefficient"); ax.set_title("Frozen Elastic Net: persistent signals",fontweight="bold"); ax.grid(axis="x",color="#D9DEE2",lw=.55); ax.set_axisbelow(True); ax.spines[["top","right","left"]].set_visible(False); ax.tick_params(axis="y",labelsize=7.4); fig.subplots_adjust(left=.39,right=.97,bottom=.12,top=.9); feature=FIG/"final_elastic_net_coefficients.png"; fig.savefig(feature,bbox_inches="tight",facecolor="white"); plt.close(fig)

    cost=pd.read_csv(FINAL/"cost_sensitivity.csv"); cost=cost[(cost.top_k.eq(3))&(cost.forecast_hurdle.eq(0.0))].sort_values("round_trip_cost_bps")
    fig,ax=plt.subplots(figsize=(8.8,3.8),dpi=240); ax.plot(cost.round_trip_cost_bps,cost.sharpe,marker="o",color="#003D7C",lw=1.8); ax.axhline(0,color="#333",lw=.7); ax.axvline(15,color="#E97824",ls="--",lw=1.2,label="Standard assumption: 15 bps"); ax.set_xlabel("Round-trip cost (bps)"); ax.set_ylabel("Annualized net Sharpe"); ax.set_title("2025 transaction-cost robustness",fontweight="bold"); ax.grid(color="#D9DEE2",lw=.55); ax.set_axisbelow(True); ax.spines[["top","right"]].set_visible(False); ax.legend(frameon=False,fontsize=8); cost_path=FIG/"final_cost_robustness.png"; fig.savefig(cost_path,bbox_inches="tight",facecolor="white"); plt.close(fig)
    return leaderboard,stability,wealth_path,feature,cost_path


def build_additional_figures(screen_lb):
    """Create compact, decision-relevant diagnostics from development data only."""
    panel = pd.read_parquet(DATASET / "panel.parquet")
    panel["decision_date"] = pd.to_datetime(panel["decision_date"])
    dev = panel.loc[panel["decision_date"].le("2024-12-31")].copy()
    assets = sorted(dev["asset"].unique())

    # Distribution and volatility: the two diagnostics that directly motivate
    # robust evaluation and rolling refits.
    samples = [dev.loc[dev.asset.eq(asset), "target_oc_return"].clip(-.08, .08) * 100 for asset in assets]
    fig, ax = plt.subplots(figsize=(9.0, 4.5), dpi=240)
    parts = ax.violinplot(samples, showmeans=False, showmedians=True, widths=.75)
    for body in parts["bodies"]: body.set_facecolor("#2F5D73"); body.set_alpha(.8)
    parts["cmedians"].set_color("#E97824")
    ax.set_xticks(range(1, len(assets)+1), [x.replace(".NS", "") for x in assets], rotation=35, ha="right")
    ax.set_ylabel("Open-to-close return (%)"); ax.set_title("Development-sample return distributions (2016–2024)", fontweight="bold")
    ax.axhline(0, color="#444", lw=.7); ax.grid(axis="y", color="#D9DEE2", lw=.55); ax.spines[["top","right"]].set_visible(False)
    fig.subplots_adjust(left=.09,right=.98,bottom=.24,top=.88); distribution=FIG/"development_return_distributions.png"; fig.savefig(distribution,bbox_inches="tight",facecolor="white"); plt.close(fig)

    cohort = dev.groupby("decision_date")["target_oc_return"].mean().sort_index()
    rolling_mean = cohort.rolling(63, min_periods=30).mean() * 252 * 100
    rolling_vol = cohort.rolling(63, min_periods=30).std() * np.sqrt(252) * 100
    fig, axes = plt.subplots(2,1,figsize=(9.0,4.8),dpi=240,sharex=True)
    axes[0].plot(rolling_mean.index, rolling_mean, color="#003D7C", lw=1.3); axes[0].axhline(0,color="#444",lw=.6); axes[0].set_ylabel("Return (%)")
    axes[1].plot(rolling_vol.index, rolling_vol, color="#E97824", lw=1.3); axes[1].set_ylabel("Volatility (%)")
    for ax in axes: ax.grid(color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False)
    axes[0].set_title("63-session annualized cohort return and volatility (development only)",fontweight="bold")
    fig.subplots_adjust(left=.1,right=.98,bottom=.1,top=.9,hspace=.16); regimes=FIG/"development_rolling_regimes.png"; fig.savefig(regimes,bbox_inches="tight",facecolor="white"); plt.close(fig)

    wide = dev.pivot(index="decision_date", columns="asset", values="target_oc_return").rename(columns=lambda x:x.replace(".NS",""))
    corr = wide.corr()
    fig, ax = plt.subplots(figsize=(7.3,6.0),dpi=240); im=ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)),corr.columns,rotation=45,ha="right",fontsize=7); ax.set_yticks(range(len(corr)),corr.index,fontsize=7)
    for i in range(len(corr)):
        for j in range(len(corr)): ax.text(j,i,f"{corr.iloc[i,j]:.2f}",ha="center",va="center",fontsize=6,color="white" if abs(corr.iloc[i,j])>.55 else "#222")
    ax.set_title("Cross-asset return correlation (development sample)",fontweight="bold"); fig.colorbar(im,ax=ax,fraction=.045,pad=.03)
    fig.subplots_adjust(left=.18,right=.93,bottom=.2,top=.9); correlation=FIG/"development_cross_asset_correlation.png"; fig.savefig(correlation,bbox_inches="tight",facecolor="white"); plt.close(fig)

    daily = dev.groupby("decision_date").agg(cohort_return=("target_oc_return","mean"))
    daily["weekday"] = daily.index.day_name().str[:3]
    daily["month"] = daily.index.month
    weekdays=["Mon","Tue","Wed","Thu","Fri"]
    w=daily.groupby("weekday").cohort_return.mean().reindex(weekdays)*100
    m=daily.groupby("month").cohort_return.mean().reindex(range(1,13))*100
    fig,axes=plt.subplots(1,2,figsize=(9.0,3.8),dpi=240)
    axes[0].bar(w.index,w.values,color=["#A44747" if x<0 else "#2A9D8F" for x in w]); axes[0].set_title("Weekday mean",fontweight="bold")
    axes[1].bar(range(1,13),m.values,color=["#A44747" if x<0 else "#003D7C" for x in m]); axes[1].set_title("Month mean",fontweight="bold"); axes[1].set_xticks(range(1,13))
    for ax in axes: ax.axhline(0,color="#444",lw=.7); ax.set_ylabel("Cohort O–C return (%)"); ax.grid(axis="y",color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Calendar diagnostics in the development sample",fontweight="bold"); fig.subplots_adjust(left=.08,right=.98,bottom=.16,top=.78,wspace=.28); seasonality=FIG/"development_calendar_effects.png"; fig.savefig(seasonality,bbox_inches="tight",facecolor="white"); plt.close(fig)

    us_cols=[c for c in dev.columns if c.startswith("us_tech__") and c.endswith("__intraday_return")]
    us_signal=dev.groupby("decision_date")[us_cols].first().mean(axis=1)
    aligned=pd.concat([cohort.rename("india"),us_signal.rename("us")],axis=1).dropna()
    lags=range(-5,6); lag_corr=pd.Series({lag:aligned.us.shift(lag).corr(aligned.india) for lag in lags})
    fig,ax=plt.subplots(figsize=(8.7,3.7),dpi=240); ax.bar(lag_corr.index,lag_corr.values,color=["#E97824" if lag==0 else "#6B8796" for lag in lag_corr.index]); ax.axhline(0,color="#444",lw=.7)
    ax.set_xticks(list(lags)); ax.set_xlabel("Additional lag of the already-completed U.S. session (days)"); ax.set_ylabel("Correlation"); ax.set_title("U.S. technology signal and Indian IT return timing",fontweight="bold"); ax.grid(axis="y",color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False)
    fig.subplots_adjust(left=.1,right=.98,bottom=.2,top=.86); lead_lag=FIG/"development_us_india_lead_lag.png"; fig.savefig(lead_lag,bbox_inches="tight",facecolor="white"); plt.close(fig)

    feature_cols=[c for c in dev.columns if "__" in c and c not in {"target_oc_return"}]
    families={}
    for col in feature_cols: families.setdefault(col.split("__",1)[0],[]).append(col)
    miss=pd.Series({family:dev[cols].isna().mean().mean()*100 for family,cols in families.items()}).sort_values()
    fig,ax=plt.subplots(figsize=(8.7,4.3),dpi=240); ax.barh(miss.index,miss.values,color="#6B8796"); ax.axvline(40,color="#E97824",ls="--",lw=1.2,label="40% training-window exclusion threshold")
    ax.set_xlabel("Mean missing observations (%)"); ax.set_title("Feature-family missingness before model-time filtering",fontweight="bold"); ax.grid(axis="x",color="#D9DEE2",lw=.5); ax.spines[["top","right","left"]].set_visible(False); ax.legend(frameon=False,fontsize=7.5)
    fig.subplots_adjust(left=.24,right=.98,bottom=.15,top=.88); missingness=FIG/"development_feature_missingness.png"; fig.savefig(missingness,bbox_inches="tight",facecolor="white"); plt.close(fig)

    configs=screen_lb.configuration.fillna("")
    progression=screen_lb.loc[configs.str.contains('"experiment": "feature_progression"')].copy()
    order=["F0_own","F1_india","F2_us_tech","F3_global","F4_full_us","F5_macro_nonlinear"]
    progression["feature_set"]=pd.Categorical(progression.feature_set,order,ordered=True); progression=progression.sort_values("feature_set")
    fig,axes=plt.subplots(1,2,figsize=(9.0,3.8),dpi=240)
    axes[0].plot(progression.feature_set.astype(str),progression.oos_r2_asset_mean*100,marker="o",color="#003D7C"); axes[0].set_ylabel("OOS R² vs asset mean (%)"); axes[0].axhline(0,color="#444",lw=.7)
    axes[1].plot(progression.feature_set.astype(str),progression.net_sharpe,marker="o",color="#2A9D8F"); axes[1].set_ylabel("Post-cost net Sharpe"); axes[1].axhline(0,color="#444",lw=.7)
    for ax in axes: ax.tick_params(axis="x",rotation=35,labelsize=7); ax.grid(color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Controlled information-set progression in screening",fontweight="bold"); fig.subplots_adjust(left=.09,right=.98,bottom=.28,top=.8,wspace=.28); progression_path=FIG/"screening_feature_progression.png"; fig.savefig(progression_path,bbox_inches="tight",facecolor="white"); plt.close(fig)

    complexity=screen_lb.loc[configs.str.contains('"experiment": "complexity"')].copy()
    complexity["ratio"]=complexity.configuration.str.extract(r'"complexity_ratio":\s*([0-9.]+)')[0].astype(float)
    complexity=complexity.loc[complexity.configuration.str.contains('"penalty": 1.0')].sort_values("ratio")
    fig,axes=plt.subplots(1,2,figsize=(9.0,3.8),dpi=240)
    axes[0].plot(complexity.ratio,complexity.oos_r2_asset_mean*100,marker="o",color="#003D7C"); axes[0].set_ylabel("OOS R² vs asset mean (%)")
    axes[1].plot(complexity.ratio,complexity.net_sharpe,marker="o",color="#E97824"); axes[1].set_ylabel("Post-cost net Sharpe")
    for ax in axes: ax.set_xscale("log"); ax.set_xlabel("RFF complexity ratio"); ax.axhline(0,color="#444",lw=.7); ax.grid(color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Approximation complexity with fixed ridge shrinkage",fontweight="bold"); fig.subplots_adjust(left=.09,right=.98,bottom=.2,top=.8,wspace=.28); complexity_path=FIG/"screening_complexity_path.png"; fig.savefig(complexity_path,bbox_inches="tight",facecolor="white"); plt.close(fig)

    ledger=pd.read_parquet(FINAL/"strategy_ledgers.parquet"); ledger=ledger.loc[ledger.config_id.eq(SELECTED_ID)].sort_values("decision_date").copy(); ledger["decision_date"]=pd.to_datetime(ledger.decision_date)
    wealth=(1+ledger.net_return.fillna(0)).cumprod(); drawdown=(wealth/wealth.cummax()-1)*100
    monthly=ledger.set_index("decision_date").net_return.resample("ME").apply(lambda s:(1+s).prod()-1)*100
    fig,axes=plt.subplots(2,1,figsize=(9.0,4.8),dpi=240,sharex=False)
    axes[0].fill_between(ledger.decision_date,drawdown,0,color="#A44747",alpha=.82); axes[0].set_ylabel("Drawdown (%)"); axes[0].set_title("Frozen strategy risk path during 2025",fontweight="bold")
    axes[1].bar(monthly.index,monthly.values,width=20,color=["#A44747" if x<0 else "#2A9D8F" for x in monthly]); axes[1].axhline(0,color="#444",lw=.7); axes[1].set_ylabel("Monthly net return (%)")
    for ax in axes: ax.grid(axis="y",color="#D9DEE2",lw=.5); ax.spines[["top","right"]].set_visible(False)
    fig.subplots_adjust(left=.09,right=.98,bottom=.12,top=.9,hspace=.25); final_risk=FIG/"final_2025_drawdown_monthly.png"; fig.savefig(final_risk,bbox_inches="tight",facecolor="white"); plt.close(fig)

    imp=pd.read_csv(FINAL/"feature_importance_by_refit.csv"); groups=imp.loc[(imp.config_id.eq(SELECTED_ID))&imp.feature.str.startswith("GROUP::",na=False)].copy(); groups["family"]=groups.feature.str.replace("GROUP::","",regex=False); grouped=groups.groupby("family").importance.mean().sort_values()
    fig,ax=plt.subplots(figsize=(8.7,4.3),dpi=240); ax.barh(grouped.index,grouped.values*1e6,color=["#A44747" if x<0 else "#2F5D73" for x in grouped]); ax.axvline(0,color="#444",lw=.7); ax.set_xlabel("OOS permutation MSE increase (×10⁻⁶)"); ax.set_title("Feature-family contribution in the frozen 2025 model",fontweight="bold"); ax.grid(axis="x",color="#D9DEE2",lw=.5); ax.spines[["top","right","left"]].set_visible(False)
    fig.subplots_adjust(left=.23,right=.98,bottom=.15,top=.88); group_importance=FIG/"final_group_permutation_importance.png"; fig.savefig(group_importance,bbox_inches="tight",facecolor="white"); plt.close(fig)

    return distribution,regimes,correlation,seasonality,lead_lag,missingness,progression_path,complexity_path,final_risk,group_importance


def configure(doc: Document):
    s=doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7); s.top_margin=Cm(1.9); s.bottom_margin=Cm(1.8); s.left_margin=Cm(2.3); s.right_margin=Cm(2.3); s.header_distance=Cm(.75); s.footer_distance=Cm(.75); s.different_first_page_header_footer=True
    normal=doc.styles["Normal"]; normal.font.name="Times New Roman"; normal.font.size=Pt(9.9); normal.font.color.rgb=RGBColor.from_string(TEXT); normal._element.rPr.rFonts.set(qn("w:eastAsia"),"Times New Roman"); normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; normal.paragraph_format.line_spacing=1.05; normal.paragraph_format.space_after=Pt(4)
    for name,size,before,after,color in (("Title",12,0,7,NUS_BLUE),("Subtitle",9.9,0,6,TEXT),("Heading 1",12,10,5,TEXT),("Heading 2",11.1,8,3,TEXT),("Heading 3",9.9,6,2,TEXT),("Caption",9,1,5,TEXT)):
        st=doc.styles[name]; st.font.name="Times New Roman"; st.font.size=Pt(size); st.font.color.rgb=RGBColor.from_string(color); st._element.rPr.rFonts.set(qn("w:eastAsia"),"Times New Roman"); st.paragraph_format.space_before=Pt(before); st.paragraph_format.space_after=Pt(after)
        if name.startswith("Heading") or name=="Title": st.font.bold=True
        if name.startswith("Heading"): st.paragraph_format.keep_with_next=True
    doc.styles["Caption"].font.italic=True
    h=s.header.paragraphs[0]; h.text="CROSS-MARKET PRE-OPEN FORECASTING OF NIFTY IT STOCKS  |  DSA5205"; h.alignment=WD_ALIGN_PARAGRAPH.LEFT; hr=h.runs[0]; hr.font.name="Times New Roman"; hr.font.size=Pt(8.4); hr.font.bold=True
    page_field(s.footer.paragraphs[0])
    for r in s.footer.paragraphs[0].runs: r.font.name="Times New Roman"; r.font.size=Pt(8.1); r.font.color.rgb=RGBColor.from_string("4A4A4A")
    s.first_page_header.paragraphs[0].clear(); s.first_page_footer.paragraphs[0].clear()


def build():
    required=[DATASET/"manifest.json",EDA/"manifest.json",SCREENING/"manifest.json",CONFIRMATION/"manifest.json",SOURCE_FINAL/"manifest.json",FINAL/"manifest.json",FREEZE,LOGO]
    missing=[str(p) for p in required if not p.exists()]
    if missing: raise FileNotFoundError("Missing report evidence:\n"+"\n".join(missing))
    dataset_manifest=read_json(DATASET/"manifest.json"); freeze=read_json(FREEZE); final_manifest=read_json(FINAL/"manifest.json"); authors=sorted(x["name"] for x in read_json(ROOT/"assets/authors.json"))
    screen_lb=pd.read_csv(SCREENING/"leaderboard.csv"); confirm_lb=pd.read_csv(CONFIRMATION/"leaderboard.csv"); final_lb=pd.read_csv(FINAL/"leaderboard.csv"); final=final_lb[final_lb.config_id.eq(SELECTED_ID)].iloc[0]
    final_inf=read_json(FINAL/"selected_model_inference.json"); hac=pd.read_csv(FINAL/"forecast_hac_comparisons.csv"); hac=hac[hac.config_id.eq(SELECTED_ID)].iloc[0]; annual=pd.read_csv(FINAL/"annual_performance.csv")
    return_tests=pd.read_csv(EDA/"return_statistical_tests.csv")
    leader_fig,stability_fig,wealth_fig,feature_fig,cost_fig=build_figures(screen_lb,confirm_lb,final_lb)
    distribution_fig,regimes_fig,correlation_fig,seasonality_fig,lead_lag_fig,missingness_fig,progression_fig,complexity_fig,final_risk_fig,group_importance_fig=build_additional_figures(screen_lb)
    eq_target=FIG/"eq_target.png"; eq_info=FIG/"eq_information_set.png"; eq_strategy=FIG/"eq_strategy.png"; equation(eq_target,r"$y_{i,t}=\frac{P^{close}_{i,t}}{P^{open}_{i,t}}-1$"); equation(eq_info,r"$\mathcal{I}_{t}^{08{:}55}=\{x_{j,s}:\tau^{available}_{j,s}<08{:}55\;\mathrm{IST}\}$"); equation(eq_strategy,r"$w_{i,t}\propto\max(\widehat y_{i,t}-h_t,0),\quad r^{net}_{p,t}=\sum_i w_{i,t}y_{i,t}-c\,\mathrm{turnover}_t$")
    doc=Document(); configure(doc); doc.core_properties.title="Cross-Market Pre-Open Forecasting of Nifty IT Stocks"; doc.core_properties.subject="DSA5205 Project 2"; doc.core_properties.author="; ".join(authors)

    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run("Cross-Market Pre-Open Forecasting of Nifty IT Stocks"); r.bold=True; r.font.size=Pt(12); r.font.color.rgb=RGBColor.from_string(NUS_BLUE)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(LOGO),width=Inches(1.55))
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run("Information progression, shrinkage, and complexity under leakage-controlled daily evaluation"); r.italic=True
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run("Data Science in Quantitative Finance DSA5205\nProject2 Teams 16"); r.bold=True
    at=doc.add_table(rows=1,cols=1); at.alignment=WD_TABLE_ALIGNMENT.CENTER; set_widths(at,[10.8]); shade(at.cell(0,0),PALE); hp=at.cell(0,0).paragraphs[0]; hp.alignment=WD_ALIGN_PARAGRAPH.CENTER; rr=hp.add_run("AUTHORS"); rr.bold=True; rr.font.color.rgb=RGBColor.from_string(MUTED)
    for name in authors:
        row=at.add_row(); margins(row.cells[0]); pp=row.cells[0].paragraphs[0]; pp.alignment=WD_ALIGN_PARAGRAPH.CENTER; pp.add_run(name)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run("Repository: "); hyperlink(p,GITHUB,GITHUB)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run("Market data: Yahoo Finance · Macro-financial data: FRED/ALFRED"); r.italic=True; r.font.color.rgb=RGBColor.from_string(MUTED)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run("October 2026"); doc.add_page_break()

    doc.add_heading("Contents",level=1)
    p=doc.add_paragraph("A compact reading map separates research design, empirical evidence, and reproducibility material.")
    p.paragraph_format.space_after=Pt(8); p.runs[0].font.color.rgb=RGBColor.from_string(MUTED)
    toc_rows=[
        ("Abstract","Question, design, and principal finding","3"),
        ("1. Research question and contribution","Hypotheses and relation to the two assigned papers","3"),
        ("2. Markets, assets, and information timing","Tradable universe, clock, labels, and benchmarks","4"),
        ("3. Data engineering and quality control","Sources, cleaning, missingness, and leakage controls","5"),
        ("4. Feature engineering and exploratory analysis","Development-only EDA and nested information sets","7"),
        ("5. Models, validation, and trading rule","Complexity, shrinkage, temporal selection, costs","11"),
        ("6. Results","Confirmation, 2025 evaluation, robustness","14"),
        ("7. Interpretation, limitations, and conclusion","What worked, what failed, and scope of inference","17"),
        ("AI usage declaration and references","Academic-integrity disclosure and sources","18"),
        ("Appendix A. Reproducibility and provenance","Immutable identifiers and exact evidence chain","19"),
        ("Appendix B. Assignment alignment","Rubric coverage and submission checklist","20"),
    ]
    table(doc,["Section","Purpose","Page"],toc_rows,[6.2,8.8,1.1],8.1)
    callout(doc,"Report logic","Design is fixed in Sections 1–5. Section 6 reports the frozen model on the complete 2025 calendar year. Appendices contain provenance and grading-rubric crosswalks rather than additional model tuning.")
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(12); hyperlink(p,"Source code and reproducibility artifacts",GITHUB); doc.add_page_break()

    doc.add_heading("Abstract",level=1)
    doc.add_paragraph("This study tests whether information available immediately before the Indian market open improves same-day open-to-close forecasts for ten current Nifty IT constituents. At 08:55 IST, a daily panel combines own-stock history, Indian market state, completed U.S. technology returns, Indian ADRs, global assets, point-in-time S&P 500 membership, and release-lagged macro-financial variables. The source panel contains 25,380 stock-days and 3,333 candidate features. Thirty-six configurations were screened in 2021–2022; ten family representatives were confirmed in 2023–2024; one Elastic Net model using the F4 broad-U.S. information set was frozen before final evaluation. For the complete 2025 calendar year, the frozen strategy returned −4.72% net, with −0.934 Sharpe, −5.98% maximum drawdown, 0.84% OOS R² versus an asset-mean forecast, and 55.66% directional accuracy. It outperformed the Nifty IT proxy (−10.66%) but trailed Nifty 50 (+11.66%). The Sharpe interval crosses zero and HAC alpha is insignificant; the evidence therefore supports limited forecast content, not a reliable trading anomaly.")
    callout(doc,"Evidence status",f"Frozen chain: {SCREENING_ID} → {CONFIRMATION_ID} → {FREEZE_ID} → {SOURCE_FINAL_ID}. The report evaluates the immutable 2025 slice {FINAL_ID}; no refitting, reselection, or forecast regeneration occurred.")
    doc.add_heading("1. Research question and contribution",level=1)
    doc.add_paragraph("The central question is whether completed overseas sessions contain incremental information for Indian technology stocks after controlling for their own histories and the domestic market state. The design contributes a real-time information clock, nested feature progression, explicit complexity controls, staged model selection, and a cost-aware strategy evaluated against Nifty 50 and Nifty IT buy-and-hold alternatives.")
    table(doc,["Hypothesis","Comparison","Decision criterion"],[("Cross-market information","F2/F3 versus F0/F1","OOS loss, IC, and net performance"),("Broad U.S. breadth","F4 versus F2","Incremental generalization"),("Controlled complexity","RFF ratios and shrinkage","Accuracy without unstable turnover"),("Economic value","Frozen strategy versus benchmarks","Net Sharpe, drawdown, and alpha")],[3.5,5.0,7.6],7.8)
    doc.add_paragraph("Chinco, Clark-Joseph, and Ye (2019) motivate sparse, short-lived cross-stock links and penalized estimation. Kelly, Malamud, and Zhou (2024) motivate large nonlinear feature maps controlled by shrinkage. These principles are adapted to daily cross-market prediction: many potential signals are permitted, but time ordering, regularization, independent confirmation, and a frozen OOS prediction archive govern interpretation.")
    figure(doc,DESIGN/"10_research_architecture.png","Figure 1. Research architecture. The target remains fixed while information expands from own-stock history to Indian, U.S. technology, global, and point-in-time broad-U.S. predictors.",5.5)

    doc.add_page_break(); doc.add_heading("2. Markets, assets, and information timing",level=1); assets=dataset_manifest["evidence_summary"]["assets"]
    doc.add_paragraph("The traded universe is the frozen current-member cohort: "+", ".join(x.replace(".NS","") for x in assets)+". This supports complete stock-level tracking but is not a historical Nifty IT reconstruction; survivorship conditioning is retained as a limitation. Nifty 50 buy-and-hold is the principal investable benchmark, with Nifty IT and the equal-weight fixed cohort as diagnostics.")
    table(doc,["Information block","Representative inputs","Availability rule"],[("India","Nifty IT stocks, Nifty 50, Bank, India VIX","Known by 08:55 IST"),("Focused U.S. tech","20 technology leaders; INFY/WIT ADRs","Prior completed U.S. session"),("Broad U.S.","SPY, QQQ, sectors, PIT S&P 500","Dated membership and completed session"),("Global and macro","Indices, FX, rates, curves, spreads","Completed market or release-lagged value")],[3.5,7.4,5.2],7.7)
    figure(doc,DESIGN/"12_information_clock.png","Figure 2. Leakage-safe information clock. Forecasting occurs at 08:55 IST; execution follows at the reported 09:15 NSE open.")
    figure(doc,eq_target,"Equation 1. Same-day stock-level open-to-close target.",5.4); figure(doc,eq_info,"Equation 2. Feature eligibility is governed by availability time, not calendar date alone.",6.0)

    doc.add_page_break(); doc.add_heading("3. Data engineering and quality control",level=1)
    doc.add_paragraph("Immutable raw snapshots feed a content-addressed panel builder. Symbol-specific rules quarantine impossible OHLC rows, preserve dated constituent membership, and record current-vintage macro fallbacks. INR=X is restricted to close-to-close use; the anomalous NIFTYBEES open on 7 July 2009 is excluded from open-to-close calculations. The completed audit passed with warnings rather than silently repairing source values.")
    table(doc,["Item","Value","Interpretation"],[("Panel","25,380 stock-days","10 assets × 2,538 decisions"),("Span","21 Jul 2016–29 Oct 2026","Daily Indian-market frequency"),("Features","3,333","Nested F0–F5 information sets"),("Quarantined rows",str(dataset_manifest["evidence_summary"]["quarantined_row_count"]),"Invalid or impossible source bars"),("Macro fallbacks",str(len(dataset_manifest["evidence_summary"]["macro_current_vintage_fallbacks"])),"Disclosed current-vintage series")],[3.1,3.8,9.2],8)
    callout(doc,"Leakage controls","Rolling features use past values only; availability precedes the decision; preprocessing and feature screening are fitted within each training window; dated S&P 500 membership is used; the final holdout is opened only after the confirmation winner is frozen.")
    doc.add_heading("3.1 Sources, adjustments, and lawful access",level=2)
    table(doc,["Source","Content used","Research treatment"],[("Yahoo Finance","Daily OHLCV for Indian, U.S., ADR, global, ETF, and FX symbols","Immutable snapshots; adjusted-history caveats retained"),("FRED/ALFRED","U.S. policy rates, yields, curves, credit spreads, dollar and India macro series","Vintage-aware where available; conservative release lags otherwise"),("Historical constituent files","Dated S&P 500 and Nifty membership","Membership joined by date to reduce constituent look-ahead"),("NSE reference files","Current Nifty IT membership and index context","Fixed-current cohort disclosed as survivorship-conditioned")],[3.2,5.2,7.7],7.6)
    doc.add_paragraph("The source panel extends into 2026 because it was built before the complete-year reporting decision. All development plots in this report stop at 31 December 2024, and the canonical final evaluation stops at 31 December 2025. Rows from 2026 are neither used to fit the frozen model nor included in reported performance.")
    doc.add_page_break(); doc.add_heading("3.2 Missingness and model-time filtering",level=2)
    figure(doc,missingness_fig,"Figure 3. Development-sample missingness by feature family. Broad constituent histories are intentionally sparse because entry dates differ; columns above the 40% threshold are removed using the current training window only.",6.15)
    doc.add_paragraph("Missing values are not filled globally. At every refit, columns with more than 40% training-window missingness or negligible variance are removed; surviving columns are median-imputed, winsorized at training-only 0.5% and 99.5% quantiles, and standardized using past observations. This procedure allows membership-aware breadth variables without leaking future coverage patterns.")

    doc.add_page_break(); doc.add_heading("4. Feature engineering and exploratory analysis",level=1)
    doc.add_heading("4.1 Development-only exploratory analysis",level=2)
    doc.add_paragraph("Exploratory analysis is restricted to observations dated no later than 31 December 2024. Its role is diagnostic: establish tail behavior, regime variation, cross-sectional dependence, calendar structure, and plausible transmission timing. It is not used to search retrospectively for profitable 2025 subperiods.")
    figure(doc,distribution_fig,"Figure 4. Development-sample return distributions. Heavy tails and stock-level heterogeneity rule out Gaussian-error intuition and motivate robust, repeated OOS evaluation.",6.15)
    figure(doc,regimes_fig,"Figure 5. Rolling cohort return and volatility through 2024. Persistent regime variation motivates rolling estimation and prevents a static historical fit from representing all market states.",6.15)
    doc.add_page_break()
    figure(doc,correlation_fig,"Figure 6. Development-sample cross-asset correlation. The sector factor is material, but correlations remain below unity, leaving scope for stock ranking rather than only index timing.",5.55)
    figure(doc,seasonality_fig,"Figure 7. Weekday and month diagnostics. Calendar differences are small and unstable; Fourier terms are retained as low-cost controls rather than treated as stand-alone trading signals.",6.1)
    figure(doc,lead_lag_fig,"Figure 8. U.S.–India timing diagnostic. Lag zero represents the completed U.S. session already available before the Indian open. The pattern is descriptive and does not identify causal transmission.",6.1)
    doc.add_paragraph("Formal return diagnostics reinforce these choices. Augmented Dickey–Fuller tests reject unit roots for all ten stock-return series, while Jarque–Bera tests reject normality and ARCH-LM tests reject constant conditional variance. Several Ljung–Box tests detect short-lag dependence, but the pattern differs by stock. Consequently, the model uses regularized cross-market and rolling-state features rather than imposing one common low-order autoregression.")
    table(doc,["Diagnostic","Assets significant at 5%","Modeling implication"],[("ADF unit-root rejection",f"{int((return_tests.adf_pvalue<.05).sum())}/10","Returns are modeled in levels, not prices"),("Jarque–Bera non-normality",f"{int((return_tests.jarque_bera_pvalue<.05).sum())}/10","Use tail-aware evaluation and drawdown metrics"),("ARCH-LM heteroskedasticity",f"{int((return_tests.arch_lm_10_pvalue<.05).sum())}/10","Include rolling volatility and recurrent refits"),("Ljung–Box dependence, lag 5",f"{int((return_tests.ljung_box_5_pvalue<.05).sum())}/10","Retain short return lags but do not assume universality")],[5.1,4.1,6.9],7.5)

    doc.add_page_break(); doc.add_heading("4.2 Feature construction and information progression",level=2)
    table(doc,["Set","Increment","Examples","Purpose"],[("F0","Own + calendar","lags, momentum, volatility, Fourier calendar","Forecast baseline"),("F1","+ India","Nifty 50/Bank/VIX, breadth, dispersion","Domestic state"),("F2","+ U.S. tech/ADR","returns, gaps, momentum, volatility","Focused spillover"),("F3","+ Global","SPY/QQQ/sectors, indices, FX","Risk context"),("F4","+ PIT S&P 500","dated-member signals and aggregates","Broad complexity"),("F5","+ Macro/nonlinear","rates, curves, regimes, interactions","Robustness")],[.9,3.0,7.4,4.8],7.5)
    doc.add_paragraph("Engineering includes 1/2/3/5/10/21-day return lags, 5–252-day momentum, 5–63-day volatility, price-to-moving-average ratios, RSI, log-volume z-scores, gaps, intraday ranges, close location, breadth, dispersion, Fourier seasonality, and predeclared nonlinear transformations. Macro variables include Federal Reserve policy rates, Treasury yields and curve slopes, credit spreads, dollar/INR measures, Indian interest-rate proxies, and conservative release lags.")
    table(doc,["Feature mechanism","Economic interpretation","Leakage control"],[("Overnight U.S. and ADR returns","Global client demand and technology risk are observed before India opens","Prior completed session only"),("Indian index and volatility state","Domestic risk appetite and market-wide opening conditions","Lagged or pre-open-known values"),("Rolling momentum and volatility","Persistent trend and time-varying risk","Trailing windows ending before decision"),("Breadth and dispersion","Whether U.S. moves are broad or stock-specific","Dated membership; training-window filtering"),("Fourier and calendar controls","Smooth seasonality without one dummy per date","Deterministic from decision date"),("Macro and regime interactions","Transmission may vary with rates and stress","Release lag plus predeclared transforms")],[4.3,7.0,4.8],7.5)
    figure(doc,progression_fig,"Figure 9. Controlled feature progression in screening. The same ridge penalty is used while information expands, separating information gain from model-family changes.",6.2)
    callout(doc,"Interpretation discipline","Univariate correlations and feature progression are screening diagnostics. Economic claims rely on independent confirmation and the frozen 2025 evaluation, not on the largest in-sample or full-panel correlation.")

    doc.add_page_break(); doc.add_heading("5. Models, validation, and trading rule",level=1)
    doc.add_heading("5.1 Model families and complexity control",level=2)
    table(doc,["Family","Research role","Control"],[("Baselines","Zero, asset mean, autoregression","Minimal capacity"),("Ridge/Lasso/Elastic Net","Dense and sparse linear shrinkage","Penalty + preselection"),("PCA + Ridge","Compressed linear structure","Components + ridge"),("Forests/boosting","Nonlinear interactions","Depth, leaves, subsampling"),("RFF + Ridge","Explicit complexity path","Feature ratio, cap, shrinkage")],[4.0,6.1,6.0],7.7)
    doc.add_paragraph("Chinco, Clark-Joseph, and Ye (2019) motivate sparsity because many potential cross-stock signals are short lived; Lasso and Elastic Net operationalize this idea. Kelly, Malamud, and Zhou (2024) motivate an explicit complexity path: random Fourier features approximate nonlinear functions, while ridge shrinkage stabilizes estimation as trainable dimension approaches or exceeds the original feature count. Tree ensembles provide a separate nonlinear benchmark rather than being assumed superior.")
    figure(doc,complexity_fig,"Figure 10. Random-Fourier approximation complexity in screening. Increasing dimension does not improve performance monotonically; shrinkage controls variance but does not guarantee generalization.",6.2)
    table(doc,["Control","Implementation","Purpose"],[("Predeclared grid","36 screening configurations across nested feature sets and model families","Limits researcher degrees of freedom"),("Training-only transforms","Winsorization, imputation, scaling, and univariate preselection refitted each window","Prevents validation distribution leakage"),("Rolling history","1,260 prior Indian sessions with a one-session embargo","Adapts to regimes while preserving order"),("Capacity constraints","Penalties, PCA dimensions, tree depth/leaves, RFF cap of 4,096","Controls high-dimensional variance"),("Single frozen winner","Confirmation net Sharpe with accuracy and turnover tie-breakers","Separates selection from final evaluation")],[3.4,7.5,5.2],7.4)

    doc.add_page_break(); doc.add_heading("5.2 Temporal validation and model selection",level=2)
    figure(doc,DESIGN/"11_experiment_design.png","Figure 11. Staged experiment design: broad screening, independent confirmation, immutable freeze, and a final prediction archive later restricted to the complete 2025 calendar year.",6.2)
    table(doc,["Stage","Dates","Design","Role"],[("Initial training","2016–2020","Past observations only","Initialize screening"),("Screening","2021–2022","36 configs; quarterly refits","Promote family representatives"),("Confirmation","2023–2024","10 configs; quarterly refits","Select one model"),("Frozen evaluation","1 Jan–31 Dec 2025","4 configs; monthly refits","Complete-year OOS estimate")],[3.0,3.5,5.7,3.9],7.6)
    doc.add_paragraph("Quarterly refitting in screening and confirmation preserves daily OOS predictions while respecting the four-hour compute budget. The final archive uses monthly refits for the frozen model and three forecast baselines. Every prediction on date t is trained only on dates before t after a one-session embargo; the training window then advances through time.")

    doc.add_page_break(); doc.add_heading("5.3 Forecast-to-trade rule and evaluation metrics",level=2)
    figure(doc,eq_strategy,"Equation 3. Long-only forecast-to-position mapping with a hurdle and turnover costs.",6.2)
    doc.add_paragraph("The strategy trades up to three forecasts that exceed the larger of the forecast hurdle and round-trip cost hurdle, caps single-stock weight at 50%, and charges 5 bps commission plus 2.5 bps slippage on each side. Uninvested weight remains in cash; leverage and short selling are excluded from the primary specification. Positions enter at the reported NSE open and exit at the same session's close.")
    table(doc,["Evaluation layer","Metric","Interpretation"],[("Forecast accuracy","RMSE, MAE, OOS R² vs zero and asset mean","Whether predictions improve squared loss"),("Cross-sectional signal","Daily Spearman IC and directional accuracy","Ranking and sign information"),("Portfolio outcome","Net annual return, volatility, Sharpe, Sortino, drawdown","Economic value after costs"),("Implementation","Turnover and cost-sensitivity curve","Dependence on friction assumptions"),("Inference","HAC loss test, HAC alpha, circular block-bootstrap Sharpe interval","Serial dependence and sampling uncertainty")],[3.1,6.7,6.3],7.5)
    callout(doc,"Benchmark discipline","Nifty 50 is the principal investable opportunity-cost benchmark. Nifty IT and the equal-weight fixed cohort diagnose sector exposure. Asset-mean, zero, and autoregressive forecasts are evaluated under the identical walk-forward clock.")

    doc.add_page_break(); doc.add_heading("6. Results",level=1); doc.add_heading("6.1 Screening and confirmation",level=2)
    doc.add_paragraph("Depth-constrained Extra Trees led 2021–2022 screening, but the independent confirmation period changed the ranking. Elastic Net became the confirmation winner with a 13.78% annualized net return, 1.257 net Sharpe, 1.47% OOS R² versus the asset mean, and −6.85% maximum drawdown. The ranking reversal demonstrates why the screening winner was not taken directly to the final evaluation.")
    figure(doc,leader_fig,"Figure 12. Confirmation-stage family comparison. Elastic Net and Lasso lead after costs; tree ensembles remain positive but weaker.",6.15)
    callout(doc,"Frozen specification","Elastic Net on F4: alpha 0.0005; L1 ratio 0.8; maximum 4,000 iterations; tolerance 0.0001; training-only preselection of 500 features. The freeze binds one model and the net-Sharpe selection rule.")
    figure(doc,stability_fig,"Figure 13. The frozen Elastic Net across stages. Confirmation strength does not persist in 2025, illustrating selection uncertainty and the need to report the final estimate rather than the validation peak.",6.2)

    doc.add_page_break(); doc.add_heading("6.2 Complete-calendar-year 2025 evaluation",level=2)
    doc.add_paragraph("The original final archive contained monthly walk-forward predictions for 2025 and a partial 2026. Because 2026 was incomplete, all rows after 31 December 2025 were removed and every metric, test, ledger, and figure was recomputed. Forecasts were not regenerated, the model was not refitted beyond its original schedule, and no specification was reselected. This is therefore a derived complete-year evaluation of pre-existing OOS predictions, not a newly untouched holdout.")
    table(doc,["Metric","2025 estimate","Interpretation"],[("Net calendar-year return",f"{100*annual.iloc[0].strategy_net_return:.2f}%","Compounded strategy return after costs"),("Annualized net return",f"{100*final.net_annual_return:.2f}%","Annualization over 249 trading sessions"),("Net Sharpe",f"{final.net_sharpe:.3f}","Negative risk-adjusted outcome"),("Maximum drawdown",f"{100*final.maximum_drawdown:.2f}%","Largest peak-to-trough loss"),("OOS R² vs asset mean",f"{100*final.oos_r2_asset_mean:.2f}%","Small positive forecast improvement"),("Directional accuracy",f"{100*final.directional_accuracy:.2f}%","Stock-day sign accuracy"),("Mean daily turnover",f"{100*final.mean_daily_turnover:.2f}%","Cost-relevant activity"),("Forecast observations",f"{int(final.observations):,}","249 dates × 10 stocks")],[4.5,3.2,8.4],7.8)
    figure(doc,wealth_fig,"Figure 14. Cumulative wealth during 2025. The strategy limits losses relative to Nifty IT but materially trails Nifty 50.",6.2)
    figure(doc,final_risk_fig,"Figure 15. Drawdown and monthly net returns. Losses are distributed across several months rather than one isolated crash, weakening a simple event-only explanation.",6.15)
    table(doc,["2025 comparator","Total return","Result versus strategy"],[("Frozen Elastic Net strategy",f"{100*annual.iloc[0].strategy_net_return:.2f}%","Reference"),("Nifty IT buy-and-hold proxy",f"{100*annual.iloc[0].nifty_it_return:.2f}%",f"Strategy ahead by {100*(annual.iloc[0].strategy_net_return-annual.iloc[0].nifty_it_return):.2f} pp"),("Nifty 50 buy-and-hold",f"{100*annual.iloc[0].nifty50_return:.2f}%",f"Strategy behind by {100*(annual.iloc[0].nifty50_return-annual.iloc[0].strategy_net_return):.2f} pp")],[5.5,3.2,7.4],7.8)
    doc.add_paragraph("The model produces a modest positive OOS R² and sign accuracy above 50%, yet the trading rule loses money after costs. Forecast improvements are therefore too small, too poorly ranked, or too concentrated to overcome turnover and the strong opportunity cost represented by Nifty 50.")

    doc.add_heading("6.3 Forecast baselines, inference, and robustness",level=2)
    baseline_rows=[]
    for _,row in final_lb.sort_values("rank").iterrows():
        baseline_rows.append((row.family.replace("_"," ").title(),row.feature_set,f"{100*row.oos_r2_asset_mean:.2f}%",("n/a" if pd.isna(row.net_sharpe) else f"{row.net_sharpe:.3f}"),f"{100*row.directional_accuracy:.2f}%"))
    table(doc,["Forecast","Features","OOS R²","Net Sharpe","Direction"],baseline_rows,[3.6,3.0,2.8,3.0,3.7],7.6)
    figure(doc,group_importance_fig,"Figure 16. Feature-family permutation importance in 2025. Broad S&P 500 signals contribute most to squared-error accuracy; negative values indicate that permutation occasionally improves the forecast.",6.15)
    figure(doc,cost_fig,"Figure 17. Transaction-cost sensitivity for the fixed top-three rule. Performance deteriorates rapidly as round-trip friction increases; the 15 bps primary assumption lies between the 10 and 20 bps grid points.",6.15)
    doc.add_paragraph(f"Elastic Net improves mean squared loss relative to the asset-mean baseline, but the HAC comparison gives t={hac.hac_t_statistic:.3f}, p={hac.hac_pvalue:.3f}, and FDR-adjusted p={hac.fdr_bh_pvalue:.3f}. Annualized alpha versus Nifty 50 is {100*final_inf['annualized_alpha']:.2f}% with HAC p={final_inf['alpha_hac_pvalue']:.3f}. The circular block-bootstrap 95% interval for net Sharpe is [{final_inf['net_sharpe_95_ci'][0]:.3f}, {final_inf['net_sharpe_95_ci'][1]:.3f}]. All intervals include economically weak outcomes, so statistical decisiveness is absent.")
    doc.add_paragraph("Cross-sectional Spearman IC is undefined on days when the selected model issues constant predictions across the ten-stock cohort. Directional accuracy and loss metrics remain well defined, but the missing IC is itself informative: part of the model behaves more like a common timing signal than a stable stock-ranking engine.")

    doc.add_heading("7. Interpretation, limitations, and conclusion",level=1)
    doc.add_heading("7.1 What worked and what did not",level=2)
    table(doc,["Finding","Evidence","Interpretation"],[("Cross-market inputs improve loss","2025 OOS R² versus asset mean = 0.84%","There is weak incremental forecast information"),("Shrinkage generalizes better than trees","Elastic Net wins confirmation and remains best among final forecast models","Sparse regularization is appropriate for many weak predictors"),("Trading performance is negative","2025 net return −4.72%; Sharpe −0.934","Accuracy gains do not translate reliably after costs"),("Sector-relative loss is smaller","Nifty IT proxy returns −10.66%","The strategy reduces sector drawdown but is not an attractive standalone allocation"),("Market benchmark dominates","Nifty 50 returns +11.66%","Opportunity-cost comparison rejects a strong investment claim"),("Inference is inconclusive","Sharpe interval crosses zero; alpha p = 0.261","The sample does not establish abnormal performance")],[4.1,6.0,6.0],7.5)
    doc.add_heading("7.2 Limitations",level=2)
    doc.add_paragraph("The fixed current-member cohort creates survivorship conditioning. Public price and constituent histories are not exchange-certified; several macro series use disclosed current-vintage fallbacks; reported opens abstract from auction queueing, bid–ask variation, taxes, liquidity, and market impact. The effective sample for portfolio inference is 249 serially dependent days rather than 2,490 independent stock-days. Cross-market associations may reflect common global risk rather than direct economic transmission.")
    doc.add_paragraph("A second limitation concerns protocol history. The source final run originally included 2025 and partial 2026. Restricting the archive to 2025 solves the incomplete-calendar problem and cannot allow 2026 observations to alter already-issued 2025 forecasts, but the resulting slice is not claimed as newly unseen after the broader archive was inspected. The derivation and its hashes are disclosed in Appendix A.")
    doc.add_heading("7.3 Conclusion",level=2)
    doc.add_paragraph("The research process is stronger than the trading result. A leakage-controlled information clock, nested features, rolling estimation, independent confirmation, shrinkage, explicit costs, investable benchmarks, and immutable provenance satisfy the core quantitative-finance requirements. The final evidence supports a narrow conclusion: completed U.S. and global information provides small incremental forecasting value for current Nifty IT constituents, but the selected long-only strategy does not deliver reliable positive performance in 2025. More complexity is not automatically virtuous; it becomes useful only when shrinkage, time-respecting validation, and economic implementation jointly survive out of sample.")

    doc.add_page_break(); doc.add_heading("AI usage declaration",level=1); doc.add_paragraph("OpenAI Codex was used to assist with code drafting, debugging, figure generation, report structuring, language refinement, and document formatting. All empirical claims are tied to repository artifacts and remain the responsibility of the listed authors. AI-assisted suggestions were checked against project requirements, manifests, and completed outputs. No AI-generated result was accepted without artifact-level verification.")
    doc.add_heading("References",level=1)
    refs=["Chinco, A. M., Clark-Joseph, A. D., & Ye, M. (2019). Sparse signals in the cross-section of returns. The Journal of Finance, 74(1), 449–492. https://doi.org/10.1111/jofi.12733","Gu, S., Kelly, B. T., & Xiu, D. (2020). Empirical asset pricing via machine learning. Review of Financial Studies, 33(5), 2223–2273.","Kelly, B. T., Malamud, S., & Zhou, K. (2024). The virtue of complexity in return prediction. The Journal of Finance, 79(1), 459–501. https://doi.org/10.1111/jofi.13298","National University of Singapore. NUS Plagiarism Policy. https://myportal.nus.edu.sg/studentportal/student-discipline/all/docs/NUS-Plagiarism-Policy.pdf","National University of Singapore. Code of Student Conduct, Section A: Academic Integrity. https://studentconduct.nus.edu.sg/wp-content/uploads/NUS-Code-of-Student-Conduct.pdf","NUS Libraries. Academic Integrity Essentials. https://libguides.nus.edu.sg/new2nus/acadintegrity","NUS CTLT. Policy for Use of AI in Teaching and Learning, Sections 3–4. http://ctlt.nus.edu.sg/policy-for-use-of-ai-in-teaching-and-learning.pdf","Project repository and reproducibility artifacts. "+GITHUB,"Yahoo Finance market data; FRED/ALFRED macro-financial data; public historical constituent files cited in repository manifests."]
    for i,ref in enumerate(refs,1):
        p=doc.add_paragraph(); p.paragraph_format.left_indent=Cm(.6); p.paragraph_format.first_line_indent=Cm(-.6); p.add_run(f"[{i}] ").bold=True; p.add_run(ref)

    doc.add_page_break(); doc.add_heading("Appendix A. Reproducibility and provenance",level=1)
    table(doc,["Artifact","Immutable identifier"],[("Processed source panel",DATASET_ID),("EDA evidence run",ANALYSIS_ID),("Screening run",SCREENING_ID),("Confirmation run",CONFIRMATION_ID),("Model freeze",FREEZE_ID),("Source final prediction archive",SOURCE_FINAL_ID),("Canonical 2025 evaluation",FINAL_ID),("Frozen configuration",SELECTED_ID),("Completed refits","288 screening + 80 confirmation + 48 retained final diagnostics"),("2025 integrity check","249 dates; 9,960 predictions; every derived file hash verified"),("Environment","Python 3.10.10; scikit-learn 1.7.2; macOS arm64")],[5.2,10.9],7.2)
    doc.add_paragraph("The canonical 2025 artifact is created with: python scripts/derive_cross_market_holdout_slice.py --source-run-id "+SOURCE_FINAL_ID+" --start 2025-01-01 --end 2025-12-31. The command filters pre-existing forecasts, recomputes all metrics and figures, and records that no fitting or model reselection occurred.")
    doc.add_paragraph("Exact source snapshots, content hashes, checkpoints, predictions, ledgers, plots, package versions, and report inputs are stored under configs/, data/processed/cross_market/, and artifacts/cross_market/. The repository README is the operational entry point.")

    doc.add_page_break(); doc.add_heading("Appendix B. Assignment alignment",level=1)
    table(doc,["Project requirement","Implemented evidence"],[("Markets, assets, frequency, and timing","Section 2; Figures 1–2; Equations 1–2"),("Labels, aligned features, scaling, and cleaning","Sections 3–4; Figures 3–9"),("Buy-and-hold and forecast baselines","Sections 2, 5.3, and 6.2–6.3"),("Economic model story and overfitting control","Sections 1 and 5.1; Figure 10"),("Training and reproducible settings","Sections 5.1–5.2; Appendix A"),("Time-respecting validation and selection","Section 5.2; Figures 11–13"),("Trades, costs, and constraints","Section 5.3; Equation 3; Figure 17"),("OOS return, Sharpe, drawdown, and benchmarks","Section 6.2; Figures 14–15"),("Interpretation of weak performance","Sections 6.3 and 7"),("Code, commands, and immutable evidence","Repository link; Appendix A")],[7.2,8.9],7.6)
    doc.add_heading("Contribution note",level=2)
    doc.add_paragraph("The report, codebase, data audit, model-validation protocol, and interpretation are joint team outputs. All listed authors reviewed the empirical claims and share responsibility for the submitted work. A more granular individual task allocation may be added before submission if required by the course instructor.")
    callout(doc,"Submission check","The final PDF should be exported from this DOCX after updating fields, and the repository link, video access, requirements file, README commands, and absence of API secrets should be checked immediately before Canvas upload.")

    doc.save(OUT)
    print(json.dumps({"output":str(OUT),"authors":authors,"dataset_id":DATASET_ID,"screening_run_id":SCREENING_ID,"confirmation_run_id":CONFIRMATION_ID,"freeze_id":FREEZE_ID,"final_run_id":FINAL_ID,"final_status":final_manifest["status"],"selected_final_config":freeze["selected_config_id"],"pdf_modified":False},indent=2))


if __name__ == "__main__": build()
