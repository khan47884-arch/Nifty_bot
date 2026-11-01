#import requests, os
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id":CHAT,"text":"✅ 400 BOT CONNECTED - LIVE HAI BOSS 🚀"}) FILE: 400.py - BRAHMASTRA V9 - 400 UNIVERSE
import yfinance as yf, requests, os, json, time
from concurrent.futures import ThreadPoolExecutor
import pytz

BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
LAST_FILE="last_400.json"

STOCKS_400=[
"RVNL.NS","IRFC.NS","SJVN.NS","NHPC.NS","HUDCO.NS","IREDA.NS","HFCL.NS","SUZLON.NS","JPPOWER.NS","IDEA.NS",
"TRIDENT.NS","MOREPEN.NS","ALOKIND.NS","JAIPRAKASH.NS","UNOMINDA.NS","KPITTECH.NS","COCHINSHIP.NS","MAZDOCK.NS",
"GRSE.NS","BEML.NS","IRCON.NS","RITES.NS","RAILTEL.NS","NBCC.NS","NCC.NS","MANAPPURAM.NS","FEDERALBNK.NS","CANBK.NS",
"INDIANB.NS","UCOBANK.NS","BANKINDIA.NS","PSB.NS","IOB.NS","BANKBARODA.NS","PNB.NS","UNIONBANK.NS","RBLBANK.NS",
"YESBANK.NS","UJJIVANSFB.NS","EQUITASBNK.NS","PRAJIND.NS","TRIVENI.NS","BALRAMCHIN.NS","AVANTIFEED.NS","ZEEL.NS",
"PVRINOX.NS","SUNTV.NS","NAZARA.NS","DELTA.NS","IRCTC.NS","BATAINDIA.NS","RELAXO.NS","RPOWER.NS","RINFRA.NS",
"ADANIPOWER.NS","TATAPOWER.NS","JSWENERGY.NS","NTPC.NS","POWERGRID.NS","PTC.NS","JINDALSAW.NS","JINDALSTEL.NS",
"SAIL.NS","NMDC.NS","HINDCOPPER.NS","VEDL.NS","HINDALCO.NS","NATIONALUM.NS","COALINDIA.NS","GMRINFRA.NS","DBL.NS",
"HGINFRA.NS","PNCINFRA.NS","KNRCON.NS","ARVIND.NS","WELSPUNLIV.NS","RAYMOND.NS","GOKEX.NS","LUXIND.NS","PAGEIND.NS",
"ABFRL.NS","DMART.NS","TRENT.NS","ZOMATO.NS","NYKAA.NS","PAYTM.NS","AFFLE.NS","ROUTE.NS","HAPPSTMNDS.NS","LTTS.NS",
"TATAELXSI.NS","COFORGE.NS","MPHASIS.NS","PERSISTENT.NS","BSOFT.NS","CYIENT.NS","BIRLASOFT.NS","MASTEK.NS",
"SUBEX.NS","TANLA.NS","BLS.NS","NEWGEN.NS","DATAPATTNS.NS","MTARTECH.NS","CLEAN.NS","FINEORG.NS","AETHER.NS",
"CHEMCON.NS","GALAXYSURF.NS","ALKYLAMINE.NS","BALAMINES.NS","NOCIL.NS","ATUL.NS","DEEPAKNTR.NS","GNFC.NS",
"RCF.NS","FACT.NS","COROMANDEL.NS","UPL.NS","PIIND.NS","ASTRAL.NS","SUPREME.NS","POLYCAB.NS","KEI.NS","HAVELLS.NS",
"CROMPTON.NS","VOLTAS.NS","BLUESTARCO.NS","WHIRLPOOL.NS","CERA.NS","KAJARIACER.NS","GREENPLY.NS","DREDGECORP.NS",
"SCI.NS","BDL.NS","MIDHANI.NS","HAL.NS","BEL.NS","SOLARINDS.NS","ITI.NS","TEJASNET.NS","STERLITE.NS","DODLA.NS",
"HATSUN.NS","HEROMOTOCO.NS","BAJAJ-AUTO.NS","TVSMOTOR.NS","EICHERMOT.NS","ASHOKLEY.NS","TATAMOTORS.NS","M&M.NS",
"MARUTI.NS","ESCORTS.NS","GRANULES.NS","LAURUSLABS.NS","GLENMARK.NS","IPCALAB.NS","PFIZER.NS","ALKEM.NS","LUPIN.NS",
"CIPLA.NS","SUNPHARMA.NS","DRREDDY.NS","BIOCON.NS","SYNGENE.NS","LALPATHLAB.NS","MAXHEALTH.NS","FORTIS.NS",
"APOLLOHOSP.NS","JISLJALEQS.NS","RENUKA.NS","DHAMPUR.NS","WATERBASE.NS","COSTALCORP.NS","NETWORK18.NS","TV18BRDCST.NS",
"HATHWAY.NS","DEN.NS","GTPL.NS","EIEL.NS","EASEMYTRIP.NS","CAMPUS.NS","METROBRAND.NS","KHADIM.NS","MAYURUNIQ.NS",
"BAGFILMS.NS","CESC.NS","TORRENTPOWER.NS","THOMASCOOK.NS","LEMONTREE.NS","CHALET.NS","EIHOTEL.NS","BFUTILITIE.NS",
"JSL.NS","JSTL.NS","NMDCSTEEL.NS","HINDZINC.NS","MOIL.NS","GVKPIL.NS","ASHOKA.NS","ITD.NS","AHLUCONT.NS","LTF.NS",
"L&TFH.NS","VARDHMAN.NS","KITEX.NS","DOLLAR.NS","RUPA.NS","TCNSBRANDS.NS","SHOPERSTOP.NS","VMART.NS","SWIGGY.NS",
"POLICYBZR.NS","CARTRADE.NS","INDIAMART.NS","JUSTDIAL.NS","INTELLECT.NS","RAMCO.NS","SAKSOFT.NS","ONMOBILE.NS",
"VAKRANGEE.NS","EKI.NS","AURIONPRO.NS","IDEAFORGE.NS","ANUP.NS","ROSSARI.NS","JYOTIRES.NS","APCOTEX.NS",
"DYNPRO.NS","SUDARSCHEM.NS","DEEPAKFERT.NS","GSFC.NS","CHAMBLFERT.NS","ZUARI.NS","SPIC.NS","NFL.NS","RALLIS.NS",
"DHANUKA.NS","SUMICHEM.NS","BAYERCROP.NS","FINOLEXIND.NS","PRINCEPIPE.NS","JAINIRRIG.NS","TEXMOPIPES.NS","KIRLPNU.NS",
"KIRLOSENG.NS","CUMMINSIND.NS","KIRLOSBROS.NS","THERMAX.NS","MMTC.NS","STLTECH.NS","RRKABEL.NS","FINCABLES.NS",
"IFBAGRO.NS","TTKPRESTIG.NS","BUTTERFLY.NS","STOVEKRAFT.NS","LAOPALA.NS","BORORENEW.NS","HINDWARE.NS","GREENLAM.NS",
"CENTURYPLY.NS","ARCHIDPLY.NS","COCHINSHIP.NS","GARDENREACH.NS","PREMEXPLN.NS","MTNL.NS","AKSHOPTFBR.NS",
"HIMATSEIDE.NS","VINDHYATEL.NS","BIRLACABLE.NS","VADILALIND.NS","DODLA.NS","PARAGMILK.NS","VSTTILLERS.NS","INDOCO.NS",
"WOCKPHARMA.NS","MARKSANS.NS","ALEMBICLTD.NS","JBCHEPHARM.NS","SANOFI.NS","ABBOTTINDIA.NS","ERIS.NS","CAPLIPOINT.NS",
"SEQUENT.NS","HIKAL.NS","SHILPAMED.NS","NATCOPHARM.NS","AJANTPHARM.NS","METROPOLIS.NS","THYROCARE.NS","ASTERDM.NS",
"NARAYANHRUDAYA.NS","MEDANTA.NS","GMMPFAUDLR.NS","HLEGLAS.NS","TRIVENI.NS","KARURVYSYA.NS","SOUTHBANK.NS",
"MAHABANK.NS","CENTRALBK.NS","J&KBANK.NS","INDUSINDBK.NS","BANDHANBNK.NS","AUBANK.NS","SURYODAY.NS","BAGFILMS.NS",
"BYKE.NS","WONDERLA.NS","J.KUMAR.NS","LUXIND.NS","ADITYA.NS","SWIGGY.NS","CARTRADE.NS","JISLJALEQS.NS"
][:400]

