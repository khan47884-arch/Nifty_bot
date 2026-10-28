import yfinance as yf
import requests, os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def cd(r):
    o=float(r['Open']); h=float(r['High']); l=float(r['Low']); c=float(r['Close'])
    body=abs(c-o); rng=h-l
    if rng==0: return None
    return o,h,l,c,body,rng,h-max(o,c),min(o,c)-l

def get_patterns(df):
    if len(df)<3: return []
    curr=df.iloc[-1]; prev=df.iloc[-2]
    pats=[]
    d=cd(curr)
    if not d: return []
    o,h,l,c,body,rng,up,low=d
    if body/rng>0.1 and body/rng<0.4 and low>=2*body: pats.append(("HAMMER","BULLISH_01"))
    if body/rng>0.1 and body/rng<0.4 and up>=2*body: pats.append(("INVERTED HAMMER","BULLISH_02"))
    if float(prev['Close'])<float(prev['Open']) and float(curr['Close'])>float(curr['Open']) and float(curr['Open'])<=float(prev['Close']) and float(curr['Close'])>=float(prev['Open']):
        pats.append(("BULLISH ENGULFING","BULLISH_03"))
    if float(prev['Close'])<float(prev['Open']) and float(curr['Close'])>float(curr['Open']) and float(curr['Open'])<float(prev['Low']):
        pats.append(("PIERCING PATTERN","BULLISH_04"))
    a=df.iloc[-3]; b=df.iloc[-2]
    if float(a['Close'])<float(a['Open']) and float(curr['Close'])>float(curr['Open']):
        pats.append(("MORNING STAR","BULLISH_05"))
    if all(float(df.iloc[i]['Close'])>float(df.iloc[i]['Open']) for i in [-3,-2,-1]):
        pats.append(("THREE WHITE SOLDIERS","BULLISH_06"))
    if body/rng<0.15 and low>rng*0.6: pats.append(("DRAGONFLY DOJI","BULLISH_07"))
    if float(prev['Close'])>float(prev['Open']) and float(curr['Close'])<float(curr['Open']) and float(curr['Open'])>=float(prev['Close']) and float(curr['Close'])<=float(prev['Open']):
        pats.append(("BEARISH ENGULFING","BEARISH_03"))
    if all(float(df.iloc[i]['Close'])<float(df.iloc[i]['Open']) for i in [-3,-2,-1]):
        pats.append(("THREE BLACK CROWS","BEARISH_06"))
    if body/rng<0.15 and up>rng*0.6: pats.append(("GRAVESTONE DOJI","BEARISH_07"))
    if body/rng>0.1 and body/rng<0.4 and up>=2*body: pats.append(("SHOOTING STAR","BEARISH_02"))
    return pats

for sym,name in [("^NSEI","NIFTY"),("^BSESN","SENSEX")]:
    try:
        daily = yf.download(sym, period="5d", interval="1d", auto_adjust=True, progress=False)
        DH=float(daily['High'].iloc[-2]); DL=float(daily['Low'].iloc[-2])
        intraday = yf.download(sym, period="1d", interval="5m", auto_adjust=True, progress=False)
        if len(intraday)<3: continue
        curr=float(intraday['Close'].iloc[-1])
        if abs(curr-DH)/DH<0.005 or abs(curr-DL)/DL<0.005:
            for pat,code in get_patterns(intraday):
                emoji="🔥" if "BULLISH" in code else "🔻"
                send_telegram(f"{emoji} {name} {pat}\nCODE: {code}\nDH: {DH:.2f} | DL: {DL:.2f}\nPrice: {curr:.2f}\n5min")
    except: pass
