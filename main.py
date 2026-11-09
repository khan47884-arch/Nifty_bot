import yfinance as yf
import pandas as pd
import requests, os, time
from datetime import datetime
import pytz
IST = pytz.timezone('Asia/Kolkata')
BOT = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")

def tg(m):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id": CHAT, "text": m}, timeout=20)
        print("TG:", r.status_code)
    except Exception as e: print("TG Fail", e)

SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN"}
LOT = {"NIFTY": 65, "SENSEX": 20}
box_data = {}
already_sent = set()
system_built = False
exit_sent = False
last_box_date = None
daily_trades = []

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calc_vwap_daily(df):
    df = df.copy()
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['TPV'] = df['TP'] * df['Volume']
    df['VWAP'] = df.groupby(df['Dt'].dt.date)['TPV'].cumsum() / df.groupby(df['Dt'].dt.date)['Volume'].cumsum()
    return df.drop(columns=['TP','TPV'])

def clean_df(df):
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()
    df['Dt'] = pd.to_datetime(df.iloc[:,0])
    try: df['Dt'] = df['Dt'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    except: pass
    return df

def build_box():
    global box_data, last_box_date
    box_data = {}
    today = datetime.now(IST).date(); last_box_date = today
    msg = "✨ Option Bond 💥 V13 BOX READY ✨\n━━━━━━━━━━━━━━━━\n⏰ 9:15 - 9:30 BOX VERIFIED ✅\n"
    for name, sym in SYMBOLS.items():
        bh=None; bl=None
        for attempt in range(3):
            try:
                df = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
                df = clean_df(df); df = df[df['Dt'].dt.date == today]
                box_candle = df[(df['Dt'].dt.hour==9) & (df['Dt'].dt.minute==15)]
                if box_candle.empty: box_candle = df.iloc[[0]]
                bh=float(box_candle["High"].iloc[0]); bl=float(box_candle["Low"].iloc[0]); break
            except Exception as e: print(name, e); time.sleep(2)
        if bh is not None: box_data[name]=(bh,bl); msg+=f"📊 {name} BOX [15m]: {bl:.0f} - {bh:.0f}\n"
        else: msg+=f"📊 {name} BOX: ❌ FAIL\n"
    msg+="━━━━━━━━━━━━━━━━\n👑 V13 LOCK: 15m Trend + 5m Pattern (Main + Bonus) + Volume 2x\n📦 BOX 15m | 📈 TREND 15m | ⚡ WORK 5m"
    tg(msg)

def get_strike(name, entry):
    return int(round(entry/50)*50) if name=="NIFTY" else int(round(entry/100)*100)

def gv(c): return float(c["Open"]), float(c["Close"]), float(c["High"]), float(c["Low"])
def is_hammer(c):
    o,cl,h,l=gv(c); body=abs(cl-o); rng=h-l
    return rng!=0 and cl>o and (min(o,cl)-l)>body*2 and (h-max(o,cl))<body*0.5
def is_inv_hammer(c):
    o,cl,h,l=gv(c); body=abs(cl-o); rng=h-l
    return rng!=0 and cl>o and (h-max(o,cl))>body*2 and (min(o,cl)-l)<body*0.5
def is_dragonfly(c):
    o,cl,h,l=gv(c); body=abs(cl-o); rng=h-l
    return rng!=0 and body<rng*0.1 and (min(o,cl)-l)>rng*0.7
def is_shooting(c):
    o,cl,h,l=gv(c); body=abs(cl-o); rng=h-l
    return rng!=0 and cl<o and (h-max(o,cl))>body*2 and (min(o,cl)-l)<body*0.5
def is_hanging(c):
    o,cl,h,l=gv(c); body=abs(cl-o); rng=h-l
    return rng!=0 and cl<o and (min(o,cl)-l)>body*2 and (h-max(o,cl))<body*0.5
def is_grave(c):
    o,cl,h,l=gv(c); body=abs(cl-o); rng=h-l
    return rng!=0 and body<rng*0.1 and (h-max(o,cl))>rng*0.7

def detect_bonus(df):
    if len(df) < 20: return None, None
    d = df.tail(20)
    highs = d["High"].values; lows = d["Low"].values; closes = d["Close"].values
    l1 = min(lows[:8]); l2 = min(lows[-8:])
    mid_high = max(highs[8:12])
    if abs(l1-l2) < (max(highs)-min(lows))*0.08 and closes[-1] > mid_high:
        return "DOUBLE BOTTOM (Bonus)", "Bullish"
    h1 = max(highs[:8]); h2 = max(highs[-8:])
    mid_low = min(lows[8:12])
    if abs(h1-h2) < (max(highs)-min(lows))*0.08 and closes[-1] < mid_low:
        return "DOUBLE TOP (Bonus)", "Bearish"
    if abs(max(highs[-6:])-max(highs[:6])) < (max(highs)-min(lows))*0.08 and min(lows[-6:]) > min(lows[:6]) and closes[-1] > max(highs[-6:]):
        return "ASCENDING TRIANGLE (Bonus)", "Bullish"
    if abs(min(lows[-6:])-min(lows[:6])) < (max(highs)-min(lows))*0.08 and max(highs[-6:]) < max(highs[:6]) and closes[-1] < min(lows[-6:]):
        return "DESCENDING TRIANGLE (Bonus)", "Bearish"
    if closes[5] > closes[0]*1.001 and closes[-1] > max(highs[-5:-1]):
        return "BULLISH FLAG (Bonus)", "Bullish"
    if closes[5] < closes[0]*0.999 and closes[-1] < min(lows[-5:-1]):
        return "BEARISH FLAG (Bonus)", "Bearish"
    if max(highs[:5]) > max(highs[-5:]) and min(lows[:5]) > min(lows[-5:]) and (max(highs[-5:])-min(lows[-5:])) < (max(highs[:5])-min(lows[:5]))*0.6 and closes[-1] > max(highs[-3:]):
        return "FALLING WEDGE (Bonus)", "Bullish"
    if max(highs[:5]) < max(highs[-5:]) and min(lows[:5]) < min(lows[-5:]) and (max(highs[-5:])-min(lows[-5:])) < (max(highs[:5])-min(lows[:5]))*0.6 and closes[-1] < min(lows[-3:]):
        return "RISING WEDGE (Bonus)", "Bearish"
    if len(d)>=15:
        left = max(highs[2:5]); head = max(highs[6:9]); right = max(highs[10:13])
        if head > left and head > right and abs(left-right) < (head-min(lows))*0.1 and closes[-1] < min(lows[5:12]):
            return "HEAD & SHOULDERS (Bonus)", "Bearish"
        l_left = min(lows[2:5]); l_head = min(lows[6:9]); l_right = min(lows[10:13])
        if l_head < l_left and l_head < l_right and abs(l_left-l_right) < (max(highs)-l_head)*0.1 and closes[-1] > max(highs[5:12]):
            return "INV. HEAD & SHOULDERS (Bonus)", "Bullish"
    if (max(highs[-3:])-min(lows[-3:])) < (max(highs[:5])-min(lows[:5]))*0.4:
        if closes[-1] > max(highs[-4:]): return "SYMMETRICAL TRIANGLE UP (Bonus)", "Bullish"
        if closes[-1] < min(lows[-4:]): return "SYMMETRICAL TRIANGLE DOWN (Bonus)", "Bearish"
    return None, None

def detect_main(df5):
    if len(df5)<3: return None,None
    c1=df5.iloc[-3]; c2=df5.iloc[-2]; c3=df5.iloc[-1]
    o1,cl1,h1,l1=gv(c1); o2,cl2,h2,l2=gv(c2); o3,cl3,h3,l3=gv(c3)
    if is_hammer(c3): return "HAMMER", "Bullish"
    if is_inv_hammer(c3): return "INVERTED HAMMER", "Bullish"
    if is_dragonfly(c3): return "DRAGONFLY DOJI", "Bullish"
    if cl1<o1 and abs(cl2-o2)<abs(cl1-o1)*0.4 and cl3>o3 and cl3>(o1+cl1)/2: return "MORNING STAR", "Bullish"
    if is_shooting(c3): return "SHOOTING STAR", "Bearish"
    if is_hanging(c3): return "HANGING MAN", "Bearish"
    if is_grave(c3): return "GRAVESTONE DOJI", "Bearish"
    if cl1>o1 and abs(cl2-o2)<abs(cl1-o1)*0.4 and cl3<o3 and cl3<(o1+cl1)/2: return "EVENING STAR", "Bearish"
    return None,None

def check_one(name, sym):
    if name not in box_data: return
    try:
        box_high, box_low = box_data[name]
        today = datetime.now(IST).date()
        df15 = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
        df15 = clean_df(df15); df15 = df15[df15['Dt'].dt.date==today]
        if len(df15)<5: return
        df15 = calc_vwap_daily(df15)
        df15["EMA20"]=df15["Close"].ewm(span=20, adjust=False).mean()
        df15["EMA50"]=df15["Close"].ewm(span=50, adjust=False).mean()
        last15=df15.iloc[-1]
        c15=float(last15['Close']); v15=float(last15['VWAP']); e20=float(last15['EMA20']); e50=float(last15['EMA50'])
        if c15>v15 and c15>e20 and e20>e50: trend="UPTREND"
        elif c15<v15 and c15<e20 and e20<e50: trend="DOWNTREND"
        else: print(f"{name} SIDEWAYS"); return
        df5 = yf.download(sym, period="2d", interval="5m", progress=False, auto_adjust=True)
        df5 = clean_df(df5); df5 = df5[df5['Dt'].dt.date==today]
        if len(df5)<22: return
        df5["RSI"]=calc_rsi(df5["Close"])
        prev=df5.iloc[-3]; curr=df5.iloc[-2]; nxt=df5.iloc[-1]
        pat, side = detect_main(df5.iloc[:-2])
        if pat is None:
            pat, side = detect_bonus(df5.iloc[:-1])
        if pat is None: print(f"{name} Pattern nahi"); return
        vol_ok = float(curr['Volume']) >= 2*float(prev['Volume']) if float(prev['Volume'])>0 else False
        if not vol_ok: print(f"{name} Volume 2x nahi"); return
        rsi5=float(curr['RSI']); rsi_txt="STRONG" if rsi5>60 else ("OK" if rsi5>=50 else "WEAK")
        if trend=="UPTREND" and side=="Bullish" and float(nxt['High'])>float(prev['High']):
            key=f"{today}_{name}_CALL_{str(nxt['Dt'])}"
            if key not in already_sent:
                strike=get_strike(name, float(nxt['Close'])); sl=int(float(prev['Low']))
                tgt_pts=100 if name=="NIFTY" else 200; target=int(float(nxt['Close'])+tgt_pts); profit_rs=tgt_pts*LOT[name]
                msg=f"👑 V13 CALL 👑\n✨ Option Bond 💥 V13 ✨\n━━━━━━━━━━━━━━━━\n📊 {name} - CALL\n📦 BOX: {box_low:.0f} - {box_high:.0f}\n📈 TREND [15m]: {trend} ✅\n🕯️ Pattern: {pat} ✅\n📊 Volume: DOUBLE (2x) ✅\n💥 Entry: HIGH Break ✅\n📈 RSI [5m]: {rsi5:.0f} - {rsi_txt} (Signal Only)\n━━━━━━━━━━━━━━━━\n💰 Entry {strike}-CE @ {float(nxt['Close']):.0f}\n🛑 SL: {sl}\n🎯 Target: {target} (+{tgt_pts} pts = +Rs {profit_rs} 1 Lot)\n📦 Qty: 1 LOT"
                tg(msg); already_sent.add(key); daily_trades.append([name,"CALL",float(nxt['Close']),sl,target,tgt_pts,profit_rs]); return
        if trend=="DOWNTREND" and side=="Bearish" and float(nxt['Low'])<float(prev['Low']):
            key=f"{today}_{name}_PUT_{str(nxt['Dt'])}"
            if key not in already_sent:
                strike=get_strike(name, float(nxt['Close'])); sl=int(float(prev['High']))
                tgt_pts=100 if name=="NIFTY" else 200; target=int(float(nxt['Close'])-tgt_pts); profit_rs=tgt_pts*LOT[name]
                msg=f"👑 V13 PUT 👑\n✨ Option Bond 💥 V13 ✨\n━━━━━━━━━━━━━━━━\n📊 {name} - PUT\n📦 BOX: {box_low:.0f} - {box_high:.0f}\n📉 TREND [15m]: {trend} ✅\n🕯️ Pattern: {pat} ✅\n📊 Volume: DOUBLE (2x) ✅\n💥 Entry: LOW Break ✅\n📈 RSI [5m]: {rsi5:.0f} - {rsi_txt} (Signal Only)\n━━━━━━━━━━━━━━━━\n💰 Entry {strike}-PE @ {float(nxt['Close']):.0f}\n🛑 SL: {sl}\n🎯 Target: {target} (-{tgt_pts} pts = +Rs {profit_rs} 1 Lot)\n📦 Qty: 1 LOT"
                tg(msg); already_sent.add(key); daily_trades.append([name,"PUT",float(nxt['Close']),sl,target,tgt_pts,profit_rs]); return
    except Exception as e: print(name, e)

def send_daily_report():
    n_pts=0; s_pts=0; tot=0; lines=""
    for t in daily_trades:
        name,typ,entry,sl,target,pts,rs=t
        if name=="NIFTY": n_pts+=pts
        else: s_pts+=pts
        tot+=rs; lines+=f"{name} {typ}: +{pts} pts x {LOT[name]} = +Rs {rs}\n"
    if not lines: lines="Aaj koi Trade nahi bana - NO TRADE\n"
    tg(f"📊 V13 DAILY REPORT - PURA HISAB 📊\n━━━━━━━━━━━━━━━━\n{lines}━━━━━━━━━━━━━━━━\nNIFTY Net: +{n_pts} pts\nSENSEX Net: +{s_pts} pts\nTOTAL: +Rs {tot} (1 Lot Each)\n━━━━━━━━━━━━━━━━\nFormula: NIFTY x 65 | SENSEX x 20")

tg("✨ Option Bond 💥 V13 BOT ON ✨\n━━━━━━━━━━━━━━━━\n✅ V13 + Bonus Pattern Ready\n📦 NIFTY + SENSEX ONLY\n📈 TREND 15m | 🕯️ PATTERN 5m - Main + Bonus 12\n📊 VOLUME 2x | 💥 BREAK MUST")
print("BOT V13 STARTED", datetime.now(IST))
start_time=time.time()
while True:
    now=datetime.now(IST); is_day=(now.weekday()<5)
    if is_day and ((now.hour==9 and now.minute>=15) or (now.hour>9 and now.hour<15) or (now.hour==15 and now.minute<=15)):
        if last_box_date!=now.date(): build_box(); system_built=True
    is_market=is_day and ((now.hour==9 and now.minute>=30) or (now.hour>9 and now.hour<15) or (now.hour==15 and now.minute<=15))
    if is_market and system_built:
        for name,sym in SYMBOLS.items(): check_one(name,sym); time.sleep(1)
    if is_day and now.hour==15 and now.minute>=15 and not exit_sent:
        send_daily_report(); tg("✨ Option Bond 💥 EXIT ✨\n━━━━━━━━━━━━━━━━\n⏰ 3:15 HO GAYA\n❌ Trade Kaat Do"); exit_sent=True; break
    if time.time()-start_time>20000: break
    time.sleep(60)
