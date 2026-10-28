import yfinance as yf
import requests, os, time
import pandas as pd
import numpy as np
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass
def cd(r):
    try:
        o=float(r['Open']); h=float(r['High']); l=float(r['Low']); c=float(r['Close'])
        body=abs(c-o); rng=h-l
        if rng==0: return None
        return o,h,l,c,body,rng,h-max(o,c),min(o,c)-l
    except: return None
def get_candle_patterns(df):
    if len(df)<3: return []
    curr=df.iloc[-1]; prev=df.iloc[-2]
    pats=[]
    d=cd(curr)
    if not d: return []
    o,h,l,c,body,rng,up,low=d
    if rng==0: return []
    if body/rng>0.1 and body/rng<0.4 and low>=2*body: pats.append("HAMMER")
    if body/rng>0.1 and body/rng<0.4 and up>=2*body and o<c: pats.append("INVERTED HAMMER")
    if float(prev['Close'])<float(prev['Open']) and float(curr['Close'])>float(curr['Open']) and float(curr['Open'])<=float(prev['Close']) and float(curr['Close'])>=float(prev['Open']):
        pats.append("BULLISH ENGULFING")
    if all(float(df.iloc[i]['Close'])>float(df.iloc[i]['Open']) for i in [-3,-2,-1]): pats.append("THREE WHITE SOLDIERS")
    if body/rng<0.15 and low>rng*0.6: pats.append("DRAGONFLY DOJI")
    return pats
def detect_new_patterns_confirmed(df):
    if len(df)<30: return []
    pats=[]
    try:
        close=df['Close'].values; high=df['High'].values; low=df['Low'].values
        vol=df['Volume'].values if 'Volume' in df.columns else np.ones(len(close))
        c30=close[-30:]; h30=high[-30:]; l30=low[-30:]; v30=vol[-30:]
        idx1=np.argmin(l30[:15]); idx2=np.argmin(l30[15:])+15
        if abs(l30[idx1]-l30[idx2])/l30[idx1] < 0.025:
            neck=np.max(h30[idx1:idx2])
            if float(c30[-1]) > neck and float(c30[-2]) <= neck:
                target = neck + (neck - min(l30[idx1],l30[idx2]))
                vol_ok = v30[-1] > np.mean(v30[-10:-1])*1.15
                pats.append(f"DOUBLE BOTTOM CONFIRMED{' + VOL' if vol_ok else ''} | Neck:{neck:.2f} Tgt:{target:.2f}")
        idx1=np.argmax(h30[:15]); idx2=np.argmax(h30[15:])+15
        if abs(h30[idx1]-h30[idx2])/h30[idx1] < 0.025:
            neck=np.min(l30[idx1:idx2])
            if float(c30[-1]) < neck and float(c30[-2]) >= neck:
                pats.append(f"DOUBLE TOP CONFIRMED | Neck:{neck:.2f}")
        if h30[10] > h30[5] and h30[10] > h30[15] and h30[10] > np.mean(h30)+np.std(h30):
            neck=np.min(l30[5:15])
            if float(c30[-1]) < neck: pats.append("HEAD & SHOULDER CONFIRMED")
        if l30[10] < l30[5] and l30[10] < l30[15] and l30[10] < np.mean(l30)-np.std(l30):
            neck=np.max(h30[5:15])
            if float(c30[-1]) > neck: pats.append("INVERSE HEAD & SHOULDER CONFIRMED")
        hslope=np.polyfit(range(10), h30[-10:],1)[0]; lslope=np.polyfit(range(10), l30[-10:],1)[0]
        if hslope<0 and lslope<0 and abs(hslope)>abs(lslope) and float(c30[-1])>np.max(h30[-3:]): pats.append("FALLING WEDGE BREAKOUT")
        if hslope>0 and lslope>0 and lslope>hslope and float(c30[-1])<np.min(l30[-3:]): pats.append("RISING WEDGE BREAKDOWN")
        if np.std(c30[-10:]) < np.std(c30[-20:-10])*0.65:
            if float(c30[-1]) > np.max(h30[-10:]): pats.append("BULLISH PENNANT / FLAG CONFIRMED")
            if float(c30[-1]) < np.min(l30[-10:]): pats.append("BEARISH PENNANT / FLAG CONFIRMED")
        if np.std(h30[-10:])/np.mean(h30[-10:]) < 0.012 and float(c30[-1]) > np.max(h30[-10:]): pats.append("BULLISH RECTANGLE BREAKOUT")
        if np.std(l30[-10:])/np.mean(l30[-10:]) < 0.012 and float(c30[-1]) < np.min(l30[-10:]): pats.append("BEARISH RECTANGLE BREAKDOWN")
    except: pass
    return pats
