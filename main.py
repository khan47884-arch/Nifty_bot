import yfinance as yf
import requests, os, time
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
def get_patterns(df):
    if len(df)<3: return []
    curr=df.iloc[-1]; prev=df.iloc[-2]
    pats=[]
    d=cd(curr)
    if not d: return []
    o,h,l,c,body,rng,up,low=d
    if rng==0: return []
    if body/rng>0.1 and body/rng<0.4 and low>=2*body: pats.append("HAMMER")
    if body/rng>0.1 and body/rng<0.4 and up>=2*body: pats.append("INVERTED HAMMER")
    if float(prev['Close'])<float(prev['Open']) and float(curr['Close'])>float(curr['Open']) and float(curr['Open'])<=float(prev['Close']) and float(curr['Close'])>=float(prev['Open']):
        pats.append("BULLISH ENGULFING")
    if all(float(df.iloc[i]['Close'])>float(df.iloc[i]['Open']) for i in [-3,-2,-1]): pats.append("THREE WHITE SOLDIERS")
    if body/rng<0.15 and low>rng*0.6: pats.append("DRAGONFLY DOJI")
    if float(prev['Close'])>float(prev['Open']) and float(curr['Close'])<float(curr['Open']) and float(curr['Open'])>=float(prev['Close']) and float(curr['Close'])<=float(prev['Open']):
        pats.append("BEARISH ENGULFING")
    if all(float(df.iloc[i]['Close'])<float(df.iloc[i]['Open']) for i in [-3,-2,-1]): pats.append("THREE BLACK CROWS")
    if body/rng<0.15 and up>rng*0.6: pats.append("GRAVESTONE DOJI")
    if body/rng>0.1 and body/rng<0.4 and up>=2*body and o>c: pats.append("SHOOTING STAR")
    return pats
for sym,name in [("^NSEI","NIFTY"),("^BSESN","SENSEX")]:
    try:
        daily = yf.download(sym, period="5d", interval="1d", auto_adjust=True, progress=False)
        DH=float(daily['High'].iloc[-2]); DL=float(daily['Low'].iloc[-2])
        intraday = yf.download(sym, period="1d", interval="5m", auto_adjust=True, progress=False)
        if len(intraday)<3: continue
        curr=float(intraday['Close'].iloc[-1])
        if abs(curr-DH)/DH<0.005 or abs(curr-DL)/DL<0.005:
            for pat in get_patterns(intraday):
                emoji="🔥" if pat in ["HAMMER","INVERTED HAMMER","BULLISH ENGULFING","THREE WHITE SOLDIERS","DRAGONFLY DOJI"] else "🔻"
                send_telegram(f"{emoji} {name} {pat}\nDH: {DH:.2f} | DL: {DL:.2f}\nPrice: {curr:.2f}\n5min")
    except: pass
STOCKS=["RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","WIPRO.NS","HCLTECH.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS","ADANIENT.NS","ADANIPORTS.NS","BAJAJFINSV.NS","BPCL.NS","BRITANNIA.NS","CIPLA.NS","COALINDIA.NS","DIVISLAB.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS","HINDALCO.NS","HINDUNILVR.NS","INDUSINDBK.NS","JSWSTEEL.NS","M&M.NS","NESTLEIND.NS","NTPC.NS","ONGC.NS","POWERGRID.NS","SHREECEM.NS","TATAMOTORS.NS","TATASTEEL.NS","TECHM.NS","UPL.NS","VEDL.NS","WIPRO.NS","ZEEL.NS","BANKBARODA.NS","PNB.NS"]
if os.path.exists("nifty1000.csv"):
    try:
        import pandas as pd
        df_csv=pd.read_csv("nifty1000.csv")
        STOCKS=[s.strip()+".NS" if ".NS" not in s else s.strip() for s in df_csv.iloc[:,0].tolist()][:1000]
    except: pass
count=0
for ticker in STOCKS[:1000]:
    try:
        monthly=yf.download(ticker, period="2y", interval="1mo", auto_adjust=True, progress=False)
        m_pat=get_patterns(monthly)[-1] if len(monthly)>=3 and get_patterns(monthly) else ""
        weekly=yf.download(ticker, period="1y", interval="1wk", auto_adjust=True, progress=False)
        w_pat=get_patterns(weekly)[-1] if len(weekly)>=3 and get_patterns(weekly) else ""
        daily_s=yf.download(ticker, period="3mo", interval="1d", auto_adjust=True, progress=False)
        d_pat=get_patterns(daily_s)[-1] if len(daily_s)>=3 and get_patterns(daily_s) else ""
        curr_p=float(daily_s['Close'].iloc[-1]) if len(daily_s)>0 else 0
        bullish_list=["HAMMER","INVERTED HAMMER","BULLISH ENGULFING","THREE WHITE SOLDIERS","DRAGONFLY DOJI"]
        score=sum([1 for p in [m_pat,w_pat,d_pat] if p in bullish_list])
        if score>=2 and curr_p>0:
            send_telegram(f"🚀 {ticker.replace('.NS','')} BULLISH\nM: {m_pat} | W: {w_pat} | D: {d_pat}\nPrice: {curr_p:.2f}\nScore: {score}/3")
            count+=1
            if count>=20: break
        time.sleep(0.2)
    except: continue
