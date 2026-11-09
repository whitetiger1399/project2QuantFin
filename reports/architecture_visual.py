"""Report-native architecture with sourced brand marks and vector process icons."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon


def _legacy_architecture():
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
    text(.93,6.88,'Last completed U.S. session • timestamps • clean bars • missingness • availability flags',10.1)
    text(.93,6.65,'Strict-vintage audit complete · 60 flagged features excluded · 0 retained',8.4,teal,True)
    text(5.25,6.31,'OFFLINE FIT AND SELECTION',9.2,color='#526575',bold=True,ha='center')
    arrow(2.57,6.49,2.57,6.17)
    card(.05,4.91,5.05,1.22,blue);icon(.25,5.72,'features',blue)
    text(.93,5.98,'FEATURE ENGINEERING',11.7,blue,True)
    text(.25,5.52,'Lags · momentum · volatility · peer signals\nFit transformations inside each training window',10.7)
    card(5.40,4.91,5.05,1.22,navy);icon(5.62,5.72,'model')
    text(6.30,5.98,'MODELS + VALIDATION',11.7,navy,True)
    text(5.60,5.52,'2021–22 screen → 2023–24 confirm → freeze\n2025 quarterly refits → 2026 fixed fit',10.5)
    arrow(5.13,5.52,5.36,5.52)
    arrow(7.92,4.88,7.92,4.58)
    card(.05,3.84,10.40,.70,navy,'#EAF2FA')
    text(.25,4.42,'DAILY INFERENCE',8.8,color='#526575',bold=True)
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


def _compact_architecture():
    """Monochrome process view; detailed audit results belong in report prose."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set(xlim=(0, 10), ylim=(0, 5.5)); ax.axis('off')
    def box(x,y,w,h,title,body):
        ax.add_patch(Rectangle((x,y),w,h,facecolor='white',edgecolor='black',linewidth=1.15))
        ax.text(x+w/2,y+h-.16,title,ha='center',va='top',fontsize=11,weight='bold',color='black')
        ax.text(x+w/2,y+h-.47,body,ha='center',va='top',fontsize=10,color='#222',linespacing=1.4)
    def arrow(x,y,u,v):
        ax.annotate('',xy=(u,v),xytext=(x,y),arrowprops=dict(arrowstyle='-|>',color='black',lw=1.15))
    def symbol(x,y,kind):
        # Dedicated icon space above the text; no badges overlay box labels.
        if kind in ('India','US'):
            if kind=='India':
                for j,c in enumerate(['#138808','white','#FF9933']):
                    ax.add_patch(Rectangle((x,y+j*.055),.29,.055,fc=c,ec='none'))
                ax.add_patch(Circle((x+.145,y+.0825),.024,fc='none',ec='#000080',lw=.6))
            else:
                for j in range(13):ax.add_patch(Rectangle((x,y+j*.165/13),.29,.165/13,fc='#B22234' if j%2==0 else 'white',ec='none'))
                ax.add_patch(Rectangle((x,y+.08),.13,.085,fc='#3C3B6E',ec='none'))
                for j in range(3):
                    for k in range(4):ax.plot(x+.02+k*.028,y+.095+j*.025,'.',color='white',ms=.5)
        elif kind=='bank':
            ax.add_patch(Polygon([(x,y+.12),(x+.15,y+.23),(x+.30,y+.12)],fc='black'))
            for dx in [.04,.13,.22]:ax.add_patch(Rectangle((x+dx,y),.04,.12,fc='black'))
            ax.plot([x,x+.30],[y-.02,y-.02],color='black',lw=1)
        elif kind=='clock':
            ax.add_patch(Circle((x+.12,y+.10),.11,fc='white',ec='black',lw=1))
            ax.plot([x+.12,x+.12,x+.19],[y+.18,y+.10,y+.06],color='black',lw=1)
        elif kind=='model':
            for dx,dy in [(0,0),(0,.2),(.30,0),(.30,.2)]:
                ax.plot([x+.15,x+dx],[y+.1,y+dy],color='black',lw=.8)
                ax.add_patch(Circle((x+dx,y+dy),.03,fc='black'))
            ax.add_patch(Circle((x+.15,y+.1),.035,fc='black'))
        else:
            ax.plot([x,x+.07,x+.16,x+.29],[y,y+.12,y+.06,y+.22],color='black',lw=1.3)
    box(.1,4.25,3.05,1.1,'INDIAN MARKET','Nifty IT own history and peers\nNifty 50 context')
    box(3.48,4.25,3.05,1.1,'U.S. MARKET','IT services and technology\nS&P 500 context')
    box(6.85,4.25,3.05,1.1,'ECONOMIC & AI CONTEXT','Rates, FX and global indicators\nDated frontier-model releases')
    for x in [1.62,5,8.38]: arrow(x,4.25,x,3.91)
    box(.1,2.95,9.8,.94,'08:55 IST: ALIGN INPUTS AND BUILD FEATURES',
        'Available history → lags, momentum, volatility and peer signals')
    arrow(2.38,2.95,2.38,2.62)
    box(.1,1.65,4.55,.94,'FIT AND VALIDATE THROUGH TIME',
        'Past-only preprocessing · rolling fits\nScreen → confirm → freeze specification')
    box(5.05,1.65,4.85,.94,'FORECAST EACH NIFTY IT STOCK',
        'Expected open-to-close return\nApply the frozen decision rule')
    arrow(4.65,2.12,5.05,2.12)
    arrow(7.48,1.65,7.48,1.31)
    box(.1,.13,9.8,1.14,'LONG  > +15 bps     |     FLAT  within ±15 bps     |     SHORT  < −15 bps',
        'Trade at open; close all positions at the end of the session\nCap exposure → subtract turnover costs → compare net returns with benchmarks')
    # Put icons in their own left gutter and shift titles clear of that gutter.
    titles=[t for t in ax.texts if t.get_weight()=='bold']
    for t in titles[:3]:
        x,y=t.get_position();t.set_position((x+.17,y));t.set_fontsize(9.5)
    for t in titles[4:6]:
        x,y=t.get_position();t.set_position((x+.12,y));t.set_fontsize(10)
    symbol(.23,5.01,'India');symbol(3.61,5.01,'US');symbol(6.98,4.99,'bank')
    symbol(.30,3.51,'clock');symbol(.28,2.22,'model');symbol(5.22,2.22,'chart')
    fig.subplots_adjust(left=.01,right=.99,bottom=.01,top=.99)
    return fig


