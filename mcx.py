import yfinance as yf
import requests
import os
from datetime import datetime
import pytz
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYMBOLS = {"GOLDMINI": "GC=F", "SILVERM": "SI=F", "CRUDEOIL": "CL=F"}

def get_rsi(s, p=14):
    d = s.diff()
    g = (d.where(d > 0, 0)).rolling(p).mean()
    l = (-d.where(d < 0, 0)).rolling(p).mean()
    rs = g / l
    return (100 - (100 / (1 + rs))).fillna(50)

def to_mcx(n, comex, usd):
    if n=="GOLDMINI": return (comex*usd/31.1035)*10
    elif n=="SILVERM": return (comex*usd/31.1035)*1000*1.18
    else: return comex*usd

def get_usd():
    try:
        df=yf.download("INR=X", period="1d", interval="1m", progress=False)
        df.columns=[c[0] if isinstance(c,tuple) else c for c in df.columns]
        p=float(df['Close'].iloc[-1])
        return p if 80<p<100 else 88.5
    except: return 88.5

def check(n, sym, usd):
    df=yf.download(sym, period="10d", interval="15m", progress=False)
    if len(df)<60: return None
    df.columns=[c[0] if isinstance(c,tuple) else c for c in df.columns]
    df['RSI']=get_rsi(df['Close'])
    df['EMA20']=df['Close'].ewm(span=20).mean()
    df['EMA50']=df['Close'].ewm(span=50).mean()
    df['EMA200']=df['Close'].ewm(span=200).mean()
    df['VWAP']=(df['Close']*df['Volume']).cumsum()/df['Volume'].cumsum()
    df['VolAvg']=df['Volume'].rolling(20).mean()

    last=df.iloc[-1]; prev=df.iloc[-2]
    rsi=float(last['RSI'])
    if rsi > 68: return None
    if float(last['VolAvg'])==0: return None
    vol=float(last['Volume']/last['VolAvg'])
    if vol<2.0: return None
    o=float(last['Open']); c=float(last['Close']); h=float(last['High']); l=float(last['Low'])
    body=abs(c-o); rng=h-l
    if rng==0 or body<rng*0.5: return None
    uw=h-max(c,o); lw=min(c,o)-l
    ema20=float(last['EMA20']); ema50=float(last['EMA50']); ema200=float(last['EMA200']); vwap=float(last['VWAP'])
    sup=float(df['Low'].tail(20).min()); res=float(df['High'].tail(20).max())
    is_hammer = lw>body*2.2 and c>o
    is_inv_hammer = uw>body*2.2 and c>o
    is_shoot = uw>body*2.2 and c<o
    is_bear_eng = c<o and prev['Close']>prev['Open'] and c<prev['Open'] and o>prev['Close']
    is_bull_eng = c>o and prev['Close']<prev['Open'] and c>prev['Open'] and o<prev['Close']
    sig=None; name=""
    if is_hammer or is_bull_eng or is_inv_hammer: 
        name="Hammer" if is_hammer else "Inv Hammer" if is_inv_hammer else "Bull Engulf"
        sig="BUY"
    elif is_shoot or is_bear_eng:
        name="Shooting Star" if is_shoot else "Bear Engulf"
        sig="SELL"
    else: return None
    if sig=="BUY":
        if not (c>ema20 and ema20>ema50 and c>ema200 and c>vwap): return None
    else:
        if not (c<ema20 and ema20<ema50 and c<ema200 and c<vwap): return None
    if n=="CRUDEOIL": pts=60; t2=20; t3=40
    elif n=="GOLDMINI": pts=150; t2=150; t3=300
    else: pts=1000; t2=1000; t3=2000
    ist=pytz.timezone('Asia/Kolkata'); dt=datetime.now(ist).strftime("%d-%m %H:%M")
    mcx=to_mcx(n,c,usd); sl_l=to_mcx(n,l,usd); sl_h=to_mcx(n,h,usd)
    mcx_sup=to_mcx(n,sup,usd); mcx_res=to_mcx(n,res,usd)
    if sig=="BUY":
        return f"""💥 15M BOOM BUY
📅 {dt} | {n} | RSI:{rsi:.1f}
🕯️ {name} @ Sup {mcx_sup:.0f}
📈 Vol {vol:.1f}x UP
🎯 ENTRY {mcx:.0f} SL {sl_l:.0f}
🚀 T1 {mcx+pts:.0f} T2 {mcx+pts+t2:.0f} T3 {mcx+pts+t3:.0f}"""
    else:
        return f"""💥 15M BOOM SELL
📅 {dt} | {n} | RSI:{rsi:.1f}
🕯️ {name} @ Res {mcx_res:.0f}
📈 Vol {vol:.1f}x DOWN
🎯 ENTRY {mcx:.0f} SL {sl_h:.0f}
🚀 T1 {mcx-pts:.0f} T2 {mcx-pts-t2:.0f} T3 {mcx-pts-t3:.0f}"""

def send(m):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m})

usd=get_usd(); out=[]
for k,v in SYMBOLS.items():
    x=check(k,v,usd)
    if x: out.append(x)
ist=pytz.timezone('Asia/Kolkata'); now=datetime.now(ist).strftime("%d-%m %I:%M %p")
if out:
    for m in out: send(m)
else:
    send(f"⚪ 15M FLAT | {now}\nNo BOOM")
