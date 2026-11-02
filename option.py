import yfinance as yf, requests, os, json, time
from datetime import datetime
import pytz
import pandas as pd
import numpy as np
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
    k=f"{i}_{s}_{sd}"; d={}
    if os.path.exists(LAST_FILE):
        try: d=json.load(open(LAST_FILE))
        except: pass
    d[k]=time.time()
    json.dump(d,open(LAST_FILE,'w'))
def send_tg(t):
    tk=os.getenv('TELEGRAM_BOT_TOKEN')
    cid=os.getenv('TELEGRAM_CHAT_ID')
    try: requests.post(f"https://api.telegram.org/bot{tk}/sendMessage",data={"chat_id":cid,"text":t,"parse_mode":"Markdown"},timeout=15)
    except: pass
def add_ind(df):
    df['EMA20']=df['Close'].ewm(span=20).mean()
    df['EMA50']=df['Close'].ewm(span=50).mean()
    df['EMA200']=df['Close'].ewm(span=200).mean()
    df['VWAP']=(df['Close']*df['Volume']).cumsum()/df['Volume'].cumsum() if df['Volume'].sum()!=0 else df['Close'].ewm(span=20).mean()
    df['Volx']=(df['Volume']/df['Volume'].rolling(20).mean()).fillna(1.0)
    delta=df['Close'].diff()
    gain=delta.where(delta>0,0).rolling(14).mean()
    loss=-delta.where(delta<0,0).rolling(14).mean()
    df['RSI']=100-(100/(1+gain/loss))
    df['ATR']=(df['High']-df['Low']).rolling(14).mean()
    df['HH']=df['High'].rolling(5).max()
    df['LL']=df['Low'].rolling(5).min()
    return df.bfill()
def get_data(sym):
    df1=yf.download(sym,period="5d",interval="5m",progress=False,auto_adjust=True)
    if isinstance(df1.columns,pd.MultiIndex): df1.columns=df1.columns.get_level_values(0)
    if len(df1)<100: return None,None
    df5=df1.copy()
    df15=df1.resample('15min').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
    return add_ind(df5), add_ind(df15)
def check_triple_top(df):
    last60=df.iloc[-60:]
    highs=last60['High'].nlargest(5).values
    if abs(highs[0]-highs[1])/highs[0] < 0.012 and abs(highs[1]-highs[2])/highs[1] < 0.012:
        neckline = last60['Low'].nsmallest(10).mean()
        breakdown = df.iloc[-1]['Close'] < neckline
        return True, neckline, highs[0]
    return False,0,0
def check_double_top(df):
    last40=df.iloc[-40:]
    h1=last40['High'].max()
    recent_highs = last40['High'].rolling(10).max().dropna().values[-5:]
    if len(recent_highs)>=2 and abs(recent_highs[-1]-recent_highs[-2])/recent_highs[-1] < 0.01:
        return True, h1
    return False,0
def check_demand_zones(df):
    last=df.iloc[-1]; prev=df.iloc[-2]
    last50=df.iloc[-50:]
    demand_low = last50['Low'].min()
    demand_zone = last['Low'] <= demand_low * 1.01
    order_block = prev['Close'] < prev['Open'] and last['Close'] > last['Open'] and last['Close'] > last50['High'].mean()
    liquidity_sweep = last50['Low'].min() < df.iloc[-60:-20]['Low'].min() and last['Close'] > last50['Low'].min()*1.005
    return demand_zone, order_block, liquidity_sweep
def check_breakout_continuation(df):
    df_last = df.iloc[-30:]
    trend_up = df_last['Close'].iloc[-1] > df_last['Close'].iloc[0] and df['EMA20'].iloc[-1] > df['EMA50'].iloc[-1]
    recent_high = df_last['High'].max()
    curr = df.iloc[-1]['Close']
    distribution = curr < recent_high * 0.97 and curr > recent_high * 0.93
    return trend_up, distribution