for sym,name in [("^NSEI","NIFTY"),("^BSESN","SENSEX")]:
    try:
        df=yf.download(sym, period="3mo", interval="15m", auto_adjust=True, progress=False)
        if len(df)<30: continue
        curr=float(df['Close'].iloc[-1])
        for pat in get_candle_patterns(df):
            send_telegram(f"🎩 BOND 007 - INDEX CANDLE\n━━━━━━━━━━━━━━\n🎯 {name} | {pat}\n💰 {curr:.2f} | 15min")
        for pat in detect_new_patterns_confirmed(df):
            send_telegram(f"🎩 BOND 007 - CHART CONFIRMED\n━━━━━━━━━━━━━━\n🎯 {name}\n📈 {pat}\n💰 {curr:.2f}\n⏱️ 15m | BREAKOUT CONFIRMED\n━━━━━━━━━━━━━━\nProfit Bond 😎")
    except: pass
STOCKS=["RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","WIPRO.NS","HCLTECH.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","ADANIENT.NS","ADANIPORTS.NS","BAJAJFINSV.NS","BPCL.NS","BRITANNIA.NS","CIPLA.NS","COALINDIA.NS","DIVISLAB.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS","HINDALCO.NS","HINDUNILVR.NS","INDUSINDBK.NS","JSWSTEEL.NS","M&M.NS","NESTLEIND.NS","NTPC.NS","ONGC.NS","POWERGRID.NS","SHREECEM.NS","TATAMOTORS.NS","TATASTEEL.NS","TECHM.NS","UPL.NS","VEDL.NS","ZEEL.NS","BANKBARODA.NS","PNB.NS"]
if os.path.exists("nifty1000.csv"):
    try:
        df_csv=pd.read_csv("nifty1000.csv")
        STOCKS=[s.strip()+".NS" if ".NS" not in s else s.strip() for s in df_csv.iloc[:,0].tolist()][:1000]
    except: pass
for ticker in STOCKS[:1000]:
    try:
        daily=yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
        if len(daily)<210: continue
        curr_p=float(daily['Close'].iloc[-1])
        ma50=daily['Close'].rolling(50).mean(); ma200=daily['Close'].rolling(200).mean()
        if float(ma50.iloc[-2]) <= float(ma200.iloc[-2]) and float(ma50.iloc[-1]) > float(ma200.iloc[-1]):
            send_telegram(f"🎩 BOND 007 - GOLDEN CROSS CONFIRMED\n━━━━━━━━━━━━━━\n🎯 {ticker.replace('.NS','')}\n💰 {curr_p:.2f}\n🚀 50MA CROSSED 200MA")
        for pat in detect_new_patterns_confirmed(daily):
            send_telegram(f"🎩 BOND 007 - CHART CONFIRMED\n━━━━━━━━━━━━━━\n🎯 {ticker.replace('.NS','')}\n📈 {pat}\n💰 {curr_p:.2f}\n📅 DAILY CONFIRMED")
        monthly=yf.download(ticker, period="2y", interval="1mo", auto_adjust=True, progress=False)
        m_pat=get_candle_patterns(monthly)[-1] if len(monthly)>=3 and get_candle_patterns(monthly) else ""
        weekly=yf.download(ticker, period="1y", interval="1wk", auto_adjust=True, progress=False)
        w_pat=get_candle_patterns(weekly)[-1] if len(weekly)>=3 and get_candle_patterns(weekly) else ""
        d_pat=get_candle_patterns(daily)[-1] if len(daily)>=3 and get_candle_patterns(daily) else ""
        if m_pat!="" and w_pat!="" and d_pat!="" and curr_p>0:
            send_telegram(f"🎩 BOND 007 - ELITE SIGNAL\n━━━━━━━━━━━━━━\n🎯 {ticker.replace('.NS','')}\n📊 3/3 CONFIRMED\n🕯️ M:{m_pat} | W:{w_pat} | D:{d_pat}\n💰 {curr_p:.2f}\n━━━━━━━━━━━━━━\nProfit Bond 😎🔥")
        time.sleep(0.15)
    except: continue
