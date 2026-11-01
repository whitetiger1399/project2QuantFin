#!/usr/bin/env python3
"""Build an audited figure-only publication pack from existing evidence (no training)."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import shutil
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import ListedColormap
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import PercentFormatter, ScalarFormatter
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reports"))
import build_report_ai_capability as old
from quantfin.io import sha256_file, atomic_json_dump, stable_object_hash
from quantfin.progress import progress

INDIA, US, NET, GROSS, SHORT, FLAT = "#175B9A", "#B75B16", "#123D65", "#138577", "#B34155", "#DFE4EA"
HYP = ROOT / "artifacts/research_hypotheses" / os.environ.get(
    "REPORT_HYPOTHESIS_ANALYSIS_ID", "hypotheses_20261101T030841Z_d494c2f238ca64a6"
)
INPUTS = {}
CATALOG = []


def track(p):
    p = Path(p)
    INPUTS[str(p.relative_to(ROOT))] = sha256_file(p)
    return p


def csv(p):
    return pd.read_csv(track(p))


def parquet(p, **kwargs):
    return pd.read_parquet(track(p), **kwargs)


def clean_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E5E9EE", linewidth=.6)
    ax.set_axisbelow(True)


def dates(ax):
    locator = mdates.AutoDateLocator(minticks=4, maxticks=7)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


def legend(ax, cols=2):
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.15), ncol=cols, frameon=False, fontsize=10)


def save(fig, output, name, title, caption, reason, placement="main"):
    for suffix in ["png", "svg", "pdf"]:
        fig.savefig(output / f"{name}.{suffix}", dpi=240, bbox_inches="tight", pad_inches=.12)
    plt.close(fig)
    CATALOG.append(dict(id=name, title=title, caption=caption, change=reason, placement=placement,
                        png=f"{name}.png", svg=f"{name}.svg", pdf=f"{name}.pdf"))


def architecture(output):
    from architecture_visual import draw_architecture
    track(ROOT/'reports/architecture_visual.py')
    for icon in (ROOT/'assets/architecture_icons').glob('*'):
        if icon.is_file(): track(icon)
    save(draw_architecture(), output, '01_architecture', 'Research architecture',
         'Country flags and provider marks distinguish available inputs. The signed_forecast policy selects up to three stocks per side, subject to exposure caps. The 15 bps round-trip assumption includes a fee/spread proxy and slippage, not a complete Indian tax schedule. Hypotheses are discussed separately; retrospective benchmark scores do not enter historical forecasts.',
         'Added country flags, sourced AI-provider marks, timing and process icons; removed hypotheses from the operational flow.')


def load_prices(root, assets):
    values = {}
    for asset in assets:
        d = parquet(root / f"{asset}.parquet")
        values[asset] = pd.Series(d.adjusted_close.to_numpy(),index=pd.to_datetime(d.session)).sort_index()
    return pd.concat(values,axis=1).sort_index()


def market_figures(output, india, us):
    view = india.loc["2020":"2026-09-30"]
    norm = view.div(view.apply(lambda s:s.dropna().iloc[0]))*100
    fig, ax = plt.subplots(figsize=(9,5.5))
    for asset,color in zip(norm,plt.cm.tab10(np.arange(10))):
        ax.plot(norm.index,norm[asset],lw=1.1,label=asset.replace('.NS',''),color=color)
    ax.set_yscale("log"); ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.axvspan(pd.Timestamp("2025-01-01"),pd.Timestamp("2026-09-30"),color=INDIA,alpha=.06)
    ax.axvline(pd.Timestamp("2025-01-01"),color=INDIA,ls="--",lw=1)
    ax.set(title="INDIA | Ten current Nifty IT constituents",ylabel="Adjusted-price index (log scale)")
    clean_axis(ax); dates(ax); legend(ax,5); fig.subplots_adjust(bottom=.25,top=.89,left=.11,right=.98)
    save(fig,output,"02_india_paths","Daily market context",
         "Daily adjusted-price paths in local currency. The logarithmic axis makes proportional changes comparable when one constituent grows much faster than others. Shading marks the 2025–September 2026 reported evaluation period. Constituents are the frozen current-member cohort, not a historical Nifty IT membership portfolio.",
         "Replaces compressed linear-axis ten-stock chart; explicit log scale and membership caveat.")
    fig,axes=plt.subplots(2,1,figsize=(9,6.3),sharex=True,sharey=True)
    for ax,frame,assets,cmap,title,color,style in [
        (axes[0],india,['TCS.NS','INFY.NS','WIPRO.NS'],'Blues','INDIA | TCS · Infosys · Wipro',INDIA,'-'),
        (axes[1],us,['ACN','IBM','CTSH'],'Oranges','U.S. | Accenture · IBM · Cognizant',US,'--')]:
        x=frame[assets].loc['2020':'2026-09-30'];x=x/x.apply(lambda s:s.dropna().iloc[0])*100
        for asset,c in zip(assets,plt.get_cmap(cmap)([.5,.7,.9])):
            ax.plot(x.index,x[asset],color=c,ls=style,lw=1.5,label=asset.replace('.NS',''))
        ax.set_title(title,loc='left',color=color,weight='bold');ax.set_ylabel('Local-price index (100)')
        ax.axvline(pd.Timestamp('2025-01-01'),color='#777',ls=':',lw=1)
        clean_axis(ax);ax.legend(ncol=3,frameon=False,loc='upper left',fontsize=10)
    dates(axes[1]);fig.subplots_adjust(hspace=.3,left=.1,right=.98,top=.94,bottom=.1)
    save(fig,output,'03_india_us_paths','India and U.S. services: distinct markets',
         'Selected Indian firms (blue solid) and U.S. firms (orange dashed), on shared scales and normalized independently at their first available 2020 observation. These are local-currency price paths, without FX conversion. Visual co-movement is descriptive; predictive association is tested on decision-aligned returns in Figure 5.',
         'Separates countries into labelled panels; consistent colour and line-style encoding.')
    returns=india.loc['2020':'2024'].pct_change(fill_method=None)
    corr=returns.corr(min_periods=100)
    corr.to_csv(output/'04_peer_correlations.csv')
    heatmap(output,corr,'04_peer_correlations','INDIA | Peer return correlation, 2020–2024',
            'Indian constituents','Indian constituents',INDIA,INDIA,triangle=True,bound=1,
            caption='Pearson correlations of daily adjusted close-to-close returns during development. Only the lower triangle is shown to remove duplicate information; blank cells are intentionally masked. Correlation supports studying shared movements but does not establish incremental forecast value.')
    panel_file=old.DATASET/'panel.parquet'
    cols=[c for c in pq.read_schema(panel_file).names if c.startswith('us_it_services__') and c.endswith('__ret_lag_1')]
    p=parquet(panel_file,columns=['decision_date','asset','target_oc_return',*cols])
    p=p.loc[p.decision_date.between('2020-01-01','2024-12-31')]
    target=p.pivot(index='decision_date',columns='asset',values='target_oc_return')
    predictors=p.groupby('decision_date')[cols].first()
    cross=pd.DataFrame({c.split('__')[1].upper():{a:target[a].corr(predictors[c]) for a in target} for c in cols})
    cross.to_csv(output/'05_cross_market_correlations.csv')
    heatmap(output,cross,'05_cross_market_correlations','U.S. → INDIA | Decision-aligned return association',
            'U.S. IT-services return available before NSE open','INDIA: same-session open-to-close return',US,INDIA,bound=max(.1,np.nanmax(abs(cross.to_numpy()))),
            caption='Pearson correlation between each completed U.S. services return available at the Indian decision cutoff and each Indian constituent\'s subsequent open-to-close return, 2020–2024. Values come from the engineered modelling panel, preserving its calendar alignment. U.S. predictor labels are orange; Indian targets are blue. Colour limits are printed on the colour bar; associations are small and not causal.')


def heatmap(output,table,name,title,xlabel,ylabel,xcolor,ycolor,caption,triangle=False,bound=None):
    values=table.to_numpy(dtype=float)
    if triangle: values=np.where(np.triu(np.ones(values.shape),0).astype(bool),np.nan,values)
    if bound is None:bound=np.nanmax(abs(values))
    cmap=plt.get_cmap('RdBu_r').copy();cmap.set_bad('#F2F4F6')
    fig,ax=plt.subplots(figsize=(9.4,6.5))
    image=ax.imshow(np.ma.masked_invalid(values),cmap=cmap,vmin=-bound,vmax=bound,aspect='auto')
    ax.set_xticks(range(len(table.columns)),[str(x).replace('.NS','') for x in table.columns],rotation=45,ha='right',fontsize=10,color=xcolor)
    ax.set_yticks(range(len(table.index)),[str(x).replace('.NS','') for x in table.index],fontsize=10,color=ycolor)
    for i,j in np.ndindex(values.shape):
        v=values[i,j]
        if np.isfinite(v):ax.text(j,i,f'{v:.2f}',ha='center',va='center',fontsize=9,color='white' if abs(v)>.6*bound else '#222')
    ax.set_title(title,fontsize=13,pad=14,weight='bold');ax.set_xlabel(xlabel,color=xcolor,labelpad=12);ax.set_ylabel(ylabel,color=ycolor,labelpad=12)
    fig.colorbar(image,ax=ax,fraction=.035,pad=.04,label='Pearson correlation')
    fig.subplots_adjust(left=.19,right=.94,bottom=.25,top=.89)
    save(fig,output,name,title,caption,'Regenerated with readable labels, explicit countries, missing-value treatment and plotted-data export.')


def ledgers():
    parts=[]
    for folder in [old.FINAL,old.FORWARD]:
        m=json.loads(track(folder/'manifest.json').read_text())
        assert m['status']=='complete' and m['selected_config_id']==old.SELECTED
        d=parquet(folder/'strategy_ledgers.parquet');d=d.loc[d.config_id.eq(old.SELECTED)].copy()
        parts.append(d)
    d=pd.concat(parts).sort_values('decision_date');d.decision_date=pd.to_datetime(d.decision_date)
    assert not d.decision_date.duplicated().any()
    assert np.isfinite(d[['gross_return','net_return','trading_cost']].to_numpy()).all()
    np.testing.assert_allclose(d.gross_return-d.trading_cost,d.net_return,atol=1e-12)
    assert (d.trading_cost >= 0).all()
    np.testing.assert_allclose(d.trading_cost,d.turnover*.00075,atol=1e-10)
    return d.set_index('decision_date')


def events(output,india,us):
    e=csv(old.EPOCH/'epoch_event_capability_returns.csv')
    e['release_date']=pd.to_datetime(e.release_date)
    e=e.loc[e.primary_event.eq(True)&e.eci.notna()&e.release_date.between('2023-01-01','2025-05-31')].sort_values('release_date')
    e=e.loc[e.eci.gt(e.eci.cummax().shift(fill_value=-np.inf))].copy()
    e['event_number']=np.arange(1,len(e)+1)
    india_assets=['TCS.NS','INFY.NS','WIPRO.NS','HCLTECH.NS','TECHM.NS']
    us_assets=['ACN','IBM','CTSH','EPAM','DXC']
    fig=plt.figure(figsize=(9.5,7.2));gs=fig.add_gridspec(3,1,height_ratios=[1,1,.65],hspace=.45)
    axes=[fig.add_subplot(gs[i]) for i in range(2)]
    for ax,frame,assets,country,color in [(axes[0],india,india_assets,'INDIA',INDIA),(axes[1],us,us_assets,'U.S.',US)]:
        q=frame[assets].loc['2023-01-01':'2025-06-30'];q=q/q.apply(lambda s:s.dropna().iloc[0])*100
        ax.plot(q.index,q.median(axis=1),color=color,lw=1.8,label='Median normalized stock path')
        ax.fill_between(q.index,q.quantile(.25,axis=1),q.quantile(.75,axis=1),color=color,alpha=.16,label='Cross-stock interquartile range')
        ax.set_title(country+' | Five IT-services firms',loc='left',color=color,weight='bold',fontsize=12)
        ax.set_ylabel('Price index (100)');clean_axis(ax);dates(ax)
        for row in e.itertuples():ax.axvline(row.release_date,color='#8A8893',lw=.65,ls=':',alpha=.6)
    axes[0].legend(frameon=False,fontsize=8.5,ncol=2,loc='upper left')
    for i,row in enumerate(e.itertuples()):
        axes[1].text(row.release_date,.96-(i%3)*.13,str(row.event_number),transform=axes[1].get_xaxis_transform(),ha='center',va='top',fontsize=10,weight='bold',bbox=dict(fc='white',ec='none',pad=1))
    key=fig.add_subplot(gs[2]);key.axis('off')
    provider_icons={
        'OpenAI': ROOT/'assets/architecture_icons/openai.png',
        'Anthropic': ROOT/'assets/architecture_icons/anthropic.png',
        'Google DeepMind': ROOT/'assets/architecture_icons/gemini.png',
    }
    for path in provider_icons.values():
        track(path)
    def add_provider_mark(ax,row,x,y,zoom=.045,coords='axes fraction'):
        path=provider_icons.get(row.provider)
        if path is not None:
            mark=OffsetImage(plt.imread(path),zoom=zoom)
            ax.add_artist(AnnotationBbox(mark,(x,y),xycoords=coords,frameon=False,box_alignment=(0,.5)))
        else:
            ax.text(x,y,'xAI',transform=ax.transAxes if coords=='axes fraction' else ax.get_xaxis_transform(),
                    fontsize=9,weight='bold',va='center',ha='left',
                    bbox=dict(boxstyle='round,pad=.18',fc='white',ec='#222',lw=.6))
    for i,row in enumerate(e.itertuples()):
        x=(i%3)/3; y=1-(i//3)*.36
        add_provider_mark(key,row,x,y-.035,zoom=.035)
        label=f'{row.event_number}. {row.provider} · {row.model_family}\n{row.release_date:%d %b %Y} | ECI {row.eci:.1f}'
        key.text(x+.045,y,label,transform=key.transAxes,fontsize=8.6,va='top')
    fig.suptitle('Frontier advances alongside service-company price paths',fontsize=14,weight='bold')
    fig.subplots_adjust(top=.89,bottom=.06,left=.11,right=.98)
    save(fig,output,'06a_frontier_timeline','What happened around the mapped frontier advances?',
         'Numbered markers identify record improvements within the available retrospective Epoch mapping, not every frontier release. The plot ends in June 2025 to match that evidence. Median paths and cross-stock interquartile bands summarize five firms per country; the bands are dispersion, not confidence intervals. India: TCS, Infosys, Wipro, HCLTech, Tech Mahindra. U.S.: Accenture, IBM, Cognizant, EPAM, DXC. Price levels and event coincidence do not identify causal announcement effects.',
         'Replaces cramped vertical event names with a numbered key, country colours and labelled dispersion bands.')
    responses=[]
    for row in e.itertuples():
        mapping=old.map_release_sessions(pd.Timestamp(row.public_at_utc),pd.DatetimeIndex(india.index),pd.DatetimeIndex(us.index))
        us_day=mapping['first_us_reaction_session'];india_day=pd.Timestamp(row.tradable_date)
        for country,assets in [('U.S.',us_assets),('India',india_assets)]:
            for asset in assets:
                if country=='U.S.':
                    values=us[asset].dropna().pct_change(fill_method=None);value=values.get(us_day,np.nan)
                else:
                    raw=parquet(old.RAW_INDIA/f'{asset}.parquet').set_index('session')
                    raw.index=pd.to_datetime(raw.index)
                    values=raw['close']/raw['open'].where(raw['open']>0)-1;value=values.get(india_day,np.nan)
                responses.append(dict(country=country,asset=asset,event_number=row.event_number,event=row.model_family,
                                      release_date=str(row.release_date.date()),return_value=value))
    response=pd.DataFrame(responses);response.to_csv(output/'06b_event_responses.csv',index=False)
    bound=max(.01,response.return_value.abs().max())*100
    fig,axes=plt.subplots(2,1,figsize=(9.5,6.3),sharex=True)
    for ax,country,color,assets,title in [(axes[0],'U.S.',US,us_assets,'U.S. | First completed reaction session: close-to-close'),
                                        (axes[1],'India',INDIA,india_assets,'INDIA | First eligible session: open-to-close')]:
        table=response.loc[response.country.eq(country)].pivot(index='asset',columns='event_number',values='return_value').reindex(assets)*100
        cmap=plt.get_cmap('RdBu_r').copy();cmap.set_bad('#E8EBEF')
        im=ax.imshow(np.ma.masked_invalid(table.to_numpy()),vmin=-bound,vmax=bound,cmap=cmap,aspect='auto')
        ax.set_yticks(range(5),[s.replace('.NS','') for s in assets],color=color,fontsize=11)
        # The U.S. panel uses three compact visual rows: heading, provider
        # marks, then heat-map cells.  Keep the bands distinct without leaving
        # an oversized void between the title and the data.
        ax.set_title(title,loc='left',color=color,fontsize=11,weight='bold',pad=32 if country=='U.S.' else 10)
        for i,j in np.ndindex(table.shape):
            v=table.iloc[i,j]
            ax.text(j,i,f'{v:+.1f}' if np.isfinite(v) else 'NA',ha='center',va='center',fontsize=10,color='white' if abs(v)>.65*bound else '#222')
    event_labels=[]
    for row in e.itertuples():
        model=str(row.model_family).replace('Claude 3.5 Sonnet','Claude 3.5').replace('Claude 3.7 Sonnet','Claude 3.7').replace('Gemini 2.5 Pro','Gemini 2.5')
        event_labels.append(f'{row.event_number}\n{model}')
    axes[1].set_xticks(range(len(e)),event_labels,fontsize=8)
    axes[1].set_xlabel('Frontier model release; returns in percent')
    for j,row in enumerate(e.itertuples()):
        path=provider_icons.get(row.provider)
        if path is not None:
            axes[0].add_artist(AnnotationBbox(OffsetImage(plt.imread(path),zoom=.025),(j,1.080),
                                             xycoords=axes[0].get_xaxis_transform(),frameon=False))
        else:
            axes[0].text(j,1.070,'xAI',transform=axes[0].get_xaxis_transform(),ha='center',va='bottom',
                         fontsize=7.5,weight='bold')
    fig.subplots_adjust(left=.13,right=.86,top=.865,bottom=.13,hspace=.38)
    cax=fig.add_axes([.9,.2,.02,.6]);fig.colorbar(im,cax=cax,label='Observed return (%)')
    save(fig,output,'06b_event_responses','Observed U.S. and Indian reactions',
         'Provider marks and model names identify each mapped frontier advance. The upper and lower panels separate countries with explicit outcome definitions. U.S. close-to-close and Indian open-to-close returns cover different horizons, so magnitudes are not a like-for-like causal comparison. Reaction sessions follow the conservative publication-time mapping. Entries are observed returns, not market-adjusted abnormal returns. This is the limited Epoch-mapped subset shown in the timeline, not the complete 2026 event calendar.',
         'Adds provider marks and model names, preserves readable country separation, and discloses unequal return horizons.',placement='main')


def regimes(output,d):
    monthly=pd.DataFrame({label:d[col].resample('ME').apply(lambda x:(1+x).prod()-1)
                          for label,col in [('Model net','net_return'),('Nifty IT ETF','benchmark_nifty_it'),('Nifty 50 ETF','benchmark_nifty50')]})
    monthly['regime']=np.select([monthly['Nifty IT ETF']>=.03,monthly['Nifty IT ETF']<=-.03],['Rising','Falling'],default='Sideways')
    previous=None;rev=[]
    for v in monthly.regime:
        rev.append(f'{previous} → {v}' if v!='Sideways' and previous and previous!=v else 'None')
        if v!='Sideways':previous=v
    monthly['reversal']=rev;monthly.to_csv(output/'16_monthly_regimes.csv')
    fig,axes=plt.subplots(1,2,figsize=(10,4.8))
    rng=np.random.default_rng(5205)
    for ax,field,labels,title in [(axes[0],'regime',['Rising','Sideways','Falling'],'All evaluation months'),
                                (axes[1],'reversal',['Falling → Rising','Rising → Falling'],'Directional reversals')]:
        ticks=[]
        for i,label in enumerate(labels):
            vals=monthly.loc[monthly[field].eq(label),'Model net']*100
            ticks.append(label.replace(' → ','\n→ ') + f'\n(n={len(vals)})')
            if len(vals):
                ax.scatter(i+rng.uniform(-.12,.12,len(vals)),vals,color=NET,alpha=.7,s=26)
                ax.plot([i-.22,i+.22],[vals.mean()]*2,color=US,lw=3)
        ax.set_xticks(range(len(labels)),ticks,fontsize=10);ax.set_title(title,fontsize=12)
        ax.axhline(0,color='#777',lw=1);ax.set_ylabel('Monthly model net return (%)');clean_axis(ax)
    fig.suptitle('Realized regimes | Dispersion matters more than a mean alone',fontsize=14,weight='bold')
    fig.subplots_adjust(top=.8,left=.09,right=.98,bottom=.2,wspace=.28)
    save(fig,output,'16_regime_distributions','Sideways markets and reversals: observed monthly outcomes',
         'Dots show individual 2025–September 2026 monthly model returns; orange strokes are group means. Regimes use realized Nifty IT ETF monthly returns: rising ≥3%, falling ≤−3%, otherwise sideways. A reversal changes the latest non-sideways direction. These labels are known after the month ends and are descriptive, not pre-trade signals. Small reversal groups cannot establish reliable regime-specific skill.',
         'Replaces bare three-bar regime summaries with individual observations, group sizes and explicit ex-post classification.')


def cost_and_performance(output,d,india):
    wealth=(1+d[['gross_return','net_return']]).cumprod()
    stats=[]
    for name,g in [('2025',d.loc['2025']),('2026 Jan–Sep',d.loc['2026']),('Combined',d)]:
        gross=(1+g.gross_return).prod()-1;net=(1+g.net_return).prod()-1
        stats.append(dict(period=name,gross=gross,net=net,terminal_wealth_gap=gross-net,sum_daily_cost=g.trading_cost.sum()))
    table=pd.DataFrame(stats);table.to_csv(output/'07_cost_accounting.csv',index=False)
    fig,axes=plt.subplots(2,1,figsize=(9,7),gridspec_kw={'height_ratios':[1.4,1]})
    for col,label,c in [('gross_return','Gross: same holdings, no costs',GROSS),('net_return','Net: after recorded costs',NET)]:
        axes[0].plot(d.index,wealth[col]-1,label=label,color=c,lw=2)
    axes[0].fill_between(d.index,wealth.gross_return-1,wealth.net_return-1,color=GROSS,alpha=.12)
    axes[0].set_title('Transaction costs change the economic conclusion',loc='left',weight='bold')
    axes[0].yaxis.set_major_formatter(PercentFormatter(1));axes[0].set_ylabel('Cumulative return')
    axes[0].legend(frameon=False,fontsize=10,loc='upper left');dates(axes[0])
    x=np.arange(3)
    for off,col,c,label in [(-.18,'gross',GROSS,'Gross'),(.18,'net',NET,'Net')]:
        bars=axes[1].bar(x+off,table[col]*100,.34,color=c,label=label)
        axes[1].bar_label(bars,labels=[f'{v:.2%}' for v in table[col]],padding=4,fontsize=11)
    # Preserve a full negative-return band so the 2025 net label sits inside
    # the plotting area rather than colliding with the x-axis labels.
    lower=min(-10.0,float(table[['gross','net']].min().min()*100*1.35))
    upper=float(table[['gross','net']].max().max()*100*1.22)
    axes[1].set_xticks(x,table.period);axes[1].set_ylabel('Period return (%)');axes[1].set_ylim(lower,upper)
    axes[1].axhline(0,color='#777',lw=.9)
    for ax in axes:clean_axis(ax)
    fig.subplots_adjust(left=.11,right=.97,top=.94,bottom=.09,hspace=.38)
    save(fig,output,'07_transaction_cost_drag','The same trades, before and after costs',
         f"Recorded 2025 returns are {table.iloc[0].gross:.2%} gross and {table.iloc[0].net:.3%} net. Both paths use identical holdings and execution dates. The shaded terminal wealth gap includes foregone compounding and is not simply the sum of cash fees. Costs are the implementation's assumed 7.5 bps per side, charged on turnover. 2026 is January–September; the joined path crosses from quarterly refits to a fixed-fit extension.",
         'New cost-isolation figure with exact ledger accounting; replaces illustrative unverified gross numbers.')
    curves={'Model net':d.net_return,'Nifty IT ETF':d.benchmark_nifty_it,'Nifty 50 ETF':d.benchmark_nifty50}
    base=india.loc[india.index<d.index.min()].iloc[-1]
    prices=india.reindex(d.index).ffill()
    assert base.notna().all() and prices.notna().all().all()
    passive=prices.div(base).mean(axis=1);ret=passive.pct_change(fill_method=None);ret.iloc[0]=passive.iloc[0]-1
    curves['Current-cohort buy & hold']=ret
    frame=pd.DataFrame(curves);frame.to_csv(output/'08_benchmark_daily_returns.csv')
    fig,ax=plt.subplots(figsize=(9,5.1))
    for col,c in zip(frame,[NET,'#BB6C24','#238C80','#7B5CA5']):
        v=(1+frame[col]).cumprod()-1;ax.plot(v.index,v,label=f'{col}: {v.iloc[-1]:+.1%}',color=c,lw=1.7)
    ax.axvline(pd.Timestamp('2026-01-01'),color='#888',ls='--',lw=1)
    ax.set(title='Reported evaluation | January 2025–September 2026',ylabel='Cumulative return')
    ax.yaxis.set_major_formatter(PercentFormatter(1));dates(ax);clean_axis(ax);legend(ax,2)
    fig.subplots_adjust(bottom=.26,left=.11,right=.98,top=.9)
    save(fig,output,'08_combined_benchmarks','Combined evaluation and passive alternatives',
         'One continuous compounded path across 2025 and the January–September 2026 extension. The dashed line identifies the change in refit protocol, not a capital reset. Model returns include recorded trading costs. ETF and fixed-share current-cohort buy-and-hold comparisons include overnight exposure and do not receive the intraday strategy cost model; the cohort has current-membership selection bias.',
         'Moves legend outside the data, labels final returns and explains the different execution exposures.')
    fig,axes=plt.subplots(2,1,figsize=(9,6.3),sharex=True,gridspec_kw={'height_ratios':[1.3,1]})
    axes[0].step(d.index,d.long_exposure,where='mid',color=GROSS,lw=1.1,label='Long exposure (+)')
    axes[0].step(d.index,-d.short_exposure,where='mid',color=SHORT,lw=1.1,label='Short exposure (−)')
    axes[0].set(ylabel='Signed portfolio exposure',title='Long, short and flat | Daily decisions and monthly activity')
    axes[0].legend(ncol=2,frameon=False,fontsize=10,loc='upper left');axes[0].set_ylim(-1.2,1.4)
    state=np.select([(d.long_exposure>0)&(d.short_exposure>0),d.long_exposure>0,d.short_exposure>0],['Mixed','Long','Short'],default='Flat')
    counts=pd.crosstab(d.index.to_period('M'),state).reindex(columns=['Long','Short','Mixed','Flat'],fill_value=0)
    counts.to_csv(output/'09_monthly_position_counts.csv')
    bottom=np.zeros(len(counts));xx=counts.index.to_timestamp()+pd.Timedelta(days=14)
    for col,c in zip(counts,[GROSS,SHORT,'#7B5CA5',FLAT]):
        axes[1].bar(xx,counts[col],width=22,bottom=bottom,label=col,color=c);bottom+=counts[col].to_numpy()
    axes[1].set_ylabel('Trading sessions');legend(axes[1],4)
    for ax in axes:clean_axis(ax)
    dates(axes[1]);fig.subplots_adjust(left=.11,right=.98,top=.92,bottom=.18,hspace=.3)
    save(fig,output,'09_signed_positions','What was actually traded',
         'Daily gross long and short exposures are shown with opposite signs. The lower panel counts actual sessions classified as long-only, short-only, mixed or flat. A flat month or session is retained rather than omitted. The policy allows simultaneous long and short positions even if the observed ledger contains none.',
         'Makes flat states explicit and avoids interpolating decisions with misleading smooth exposure paths.')
    # Existing cost assumptions, fixed realized holdings; no policy optimization.
    fig,ax=plt.subplots(figsize=(8.8,4.8));cost_grid=np.arange(0,51)
    sensitivity=[]
    for period,g,color in [('2025',d.loc['2025'],NET),('2026 Jan–Sep',d.loc['2026'],US)]:
        vals=[(1+g.gross_return-g.turnover*(cost/2)/10000).prod()-1 for cost in cost_grid]
        ax.plot(cost_grid,vals,color=color,lw=2,label=period)
        sensitivity.extend(dict(period=period,round_trip_bps=int(c),cumulative_return=v) for c,v in zip(cost_grid,vals))
    ax.axhline(0,color='#777',lw=1);ax.axvline(15,color='#777',ls='--',lw=1,label='Recorded 15 bps assumption')
    ax.set(title='Cost sensitivity | Fixed holdings and fixed decisions',xlabel='Round-trip trading cost at full exposure (basis points)',ylabel='Period cumulative return')
    ax.yaxis.set_major_formatter(PercentFormatter(1));clean_axis(ax);legend(ax,3)
    fig.subplots_adjust(left=.11,right=.98,bottom=.23,top=.89)
    pd.DataFrame(sensitivity).to_csv(output/'10_fixed_holdings_cost_sensitivity.csv',index=False)
    save(fig,output,'10_cost_sensitivity','How much trading friction can the strategy withstand?',
         'Counterfactual cost deductions on the exact same recorded decisions; forecast hurdles and holdings are never recalculated. This isolates cost exposure. The 2025 curve approaches zero at the recorded 15 bps assumption. These sweeps are descriptive stress tests, not a choice of the most attractive fee assumption.',
         'New fixed-holdings sensitivity avoids confusing cost-induced policy changes with pure cost drag.',placement='appendix')
    return frame


def family_and_ladder(output):
    stages=[
        ('Screening\n2021–2022',old.SCREEN,'search'),
        ('Confirmation\n2023–2024',old.CONFIRM,'search'),
        ('Frozen replication\n2025',old.FINAL,'evaluation'),
        ('Fixed extension\n2026 Jan–Sep',old.FORWARD,'evaluation'),
    ]
    tables=[]
    for _,folder,_ in stages:
        frame=csv(folder/'leaderboard.csv')
        frame['source_folder']=folder.name
        tables.append(frame)
    candidate_order=['autoregression','ridge','lasso','elastic_net','pca_ridge','hist_gradient_boosting','extra_trees']
    # Omit families that have no finite trading Sharpe in any displayed stage.
    # An undefined Sharpe is recorded in the underlying leaderboard and must
    # never be plotted as a zero-return result.
    families=[family for family in candidate_order if any(
        table.loc[table.family.eq(family),'net_sharpe'].notna().any() for table in tables
    )]
    matrix=np.full((len(families),len(stages)),np.nan);labels={}
    for j,((_,_,role),d) in enumerate(zip(stages,tables)):
        for i,family in enumerate(families):
            g=d.loc[d.family.eq(family)];finite=g.net_sharpe.dropna()
            v=finite.max() if len(finite) else np.nan
            matrix[i,j]=v
            if pd.notna(v):
                if role=='search':
                    suffix='config' if len(g)==1 else 'configs'
                else:
                    suffix='evaluated row' if len(g)==1 else 'evaluated rows'
                labels[i,j]=f'{v:+.2f}\n{len(g)} {suffix}'
            else:
                labels[i,j]='Not evaluated'
    fig,ax=plt.subplots(figsize=(10.2,5.5));cmap=plt.get_cmap('RdBu').copy();cmap.set_bad('#E8EBEF')
    bound=max(1,np.nanmax(abs(matrix)))
    im=ax.imshow(np.ma.masked_invalid(matrix),cmap=cmap,vmin=-bound,vmax=bound,aspect='auto')
    for (i,j),label in labels.items():ax.text(j,i,label,ha='center',va='center',fontsize=10,color='white' if abs(matrix[i,j])>.65*bound else '#222')
    ax.set_yticks(range(len(families)),[s.replace('_',' ').title().replace('Rff','RFF').replace('Pca','PCA') for s in families],fontsize=11)
    ax.set_xticks(range(len(stages)),[label for label,_,_ in stages])
    ax.set_title('Model search and frozen-specification evaluation | Net Sharpe',fontsize=13,pad=18)
    fig.colorbar(im,ax=ax,fraction=.035,pad=.04,label='Net Sharpe (symmetric, unclipped scale)')
    fig.subplots_adjust(left=.29,right=.94,top=.88,bottom=.16)
    save(fig,output,'11_model_family_evidence','Model families and selection stages',
         'Screening and confirmation cells show the best observed net Sharpe within each family and the number of searched configurations. The 2025 and 2026 columns are frozen-period evaluations rather than new family searches; 2026 uses one pre-2026 fit with no reselection. Grey means not evaluated. Families with no finite trading Sharpe in every displayed stage are omitted rather than represented as zero.',
         'Adds the 2026 fixed-specification extension, separates search from evaluation and removes all-undefined family rows.')
    d=csv(old.LADDER/'information_ladder_summary.csv').sort_values('ladder_order')
    labels=[f"F{i}: {s}" for i,s in enumerate(['Own history','+ Indian peers','+ U.S. services','+ Nifty 50','+ S&P 500 aggregates','+ S&P 500 constituents','+ AI capability','+ Full context'])]
    assert len(d)==len(labels)
    fig,axes=plt.subplots(1,2,figsize=(9.5,5),sharey=True)
    y=np.arange(len(d))
    for ax,values,color,title in [(axes[0],d.oos_r2_asset_mean*100,INDIA,'Forecast improvement: OOS R² (%)'),(axes[1],d.net_sharpe,US,'Trading outcome: net Sharpe')]:
        ax.hlines(y,0,values,color=color,alpha=.35);ax.scatter(values,y,color=color,s=35);ax.axvline(0,color='#999',lw=.8)
        ax.set_title(title,fontsize=11);clean_axis(ax)
    axes[0].set_yticks(y,labels,fontsize=10);axes[0].invert_yaxis()
    fig.suptitle('More information does not guarantee better forecasts or trades',fontsize=14,weight='bold')
    fig.subplots_adjust(left=.31,right=.98,bottom=.12,top=.84,wspace=.25)
    save(fig,output,'12_information_ladder','Feature progression at fixed ridge family',
         'The controlled ridge ladder in the historical 2025 period compares forecast R² against an asset-mean baseline and net Sharpe. Horizontal rows represent distinct information sets rather than a continuous parameter. This diagnoses information complexity and does not establish that the best row generalizes.',
         'Replaces steep rotated labels with aligned horizontal rows and explicit predictive/economic objectives.')


def hypothesis_figures(output):
    tests=csv(HYP/'hypothesis_tests.csv');coverage=csv(HYP/'event_coverage_by_year.csv')
    d=tests.loc[tests.hypothesis.eq('H1_US_transmission') & tests.status.eq('estimated')].copy()
    fig,ax=plt.subplots(figsize=(8.7,5.1));y=np.arange(len(d))
    for yy,row in zip(y,d.itertuples()):
        color=INDIA if row.pvalue_holm<.05 else '#8391A0'
        ax.errorbar(row.coefficient,yy,xerr=[[row.coefficient-row.ci_low],[row.ci_high-row.coefficient]],fmt='o',color=color,capsize=4)
        ax.text(.99,yy,f'p(Holm) = {row.pvalue_holm:.3f}',transform=ax.get_yaxis_transform(),ha='right',fontsize=10)
    ax.set_yticks(y,[('Full sample' if str(p)=='all' else str(p)) for p in d.period]);ax.invert_yaxis();ax.axvline(0,color='#777',ls='--')
    ax.set_xlim(-.24,.48);ax.set_title('U.S. → INDIA | Association with subsequent intraday returns',fontsize=13,pad=14)
    ax.set_xlabel('Indian return change for a one-unit U.S. return change\nConditional coefficient and pointwise 95% HAC interval')
    clean_axis(ax);fig.subplots_adjust(left=.16,right=.98,bottom=.18,top=.88)
    save(fig,output,'13_transmission_inference','Association can exist without a profitable strategy',
         'Conditional U.S.-services coefficients control for lagged Indian-cohort and Nifty50 returns. Blue denotes Holm-adjusted p < 0.05 within the declared analysis batch; intervals are pointwise. A +1% U.S. return corresponds to approximately +0.098 percentage points in the full-sample Indian intraday outcome. Annual differences are not themselves significant: the direct period-interaction test was inconclusive. This is exploratory association, not causality.',
         'Adds effect uncertainty and adjusted evidence; distinguishes association from profitable prediction.')
    # Explicit coverage chart built from the current audited event calendar.
    fig,ax=plt.subplots(figsize=(8.7,4.5));x=np.arange(len(coverage))
    years=coverage.iloc[:,0].astype(int)
    counts=coverage.event_sessions.astype(int)
    colors=[US if year==2026 and count>0 else (FLAT if count==0 else INDIA) for year,count in zip(years,counts)]
    bars=ax.bar(x,counts,color=colors,edgecolor=INDIA)
    ax.bar_label(bars,padding=4,fontsize=11)
    ax.set_xticks(x,[str(v) for v in years]);ax.set_ylim(0,max(5,int(counts.max())+4))
    for index,(count,year) in enumerate(zip(counts,years)):
        if count==0:
            ax.text(index,1,'No mapped\nevents',ha='center',color=SHORT,weight='bold',fontsize=10)
    ax.set(title='AI-release evidence | Audited official-provider calendar',ylabel='Marked Indian trading sessions')
    clean_axis(ax);fig.subplots_adjust(left=.1,right=.98,bottom=.13,top=.88)
    coverage_text=', '.join(f'{year}: {count}' for year,count in zip(years,counts))
    save(fig,output,'14_event_coverage','Why later-period event conclusions remain unresolved',
         f'Marked Indian sessions by year are {coverage_text}. The 2026 calendar now uses dated official-provider announcements through 30 September under a fixed general-purpose frontier-release rule. Same-session releases can map to one Indian session, so session counts need not equal release counts. Small annual event samples still limit power and do not establish causal effects.',
         'Uses the audited 2026 calendar and no longer labels observed zero coverage as an economic result.',placement='appendix')
    annual=[]
    for stage,folder in [('Screening',old.SCREEN),('Confirmation',old.CONFIRM),('Replication',old.FINAL),('Extension',old.FORWARD)]:
        q=parquet(folder/'strategy_ledgers.parquet')
        q=q.loc[q.config_id.eq(old.SELECTED)].copy();q['year']=pd.to_datetime(q.decision_date).dt.year
        for year,group in q.groupby('year'):
            annual.append({'stage':stage,'year':int(year),'sessions':len(group),
                           'cumulative_return':float((1+group.net_return.fillna(0)).prod()-1)})
    p=pd.DataFrame(annual).sort_values('year');p.to_csv(output/'15_annual_model_record.csv',index=False)
    stage_color={'Screening':'#7F8C9A','Confirmation':US,'Replication':SHORT,'Extension':GROSS}
    fig,ax=plt.subplots(figsize=(9.4,4.9));colors=[stage_color[s] for s in p.stage]
    bars=ax.bar(p.year.astype(str),p.cumulative_return*100,color=colors,width=.62)
    ax.bar_label(bars,labels=[f'{v:+.2%}' for v in p.cumulative_return],padding=5,fontsize=11)
    ax.axhline(0,color='#777',lw=1)
    for x in [1.5,3.5]:ax.axvline(x,color='#A7ADB4',ls='--',lw=.9)
    ax.set_ylim(min(-8,100*p.cumulative_return.min()-4),max(20,100*p.cumulative_return.max()+4))
    ax.set(title='Selected Extra Trees specification | Annual net record, 2021–Sep 2026',ylabel='Calendar-period cumulative net return (%)')
    handles=[plt.Rectangle((0,0),1,1,color=stage_color[s]) for s in stage_color]
    ax.legend(handles,list(stage_color),frameon=False,ncol=4,loc='upper left',fontsize=9)
    clean_axis(ax);fig.subplots_adjust(left=.12,right=.98,bottom=.13,top=.89)
    values=', '.join(f"{int(r.year)} {r.cumulative_return:+.2%}" for r in p.itertuples())
    save(fig,output,'15_confirmation_diagnostic','One specification across search, confirmation, replication, and extension',
         f'Annual net returns for the selected Extra Trees specification are {values}. The same configuration identifier is evaluated throughout, but each protocol stage uses its declared rolling or fixed-fit estimator. The 2021–2024 observations influenced model search and confirmation and are not holdout evidence; 2025 is a historical replication and 2026 is a retrospectively inspected fixed-specification extension through September. The wide 2025 and 2026 bootstrap Sharpe intervals prevent a stable-alpha claim.',
         'Expands the stability view to the complete 2021–September 2026 protocol and clearly separates selection-exposed years from later evaluation.',placement='main')


def gallery(output):
    blocks=[]
    for item in CATALOG:
        blocks.append(f"<section><h2>{html.escape(item['id']+' | '+item['title'])}</h2><p class='tag'>{item['placement'].upper()}</p><img src='{item['png']}'><p>{html.escape(item['caption'])}</p><p class='change'>Review: {html.escape(item['change'])}</p><a href='{item.get('svg',item['png'])}'>Vector / original</a></section>")
    (output/'index.html').write_text("<!doctype html><meta charset='utf-8'><title>DSA5205 figure review</title><style>body{max-width:1000px;margin:35px auto;font:17px/1.6 Georgia;color:#19344b;background:#f3f5f8}section{background:white;padding:26px;margin:30px 0;border-radius:8px}img{width:100%;height:auto}h1,h2{font-family:Arial}h2{font-size:22px}.tag,.change{font:14px Arial;color:#526578}</style><h1>DSA5205 — Reviewed figure pack</h1><p>Figure-only preparation. Captions distinguish canonical evaluation, development diagnostics and retrospective analysis.</p>"+''.join(blocks))
    with PdfPages(output/'figure_review.pdf') as pdf:
        for item in CATALOG:
            fig=plt.figure(figsize=(11.7,8.3));ax=fig.add_axes([.04,.23,.92,.7]);ax.imshow(plt.imread(output/item['png']));ax.axis('off')
            fig.text(.05,.96,item['id']+' | '+item['title'],fontsize=13,weight='bold',va='top')
            fig.text(.05,.19,textwrap.fill(item['caption'],125),fontsize=10,va='top',linespacing=1.4)
            pdf.savefig(fig);plt.close(fig)


def retain_importance(output):
    source=track(old.FIG/'group_importance_2025_2026.png')
    name='17_group_importance_existing.png';shutil.copy2(source,output/name)
    CATALOG.append(dict(id='17_group_importance_existing',title='Exploratory model reliance',png=name,
                        caption='Existing grouped permutation importance for the canonical model in 2025 and 2026. Positive values indicate greater prediction error after permutation. These historical artifacts use a single stock-day permutation, not repeated date-block uncertainty; values are exploratory model reliance, not causal or isolated feature contributions.',
                        change='Retained unchanged: labels and zero baseline are readable. Restrict to appendix because the historical importance estimator has limited uncertainty assessment.',placement='appendix'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='reports/publication_figure_pack_2026-11-01')
    parser.add_argument('--architecture-only',action='store_true',help='Refresh only the architecture and its catalog/hash records.')
    args=parser.parse_args();output=ROOT/args.output
    output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':13,'axes.labelsize':11,
                         'xtick.labelsize':10,'ytick.labelsize':10,'svg.fonttype':'none','pdf.fonttype':42})
    track(Path(__file__));track(ROOT/'reports/build_report_ai_capability.py')
    if args.architecture_only:
        previous=json.loads((output/'manifest.json').read_text())
        current_inputs=dict(INPUTS)
        INPUTS.update(previous['inputs']); INPUTS.update(current_inputs)
        CATALOG.extend(x for x in json.loads((output/'figure_catalog.json').read_text()) if x['id']!='01_architecture')
        architecture(output)
        CATALOG.sort(key=lambda item:item['id'])
        gallery(output)
        atomic_json_dump(CATALOG,output/'figure_catalog.json')
        previous.update(created_at_utc=datetime.now(timezone.utc).isoformat(),inputs=INPUTS,
                        content_hash=stable_object_hash(INPUTS)[:16])
        previous['files']={str(p.relative_to(output)):sha256_file(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}
        atomic_json_dump(previous,output/'manifest.json')
        print('Architecture refreshed; other statistical figures retained.')
        return
    india=load_prices(old.RAW_INDIA,old.INDIA_ASSETS);us=load_prices(old.RAW_US_SERVICES,old.US_SERVICE_ASSETS)
    d=ledgers()
    tasks=[('architecture',lambda:architecture(output)),('market context and correlations',lambda:market_figures(output,india,us)),
           ('event timeline and responses',lambda:events(output,india,us)),
           ('returns and transaction costs',lambda:cost_and_performance(output,d,india)),
           ('model-family evidence',lambda:family_and_ladder(output)),('hypothesis diagnostics',lambda:hypothesis_figures(output)),
           ('regime diagnostics',lambda:regimes(output,d)),('retained importance',lambda:retain_importance(output))]
    for name,fn in progress(tasks,description='Publication figure pack',unit='section'):fn()
    CATALOG.sort(key=lambda item:item['id'])
    gallery(output)
    atomic_json_dump(CATALOG,output/'figure_catalog.json')
    content_hash=stable_object_hash(INPUTS)[:16]
    atomic_json_dump({'status':'complete','created_at_utc':datetime.now(timezone.utc).isoformat(),'content_hash':content_hash,
                      'inputs':INPUTS,'figure_count':len(CATALOG),'canonical_config':old.SELECTED,
                      'files':{str(p.relative_to(output)):sha256_file(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}},output/'manifest.json')
    print(json.dumps({'status':'complete','directory':str(output),'figures':len(CATALOG),'content_hash':content_hash},indent=2))


if __name__=='__main__':main()
