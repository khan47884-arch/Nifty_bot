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
        if time.time()-d.get(k,0)<1200: return False
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
    try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage",data={"chat_id":cid,"text":t},timeout=15)
    except: pass
def add_ind(df):
    df['EMA20']=df['Close'].ewm(span=20).mean()
    df['EMA50']=df['Close'].ewm(span=50).mean()
    df['VWAP']=(df['Close']*df['Volume']).cumsum()/df['Volume'].cumsum() if df['Volume'].sum()!=0 else df['Close'].ewm(span=20).mean()
    df['Volx']=(df['Volume']/df['Volume'].rolling(20).mean()).fillna(1.0)
    delta=df['Close'].diff()
    gain=delta.where(delta>0,0).rolling(14).mean()
    loss=-delta.where(delta<0,0).rolling(14).mean()
    df['RSI']=100-(100/(1+gain/loss))
    df['ATR']=(df['High']-df['Low']).rolling(14).mean()
    return df.bfill()
def get_data(sym):
    df1=yf.download(sym,period="5d",interval="1m",progress=False,auto_adjust=True)
    if isinstance(df1.columns,pd.MultiIndex): df1.columns=df1.columns.get_level_values(0)
    if len(df1)<100: return None,None
    df5=df1.resample('5min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    df15=df1.resample('15min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    return add_ind(df5), add_ind(df15)
def find_blocks(df):
    last=df.iloc[-1]; prev=df.iloc[-2]
    last50=df.iloc[-50:]
    order_block = prev['Close'] < prev['Open'] and last['Close'] > last['Open'] and last['Volx']>1.2
    low_50 = last50['Low'].min()
    low_prev = df.iloc[-80:-20]['Low'].min() if len(df)>80 else low_50
    liq_sweep = low_50 < low_prev * 0.998 and last['Close'] > low_50 * 1.003
    breaker = liq_sweep and last['Close'] > last['VWAP']
    demand = last['Low'] <= last50['Low'].nsmallest(5).mean() * 1.01
    return order_block, liq_sweep, breaker, demand
def run_for(sym,name,gap):
    df5,df15=get_data(sym)
    if df5 is None: return None
    last5=df5.iloc[-1]; prev5=df5.iloc[-2]
    last15=df15.iloc[-1]
    rsi5=float(last5['RSI']); rsi15=float(last15['RSI'])
    atr=float(last5['ATR']); sl=int(round(atr))
    if sl<20: sl=20
    if sl>40: sl=40
    if rsi15 >= 72: return None
    ob15, liq15, break15, dem15 = find_blocks(df15)
    ob5, liq5, break5, dem5 = find_blocks(df5)
    body = abs(last5['Close']-last5['Open'])
    rng = last5['High']-last5['Low']
    bullet5 = (body/rng)>0.6 and last5['Close']>last5['Open'] and last5['Close']>prev5['High'] if rng!=0 else False
    trend_up_15 = last15['EMA20'] > last15['EMA50'] and last15['Close'] > last15['VWAP']
    trend_up_5 = last5['EMA20'] > last5['EMA50'] and last5['Close'] > last5['VWAP']
    trend_down_15 = last15['EMA20'] < last15['EMA50'] and last15['Close'] < last15['VWAP']
    side=None; stamp=None; pts=0; block_name=""
    if trend_up_15 and break15 and bullet5 and 53<=rsi15<=65 and 58<=rsi5<=68:
        stamp="KOHINOOR"; side="CE"; pts=200; block_name="15M BREAKER + LIQ SWEEP - LAMBA TARGET"
    elif trend_up_15 and ob15 and bullet5 and 53<=rsi15<=68 and 58<=rsi5<=68:
        stamp="DIAMOND"; side="CE"; pts=150; block_name="15M ORDER BLOCK - LAMBA"
    elif trend_up_15 and dem15 and 53<=rsi15<=62 and 58<=rsi5<=65:
        stamp="GOLD"; side="CE"; pts=100; block_name="15M DEMAND ZONE - LAMBA"
    elif trend_up_5 and break5 and bullet5 and 58<=rsi5<=68:
        stamp="KOHINOOR"; side="CE"; pts=80; block_name="5M BREAKER + LIQ SWEEP - IDEA"
    elif trend_up_5 and ob5 and bullet5 and 58<=rsi5<=68:
        stamp="DIAMOND"; side="CE"; pts=80; block_name="5M ORDER BLOCK BANA HAI"
    elif trend_up_5 and dem5 and 58<=rsi5<=65:
        stamp="GOLD"; side="CE"; pts=50; block_name="5M DEMAND ZONE"
    elif trend_down_15 and 35<=rsi15<=48 and last5['Close']<prev5['Low']:
        stamp="DIAMOND"; side="PE"; pts=80; block_name="15M DOWN"
    if stamp is None: return None
    strike=int(round(last5['Close']/gap)*gap)
    if can_send(name,f"{strike} {side}",side):
        if "15M" in block_name:
            msg = f"""👑👑👑 {stamp} BOMB {side} - 15M
📅 {datetime.now(IST).strftime('%d-%m %H:%M')} | {name}
🧱 BLOCK: {block_name}
🎯 STRIKE: {strike} {side} - CURRENT PE LO
🛑 SL: -{sl} pts | 🎯 +{pts} pts (LAMBA)
💡 RSI15:{rsi15:.0f} RSI5:{rsi5:.0f} BULLET:{'YES' if bullet5 else 'NO'}"""
        else:
            msg = f"""💎💎💎 {stamp} BOMB {side} - 5M
📅 {datetime.now(IST).strftime('%d-%m %H:%M')} | {name}
🧱 BLOCK: {block_name}
🎯 STRIKE: {strike} {side} - CURRENT PE LO
🛑 SL: -{sl} pts | 🎯 +{pts} pts (IDEA)
💡 RSI15:{rsi15:.0f} RSI5:{rsi5:.0f} BULLET:{'YES' if bullet5 else 'NO'}"""
        send_tg(msg); mark_sent(name,f"{strike} {side}",side); return True
    return None
if __name__=="__main__":
    run_for("^NSEI","NIFTY",50)
    run_for("^BSESN","SENSEX",100)
