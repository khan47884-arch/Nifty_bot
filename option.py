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
        if time.time()-d.get(k,0)<900: return False
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
    if len(df1)<100: return None,None
    df5=df1.resample('5min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    df15=df1.resample('15min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    return add_ind(df5), add_ind(df15)

def run_for(sym,name,gap):
    df5,df15=get_data(sym)
    if df5 is None: return None
    last5=df5.iloc[-1]; prev5=df5.iloc[-2]
    last15=df15.iloc[-1]
    rsi5=float(last5['RSI']); rsi15=float(last15['RSI'])
    atr=float(last5['ATR'])
    sl=int(round(atr))
    if sl<20: sl=20
    if sl>40: sl=40
    up15 = last15['Close']>last15['EMA20'] and last15['EMA20']>last15['EMA50'] and last15['Close']>last15['VWAP']
    down15 = last15['Close']<last15['EMA20'] and last15['EMA20']<last15['EMA50']
    ce_break = last5['Close']>prev5['High'] and last5['Close']>last5['VWAP']
    pe_break = last5['Close']<prev5['Low'] and last5['Close']<last5['VWAP']
    vol=float(last5['Volx'])
    side=None
    if up15 and ce_break and 50<=rsi15<=70 and 50<=rsi5<=75 and vol>=1.0:
        side="CE"
    elif down15 and pe_break and 30<=rsi15<=60 and 30<=rsi5<=60:
        side="PE"
    if side is None: return None
    strike=int(round(last5['Close']/gap)*gap)
    if can_send(name,f"{strike} {side}",side):
        t1=60; t2=100; t3=200
        msg=f"""🚀 {name} {side} - 15M TREND + 5M BREAKOUT
📅 {datetime.now(IST).strftime('%d-%m %H:%M')} | {name}: {last5['Close']:.0f}
📈 15M TREND: {'UP ✅' if up15 else 'DOWN ✅'} RSI15:{rsi15:.0f} | 5M RSI5:{rsi5:.0f} Vol:{vol:.1f}x
💥 BREAK: {last5['Close']:.0f} vs {prev5['High']:.0f if side=='CE' else prev5['Low']:.0f}
🎯 STRIKE: {strike} {side}
💰 ENTRY: CURRENT PRICE PE LO
🛑 SL: {sl} Pts (ATR Pure)

🎯 T1: +{t1} Pts (50% Book)
🎯 T2: +{t2} Pts (30% Book)
🎯 T3: +{t3} Pts (Maha Target)

💡 Logic: T1 pe SL Cost pe, T2 pe Trail

⚡ PROFITABLE TRADERS AI - 101%"""
        send_tg(msg); mark_sent(name,f"{strike} {side}",side); return True
    return None

if __name__=="__main__":
    run_for("^NSEI","NIFTY",50)
    time.sleep(3)
    run_for("^BSESN","SENSEX",100)
