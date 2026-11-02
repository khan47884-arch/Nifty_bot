import yfinance as yf, requests, os, json, time
from datetime import datetime
import pytz
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

def get_fast(sym, interval):
    try:
        df=yf.download(sym, period="2d", interval=interval, progress=False, auto_adjust=True, threads=True)
        if hasattr(df.columns, 'get_level_values'):
            try: df.columns=df.columns.get_level_values(0)
            except: pass
        df=df.dropna()
        if len(df)<20: return None
        df['EMA20']=df['Close'].ewm(span=20).mean()
        df['EMA50']=df['Close'].ewm(span=50).mean()
        df['VWAP']=df['Close'].rolling(20).mean()
        delta=df['Close'].diff()
        gain=delta.where(delta>0,0).rolling(14).mean()
        loss=-delta.where(delta<0,0).rolling(14).mean()
        df['RSI']=100-(100/(1+gain/loss))
        df['ATR']=(df['High']-df['Low']).rolling(14).mean()
        df['Volx']=(df['Volume']/df['Volume'].rolling(20).mean()).fillna(1.0)
        return df.bfill()
    except: return None

def run_for(sym,name,gap):
    df5=get_fast(sym,"5m")
    df15=get_fast(sym,"15m")
    if df5 is None or df15 is None: return False
    last5=df5.iloc[-1]; prev5=df5.iloc[-2]
    last15=df15.iloc[-1]
    rsi5=float(last5['RSI']); rsi15=float(last15['RSI'])
    sl=int(round(float(last5['ATR'])))
    if sl<20: sl=20
    if sl>40: sl=40
    up15 = last15['Close']>last15['EMA20'] and last15['EMA20']>last15['EMA50']
    down15 = last15['Close']<last15['EMA20'] and last15['EMA20']<last15['EMA50']
    ce_break = last5['Close']>prev5['High']
    pe_break = last5['Close']<prev5['Low']
    side=None
    if up15 and ce_break and 50<=rsi15<=70 and 50<=rsi5<=75:
        side="CE"
    elif down15 and pe_break and 30<=rsi15<=60 and 30<=rsi5<=60:
        side="PE"
    if side is None: return False
    strike=int(round(last5['Close']/gap)*gap)
    if can_send(name,f"{strike} {side}",side):
        msg=f"""🚀 {name} {side} - 15M TREND + 5M BREAKOUT
📅 {datetime.now(IST).strftime('%d-%m %H:%M')} | {name}: {last5['Close']:.0f}
📈 15M: {'UP ✅' if up15 else 'DOWN ✅'} RSI:{rsi15:.0f} | 5M RSI:{rsi5:.0f} Vol:{float(last5['Volx']):.1f}x
💥 BREAK: {last5['Close']:.0f} vs {prev5['High']:.0f if side=='CE' else prev5['Low']:.0f}
🎯 STRIKE: {strike} {side}
💰 ENTRY: CURRENT PRICE PE LO
🛑 SL: {sl} Pts (ATR Pure)

🎯 T1: +60 Pts (50% Book)
🎯 T2: +100 Pts (30% Book)
🎯 T3: +200 Pts (Maha Target)

⚡ PROFITABLE TRADERS AI - 101%"""
        send_tg(msg); mark_sent(name,f"{strike} {side}",side); return True
    return False

if __name__=="__main__":
    send_tg(f"""🔴 BOT LIVE - {datetime.now(IST).strftime('%d-%m %H:%M:%S')}
✅ Connection OK - Checking Market...""")
    time.sleep(1)
    found1=run_for("^NSEI","NIFTY",50)
    time.sleep(1)
    found2=run_for("^BSESN","SENSEX",100)
    if not found1 and not found2:
        send_tg(f"""ℹ️ {datetime.now(IST).strftime('%d-%m %H:%M')} No Breakout
📊 Abhi koi signal nahi
✅ Bot ACTIVE hai
⏰ 9:15 AM pe auto signal ayega""")
