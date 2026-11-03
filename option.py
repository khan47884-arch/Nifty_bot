import yfinance as yf, requests, os, json, time
from datetime import datetime
import pytz
LAST_FILE = "last_trade.json"
IST = pytz.timezone('Asia/Kolkata')

def can_send(k):
    if not os.path.exists(LAST_FILE): return True
    try:
        d=json.load(open(LAST_FILE))
        if time.time()-d.get(k,0)<300: return False
    except: pass
    return True

def mark_sent(k):
    d={}
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

def get_data(sym, interval):
    try:
        df=yf.download(sym, period="2d", interval=interval, progress=False, auto_adjust=True)
        if hasattr(df.columns, 'get_level_values'):
            try: df.columns=df.columns.get_level_values(0)
            except: pass
        df=df.dropna()
        if len(df)<40: return None
        df['EMA9']=df['Close'].ewm(span=9).mean()
        df['EMA20']=df['Close'].ewm(span=20).mean()
        df['EMA50']=df['Close'].ewm(span=50).mean()
        delta=df['Close'].diff()
        gain=delta.where(delta>0,0).rolling(14).mean()
        loss=-delta.where(delta<0,0).rolling(14).mean()
        df['RSI']=100-(100/(1+gain/loss))
        df['VolSMA']=df['Volume'].rolling(20).mean()
        df['Volx']=df['Volume']/df['VolSMA']
        return df.bfill()
    except: return None

def detect_pattern(df):
    last=df.iloc[-1]; prev=df.iloc[-2]
    body=abs(last['Close']-last['Open'])
    rng=last['High']-last['Low']
    if rng==0: return "NO PATTERN"
    upper=last['High']-max(last['Close'],last['Open'])
    lower=min(last['Close'],last['Open'])-last['Low']
    if lower > body*1.2: return "HAMMER(BULLISH)"
    if upper > body*1.2: return "INVERTED HAMMER(BEARISH)"
    if last['Close']>last['Open'] and last['Close']>prev['High']: return "BREAKOUT BULL"
    if last['Close']<last['Open'] and last['Close']<prev['Low']: return "BREAKDOWN BEAR"
    return "MOMENTUM"

def run_for(sym,name,gap):
    df5=get_data(sym,"5m")
    df15=get_data(sym,"15m")
    if df5 is None or df15 is None: return False
    last5=df5.iloc[-1]; prev5=df5.iloc[-2]
    last15=df15.iloc[-1]; prev15=df15.iloc[-2]
    rsi5=float(last5['RSI']); rsi15=float(last15['RSI'])
    vol5=float(last5['Volx']); vol15=float(last15['Volx'])
    
    up15_fast = last15['Close']>last15['EMA9'] and last15['EMA9']>last15['EMA20']
    up15_slow = last15['Close']>last15['EMA20']
    down15_fast = last15['Close']<last15['EMA9'] and last15['EMA9']<last15['EMA20']
    down15_slow = last15['Close']<last15['EMA20']
    up15 = up15_fast or up15_slow
    down15 = down15_fast or down15_slow
    if not up15 and not down15:
        up15 = last5['Close'] > last5['EMA20']
        down15 = last5['Close'] < last5['EMA20']

    ce_break_5 = last5['Close'] > prev5['High']
    pe_break_5 = last5['Close'] < prev5['Low']
    ce_break_15 = last15['Close'] > prev15['High']
    pe_break_15 = last15['Close'] < prev15['Low']
    
    liq_sweep_5 = last5['High'] > prev5['High']*1.0005 or last5['Low'] < prev5['Low']*0.9995
    liq_sweep_15 = last15['High'] > prev15['High']*1.0005 or last15['Low'] < prev15['Low']*0.9995
    
    pat5=detect_pattern(df5); pat15=detect_pattern(df15)
    hammer_5 = "HAMMER" in pat5; hammer_15 = "HAMMER" in pat15

    side=None
    if ce_break_5 or ce_break_15 or (up15 and vol5>1.0): side="CE"
    if pe_break_5 or pe_break_15 or (down15 and vol5>1.0): 
        if side=="CE" and last5['Close']<prev5['Low']: side="PE"
        elif side is None: side="PE"
    if side is None: return False

    score=0
    if ce_break_5 or pe_break_5: score+=1
    if ce_break_15 or pe_break_15: score+=1
    if vol5>=1.0: score+=1
    if hammer_5 or hammer_15: score+=1
    if liq_sweep_5 or liq_sweep_15: score+=1
    if vol5>=1.8: score+=2

    tier="GOLD"
    if score>=3: tier="DIAMOND"
    if score>=4: tier="PLATINUM"
    if score>=6: tier="💥💥 NUCLEAR PLATINUM 💥💥"

    strike=int(round(last5['Close']/gap)*gap)
    key=f"{name}_{strike}_{side}"
    if not can_send(key): return False

    spot=float(last5['Close'])
    sl_pts = 50 if "PLATINUM" in tier else 40
    tgt_pts = 80 if "NUCLEAR" in tier else 50

    sl = spot-sl_pts if side=="CE" else spot+sl_pts
    tgt1 = spot+tgt_pts if side=="CE" else spot-tgt_pts
    tgt2 = spot+(tgt_pts*2) if side=="CE" else spot-(tgt_pts*2)

    break_tf = "5M" if ce_break_5 or pe_break_5 else "15M"
    if (ce_break_5 or pe_break_5) and (ce_break_15 or pe_break_15): break_tf="5M+15M"
    
    liq_tf = ""
    if liq_sweep_5 and liq_sweep_15: liq_tf="5M+15M SWEEP"
    elif liq_sweep_5: liq_tf="5M SWEEP"
    elif liq_sweep_15: liq_tf="15M SWEEP"
    else: liq_tf="NO - But Vol Active"

    msg=f"""💣 NIFTY OPTION BOND [{tier}]
🎯 {name} {strike} {side} BUY - {break_tf} BREAKOUT
🕯️ 5M:{pat5} | 15M:{pat15}
📊 Spot:{spot:.0f} EMA9:{last15['EMA9']:.0f} EMA20:{last15['EMA20']:.0f} {'BULL ✅' if up15 else 'BEAR ✅'}
📈 RSI INFO ONLY: 5M:{rsi5:.0f} 15M:{rsi15:.0f} {'(OVERBUT TRADE ON)' if rsi5>70 or rsi15>70 else ''}
💧 Liquidity: {liq_tf} | Vol: {vol5:.1f}x {vol15:.1f}x | Hammer: {'YES' if hammer_5 or hammer_15 else 'NO'}
💥 S/R Break: {break_tf} -> {prev5['High']:.0f if side=='CE' else prev5['Low']:.0f} TODA
💰 Entry:{spot:.0f} SL:{sl:.0f} (-{sl_pts}) 
🎯 TGT1:{tgt1:.0f} (+{tgt_pts}) TGT2:{tgt2:.0f}"""

    send_tg(msg); mark_sent(key); return True

if __name__=="__main__":
    run_for("^NSEI","NIFTY",50)
    time.sleep(2)
    run_for("^BSESN","SENSEX",100)
