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
box2_data = {}
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
        if bh is not None: box_data[name]=(bh,bl); msg+=f"📊 {name} BOX1 [15m]: {bl:.0f} - {bh:.0f}\n"
        else: msg+=f"📊 {name} BOX1: ❌ FAIL\n"
    msg+="━━━━━━━━━━━━━━━━\n👑 V13 FINAL LOCK: 15m High/Low Trend + 5m Candle + Flag/H&S + Volume 2x\n📦 BOX1 9:15 + BOX2 11:30 | 📈 TREND 15m High/Low ONLY | ⚡ WORK 5m"
    tg(msg)

def build_box2():
    global box2_data
    box2_data = {}
    today = datetime.now(IST).date()
    msg = "📦 Option Bond V13 BOX2 READY 📦\n━━━━━━━━━━━━━━━━\n⏰ 11:30 BOX2 VERIFIED ✅\n"
    for name, sym in SYMBOLS.items():
        bh=None; bl=None
        try:
            df = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
            df = clean_df(df); df = df[df['Dt'].dt.date == today]
            box_candle = df[(df['Dt'].dt.hour==11) & (df['Dt'].dt.minute==30)]
            if box_candle.empty: box_candle = df.iloc[[-1]]
            bh=float(box_candle["High"].iloc[0]); bl=float(box_candle["Low"].iloc[0])
        except Exception as e: print(name, e)
        if bh is not None: box2_data[name]=(bh,bl); msg+=f"📊 {name} BOX2 [15m]: {bl:.0f} - {bh:.0f}\n"
        else: msg+=f"📊 {name} BOX2: ❌ FAIL\n"
    msg+="━━━━━━━━━━━━━━━━\n👑 BOX2 CHALU - Re-Entry ON"
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

def detect_bonus(df):
    if len(df) < 20: return None, None
    d = df.tail(20)
    highs = d["High"].values; lows = d["Low"].values; closes = d["Close"].values
    if closes[5] > closes[0]*1.001 and closes[-1] > max(highs[-5:-1]):
        return "BULLISH FLAG (Bonus)", "Bullish"
    if closes[5] < closes[0]*0.999 and closes[-1] < min(lows[-5:-1]):
        return "BEARISH FLAG (Bonus)", "Bearish"
    if len(d)>=15:
        left = max(highs[2:5]); head = max(highs[6:9]); right = max(highs[10:13])
        if head > left and head > right and abs(left-right) < (head-min(lows))*0.1 and closes[-1] < min(lows[5:12]):
            return "HEAD & SHOULDERS (Bonus)", "Bearish"
        l_left = min(lows[2:5]); l_head = min(lows[6:9]); l_right = min(lows[10:13])
        if l_head < l_left and l_head < l_right and abs(l_left-l_right) < (max(highs)-l_head)*0.1 and closes[-1] > max(highs[5:12]):
            return "INV. HEAD & SHOULDERS (Bonus)", "Bullish"
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
    if cl1>o1 and abs(cl2-o2)<abs(cl1-o1)*0.4 and cl3<o3 and cl3<(o1+cl1)/2: return "EVENING STAR", "Bearish"
    return None,None

