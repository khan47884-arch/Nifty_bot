import yfinance as yf, requests, os, json, time
from datetime import datetime
import pytz
import pandas as pd
LAST_FILE = "last_trade.json"
IST = pytz.timezone('Asia/Kolkata')
def can_send(i,s,sd):
    k=f"{i}_{s}_{sd}"
    if not os.path.exists(LAST_FILE): return True
    try:
        d=json.load(open(LAST_FILE))
        if time.time()-d.get(k,0)<1800: return False
    except: pass
    return True
def mark_sent(i,s,sd):
    k=f"{i}_{s}_{sd}"
    d={}
    if os.path.exists(LAST_FILE):
        try: d=json.load(open(LAST_FILE))
        except: pass
    d[k]=time.time()
    json.dump(d,open(LAST_FILE,'w'))
def send_tg(t):
    tk=os.getenv('TELEGRAM_BOT_TOKEN')
    cid=os.getenv('TELEGRAM_CHAT_ID')
    try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage",data={"chat_id":cid,"text":t},timeout=15)
    except: pass
def add_ind(df):
    df['EMA20']=df['Close'].ewm(span=20).mean()
    df['EMA50']=df['Close'].ewm(span=50).mean()
    df['VWAP']=(df['Close']*df['Volume']).cumsum()/df['Volume'].cumsum() if df['Volume'].sum()!=0 else df['Close'].ewm(span=20).mean()
    df['Volx']=(df['Volume']/df['Volume'].rolling(20).mean()).fillna(1.5)
    delta=df['Close'].diff()
    gain=delta.where(delta>0,0).rolling(14).mean()
    loss=-delta.where(delta<0,0).rolling(14).mean()
    df['RSI']=100-(100/(1+gain/loss))
    df['ATR']=(df['High']-df['Low']).rolling(14).mean()
    return df.bfill()
def get_data(sym):
    df1=yf.download(sym,period="2d",interval="1m",progress=False,auto_adjust=True)
    if isinstance(df1.columns,pd.MultiIndex): df1.columns=df1.columns.get_level_values(0)
    if len(df1)<100: return None,None
    df5=df1.resample('5min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    df15=df1.resample('15min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    return add_ind(df5),add_ind(df15)
def run_for(sym,name,gap):
    df5,df15=get_data(sym)
    if df5 is None: return None
    t15=df15.iloc[-1]; last=df5.iloc[-1]; prev=df5.iloc[-2]
    pl=df5.iloc[-21:-1]['Low'].min(); ph=df5.iloc[-21:-1]['High'].max()
    if last['Low']<pl and last['Close']>pl+5 and last['Close']>last['VWAP'] and last['EMA20']>last['EMA50'] and 50<last['RSI']<75 and last['Close']>prev['High']:
        st=int(round(last['Close']/gap)*gap); en=round(last['ATR']*2.5+80,0); sl=max(18,round(last['ATR']*1.2,0))
        if can_send(name,f"{st} CE","CE"):
            send_tg(f"👑👑👑 KOHINOOR - LIQUIDITY BOMB CE\n📅 {datetime.now(IST).strftime('%d-%m %H:%M')} | W PATTERN + LIQ SWEEP 2nd Candle ✅\n📊 {name} 15M Trend OK | VWAP UP ✅\n📈 RSI5: {round(last['RSI'],0)} | Vol: {round(float(last['Volx']),1)}x\n🎯 STRIKE: {st} CE @ {en} Rs\n🛑 SL: {round(en-sl,1)} | T1: {round(en+sl*2,1)} | T2: {round(en+sl*3,1)} | T3: {round(en+sl*4,1)}")
            mark_sent(name,f"{st} CE","CE"); return True
    if last['High']>ph and last['Close']<ph-5 and last['Close']<last['VWAP'] and last['EMA20']<last['EMA50'] and 25<last['RSI']<50 and last['Close']<prev['Low']:
        st=int(round(last['Close']/gap)*gap); en=round(last['ATR']*2.5+80,0); sl=max(18,round(last['ATR']*1.2,0))
        if can_send(name,f"{st} PE","PE"):
            send_tg(f"👑👑👑 KOHINOOR - LIQUIDITY BOMB PE\n📅 {datetime.now(IST).strftime('%d-%m %H:%M')} | M PATTERN\n📊 {name} | VWAP DOWN ✅\n📈 RSI5: {round(last['RSI'],0)} | Vol: {round(float(last['Volx']),1)}x\n🎯 {st} PE @ {en} Rs\n🛑 SL: {round(en-sl,1)} | T1: {round(en+sl*2,1)}")
            mark_sent(name,f"{st} PE","PE"); return True
    if t15['EMA20']>t15['EMA50'] and t15['Close']>t15['VWAP']:
        c=(1 if last['Close']>prev['High'] else 0)+(1 if last['Close']>last['VWAP'] else 0)+(1 if last['EMA20']>last['EMA50'] else 0)
        if c>=2 and 50<last['RSI']<70 and last['RSI']>prev['RSI']:
            st=int(round(last['Close']/gap)*gap); en=round(last['ATR']*2.2+60,0); sl=max(15,round(last['ATR']*1.0,0))
            if can_send(name,f"{st} CE","CE"):
                send_tg(f"💎💎💎 DIAMOND BOMB CE\n📅 {datetime.now(IST).strftime('%d-%m %H:%M')} | UP TREND\n📊 {name} 15M OK | RSI: {round(last['RSI'],0)} | Volx: {round(float(last['Volx']),1)}\n🎯 {st} CE @ {en} | SL: {round(en-sl,1)} | T1: {round(en+sl*2,1)}")
                mark_sent(name,f"{st} CE","CE"); return True
    if t15['EMA20']<t15['EMA50'] and t15['Close']<t15['VWAP']:
        c=(1 if last['Close']<prev['Low'] else 0)+(1 if last['Close']<last['VWAP'] else 0)+(1 if last['EMA20']<last['EMA50'] else 0)
        if c>=2 and 20<last['RSI']<48 and last['RSI']<prev['RSI']:
            st=int(round(last['Close']/gap)*gap); en=round(last['ATR']*2.2+60,0); sl=max(15,round(last['ATR']*1.0,0))
            if can_send(name,f"{st} PE","PE"):
                send_tg(f"💎💎💎 DIAMOND BOMB PE\n📅 {datetime.now(IST).strftime('%d-%m %H:%M')} | DOWN TREND\n📊 {name} | RSI: {round(last['RSI'],0)}\n🎯 {st} PE @ {en} | SL: {round(en-sl,1)}")
                mark_sent(name,f"{st} PE","PE"); return True
    return None
if __name__=="__main__":
    a=run_for("^NSEI","NIFTY",50)
    b=run_for("^BSESN","SENSEX",100)
    if not a and not b:
        send_tg(f"✅ BOT LIVE - {datetime.now(IST).strftime('%d-%m %H:%M')}\nNIFTY/SENSEX check kiya, abhi setup nahi bana. Agle 5 min me check karega. Bot sahi chal raha hai Boss!")