def run_for(sym,name,gap):
    df5,df15=get_data(sym)
    if df5 is None: return None
    last=df5.iloc[-1]; prev=df5.iloc[-2]
    t15=df15.iloc[-1]
    atr=float(last['ATR']); sl=int(round(atr))
    if sl<18: sl=20
    is_triple, neckline, triple_top_val = check_triple_top(df5)
    is_double, double_top_val = check_double_top(df5)
    demand_zone, order_block, breaker_block = check_demand_zones(df5)
    trend_up, distribution = check_breakout_continuation(df5)
    side=None; pattern=None; future=None; T1=T2=T3=0
    if is_triple and last['Close'] < neckline:
        if last['Close'] > neckline*0.995 and last['Close'] < neckline*1.01:
            pattern="TRIPLE TOP"; side="PE"
            future="Breakdown + Pullback complete, ab Patient SELL se Move Down ayega (Photo 2 wala)"
            T1=sl*2; T2=sl*4; T3=200
    elif is_double and distribution and last['Close'] < last['VWAP']:
        pattern="DOUBLE TOP DIST"; side="PE"
        future="New High Fail + Distribution Box + Break. Ab Move Down confirm (Photo 1 Chart 2)"
        T1=sl*2; T2=sl*3; T3=150
    elif (demand_zone or order_block or breaker_block) and last['Close'] > last['VWAP'] and last['EMA20'] > last['EMA50'] and last['RSI']>50:
        if breaker_block:
            pattern="BREAKER BLOCK"; future="Liquidity Sweep + Breaker Block. Fake breakdown ke baad ab Reversal Up (Photo 3 - 4th)"
        elif order_block:
            pattern="ORDER BLOCK"; future="Resistance ka Order Block, ab Demand se Continuation Up (Photo 3 - 3rd)"
        else:
            pattern="DEMAND ZONE"; future="Demand Zone se Buyer Entry, ab Strong Bullish Move (Photo 3 - 1st)"
        side="CE"
        T1=60; T2=100; T3=200
    elif trend_up and last['Close'] > prev['High'] and last['Volx']>1.5 and last['RSI']>55:
        pattern="BREAKOUT CONT"; side="CE"
        future="HHs & HLs + Break + 50% Distribution tod diya. Ab Strong Bullish Move Continue hoga"
        T1=60; T2=120; T3=200
    else:
        last20_range = df5.iloc[-20:]['High'].max() - df5.iloc[-20:]['Low'].min()
        if last20_range < atr*2:
            if last['Close'] < last['EMA50']:
                pattern="CONSOLIDATION"; side="PE"
                future="Tight Range Consolidation + Fakeout + Break. Ab Reversal Down (Photo 1 Chart 4)"
                T1=sl*2; T2=sl*3; T3=150
    if pattern is None: return None
    strike=int(round(last['Close']/gap)*gap)
    if can_send(name,f"{strike} {side}",side):
        icon = "👑" if "TRIPLE" in pattern else "💎" if "DEMAND" in pattern or "BLOCK" in pattern else "🔥"
        msg = f"""*{icon} {icon} {icon} {pattern} {side} {icon} {icon} {icon}*
━━━━━━━━━━━━━━━━━━━━
📅 `{datetime.now(IST).strftime('%d %b %I:%M %p')}` | `{name}`

*📊 MARKET STRUCTURE*
├─ 15M: {'🟢 UP' if t15['EMA20']>t15['EMA50'] else '🔴 DOWN'} | VWAP: {'🟢' if last['Close']>last['VWAP'] else '🔴'}
├─ RSI: *{round(last['RSI'],1)}* | Vol: *{round(float(last['Volx']),1)}x* | ATR: *{round(atr,1)}*
├─ Pattern: *{pattern}*
└─ Zone: *{'TRIPLE TOP @ '+str(int(triple_top_val)) if is_triple else 'DEMAND' if demand_zone else 'ORDER/BREAKER' if order_block or breaker_block else 'BREAKOUT'}*

━━━━━━━━━━━━━━━━━━━━
*🔮 AANE WALA CANDLE KYA KAREGA?*
`{future}`

━━━━━━━━━━━━━━━━━━━━
*🎯 TRADE SETUP*
💎 STRIKE: *{strike} {side}*
💰 ENTRY: *CURRENT PRICE PE LO*
🛑 SL: *{sl} Pts* (ATR Pure)

🎯 T1: *+{T1} Pts* (50% Book)
🎯 T2: *+{T2} Pts* (30% Book) 
🎯 T3: *+{T3} Pts* (Maha Target)

💡 *Logic:* T1 pe SL Cost pe, T2 pe Trail
━━━━━━━━━━━━━━━━━━━━
⚡️ *PROFITABLE TRADERS AI - 101%*
"""
        send_tg(msg); mark_sent(name,f"{strike} {side}",side); return True
    return None

if __name__=="__main__":
    a=run_for("^NSEI","NIFTY",50)
    b=run_for("^BSESN","SENSEX",100)
    if not a and not b:
        send_tg(f"✅ *BOT LIVE* - `{datetime.now(IST).strftime('%H:%M')}`\nScanning: Breakout, Double/Triple Top, Demand/Order/Breaker Block, Consolidation Fakeout... No Setup")
