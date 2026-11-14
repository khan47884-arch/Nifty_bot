import os, requests, yfinance as yf
import pandas as pd, numpy as np
from datetime import datetime
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STOCKS = {
"RELIANCE":"RELIANCE.NS","HDFCBANK":"HDFCBANK.NS","ICICIBANK":"ICICIBANK.NS","SBIN":"SBIN.NS",
"TCS":"TCS.NS","INFY":"INFY.NS","HCLTECH":"HCLTECH.NS","WIPRO":"WIPRO.NS","TECHM":"TECHM.NS",
"LTIM":"LTIM.NS","PERSISTENT":"PERSISTENT.NS","COFORGE":"COFORGE.NS","MPHASIS":"MPHASIS.NS",
"BHEL":"BHEL.NS","BEL":"BEL.NS","HAL":"HAL.NS","MAZAGON":"MAZDOCK.NS","COCHINSHIP":"COCHINSHIP.NS",
"BDL":"BDL.NS","GRSE":"GRSE.NS","PARAS":"PARAS.NS","LT":"LT.NS","TITAN":"TITAN.NS",
"ADANIENT":"ADANIENT.NS","ADANIPORTS":"ADANIPORTS.NS","ADANIGREEN":"ADANIGREEN.NS",
"ADANIENERGY":"ADANIENSOL.NS","ADANIPOWER":"ADANIPOWER.NS","TMPV":"TMPV.NS","TMCV":"TMCV.NS",
"TATASTEEL":"TATASTEEL.NS","JSWSTEEL":"JSWSTEEL.NS","JINDALSTEEL":"JINDALSTEL.NS","SAIL":"SAIL.NS",
"NMDC":"NMDC.NS","HINDALCO":"HINDALCO.NS","VEDL":"VEDL.NS","COALINDIA":"COALINDIA.NS",
"BHARTIARTL":"BHARTIARTL.NS","JIOFIN":"JIOFIN.NS","ITC":"ITC.NS","BAJAJFINSV":"BAJAJFINSV.NS",
"BAJAJFINANCE":"BAJAJFINANCE.NS","BAJAJAUTO":"BAJAJ-AUTO.NS","MARUTI":"MARUTI.NS","M&M":"M&M.NS",
"HEROMOTOCO":"HEROMOTOCO.NS","EICHERMOT":"EICHERMOT.NS","TVSMOTOR":"TVSMOTOR.NS","ASHOKLEY":"ASHOKLEY.NS",
"ONGC":"ONGC.NS","OIL":"OIL.NS","GAIL":"GAIL.NS","BPCL":"BPCL.NS","HPCL":"HPCL.NS","IOC":"IOC.NS",
"PETRONET":"PETRONET.NS","NTPC":"NTPC.NS","POWERGRID":"POWERGRID.NS","TATAPOWER":"TATAPOWER.NS",
"JSWENERGY":"JSWENERGY.NS","NHPC":"NHPC.NS","SJVN":"SJVN.NS","HUDCO":"HUDCO.NS","NBCC":"NBCC.NS",
"IRFC":"IRFC.NS","RVNL":"RVNL.NS","IRCTC":"IRCTC.NS","LIC":"LICI.NS","HDFCLIFE":"HDFCLIFE.NS",
"SBILIFE":"SBILIFE.NS","ICICIPRULI":"ICICIPRULI.NS","SHRIRAMFIN":"SHRIRAMFIN.NS","CHOLAFIN":"CHOLAFIN.NS",
"MUTHOOTFIN":"MUTHOOTFIN.NS","TRENT":"TRENT.NS","DMART":"DMART.NS","TATACONSUM":"TATACONSUM.NS",
"TATACHEM":"TATACHEM.NS","TATAELXSI":"TATAELXSI.NS","CIPLA":"CIPLA.NS","SUNPHARMA":"SUNPHARMA.NS",
"DRREDDY":"DRREDDY.NS","DIVIS":"DIVISLAB.NS","LUPIN":"LUPIN.NS","AUROPHARMA":"AUROPHARMA.NS",
"APOLLOHOSP":"APOLLOHOSP.NS","MAXHEALTH":"MAXHEALTH.NS","ZYDUSLIFE":"ZYDUSLIFE.NS",
"DABUR":"DABUR.NS","GODREJCP":"GODREJCP.NS","MARICO":"MARICO.NS","BRITANNIA":"BRITANNIA.NS",
"NESTLEIND":"NESTLEIND.NS","HINDUNILVR":"HINDUNILVR.NS","COLPAL":"COLPAL.NS","PIDILITE":"PIDILITE.NS",
"ASIANPAINT":"ASIANPAINT.NS","BERGERPAINT":"BERGERPAINT.NS","ULTRACEMCO":"ULTRACEMCO.NS","GRASIM":"GRASIM.NS",
"ETERNAL":"ETERNAL.NS","PAYTM":"PAYTM.NS","OFSS":"OFSS.NS",
}