def draw_architecture():
    """Publication architecture with a serif hierarchy and dedicated icon panels."""
    from matplotlib import font_manager
    font_manager.findfont('Times New Roman', fallback_to_default=False)
    fig,ax=plt.subplots(figsize=(10,7.1))
    ax.set(xlim=(0,10),ylim=(0,7.1));ax.axis('off')
    def text(x,y,label,size=12,bold=False,ha='left'):
        return ax.text(x,y,label,ha=ha,va='top',fontsize=size,
                       fontfamily='Times New Roman',weight='bold' if bold else 'normal',
                       color='black',linespacing=1.25)
    def border(x,y,w,h):
        ax.add_patch(Rectangle((x,y),w,h,fc='white',ec='black',lw=1.35))
    def arrow(x,y,u,v):
        ax.annotate('',xy=(u,v),xytext=(x,y),arrowprops=dict(arrowstyle='-|>',lw=1.4,color='black',mutation_scale=13))
    def icon(x,y,kind,w=.60,h=.60):
        a=ax.inset_axes([x,y,w,h],transform=ax.transData)
        a.set(xlim=(0,1),ylim=(0,1),aspect='equal');a.axis('off')
        if kind in ('India','US'):
            if kind=='India':
                for j,c in enumerate(['#138808','white','#FF9933']):a.add_patch(Rectangle((.02,.20+j*.20),.96,.20,fc=c,ec='none'))
                a.add_patch(Circle((.5,.5),.082,fill=False,ec='#000080',lw=.7))
                for t in np.linspace(0,2*np.pi,24,endpoint=False):a.plot([.5,.5+.08*np.cos(t)],[.5,.5+.08*np.sin(t)],color='#000080',lw=.3)
            else:
                for j in range(13):a.add_patch(Rectangle((.02,.20+j*.60/13),.96,.60/13,fc='#B22234' if j%2==0 else 'white',ec='none'))
                a.add_patch(Rectangle((.02,.48),.42,.32,fc='#3C3B6E',ec='none'))
                for j in range(5):
                    for k in range(6):a.plot(.055+k*.065,.515+j*.055,'*',ms=1.3,color='white')
        elif kind=='bank':
            a.add_patch(Polygon([(.08,.68),(.5,.94),(.92,.68)],fc='black'))
            for x0 in [.18,.43,.68]:a.add_patch(Rectangle((x0,.20),.13,.43,fc='black'))
            a.plot([.08,.92],[.14,.14],color='black',lw=2)
        elif kind=='clock':
            a.add_patch(Circle((.5,.5),.44,fill=False,lw=1.7))
            for t in np.linspace(0,2*np.pi,12,endpoint=False):a.plot([.5+.36*np.sin(t),.5+.41*np.sin(t)],[.5+.36*np.cos(t),.5+.41*np.cos(t)],color='black',lw=1)
            for deg,r in [(330,.32),(267.5,.23)]:
                t=np.deg2rad(deg);a.plot([.5,.5+r*np.sin(t)],[.5,.5+r*np.cos(t)],color='black',lw=1.8)
            a.add_patch(Circle((.5,.5),.035,fc='black'))
        elif kind=='model':
            for x0,x1,y0,y1 in [(.5,.22,.82,.5),(.5,.78,.82,.5),(.22,.1,.5,.18),(.22,.36,.5,.18)]:a.plot([x0,x1],[y0,y1],color='black',lw=1.3)
            for x0,y0 in [(.5,.82),(.22,.5),(.78,.5),(.1,.18),(.36,.18)]:a.add_patch(Rectangle((x0-.075,y0-.065),.15,.13,fc='white',ec='black',lw=1.2))
            a.add_patch(Circle((.78,.18),.16,fc='white',ec='black',lw=1.1))
            a.plot([.69,.76,.89],[.18,.11,.27],color='black',lw=1.4)
        elif kind=='forecast':
            a.plot([.10,.10,.95],[.92,.12,.12],color='black',lw=1)
            a.plot([.14,.27,.39,.52,.62],[.28,.44,.36,.58,.53],color='black',lw=1.8)
            a.axvline(.62,ymin=.12,ymax=.85,color='#777',ls=':',lw=.8)
            a.plot([.62,.75,.90],[.53,.65,.83],color='black',ls='--',lw=1.6)
            a.annotate('',xy=(.93,.86),xytext=(.82,.72),arrowprops=dict(arrowstyle='->',lw=1.3,color='black'))
    text(5,7.03,'Research Architecture',22,True,'center')
    text(5,6.65,'Daily cross-market information → Nifty IT forecasts → long, short or flat',12,False,'center')
    ax.plot([.1,9.9],[6.36,6.36],color='black',lw=1)
    for x,kind,title,body in [(.1,'India','Indian market','Nifty IT own history and peers\nNifty 50 context'),(3.47,'US','U.S. market','IT services and technology\nS&P 500 context'),(6.84,'bank','Economic & AI context','Rates, FX and global indicators\nDated frontier-model releases')]:
        border(x,5.02,3.06,1.12);icon(x+.12,5.43,kind,.57,.57)
        text(x+.82,5.94,title,12,True);text(x+.15,5.36,body,11)
        arrow(x+1.53,5.02,x+1.53,4.79)
    border(.1,3.74,9.8,1.00);icon(.29,3.91,'clock',.67,.67)
    text(1.17,4.55,'08:55 IST  |  Align available inputs and build features',14,True)
    text(1.17,4.18,'Past observations → lags, momentum, volatility and peer signals',12)
    arrow(2.42,3.74,2.42,3.47)
    border(.1,2.25,4.65,1.17);icon(.24,2.55,'model',.75,.75)
    text(1.13,3.24,'Fit and validate through time',13,True)
    text(1.13,2.86,'Past-only preprocessing · rolling fits\nScreen → confirm → freeze settings',11.5)
    border(5.15,2.25,4.75,1.17);icon(5.31,2.56,'forecast',.75,.75)
    text(6.20,3.24,'Forecast each Nifty IT stock',13,True)
    text(6.20,2.86,'Expected open-to-close return\nApply the frozen decision rule',11.5)
    arrow(4.75,2.83,5.15,2.83);arrow(7.52,2.25,7.52,1.98)
    border(.1,.13,9.8,1.80)
    text(5,1.77,'DAILY POSITION DECISION',13,True,'center')
    for x,title,rule in [(1.73,'LONG','Forecast > +15 bps'),(5,'FLAT','Forecast within ±15 bps'),(8.27,'SHORT','Forecast < −15 bps')]:
        text(x,1.40,title,15,True,'center');text(x,1.06,rule,12,False,'center')
    for x in [3.37,6.63]:ax.plot([x,x],[.91,1.46],color='black',lw=.8)
    ax.plot([.3,9.7],[.79,.79],color='black',lw=.8)
    text(5,.64,'Trade at open → close positions at session end → deduct transaction costs',12,False,'center')
    text(5,.35,'Cap exposure and compare net performance with passive benchmarks',11,False,'center')
    fig.subplots_adjust(left=.01,right=.99,bottom=.01,top=.99)
    return fig
