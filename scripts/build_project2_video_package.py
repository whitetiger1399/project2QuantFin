#!/usr/bin/env python3
"""Build the synchronized 20-minute DOCX/Markdown video materials; never fit models."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import pandas as pd
from PIL import Image
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/video'
PACK=ROOT/'reports/publication_figure_pack_v2_2026-11-01'
REGISTRY=ROOT/'reports/releases/project2_team16_v2_2026-11-01/release_registry.json'
CONTENT=ROOT/'documents/video_presentation_content.py'
NAVY='142D4E';MUTED='59677A';ORANGE='B35A15'
WORDS=re.compile(r"\b[\w]+(?:['’-][\w]+)*\b")


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def clock(seconds):return f'{seconds//60:02d}:{seconds%60:02d}'
def load():
    spec=importlib.util.spec_from_file_location('video_content',CONTENT)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    authors=sorted(json.loads((ROOT/'assets/authors.json').read_text()),key=lambda a:a['name'].casefold())
    assert len(authors)==4 and len(module.SCENES)==16
    t=0
    for i,s in enumerate(module.SCENES,1):
        s.update(number=i,start=t,end=t+s['seconds'],words=len(WORDS.findall(s['say'])))
        s['narration_seconds']=math.ceil(s['words']/120*60)
        s['visual_seconds']=s['seconds']-s['narration_seconds']
        assert s['visual_seconds']>=0,(i,'Narration exceeds slot')
        assert i!=16 or s['visual_seconds']>=20,'Preserve final 20-second buffer'
        t=s['end']
    assert t==1200
    assert all(sum(s['seconds'] for s in module.SCENES if s['speaker']==j)==300 for j in range(4))
    return module,authors


def figures():
    plt.rcParams.update({'font.family':'Times New Roman','font.size':16})
    fig,ax=plt.subplots(figsize=(15,5.0));ax.set(xlim=(0,15),ylim=(0,5));ax.axis('off')
    def box(x,y,w,h,title,body,size=16):
        ax.add_patch(Rectangle((x,y),w,h,fc='white',ec='black',lw=1.6))
        ax.text(x+w/2,y+h-.14,title,va='top',ha='center',weight='bold',fontsize=size)
        ax.text(x+w/2,y+h-.61,body,va='top',ha='center',fontsize=14,linespacing=1.3)
    def arrow(x,y,u,v):ax.add_patch(FancyArrowPatch((x,y),(u,v),arrowstyle='-|>',mutation_scale=18,lw=1.5,color='black'))
    box(.05,3.42,2.9,1.15,'INDIA','Own history · IT peers\nNifty 50')
    box(.05,2.01,2.9,1.15,'UNITED STATES','IT services · technology\nS&P 500')
    box(.05,.60,2.9,1.15,'ECONOMIC + AI','Rates · FX · global context\nDated AI releases')
    for y in [1.17,2.58,4.0]:arrow(2.95,y,3.30,2.60)
    box(3.35,1.30,2.30,2.55,'08:55 IST','Availability gate\n\nLags · momentum\nVolatility · peers',15)
    arrow(5.65,2.60,6.0,2.60)
    box(6.05,1.30,2.55,2.55,'FIT + VALIDATE','Past-only transforms\nScheduled refits\n\nResearch selection:\nScreen → confirm → freeze',15)
    arrow(8.60,2.60,8.95,2.60)
    box(9.0,1.30,2.15,2.55,'FORECAST','Each Nifty IT stock\n\nExpected same-day\nopen-to-close return',15)
    arrow(11.15,2.60,11.50,2.60)
    box(11.55,1.30,3.38,2.55,'CHOOSE A POSITION','LONG > +15 bps\nFLAT within ±15 bps\nSHORT < −15 bps\n\nCap exposure; close daily',15)
    ax.text(8.98,.74,'Gross return − turnover costs = net return',ha='center',weight='bold',fontsize=18)
    ax.text(8.98,.30,'Compare with Nifty IT, Nifty 50 and fixed-cohort buy-and-hold',ha='center',fontsize=14)
    fig.tight_layout(pad=.4);fig.savefig(OUT/'video_architecture.png',dpi=200);fig.savefig(OUT/'video_architecture.pdf');plt.close(fig)
    d=pd.read_csv(PACK/'07_cost_accounting.csv')
    fig,ax=plt.subplots(figsize=(10,4.1));x=range(len(d))
    ax.bar([v-.18 for v in x],d.gross*100,.34,label='Gross: identical trades',color='#16887B')
    ax.bar([v+.18 for v in x],d.net*100,.34,label='Net: after recorded costs',color='#173E62')
    for i,row in d.iterrows():
        for dx,key in [(-.18,'gross'),(.18,'net')]:
            v=row[key]*100;ax.text(i+dx,v+(1.1 if v>=0 else -1.4),f'{v:+.2f}%',ha='center',va='bottom' if v>=0 else 'top',fontsize=15)
    ax.set_xticks(list(x),d.period);ax.set_ylim(-12,43);ax.set_ylabel('Compounded period return (%)')
    ax.axhline(0,color='#555',lw=.8);ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True)
    ax.legend(loc='upper left',fontsize=13,frameon=False);ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(OUT/'video_costs.png',dpi=200);fig.savefig(OUT/'video_costs.pdf');plt.close(fig)


def font(run,size=None,bold=False,color='111111'):
    run.font.name='Times New Roman';run.font.bold=bold;run.font.color.rgb=RGBColor.from_string(color)
    if size:run.font.size=Pt(size)
    for k in ['ascii','hAnsi','eastAsia','cs']:run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:'+k),'Times New Roman')
    return run


def para(doc,text='',size=20,bold=False,color='111111',align=None,after=8):
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(after)
    p.paragraph_format.space_before=Pt(0);p.paragraph_format.line_spacing=1.08
    if align is not None:p.alignment=align
    font(p.add_run(text),size,bold,color);return p


def setup(title):
    # compact_reference_guide with explicit screen-deck overrides from the sample.
    d=Document();s=d.sections[0];s.page_width=Inches(13+1/3);s.page_height=Inches(7.5)
    for edge in ['top_margin','bottom_margin','left_margin','right_margin']:setattr(s,edge,Inches(.45))
    s.header_distance=Inches(.15);s.footer_distance=Inches(.15)
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption','List Bullet']:
        st=d.styles[name];st.font.name='Times New Roman';st.font.size=Pt(18)
        st.paragraph_format.space_before=Pt(0);st.paragraph_format.space_after=Pt(6)
        st.paragraph_format.line_spacing=1.08;st.paragraph_format.keep_with_next=False
        st.paragraph_format.keep_together=False
    h=s.header.paragraphs[0];font(h.add_run('DSA5205 · PROJECT 2 · TEAM 16'),10,color=MUTED)
    f=s.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    font(f.add_run('NUS · Team 16  |  '),10,color=MUTED)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');f._p.append(field)
    d.core_properties.title=title;d.core_properties.author='Project2 Teams 16'
    d.core_properties.subject='20-minute recorded presentation; prepared 2 November 2026'
    return d


def picture(doc,path,max_width=12.1,max_height=4.2):
    with Image.open(path) as im:w,h=im.size
    width=min(max_width,max_height*w/h)
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after=Pt(4);p.paragraph_format.line_spacing=1
    p.add_run().add_picture(str(path),width=Inches(width))
    doc.inline_shapes[-1]._inline.docPr.set('descr',Path(path).stem.replace('_',' '))


def table(doc,headers,rows,widths,size=18):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
    total=round(sum(widths)*1440);pr=t._tbl.tblPr
    pr.find(qn('w:tblW')).set(qn('w:w'),str(total));pr.find(qn('w:tblW')).set(qn('w:type'),'dxa')
    ind=OxmlElement('w:tblInd');ind.set(qn('w:w'),'120');ind.set(qn('w:type'),'dxa');pr.append(ind)
    for col,w in zip(t.columns,widths):col.width=Inches(w)
    for row in [headers,*rows]:
        cells=t.rows[0].cells if row is headers else t.add_row().cells
        for i,(cell,val) in enumerate(zip(cells,row)):
            cell.width=Inches(widths[i]);cell._tc.get_or_add_tcPr().find(qn('w:tcW')).set(qn('w:w'),str(round(widths[i]*1440)))
            tc=cell._tc.get_or_add_tcPr();mar=OxmlElement('w:tcMar')
            for name,value in [('top',70),('bottom',70),('start',120),('end',120)]:
                e=OxmlElement('w:'+name);e.set(qn('w:w'),str(value));e.set(qn('w:type'),'dxa');mar.append(e)
            tc.append(mar);p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(4);p.paragraph_format.line_spacing=1.08
            font(p.add_run(str(val)),size,row is headers,NAVY if row is headers else '111111')
            if row is headers:
                shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EDF0F4');tc.append(shade)
    for grid,w in zip(t._tbl.tblGrid,widths):grid.set(qn('w:w'),str(round(w*1440)))
    rp=t.rows[0]._tr.get_or_add_trPr();rp.append(OxmlElement('w:tblHeader'))
    return t


def deck(module,authors):
    d=setup('Cross-Market Forecasting and Signed Trading of Nifty IT Stocks — Video Deck')
    for i,s in enumerate(module.SCENES):
        if i:d.add_page_break()
        if s['kind']=='cover':
            para(d,s['title'],30,True,NAVY,WD_ALIGN_PARAGRAPH.CENTER,12)
            picture(d,ROOT/'assets/nus_logo_full-vertical.jpg',max_width=1.15,max_height=1.55)
            para(d,'Data Science in Quantitative Finance DSA5205',21,True,align=WD_ALIGN_PARAGRAPH.CENTER,after=3)
            para(d,'Project2 Teams 16',20,True,align=WD_ALIGN_PARAGRAPH.CENTER,after=8)
            for a in authors:para(d,f"{a['name']}  ·  {a['student_id']}",18,align=WD_ALIGN_PARAGRAPH.CENTER,after=4)
            para(d,'Information, complexity and post-cost daily trading',19,color=MUTED,align=WD_ALIGN_PARAGRAPH.CENTER,after=5)
            para(d,'2 November 2026 · github.com/whitetiger1399/project2QuantFin',13,color=MUTED,align=WD_ALIGN_PARAGRAPH.CENTER)
            continue
        para(d,f"{s['number']:02d}  ·  {s['title']}",27,True,NAVY,after=10)
        if s.get('figure'):
            p=OUT/s['figure'] if s['figure'].startswith('video_') else PACK/s['figure']
            picture(d,p,max_height=4.35 if s['kind']!='architecture' else 4.5)
            if s['number']==13:
                para(d,'2025: −4.04% net · Sharpe −0.26     |     2026 Jan–Sep: +15.01% net · Sharpe 1.46',17,after=5)
                para(d,'Both Sharpe uncertainty intervals include zero. Passive comparators hold overnight; the model closes daily.',14,after=5)
            if s['number']==14:
                para(d,'434 sessions: 14 long · 113 short · 307 flat · 0 mixed long/short',17,True,after=5)
        elif s['kind'] in ['hypotheses','verdicts']:
            rows=[(p.split(':',1)[0],p.split(':',1)[1].strip()) if ':' in p else (p[:2],p[4:]) for p in s['points']]
            table(d,['ID','Research claim' if s['kind']=='hypotheses' else 'Finding'],rows,[.70,11.7],18)
        else:
            for p in s.get('points',[]):para(d,p,22,after=17)
            if s['kind']=='sources':para(d,'Coforge · HCLTech · Infosys · LTIMindtree · Mphasis · OFSS · Persistent · TCS · Tech Mahindra · Wipro',16,color=MUTED,after=10)
        para(d,s['takeaway'],17,True,NAVY,after=5)
        para(d,'Source: '+s['source'],10,color=MUTED,after=0)
    for title,key,takeaway in [
        ('Supporting figure · U.S. services and Indian IT','05_cross_market_correlations.png','Completed U.S. returns versus the following eligible Indian open-to-close return. Small descriptive correlations are not causal evidence.'),
        ('Supporting figure · mapped frontier-event reactions','06b_event_responses.png','U.S. close-to-close and Indian open-to-close outcomes have different horizons. This is a limited mapped event subset, not all 2026 releases.'),
        ('Supporting figure · rising, sideways and falling markets','16_regime_distributions.png','Retrospective monthly regimes: rising ≥3%, falling ≤−3%, otherwise sideways. Reversal groups are small; these are descriptive outcomes, not trading signals.'),
    ]:
        d.add_page_break();para(d,title,27,True,NAVY)
        picture(d,PACK/key,max_height=4.5)
        para(d,takeaway,16,True,NAVY)
        para(d,'Reference appendix only · outside the timed 16-slide recording · source: report and pinned publication figure pack',11,color=MUTED)
    d.add_page_break();para(d,'Reference appendix · not part of the timed recording',27,True,NAVY)
    table(d,['Source','What to verify and where'],[(label,detail+'\n'+path) for label,path,detail in module.REFERENCES],[2.7,9.7],15)
    para(d,'Full source links, event records and run identifiers: report References and Appendices A/E. Commands and source hashes: recording_commands.md and package_manifest.json.',14,color=MUTED)
    d.save(OUT/'Project2_Team16_Video_Deck.docx')


def slide_cue(s):
    return f"SHOW VIDEO DECK SLIDE {s['number']:02d}  ·  PDF PAGE {s['number']:02d}"


def screen_directions(s):
    cue=f"Start on deck slide {s['number']:02d}: {s['title']}.\n\n"+s['show']
    if s['kind']=='demo':
        cue+=f"\n\nSwitch from slide {s['number']:02d} to the terminal for the demonstration, then return to slide {s['number']:02d}."
    if s['number']<16:
        cue+=f"\n\nAt {clock(s['end'])}, advance to video deck slide {s['number']+1:02d}."
    else:
        cue+='\n\nFinish on video deck slide 16. Do not advance into the reference appendix during the timed recording.'
    return cue


def script(module,authors):
    d=setup('Team 16 — Timed Video Script and Screen Directions')
    para(d,'Video Script and Recording Plan',32,True,NAVY)
    para(d,'20:00 maximum · 16 timed scenes · four five-minute sections',23,True)
    para(d,'Read only “Spoken narration” aloud. Every scene explicitly names the video deck slide and PDF page to show. Match its title before speaking. Screen directions, slide cues, sources and production notes are not spoken.',19)
    para(d,'Rehearse at about 120 words per minute. The schedule includes graph tracing, terminal footage and handovers. Narration ends by 19:40; the final 20 seconds are a production buffer. Actual speech varies: measure a rehearsal and shorten pauses before changing the script.',18)
    table(d,['Presenter','Recording role','Time'],[(a['name'],role,time) for a,role,time in zip(authors,['Question, architecture, hypotheses','Data, timing, features, protocol','Model, backtest, recorded execution','Results, costs, verdicts, lessons'],['00:00–05:00','05:00–10:00','10:00–15:00','15:00–20:00'])],[3.1,6.5,2.8],16)
    para(d,'These are proposed video roles, not a claim about each member’s historical implementation contribution.',14,color=MUTED)
    total=sum(s['words'] for s in module.SCENES)
    para(d,f'Exact narration count: {total:,} words under the package’s declared word-count rule. Conservative per-scene narration at 120 wpm: {clock(sum(s["narration_seconds"] for s in module.SCENES))}; the rest of the 20-minute timeline is planned visual time and transitions.',16,True,NAVY)
    for s in module.SCENES:
        heading=para(d,f"{s['number']:02d}  ·  {s['title']}",25,True,NAVY)
        heading.paragraph_format.page_break_before=True
        para(d,f"{clock(s['start'])}–{clock(s['end'])}  |  {authors[s['speaker']]['name']}  |  {s['words']} spoken words  |  {s['visual_seconds']} seconds for visuals / transitions at 120 wpm",13,color=MUTED,after=10)
        para(d,slide_cue(s),15,True,NAVY,after=7)
        t=table(d,['Spoken narration — read aloud','Screen directions — do not read'],[(s['say'],screen_directions(s))],[8.10,4.30],16)
        # Different reading scales for the two synchronized columns.
        for run in t.cell(1,1).paragraphs[0].runs:font(run,14,color=MUTED)
        para(d,'Key message: '+s['takeaway'],15,True,NAVY,after=5)
        para(d,'Source: '+s['source'],11,color=MUTED)
    heading=para(d,'Production checklist and requirement check',28,True,NAVY)
    heading.paragraph_format.page_break_before=True
    notes=[
      'The assignment requires 15–25 minutes and an end-to-end run. It does not require real trading, a live account, or an unedited multi-hour fit. Record genuine execution; label accelerated waits and cuts.',
      'Use recording_commands.md D1–D5. Plan-only output and saved artifacts are supporting evidence, not proof of a fresh training run. Capture launch, visible progress, successful completion and dated outputs.',
      'Backtest verified in code: forecast threshold, signed weights, intraday square-off, two-sided turnover, transaction costs, daily compounding and annualized metrics. See recording_evidence.py for a read-only ledger and date check.',
      'Disclose limits: public fills; incomplete taxes/borrow/impact; fixed-current-member cohort; macro vintages; previously inspected evaluation periods; different refit schedules; ETF overnight exposure; sparse retrospective AI events.',
      'Run no commands automatically while recording. Prepare readable terminals and outputs, disable notifications, hide credentials, and keep the script on the second screen. Keep required steps in the final cut.',
      'Render deck at one screen page per slide. Spoken segments end at 05:00, 10:00, 15:00 and no later than 19:40. Final MP4 must stop by 20:00. Unspoken reference appendix is for review only.',
      'Submission: Group_16_Report.pdf, one MP4 or accessible downloadable link, and code ZIP or GitHub URL. Confirm the Canvas group number/name before naming the submission; include all four authors. Deadline: 12 November 2026, 23:59 SGT.',
    ]
    for n in notes:para(d,n,16,after=12)
    d.save(OUT/'Project2_Team16_Video_Script.docx')


def markdown(module,authors):
    deck_lines=['# Cross-Market Forecasting and Signed Trading of Nifty IT Stocks','',
      'Data Science in Quantitative Finance DSA5205 · Project2 Teams 16','',
      'Format: 960 × 540 pt (16:9), matching the supplied old-project PDF. Recording: 20:00 maximum.','',
      '![NUS logo](../../assets/nus_logo_full-vertical.jpg)','']
    deck_lines.extend(f"- {a['name']} · {a['student_id']}" for a in authors)
    script_lines=['# Team 16 — video script and screen directions','',
      'Read only the narration aloud. All 16 scene numbers match deck pages. Four presenters have five minutes each. The last 20 seconds are a production buffer; end speech by 19:40.','',
      'Timing is a rehearsal/editing budget, not a guarantee from word count. Rehearse at about 120 wpm; preserve graph-reading time and label accelerated genuine execution. See recording_commands.md for the required demonstration.','']
    for s in module.SCENES:
        heading=f"{s['number']:02d} · {s['title']}"
        deck_lines+=['---','',f'## {heading}','',f"{clock(s['start'])}–{clock(s['end'])} · {authors[s['speaker']]['name']}",'']
        if s.get('figure'):
            path=s['figure'] if s['figure'].startswith('video_') else '../publication_figure_pack_v2_2026-11-01/'+s['figure']
            deck_lines += [f"![{s['title']}]({path})",'']
        if s.get('points'):deck_lines += ['- '+p for p in s['points']]+['']
        if s['number']==13:deck_lines += ['2025: −4.04% net; Sharpe −0.26. 2026 Jan–Sep: +15.01% net; Sharpe 1.46.','', 'Both Sharpe uncertainty intervals include zero. Passive comparators hold overnight; the model closes daily.','']
        if s['number']==14:deck_lines += ['434 sessions: 14 long · 113 short · 307 flat · 0 mixed long/short','']
        deck_lines += ['**Key message:** '+s['takeaway'],'','Source: '+s['source'],'']
        script_lines += [f'## {heading}','',f"**{clock(s['start'])}–{clock(s['end'])} · {authors[s['speaker']]['name']} · {s['words']} spoken words**",'',
          '**'+slide_cue(s)+'**','', '**Deck title:** '+s['title'],'',
          '### Spoken narration','',s['say'],'','### Screen directions — not spoken','',screen_directions(s),'',f"Narration allowance at 120 wpm: {s['narration_seconds']} s; visual/transition allowance: {s['visual_seconds']} s.",'', 'Source: '+s['source'],'']
    deck_lines+=['---','','## Supporting figures — outside timed recording','',
       '![Decision-aligned U.S.–India services correlations](../publication_figure_pack_v2_2026-11-01/05_cross_market_correlations.png)','',
       'Descriptive correlation of completed U.S. returns with following eligible Indian intraday returns.','',
       '![Mapped frontier event reactions](../publication_figure_pack_v2_2026-11-01/06b_event_responses.png)','',
       'U.S. and Indian outcome horizons differ. Limited mapped subset; not all 2026 events.','',
       '![Retrospective regime outcomes](../publication_figure_pack_v2_2026-11-01/16_regime_distributions.png)','',
       'Small retrospective monthly groups; these labels are not trading signals.','',
       '## Reference appendix — outside timed recording','']
    for label,path,detail in module.REFERENCES:deck_lines += [f'- {label}: {detail}. {path}']
    script_lines+=['## Production notes — not spoken','',
      'The assignment explicitly requires data build → fit → validation → evaluation with costs. Record real launches and completion, accelerate waiting with an on-screen label, and use the saved report results only as the named historical evidence. A plan-only call is not a model fit.','',
      'Own-code backtesting is implemented in src/quantfin/cross_market/experiments.py. The assignment’s backtesting libraries are illustrative. See recording_commands.md and recording_evidence.py for concrete steps.','',
      'Use the fixed timing schedule in timing.csv. A word is a match of the Unicode regex recorded in package_manifest.json; headings and directions are excluded. Presenter allocations describe the proposed video roles only.','']
    (OUT/'Project2_Team16_Video_Deck.md').write_text('\n'.join(deck_lines)+'\n')
    (OUT/'Project2_Team16_Video_Script.md').write_text('\n'.join(script_lines)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--finalize',action='store_true',help='Hash all final formats after rendering PDFs')
    parser.add_argument('--script-only',action='store_true',help='Update narration documents and Markdown without changing deck artwork or DOCX')
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    module,authors=load()
    if not args.finalize:
        if not args.script_only:
            figures();deck(module,authors)
        script(module,authors);markdown(module,authors)
        pd.DataFrame([{'slide':s['number'],'title':s['title'],'presenter':authors[s['speaker']]['name'],
           'start':clock(s['start']),'end':clock(s['end']),'seconds':s['seconds'],'spoken_words':s['words'],
           'narration_seconds_at_120_wpm':s['narration_seconds'],'visual_transition_seconds':s['visual_seconds']} for s in module.SCENES]).to_csv(OUT/'timing.csv',index=False)
    paths=[ROOT/'documents/markdown/Project2.md',ROOT/'reports/Project2_Team16_Report.docx',ROOT/'assets/authors.json',
       ROOT/'assets/old_project/A0355860X_video_deck.pdf',ROOT/'assets/old_project/video_deck.md',ROOT/'assets/old_project/video_script.md',
       CONTENT,Path(__file__),ROOT/'documents/markdown/VIDEO_SCRIPT_DECK_GAP_ANALYSIS_2026-11-02.md',ROOT/'src/quantfin/cross_market/experiments.py',REGISTRY,PACK/'manifest.json',PACK/'07_cost_accounting.csv',
       ROOT/'scripts/recording_evidence.py',OUT/'recording_commands.md']
    paths += [PACK/s['figure'] for s in module.SCENES if s.get('figure') and not s['figure'].startswith('video_')]
    paths += [PACK/p for p in ['05_cross_market_correlations.png','06b_event_responses.png','16_regime_distributions.png']]
    files=[p for p in OUT.iterdir() if p.is_file() and p.name!='package_manifest.json']
    if args.finalize:
        for stem in ['Project2_Team16_Video_Deck','Project2_Team16_Video_Script']:
            for ext in ['docx','pdf','md']:assert (OUT/f'{stem}.{ext}').is_file()
        for stem in ['Project2_Team16_Video_Deck','Project2_Team16_Video_Script']:
            d=Document(OUT/(stem+'.docx'));s=d.sections[0]
            assert abs(s.page_width/Inches(1)-13-1/3)<.001 and abs(s.page_height/Inches(1)-7.5)<.001
        script_doc=Document(OUT/'Project2_Team16_Video_Script.docx')
        script_text='\n'.join(p.text for p in script_doc.paragraphs)
        script_md=(OUT/'Project2_Team16_Video_Script.md').read_text()
        deck_doc=Document(OUT/'Project2_Team16_Video_Deck.docx')
        deck_titles={p.text for p in deck_doc.paragraphs}
        for scene in module.SCENES:
            assert script_text.count(slide_cue(scene))==1 and script_md.count(slide_cue(scene))==1,'Missing or duplicate slide cue'
            expected=scene['title'] if scene['number']==1 else f"{scene['number']:02d}  ·  {scene['title']}"
            assert expected in deck_titles,'Deck title changed without synchronized script rebuild: '+expected
    manifest={'status':'complete' if args.finalize else 'awaiting_pdf_render','created_at_utc':datetime.now(timezone.utc).isoformat(),
      'source_hash':hashlib.sha256(''.join(digest(p) for p in paths).encode()).hexdigest(),
      'client_date':'2026-11-02','format_points':[960,540],'timed_slides':16,'seconds':1200,'speaking_rate_wpm':120,
      'spoken_words':sum(s['words'] for s in module.SCENES),'word_count_regex':WORDS.pattern,
      'total_narration_seconds_at_120_wpm':sum(s['narration_seconds'] for s in module.SCENES),
      'final_buffer_seconds':20,'speaker_seconds':{a['name']:300 for a in authors},
      'model_training_performed':False,'design_preset':'compact_reference_guide',
      'named_overrides':{'page':'16:9 sample screen, 13⅓ × 7½ in','margins_in':.45,'font':'Times New Roman','body':'deck 22pt, script 16pt','headers':'10pt','table_indent_dxa':120,'line_spacing':1.08},
      'inputs':{str(p.relative_to(ROOT)):digest(p) for p in dict.fromkeys(paths)},
      'outputs':{p.name:digest(p) for p in files}}
    (OUT/'package_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['status','seconds','spoken_words','total_narration_seconds_at_120_wpm','speaker_seconds']},indent=2))


if __name__=='__main__':main()
