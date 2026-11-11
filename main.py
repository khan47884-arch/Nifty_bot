import yfinance as yf
import pandas as pd
import numpy as np
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
SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN", "BEL": "BEL.NS"}
LOT = {"NIFTY": 65, "SENSEX": 20, "BEL": 3500}
already_sent = set()
daily_trades = []
exit_sent = False
def clean_df(df):
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()
    df['Dt'] = pd.to_datetime(df.iloc[:,0])
    try: df['Dt'] = df['Dt'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    except: pass
    return df
def calc_vwap(df):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    return (tp * df['Volume']).cumsum() / df['Volume'].cumsum()
def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))
def get_15m_levels(sym):
    try:
        today = datetime.now(IST).date()
        df15 = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
        df15 = clean_df(df15); df15 = df15[df15['Dt'].dt.date==today]
        if len(df15) < 1: return None, None
        first = df15.iloc[0]
        return float(first['High']), float(first['Low'])
    except Exception as e:
        print("15m Level Fail", e)
        return None, None
def get_strike(name, entry):
    if name=="NIFTY": return int(round(entry/50)*50)
    if name=="SENSEX": return int(round(entry/100)*100)
    return int(round(entry/5)*5)
def check_one(name, sym):
    try:
        high15, low15 = get_15m_levels(sym)
        if high15 is None: return
        mid15 = (high15 + low15) / 2
        box_range = high15 - low15
        today = datetime.now(IST).date()
        df5 = yf.download(sym, period="2d", interval="5m", progress=False, auto_adjust=True)
        df5 = clean_df(df5); df5 = df5[df5['Dt'].dt.date==today]
        if len(df5) < 30: return
        df5["VWAP"] = calc_vwap(df5)
        df5["AvgVol"] = df5["Volume"].rolling(window=20).mean()
        df5["RSI"] = calc_rsi(df5["Close"])
        curr = df5.iloc[-1]; prev_c = df5.iloc[-2]
        o = float(curr['Open']); h = float(curr['High']); l = float(curr['Low']); last_price = float(curr['Close'])
        po = float(prev_c['Open']); pc = float(prev_c['Close']); ph = float(prev_c['High']); pl = float(prev_c['Low'])
        prev2_c = df5.iloc[-3]
        vwap = float(curr['VWAP']); vol_now = float(curr['Volume']); vol_avg = float(curr['AvgVol']) if not pd.isna(curr['AvgVol']) else vol_now
        vol_strong = vol_now > vol_avg * 1.2
        rsi = float(curr['RSI']) if not pd.isna(curr['RSI']) else 50
        rsi_prev = float(df5.iloc[-2]['RSI']) if not pd.isna(df5.iloc[-2]['RSI']) else 50
        rsi_up = rsi > rsi_prev
        rsi_down = rsi < rsi_prev
        body = abs(last_price - o)
        rng = h - l if h > l else 1
        # CANDLE PATTERNS - 5 MIN
        bull_engulf = pc < po and last_price > o and last_price > po and o < pc
        bear_engulf = pc > po and last_price < o and last_price < po and o > pc
        hammer = (min(o, last_price) - l) > 2 * body and body > 0
        shoot_star = (h - max(o, last_price)) > 2 * body and body > 0
        strong_bull = last_price > o and body > rng * 0.6
        strong_bear = last_price < o and body > rng * 0.6
        first_green = last_price > o and pc < po
        first_red = last_price < o and pc > po
        # ============ FINAL LOGIC - AKHRI BAAR ============
        # RULE 1: UPAR SE NEECHE AA RAHA HAI
        # Bearish candle bani + RSI neeche muda = PUT CHAHIYE
        # Resistance pe ya Resistance se neeche, Box ke andar bhi
        upar_se_neeche_put = (bear_engulf or shoot_star or strong_bear or first_red) and rsi_down and last_price < o and h >= mid15 - box_range * 0.10
        # RULE 2: SUPPORT TOD KE NEECHE GAYA = PUT RAHEGI
        support_tod_put = pc >= low15 and last_price < low15 and (bear_engulf or strong_bear or first_red or rsi_down)
        # RULE 3: SUPPORT TOD KE NEECHE NAHI GAYA + SUPPORT PE BULLISH CANDLE
        # Pehli GREEN candle + RSI upar muda + 5-min = CALL
        # SL = Previous Candle ka LOW
        support_pe_call = l <= low15 + box_range * 0.15 and last_price > low15 and (bull_engulf or hammer or strong_bull or first_green) and rsi_up and last_price > o
        # RULE 4: MID SE REJECTION = PUT / MID SE SUPPORT = CALL
        mid_reject_put = h >= mid15 - 5 and h <= mid15 + 10 and (bear_engulf or shoot_star or strong_bear) and rsi_down and last_price < o
        mid_support_call = l <= mid15 + 5 and l >= mid15 - 10 and (bull_engulf or hammer or strong_bull or first_green) and rsi_up and last_price > o
        # RULE 5: BREAKOUT
        break_call = pc <= high15 and last_price > high15
        # VOLUME BLAST
        vol_blast = vol_now > vol_avg * 2.0
        if vol_blast:
            key_v = f"{today}_{name}_VOLBLAST_{str(curr['Dt'])}"
            if key_v not in already_sent:
                tg(f"💥 VOLUME BLAST - {name} 💥\n📊 Price: {last_price:.2f}\n📊 Volume: {vol_now:.0f} vs Avg {vol_avg:.0f} (2x+)\n⚠️ Taiyar Raho - Bada Move Aane Wala Hai\nResistance: {high15:.2f} / Mid: {mid15:.2f} / Support: {low15:.2f}")
                already_sent.add(key_v)
        call_cond = support_pe_call or mid_support_call or break_call
        put_cond = upar_se_neeche_put or support_tod_put or mid_reject_put
        if support_pe_call: reason = "Support pe Bullish Candle + RSI UP - Pehli GREEN Candle"
        elif mid_support_call: reason = "Mid se Support + Bullish Candle + RSI UP"
        elif break_call: reason = "Resistance Tod ke UPAR"
        else: reason = "CALL"
        if upar_se_neeche_put: reason_p = "Upar se Neeche - Bearish Candle + RSI DOWN"
        elif support_tod_put: reason_p = "Support Tod ke NEECHE - PUT Rahegi"
        elif mid_reject_put: reason_p = "Mid se Rejection - PUT"
        else: reason_p = "PUT"
        if call_cond:
            key = f"{today}_{name}_CALL_{str(curr['Dt'])}"
            if key not in already_sent:
                strike = get_strike(name, last_price)
                # CALL SL = PREVIOUS CANDLE KA LOW - FINAL RULE
                sl = round(pl, 2)
                tgt_pts = 30 if name=="BEL" else (100 if name=="NIFTY" else 200)
                target = round(last_price + tgt_pts, 2); profit_rs = tgt_pts * LOT[name]
                msg = f"👑 CALL - V18 FINAL 👑\n📊 {name} - CALL\n📈 Box: High {high15:.2f} / Mid {mid15:.2f} / Low {low15:.2f}\n💥 {reason} ✅\n📊 RSI {rsi:.0f} UP ✅ | VWAP {vwap:.2f}\n📊 Volume {'TEZ' if vol_strong else 'OK'} ✅\n💰 Entry {strike}-CE @ {last_price:.2f}\n🛑 SL: {sl} (Prev Candle Low)\n🎯 Target: {target} (+{tgt_pts} pts = +Rs {profit_rs})"
                tg(msg); already_sent.add(key); daily_trades.append([name,"CALL",last_price,sl,target,tgt_pts,profit_rs]); return
        if put_cond:
            key = f"{today}_{name}_PUT_{str(curr['Dt'])}"
            if key not in already_sent:
                strike = get_strike(name, last_price)
                # PUT SL = PREVIOUS CANDLE KA HIGH
                sl = round(ph, 2)
                tgt_pts = 30 if name=="BEL" else (100 if name=="NIFTY" else 200)
                target = round(last_price - tgt_pts, 2); profit_rs = tgt_pts * LOT[name]
                msg = f"👑 PUT - V18 FINAL 👑\n📊 {name} - PUT\n📉 Box: High {high15:.2f} / Mid {mid15:.2f} / Low {low15:.2f}\n💥 {reason_p} ✅\n📊 RSI {rsi:.0f} DOWN ✅ | VWAP {vwap:.2f}\n📊 Volume {'TEZ' if vol_strong else 'OK'} ✅\n💰 Entry {strike}-PE @ {last_price:.2f}\n🛑 SL: {sl} (Prev Candle High)\n🎯 Target: {target} (-{tgt_pts} pts = +Rs {profit_rs})"
                tg(msg); already_sent.add(key); daily_trades.append([name,"PUT",last_price,sl,target,tgt_pts,profit_rs]); return
    except Exception as e: print(name, e)