def send(msg):
    if not TOKEN or not CHAT_ID: return
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=30)
    except Exception as e: print("TG ERR", e)

def rsi_calc(s, p=14):
    d = s.diff(); up = d.where(d>0,0); dn = -d.where(d<0,0)
    rs = up.ewm(alpha=1/p, adjust=False).mean() / dn.ewm(alpha=1/p, adjust=False).mean()
    return 100 - (100/(1+rs))

def atr_calc(df, p=14):
    h=df["High"]; l=df["Low"]; c=df["Close"]
    tr=pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/p, adjust=False).mean()

def main():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist).strftime("%d %b %Y, %I:%M %p")
    rows=[]
    for name, sym in STOCKS.items():
        try:
            df = yf.download(sym, period="1y", interval="1d", progress=False, auto_adjust=True)
            if df.empty or len(df)<210: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            c=df["Close"]; v=df["Volume"]
            close=float(c.iloc[-1]); prev=float(c.iloc[-2])
            chg1=(close-prev)/prev*100
            chg5=float((c.iloc[-1]-c.iloc[-6])/c.iloc[-6]*100)
            chg20=float((c.iloc[-1]-c.iloc[-21])/c.iloc[-21]*100)
            r=float(rsi_calc(c).iloc[-1])
            e20=float(c.ewm(span=20, adjust=False).mean().iloc[-1])
            e50=float(c.ewm(span=50, adjust=False).mean().iloc[-1])
            e200=float(c.ewm(span=200, adjust=False).mean().iloc[-1])
            roc10=float((c.iloc[-1]-c.iloc[-11])/c.iloc[-11]*100)
            roc20=float((c.iloc[-1]-c.iloc[-21])/c.iloc[-21]*100)
            ema12=c.ewm(span=12, adjust=False).mean(); ema26=c.ewm(span=26, adjust=False).mean()
            macd=ema12-ema26; sig=macd.ewm(span=9, adjust=False).mean()
            macd_val=float(macd.iloc[-1]); sig_val=float(sig.iloc[-1]); hist=macd_val-sig_val
            macd_up=macd_val>sig_val
            macd_cross= float(macd.iloc[-2])<=float(sig.iloc[-2]) and macd_up
            rvol=float(v.iloc[-1]/v.tail(20).mean()) if float(v.tail(20).mean())>0 else 0
            high52=float(c.max()); dist52=(close-high52)/high52*100
            high20=float(c.tail(20).max()); breakout=close>=high20*0.998
            atr=float(atr_calc(df).iloc[-1])
            sl=close-1.5*atr; tgt1=close+2*atr; tgt2=close+3.5*atr
            above_all=close>e20 and close>e50 and close>e200
            score=0
            if chg1>0: score+=1
            if chg5>2: score+=1
            if chg20>5: score+=1
            if 55<=r<=70: score+=2
            elif 50<r<55: score+=1
            if close>e20: score+=1
            if close>e50: score+=1
            if close>e200: score+=1
            if macd_up: score+=1
            if rvol>=1.5: score+=1
            if breakout: score+=1
            if roc10>0: score+=1
            if score>=9 and above_all and rvol>=1.2: stage="💎 PLATINUM"; tag="ADVANCE"
            elif score>=7 and close>e20 and close>e50 and macd_up: stage="🚀 ADVANCE"; tag="ADVANCE"
            elif close>e20 and 45<=r<=55 and abs(close-e20)/e20*100<2: stage="🟡 ACCUMULATION"; tag="ACCUMULATION"
            elif r>=72 and dist52>-2: stage="🟠 DISTRIBUTION"; tag="DISTRIBUTION"
            elif close<e20 and not macd_up: stage="🔴 DECLINE"; tag="DECLINE"
            else: stage="⚪ SIDEWAYS"; tag="SIDEWAYS"
            rows.append({"n":name,"cl":close,"chg":chg1,"chg5":chg5,"chg20":chg20,"rsi":r,"e20":e20,"e50":e50,"e200":e200,"roc":roc10,"roc20":roc20,"macd_up":macd_up,"cross":macd_cross,"hist":hist,"rvol":rvol,"dist52":dist52,"break":breakout,"atr":atr,"sl":sl,"t1":tgt1,"t2":tgt2,"score":score,"stage":stage,"tag":tag,"above":above_all})
        except Exception as e:
            print(sym, e); continue
    if not rows:
        send(f"⚠️ MOMENTUM PRO - {now}\nData nahi aaya."); return
    adv=sorted([x for x in rows if x["tag"]=="ADVANCE"], key=lambda x: (x["score"], x["rvol"]), reverse=True)
    acc=sorted([x for x in rows if x["tag"]=="ACCUMULATION"], key=lambda x: x["rvol"], reverse=True)
    dist=[x for x in rows if x["tag"]=="DISTRIBUTION"]
    dec=sorted([x for x in rows if x["tag"]=="DECLINE"], key=lambda x: x["chg"])
    m1=f"<b>🔥 MOMENTUM PRO - SWING - {now}</b>\n\n<b>💎 PLATINUM + 🚀 ADVANCE - Best Swing (Top 15)</b>\n"
    for x in adv[:15]:
        br="🔥BRK " if x["break"] else ""
        cr="⚡MACD-X " if x["cross"] else ""
        m1+=f"{x['stage']} {x['n']} ₹{x['cl']:.0f} ({x['chg']:+.1f}% | 5D {x['chg5']:+.1f}%) RSI {x['rsi']:.0f} ROC {x['roc']:+.1f}% RVOL {x['rvol']:.1f}x {br}{cr}Score {x['score']}/13\n SL ₹{x['sl']:.0f} | T1 ₹{x['t1']:.0f} | T2 ₹{x['t2']:.0f}\n"
    if not adv: m1+="Aaj koi ADVANCE nahi - WAIT karo\n"
    send(m1)
    m2=f"<b>🟡 ACCUMULATION - Nazar Rakho (Top 10)</b>\n"
    for x in acc[:10]:
        m2+=f"🟡 {x['n']} ₹{x['cl']:.0f} ({x['chg']:+.1f}%) RSI {x['rsi']:.0f} RVOL {x['rvol']:.1f}x 52H se {x['dist52']:.1f}%\n"
    if not acc: m2+="Koi Accumulation nahi hai\n"
    m2+=f"\n<b>🟠 DISTRIBUTION - Profit Booking</b>\n"
    for x in dist: m2+=f"🟠 {x['n']} ₹{x['cl']:.0f} RSI {x['rsi']:.0f} 52H se {x['dist52']:.1f}%\n"
    if not dist: m2+="Koi Distribution nahi\n"
    m2+=f"\n<b>🔴 DECLINE - Bach Ke (Top 8)</b>\n"
    for x in dec[:8]: m2+=f"🔴 {x['n']} ₹{x['cl']:.0f} ({x['chg']:+.1f}%) RSI {x['rsi']:.0f}\n"
    m2+=f"\n<b>Rule:</b> PLATINUM/ADVANCE + RVOL 1.5x+ + RSI 55-70 + 20/50/200 ke upar = Best Swing. SL = 1.5x ATR. DISTRIBUTION me naya Swing mat lena."
    send(m2)
    m3=f"<b>📋 FULL 100 - % Change List</b>\n"
    for x in sorted(rows, key=lambda y: y["chg"], reverse=True):
        e="🟢" if x["chg"]>=0 else "🔴"
        m3+=f"{e} {x['n']} ₹{x['cl']:.0f} ({x['chg']:+.1f}%) RSI {x['rsi']:.0f}\n"
    for i in range(0, len(m3), 3800):
        send(m3[i:i+3800])
    print(f"DONE {len(rows)} ADV {len(adv)} ACC {len(acc)}")

if __name__=="__main__": main()