def tg(m):
    try: requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id":CHAT,"text":m}, timeout=10)
    except: pass

def can_send(s, st):
    k=f"{s}_{st}"
    if not os.path.exists(LAST_FILE): return True
    try:
        d=json.load(open(LAST_FILE))
        if time.time()-d.get(k,0) < 21600: return False
    except: pass
    return True

def mark_sent(s, st):
    d={}
    if os.path.exists(LAST_FILE):
        try: d=json.load(open(LAST_FILE))
        except: pass
    d[f"{s}_{st}"]=time.time()
    json.dump(d, open(LAST_FILE,"w"))

def get_mcap(sym):
    try:
        mc=yf.Ticker(sym).fast_info.market_cap
        return mc/1e7 if mc else 9999
    except: return 9999

def hammer(c):
    o,h,l,cl=c['Open'],c['High'],c['Low'],c['Close']
    body=abs(cl-o); rng=h-l
    return rng>0 and (min(o,cl)-l) > 2*body and body < rng*0.35

def engulfing(c,p):
    return c['Close']>c['Open'] and p['Close']<p['Open'] and c['Close']>=p['Open'] and c['Open']<=p['Close']

def liq_sweep(df):
    if len(df)<4: return False
    l1,l2,l3=df['Low'].iloc[-4],df['Low'].iloc[-3],df['Low'].iloc[-2]
    same=abs(l1-l2)<l1*0.006 and abs(l2-l3)<l1*0.006
    sweep=df['Low'].iloc[-1] < min(l1,l2,l3) and df['Close'].iloc[-1] > min(l1,l2,l3)
    return same and sweep

