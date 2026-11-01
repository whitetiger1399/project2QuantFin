"""Report-native architecture with sourced brand marks and vector process icons."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon


def draw_architecture():
    fig, ax = plt.subplots(figsize=(10.5, 8.6))
    ax.set(xlim=(0, 10.5), ylim=(0, 10)); ax.axis('off')
    navy, blue, orange, teal, red = '#123D65', '#175B9A', '#B75B16', '#138577', '#B34155'
    icons = Path(__file__).resolve().parents[1]/'assets/architecture_icons'
    def text(x,y,s,size=11,color=navy,bold=False,ha='left'):
        ax.text(x,y,s,fontsize=size,color=color,weight='bold' if bold else 'normal',
                va='top',ha=ha,linespacing=1.35)
    def card(x,y,w,h,color,fill='#F5F8FC'):
        ax.add_patch(FancyBboxPatch((x+.025,y-.025),w,h,boxstyle='round,pad=.025,rounding_size=.09',fc='#E5EAF0',ec='none'))
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.025,rounding_size=.09',fc=fill,ec=color,lw=1.1))
    def arrow(x,y,xx,yy,color='#697F91'):
        ax.annotate('',xy=(xx,yy),xytext=(x,y),arrowprops=dict(arrowstyle='-|>',color=color,lw=1.6))
    def flag(x,y,country):
        if country=='India':
            for j,c in enumerate(['#138808','white','#FF9933']):ax.add_patch(Rectangle((x,y+j*.10),.49,.10,fc=c,ec='none'))
            ax.add_patch(Circle((x+.245,y+.15),.045,fc='none',ec='#000080',lw=.7))
            for a in np.linspace(0,2*np.pi,24,endpoint=False):ax.plot([x+.245,x+.245+.044*np.cos(a)],[y+.15,y+.15+.044*np.sin(a)],color='#000080',lw=.25)
        else:
            for j in range(13):ax.add_patch(Rectangle((x,y+j*.3/13),.49,.3/13,fc='#B22234' if j%2==0 else 'white',ec='none'))
            ax.add_patch(Rectangle((x,y+.14),.22,.16,fc='#3C3B6E',ec='none'))
            for j in range(5):
                for k in range(6):ax.plot(x+.025+k*.034,y+.158+j*.027,'.',color='white',ms=.6)
    def icon(x,y,kind,color=navy):
        if kind=='bank':
            ax.add_patch(Polygon([(x,y+.20),(x+.25,y+.37),(x+.50,y+.20)],fc=color))
            for dx in [.08,.23,.38]:ax.add_patch(Rectangle((x+dx,y-.03),.055,.22,fc=color))
            ax.plot([x,x+.50],[y-.06,y-.06],color=color,lw=2)
        elif kind=='clock':
            ax.add_patch(Circle((x+.25,y+.14),.22,fc='white',ec=color,lw=1.5))
            ax.plot([x+.25,x+.25,x+.37],[y+.30,y+.14,y+.08],color=color,lw=1.5)
        elif kind=='features':
            for dx,h in [(0,.17),(.15,.30),(.30,.43)]:ax.add_patch(Rectangle((x+dx,y-.08),.09,h,fc=color))
        elif kind=='model':
            for dx,dy in [(0,.25),(.23,.06),(.46,.25),(0,-.08),(.46,-.08)]:
                ax.plot([x+.23,x+dx],[y+.06,y+dy],color=color,lw=1)
                ax.add_patch(Circle((x+dx,y+dy),.055,fc=color))
        elif kind=='ledger':
            ax.add_patch(Rectangle((x,y-.10),.40,.45,fc='white',ec=color,lw=1.2))
            for dy in [0,.12,.24]:ax.plot([x+.07,x+.33],[y+dy,y+dy],color=color,lw=1)
    text(.05,9.96,'Daily information → expected return → signed trade',16,bold=True)
    text(.05,9.58,'Nifty IT targets  |  Daily frequency  |  Decisions before the Indian market opens',10.8)
    # Country and provider identification is separate from data-vendor attribution.
    for x,c in [(0.05,blue),(2.72,orange),(5.39,navy),(8.06,'#70549A')]:card(x,7.70,2.39,1.55,c)
    flag(.20,8.78,'India');text(.83,9.08,'INDIA',12,blue,True)
    text(.20,8.55,'NIFTY IT targets\nOwn history + IT peers\nNIFTY 50 context',10.5,blue)
    flag(2.87,8.78,'US');text(3.50,9.08,'U.S. INPUTS',11.5,orange,True)
    text(2.87,8.55,'IT services: ACN, IBM…\nTech / software\nS&P 500 universe',10.5,orange)
    icon(5.55,8.90,'bank');text(6.19,9.08,'MACRO',12,navy,True)
    text(5.55,8.55,'Fed / rate context\nFX + global indicators\nFRED / ALFRED',10.5)
    text(8.20,9.08,'AI RELEASES',11.5,'#70549A',True)
    for j,(name,label) in enumerate([('openai','OpenAI'),('anthropic','Anthropic'),('google','Google'),('gemini','Gemini')]):
        x=8.20+(j%2)*1.10; y=8.47-(j//2)*.35
        ax.imshow(plt.imread(icons/f'{name}.png'),extent=(x,x+.23,y,y+.23),aspect='auto',zorder=4)
        text(x+.29,y+.21,label,8.2)
    text(8.20,7.96,'Public release dates only',9.7,'#70549A')
    for x in [1.25,3.92,6.59,9.26]:arrow(x,7.66,x,7.32)
    card(.05,6.52,10.40,.76,navy,'#EAF2FA');icon(.25,6.87,'clock')
    text(.93,7.12,'08:55 IST  |  Information-availability gate',12,bold=True)
    text(.93,6.81,'Last completed U.S. session • timestamps • clean bars • missingness • vintage checks',10.5)
    arrow(2.57,6.49,2.57,6.17);arrow(7.92,6.49,7.92,6.17)
    card(.05,4.91,5.05,1.22,blue);icon(.25,5.72,'features',blue)
    text(.93,5.98,'FEATURE ENGINEERING',11.7,blue,True)
    text(.25,5.52,'Lags · momentum · volatility · peer signals\nFit transformations inside each training window',10.7)
    card(5.40,4.91,5.05,1.22,navy);icon(5.62,5.72,'model')
    text(6.30,5.98,'MODELS + VALIDATION',11.7,navy,True)
    text(5.60,5.52,'2021–22 screen → 2023–24 confirm → freeze\n2025 quarterly refits → 2026 fixed fit',10.5)
    arrow(2.57,4.88,2.57,4.58);arrow(7.92,4.88,7.92,4.58)
    card(.05,3.84,10.40,.70,navy,'#EAF2FA')
    text(5.25,4.40,'FORECAST EACH STOCK → CHOOSE LONG, SHORT OR FLAT',12,bold=True,ha='center')
    text(5.25,4.10,'Expected same-day open-to-close return; rank eligible stocks and cap exposure',10.7,ha='center')
    for x in [1.70,5.25,8.80]:arrow(x,3.81,x,3.48)
    for x,c,fill,title,rule,body,symbol in [
        (.05,teal,'#EAF7F2','LONG','Forecast > +15 bps','Buy open → sell close\nUp to 3 strongest eligible stocks','↑'),
        (3.60,navy,'#F0F3F7','FLAT','Inside the hurdle','No position in that stock\nNo trading cost','—'),
        (7.15,red,'#FBEFF2','SHORT','Forecast < −15 bps','Sell open → buy back close\nUp to 3 weakest eligible stocks','↓')]:
        card(x,2.12,3.30,1.32,c,fill);text(x+.18,3.29,symbol,23,c,True)
        text(x+.65,3.29,title,15,c,True);text(x+.18,2.91,rule,11,c,True)
        text(x+.18,2.69,body,10.0,c)
    for x in [1.70,5.25,8.80]:arrow(x,2.09,x,1.77)
    card(.05,.58,10.40,1.15,navy);icon(.26,1.30,'ledger')
    text(.92,1.57,'PORTFOLIO + COST LEDGER',12,bold=True)
    text(.25,1.16,'Gross return − turnover × 7.5 bps per side = net return',12,bold=True)
    text(.25,.84,'Long and short may coexist • gross exposure ≤ 1 • 15 bps round trip • square off at close',10.5)
    text(.05,.33,'Market bars: Yahoo. Brand marks identify entities, not data vendors or endorsements.',9,color='#526575')
    text(.05,.10,'Hypotheses and retrospective capability evidence are discussed separately in Sections 1 and 7.',9,color='#526575')
    return fig