def send_daily_report():
    n_pts=0; s_pts=0; b_pts=0; tot=0; lines=""
    for t in daily_trades:
        name,typ,entry,sl,target,pts,rs=t
        if name=="NIFTY": n_pts+=pts
        elif name=="SENSEX": s_pts+=pts
        else: b_pts+=pts
        tot+=rs; lines+=f"{name} {typ}: +{pts} pts x {LOT[name]} = +Rs {rs}\n"
    if not lines: lines="Aaj koi Trade nahi bana - NO TRADE\n"
    tg(f"📊 V18 DAILY REPORT - FINAL 📊\n━━━━━━━━━━━━━━━━\n{lines}━━━━━━━━━━━━━━━━\nNIFTY Net: +{n_pts} pts\nSENSEX Net: +{s_pts} pts\nBEL Net: +{b_pts} pts\nTOTAL: +Rs {tot} (1 Lot Each)")
tg("✨ Option Bond 💥 V18 FINAL BOT ON ✨\n━━━━━━━━━━━━━━━━\n✅ FINAL LOCK V18\n📦 15m Box + 5m Trade\n📊 Upar se Neeche Bearish+RSI DOWN=PUT\n📊 Support Toda=PUT Rahegi\n📊 Support pe Pehli GREEN+RSI UP=CALL | SL=Prev Candle Low\n👀 BEL + NIFTY + SENSEX")
print("BOT V18 FINAL STARTED", datetime.now(IST))
start_time=time.time()
while True:
    now=datetime.now(IST); is_day=(now.weekday()<5)
    is_market=is_day and ((now.hour==9 and now.minute>=30) or (now.hour>9 and now.hour<15) or (now.hour==15 and now.minute<=15))
    if is_market:
        for name,sym in SYMBOLS.items():
            check_one(name,sym); time.sleep(1)
    if is_day and now.hour==15 and now.minute>=15 and not exit_sent:
        send_daily_report(); tg("✨ Option Bond 💥 EXIT ✨\n━━━━━━━━━━━━━━━━\n⏰ 3:15 HO GAYA\n❌ Trade Kaat Do"); exit_sent=True; break
    if time.time()-start_time>30000: break
    time.sleep(60)