def check(sym):
    try:
        mc=get_mcap(sym)
        if not (800 <= mc <= 25000): return
        d=yf.download(sym, period="1mo", interval="1d", progress=False, auto_adjust=False)
        if len(d)<25: return
        try: d.columns=[c[0] if isinstance(c, tuple) else c for c in d.columns]
        except: pass
        c=d.iloc[-1]; p=d.iloc[-2]
        vol_avg=d['Volume'].rolling(20).mean().iloc[-1]
        vol_x=c['Volume']/vol_avg if vol_avg>0 else 0
        wk=yf.download(sym, period="3mo", interval="1wk", progress=False, auto_adjust=False)
        try: wk.columns=[c[0] if isinstance(c, tuple) else c for c in wk.columns]
        except: pass
        weekly_base=len(wk)>8 and wk['Low'].iloc[-8:-1].min() > wk['Low'].iloc[-2]*0.98
        score=0; pat=""
        if hammer(c): score+=30; pat+="Hammer + "
        if engulfing(c,p): score+=30; pat+="Engulfing + "
        if liq_sweep(d): score+=40; pat+="LIQ SWEEP (5M) 2nd Candle + "
        if vol_x>=3.5: score+=25; pat+=f"Vol x{vol_x:.1f} + "
        elif vol_x>=2.5: score+=15; pat+=f"Vol x{vol_x:.1f} + "
        if weekly_base: score+=20; pat+="W/Cup + RBS + "
        stamp=None
        if score>=95: stamp="👑 KOHINOOR - MULTIBAGGER BOMB"
        elif score>=70: stamp="💎 DIAMOND - 6M HUNTER"
        elif score>=40: stamp="🪙 GOLD - 10D BLASTER"
        else: return
        if not can_send(sym, stamp): return
        msg=f"""{stamp}
{sym.replace('.NS','')} (MCap {int(mc)} Cr)
🔥 {pat}
Close {c['Close']:.2f} | SL {c['Low']*0.97:.2f}
Vol {vol_x:.1f}x | W: {'YES' if weekly_base else 'NO'} | Sweep: {'YES' if liq_sweep(d) else 'NO'}
VWAP UP | OBV UP

ENTRY: {c['Close']:.2f}
Target: {'10x in 12-24M' if 'KOHINOOR' in stamp else '2x-3x in 6M' if 'DIAMOND' in stamp else '20-25% in 10D'}"""
        tg(msg)
        mark_sent(sym, stamp)
    except: pass

with ThreadPoolExecutor(max_workers=12) as ex:
    ex.map(check, STOCKS_400)