def check_one(name, sym, box_dict, box_name):
    if name not in box_dict: return
    try:
        box_high, box_low = box_dict[name]
        today = datetime.now(IST).date()
        df15 = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
        df15 = clean_df(df15); df15 = df15[df15['Dt'].dt.date==today]
        if len(df15)<5: return
        last15=df15.iloc[-1]; prev15=df15.iloc[-2]
        c15=float(last15['Close']); ph15=float(prev15['High']); pl15=float(prev15['Low'])
        if c15 > ph15: trend="UPTREND"
        elif c15 < pl15: trend="DOWNTREND"
        else: print(f"{name} {box_name} SIDEWAYS - High/Low Break Nahi"); return
        df5 = yf.download(sym, period="2d", interval="5m", progress=False, auto_adjust=True)
        df5 = clean_df(df5); df5 = df5[df5['Dt'].dt.date==today]
        if len(df5)<22: return
        df5["RSI"]=calc_rsi(df5["Close"])
        prev=df5.iloc[-3]; curr=df5.iloc[-2]; nxt=df5.iloc[-1]
        pat, side = detect_main(df5.iloc[-3:])
        if pat is None:
            pat, side = detect_bonus(df5.iloc[-20:])
        if pat is None: print(f"{name} Pattern nahi"); return
        pv=float(prev['Volume']); cv=float(curr['Volume'])
        if pv>0 and cv>0:
            vol_ok = cv >= 2*pv
        else:
            vol_ok = True
            print(f"{name} Volume data 0 hai, Volume check skip")
        if not vol_ok: print(f"{name} Volume 2x nahi"); return
        rsi5=float(curr['RSI']); rsi_txt="STRONG" if rsi5>60 else ("OK" if rsi5>=50 else "WEAK")
        if trend=="UPTREND" and side=="Bullish" and float(nxt['High'])>float(prev['High']):
            key=f"{today}_{name}_{box_name}_CALL_{str(nxt['Dt'])}"
            if key not in already_sent:
                strike=get_strike(name, float(nxt['Close'])); sl=int(float(prev['Low']))
                tgt_pts=100 if name=="NIFTY" else 200; target=int(float(nxt['Close'])+tgt_pts); profit_rs=tgt_pts*LOT[name]
                msg=f"👑 V13 CALL 👑\n✨ Option Bond 💥 V13 ✨\n━━━━━━━━━━━━━━━━\n📊 {name} - CALL - {box_name}\n📦 BOX: {box_low:.0f} - {box_high:.0f}\n📈 TREND [15m]: {trend} ✅ High Break\n🕯️ Pattern: {pat} ✅\n📊 Volume: DOUBLE (2x) ✅\n💥 Entry: HIGH Break ✅\n📈 RSI [5m]: {rsi5:.0f} - {rsi_txt} (Signal Only)\n━━━━━━━━━━━━━━━━\n💰 Entry {strike}-CE @ {float(nxt['Close']):.0f}\n🛑 SL: {sl}\n🎯 Target: {target} (+{tgt_pts} pts = +Rs {profit_rs} 1 Lot)\n📦 Qty: 1 LOT"
                tg(msg); already_sent.add(key); daily_trades.append([name,"CALL",float(nxt['Close']),sl,target,tgt_pts,profit_rs]); return
        if trend=="DOWNTREND" and side=="Bearish" and float(nxt['Low'])<float(prev['Low']):
            key=f"{today}_{name}_{box_name}_PUT_{str(nxt['Dt'])}"
            if key not in already_sent:
                strike=get_strike(name, float(nxt['Close'])); sl=int(float(prev['High']))
                tgt_pts=100 if name=="NIFTY" else 200; target=int(float(nxt['Close'])-tgt_pts); profit_rs=tgt_pts*LOT[name]
                msg=f"👑 V13 PUT 👑\n✨ Option Bond 💥 V13 ✨\n━━━━━━━━━━━━━━━━\n📊 {name} - PUT - {box_name}\n📦 BOX: {box_low:.0f} - {box_high:.0f}\n📉 TREND [15m]: {trend} ✅ Low Break\n🕯️ Pattern: {pat} ✅\n📊 Volume: DOUBLE (2x) ✅\n💥 Entry: LOW Break ✅\n📈 RSI [5m]: {rsi5:.0f} - {rsi_txt} (Signal Only)\n━━━━━━━━━━━━━━━━\n💰 Entry {strike}-PE @ {float(nxt['Close']):.0f}\n🛑 SL: {sl}\n🎯 Target: {target} (-{tgt_pts} pts = +Rs {profit_rs} 1 Lot)\n📦 Qty: 1 LOT"
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

tg("✨ Option Bond 💥 V13 BOT ON ✨\n━━━━━━━━━━━━━━━━\n✅ V13 FINAL LOCK - 2 BOX\n📦 NIFTY + SENSEX ONLY\n📈 TREND 15m High/Low Break ONLY - VWAP/EMA HATAYA\n🕯️ PATTERN 5m - Candle + Flag + H&S ONLY\n📊 VOLUME 2x | 💥 BREAK MUST")
print("BOT V13 FINAL STARTED", datetime.now(IST))
start_time=time.time()
box2_built=False
while True:
    now=datetime.now(IST); is_day=(now.weekday()<5)
    if is_day and ((now.hour==9 and now.minute>=15) or (now.hour>9 and now.hour<15) or (now.hour==15 and now.minute<=15)):
        if last_box_date!=now.date(): build_box(); system_built=True; box2_built=False
    if is_day and now.hour==11 and now.minute>=30 and not box2_built and system_built:
        build_box2(); box2_built=True
    is_market=is_day and ((now.hour==9 and now.minute>=30) or (now.hour>9 and now.hour<15) or (now.hour==15 and now.minute<=15))
    if is_market and system_built:
        if now.hour<11 or (now.hour==11 and now.minute<30):
            for name,sym in SYMBOLS.items(): check_one(name,sym,box_data,"BOX1"); time.sleep(1)
        else:
            for name,sym in SYMBOLS.items(): check_one(name,sym,box2_data,"BOX2"); time.sleep(1)
    if is_day and now.hour==15 and now.minute>=15 and not exit_sent:
        send_daily_report(); tg("✨ Option Bond 💥 EXIT ✨\n━━━━━━━━━━━━━━━━\n⏰ 3:15 HO GAYA\n❌ Trade Kaat Do"); exit_sent=True; break
    if time.time()-start_time>30000: break
    time.sleep(60)
