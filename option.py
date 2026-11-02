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
        if time.time()-d.get(k,0)<600: return False
    except: pass
    return True
def mark_sent(i,s,sd):
    k=f"{i}_{s}_{sd}"; d={}
    if os.path.exists(LAST_FILE):
        try: d=json.load(open(LAST_FILE))
        except: pass
    d[k]=time.time()
    json.dump(d,open(LAST_FILE,'w'))
def send_tg(t):
    tk=os.getenv('TELEGRAM_BOT_TOKEN')
    cid=os.getenv('TELEGRAM_CHAT_ID')
    try:
        requests.post(f"https://api.telegram.org/bot{tk}/sendMessage",data={"chat_id":cid,"text":t},timeout=15)
    except: pass

def add_ind(df):
    df['EMA20']=df['Close'].ewm(span=20).mean()
    df['EMA50']=df['Close'].ewm(span=50).mean()
    df['VWAP']=(df['Close']*df['Volume']).cumsum()/df['Volume'].cumsum() if df['Volume'].sum()!=0 else df['Close'].ewm(span=20).mean()
    delta=df['Close'].diff()
    gain=delta.where(delta>0,0).rolling(14).mean()
    loss=-delta.where(delta<0,0).rolling(14).mean()
    df['RSI']=100-(100/(1+gain/loss))
    df['ATR']=(df['High']-df['Low']).rolling(14).mean()
    df['Volx']=(df['Volume']/df['Volume'].rolling(20).mean()).fillna(1.0)
    return df.bfill()

def get_data(sym):
    df1=yf.download(sym,period="5d",interval="1m",progress=False,auto_adjust=True)
    if isinstance(df1.columns,pd.MultiIndex): df1.columns=df1.columns.get_level_values(0)
    if len(df1)<50: return None,None
    df5=df1.resample('5min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    df15=df1.resample('15min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    return add_ind(df5), add_ind(df15)

def run_for(sym,name,gap):
    df5,df15=get_data(sym)
    if df5 is None: 
        send_tg(f"❌ {name} Data Fail")
        return
    last5=df5.iloc[-1]; prev5=df5.iloc[-2]
    last15=df15.iloc[-1]
    rsi5=float(last5['RSI']); rsi15=float(last15['RSI'])
    up_15 = last15['Close'] > last15['EMA20']
    ce_break = last5['Close'] > prev5['High']*0.999
    side = "CE" if up_15 else "PE"
    strike=int(round(last5['Close']/gap)*gap)
    sl=int(round(float(last5['ATR'])))
    if sl<20: sl=20
    if sl>40: sl=40
    if can_send(name,f"{strike} {side}",side):
        msg=f"""🚀 {name} {side} - 15M TREND + 5M BREAKOUT
📅 {datetime.now(IST).strftime('%d-%m %H:%M')} | {name}: {last5['Close']:.0f}
📈 15M TREND: {'UP ✅' if up_15 else 'DOWN ✅'} RSI15:{rsi15:.0f} | 5M RSI5:{rsi5:.0f} Vol:{float(last5['Volx']):.1f}x
💥 BREAK: {last5['Close']:.0f} vs Prev {prev5['High']:.0f}
🎯 STRIKE: {strike} {side} - CURRENT PE LO
🛑 SL: -{sl} pts | 🎯 +60 pts"""
        send_tg(msg); mark_sent(name,f"{strike} {side}",side)

if __name__=="__main__":
    send_tg(f"🔴 BOT LIVE TEST - {datetime.now(IST).strftime('%d-%m %H:%M:%S')} - Start")
    run_for("^NSEI","NIFTY",50)
    time.sleep(2)
    run_for("^BSESN","SENSEX",100)
