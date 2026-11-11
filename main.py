import yfinance as yf
import pandas as pd
import numpy as np
import requests, os, time, io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
def tg_photo(photo_bytes, caption):
    try:
        files = {'photo': ('chart.png', photo_bytes, 'image/png')}
        r = requests.post(f"https://api.telegram.org/bot{BOT}/sendPhoto", data={"chat_id": CHAT, "caption": caption}, files=files, timeout=30)
        print("TG PHOTO:", r.status_code, r.text[:200])
    except Exception as e: print("TG Photo Fail", e)
SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN"}
LOT = {"NIFTY": 65, "SENSEX": 20}
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
def detect_chart_pattern(df5, high15, low15, box_range):
    try:
        recent = df5.tail(30)
        lows = recent['Low'].values
        highs = recent['High'].values
        sup_touches = [x for x in lows if abs(x - low15) <= box_range*0.20]
        res_touches = [x for x in highs if abs(x - high15) <= box_range*0.20]
        if len(sup_touches) >= 2: return "Double Bottom"
        if len(res_touches) >= 2: return "Double Top"
        if len(highs) >= 10:
            h1 = float(np.mean(highs[:5])); h2 = float(np.mean(highs[-5:]))
            l1 = float(np.mean(lows[:5])); l2 = float(np.mean(lows[-5:]))
            if h2 < h1 and l2 < l1: return "Falling Channel"
            if h2 > h1 and l2 > l1: return "Rising Channel"
        return "Box Range"
    except: return "Box Range"
def make_chart(df5, name, high15, low15, mid15, entry, sl, target, typ, candle_name, chart_pattern):
    # Last 60 candles - jaise teri photo me hai
    d = df5.tail(60).copy().reset_index(drop=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    fig.patch.set_facecolor('white')
    # Candles
    for i, row in d.iterrows():
        o, h, l, c = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])
        col = 'green' if c >= o else 'red'
        ax1.plot([i, i], [l, h], color=col, linewidth=1)
        ax1.add_patch(plt.Rectangle((i-0.35, min(o, c)), 0.7, abs(c-o)+0.1, color=col, alpha=0.9))
    # Box Levels - teri photo jaisi blue lines
    ax1.axhline(high15, color='blue', linewidth=1.5, linestyle='-', label=f'Resistance {high15:.1f}')
    ax1.axhline(low15, color='blue', linewidth=1.5, linestyle='-', label=f'Support {low15:.1f}')
    ax1.axhline(mid15, color='orange', linewidth=1, linestyle='--', label=f'Mid {mid15:.1f}')
    # Entry / SL / Target - photo jaisa box
    ax1.axhline(entry, color='black', linewidth=1.5, linestyle='-', label=f'Entry {entry:.1f}')
    if typ == "CALL":
        ax1.axhline(target, color='green', linewidth=1.5, linestyle='--', label=f'Target {target:.1f}')
        ax1.axhline(sl, color='red', linewidth=1.5, linestyle='--', label=f'SL {sl:.1f}')
        ax1.fill_between([-1, len(d)], sl, target, color='green', alpha=0.08)
    else:
        ax1.axhline(target, color='green', linewidth=1.5, linestyle='--', label=f'Target {target:.1f}')
        ax1.axhline(sl, color='red', linewidth=1.5, linestyle='--', label=f'SL {sl:.1f}')
        ax1.fill_between([-1, len(d)], target, sl, color='red', alpha=0.08)
    # Last candle pe circle - teri photo wala yellow circle jaisa
    ax1.plot([len(d)-1], [entry], marker='o', markersize=14, markerfacecolor='none', markeredgecolor='orange', markeredgewidth=2)
    ax1.set_title(f"{name} 5m | {typ} | {candle_name} | {chart_pattern} | Entry {entry:.1f} SL {sl:.1f} Target {target:.1f}", fontsize=11, fontweight='bold')
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    # Volume neeche
    colors = ['green' if float(r['Close']) >= float(r['Open']) else 'red' for _, r in d.iterrows()]
    ax2.bar(range(len(d)), d['Volume'].values, color=colors, alpha=0.7)
    ax2.set_ylabel('Volume')
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    return buf.getvalue()
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
        vwap = float(curr['VWAP']); vol_now = float(curr['Volume']); vol_avg = float(curr['AvgVol']) if not pd.isna(curr['AvgVol']) else vol_now
        vol_strong = vol_now > vol_avg * 1.2
        rsi = float(curr['RSI']) if not pd.isna(curr['RSI']) else 50
        rsi_prev = float(df5.iloc[-2]['RSI']) if not pd.isna(df5.iloc[-2]['RSI']) else 50
        rsi_up = rsi > rsi_prev
        rsi_down = rsi < rsi_prev
        body = abs(last_price - o)
        rng = h - l if h > l else 1
        bull_engulf = pc < po and last_price > o and last_price > po and o < pc
        bear_engulf = pc > po and last_price < o and last_price < po and o > pc
        hammer = (min(o, last_price) - l) > 2 * body and body > 0
        shoot_star = (h - max(o, last_price)) > 2 * body and body > 0
        strong_bull = last_price > o and body > rng * 0.6
        strong_bear = last_price < o and body > rng * 0.6
        first_green = last_price > o and pc < po
        first_red = last_price < o and pc > po
        if bull_engulf: candle_name = "Bullish Engulfing"
        elif bear_engulf: candle_name = "Bearish Engulfing"
        elif hammer: candle_name = "Hammer"
        elif shoot_star: candle_name = "Shooting Star"
        elif strong_bull: candle_name = "Strong Bull Candle"
        elif strong_bear: candle_name = "Strong Bear Candle"
        elif first_green: candle_name = "First Green Candle"
        elif first_red: candle_name = "First Red Candle"
        else: candle_name = "Normal Candle"
        bullish = (bull_engulf or hammer or strong_bull or first_green) and rsi_up
        bearish = (bear_engulf or shoot_star or strong_bear or first_red) and rsi_down
        chart_pattern = detect_chart_pattern(df5, high15, low15, box_range)
        support_pe_call = l <= low15 + box_range*0.15 and last_price > low15 and bullish and last_price > o
        resistance_pe_put = h >= high15 - box_range*0.15 and last_price < high15 and bearish and last_price < o
        break_call = pc <= high15 and last_price > high15 and (bullish or last_price > o)
        break_put = pc >= low15 and last_price < low15 and (bearish or last_price < o)
        mid_support_call = l <= mid15+5 and l >= mid15-10 and bullish and last_price > o
        mid_reject_put = h >= mid15-5 and h <= mid15+10 and bearish and last_price < o
        vol_blast = vol_now > vol_avg * 2.0
        if vol_blast:
            key_v = f"{today}_{name}_VOLBLAST_{str(curr['Dt'])}"
            if key_v not in already_sent:
                tg(f"💥 VOLUME BLAST - {name} 💥\n📊 Price: {last_price:.2f}\n📊 Volume: {vol_now:.0f} vs Avg {vol_avg:.0f} (2x+)\n⚠️ Taiyar Raho - Bada Move Aane Wala Hai\nResistance: {high15:.2f} / Mid: {mid15:.2f} / Support: {low15:.2f}")
                already_sent.add(key_v)
        call_cond = support_pe_call or break_call or mid_support_call
        put_cond = resistance_pe_put or break_put or mid_reject_put
        if support_pe_call: reason = "ANDAR Support pe Bullish + RSI UP - CALL"
        elif break_call: reason = "BAHAR Resistance Tod ke UPAR - Breakout CALL"
        elif mid_support_call: reason = "Mid se Support + Bullish - CALL"
        else: reason = "CALL"
        if resistance_pe_put: reason_p = "ANDAR Resistance pe Bearish + RSI DOWN - PUT"
        elif break_put: reason_p = "BAHAR Support Tod ke NEECHE - Breakdown PUT"
        elif mid_reject_put: reason_p = "Mid se Rejection - PUT"
        else: reason_p = "PUT"
        if call_cond:
            key = f"{today}_{name}_CALL_{str(curr['Dt'])}"
            if key not in already_sent:
                strike = get_strike(name, last_price)
                sl = round(pl, 2)
                tgt_pts = 50 if name=="NIFTY" else 100
                target = round(last_price + tgt_pts, 2); profit_rs = tgt_pts * LOT[name]
                caption = f"👑 CALL - V19 LOCKED 👑\n📊 {name} - CALL\n📈 Box: High {high15:.2f} / Mid {mid15:.2f} / Low {low15:.2f}\n🕯️ Candle: {candle_name} ✅\n📐 Chart Pattern: {chart_pattern} ✅\n💥 {reason} ✅\n📊 RSI {rsi:.0f} UP ✅ | VWAP {vwap:.2f}\n📊 Volume {'TEZ' if vol_strong else 'OK'} ✅\n💰 Entry {strike}-CE @ {last_price:.2f}\n🛑 SL: {sl} (Prev Candle Low)\n🎯 Target: {target} (+{tgt_pts} pts = +Rs {profit_rs})\n📸 Photo me dekh - Entry / SL / Target line bani hai"
                img = make_chart(df5, name, high15, low15, mid15, last_price, sl, target, "CALL", candle_name, chart_pattern)
                tg_photo(img, caption)
                already_sent.add(key); daily_trades.append([name,"CALL",last_price,sl,target,tgt_pts,profit_rs]); return
        if put_cond:
            key = f"{today}_{name}_PUT_{str(curr['Dt'])}"
            if key not in already_sent:
                strike = get_strike(name, last_price)
                sl = round(ph, 2)
                tgt_pts = 50 if name=="NIFTY" else 100
                target = round(last_price - tgt_pts, 2); profit_rs = tgt_pts * LOT[name]
                caption = f"👑 PUT - V19 LOCKED 👑\n📊 {name} - PUT\n📉 Box: High {high15:.2f} / Mid {mid15:.2f} / Low {low15:.2f}\n🕯️ Candle: {candle_name} ✅\n📐 Chart Pattern: {chart_pattern} ✅\n💥 {reason_p} ✅\n📊 RSI {rsi:.0f} DOWN ✅ | VWAP {vwap:.2f}\n📊 Volume {'TEZ' if vol_strong else 'OK'} ✅\n💰 Entry {strike}-PE @ {last_price:.2f}\n🛑 SL: {sl} (Prev Candle High)\n🎯 Target: {target} (-{tgt_pts} pts = +Rs {profit_rs})\n📸 Photo me dekh - Entry / SL / Target line bani hai"
                img = make_chart(df5, name, high15, low15, mid15, last_price, sl, target, "PUT", candle_name, chart_pattern)
                tg_photo(img, caption)
                already_sent.add(key); daily_trades.append([name,"PUT",last_price,sl,target,tgt_pts,profit_rs]); return
    except Exception as e: print(name, e)
def send_daily_report():
    n_pts=0; s_pts=0; tot=0; lines=""
    for t in daily_trades:
        name,typ,entry,sl,target,pts,rs=t
        if name=="NIFTY": n_pts+=pts
        elif name=="SENSEX": s_pts+=pts
        tot+=rs; lines+=f"{name} {typ}: +{pts} pts x {LOT[name]} = +Rs {rs}\n"
    if not lines: lines="Aaj koi Trade nahi bana - NO TRADE\n"
    tg(f"📊 V19 DAILY REPORT - LOCKED 📊\n━━━━━━━━━━━━━━━━\n{lines}━━━━━━━━━━━━━━━━\nNIFTY Net: +{n_pts} pts\nSENSEX Net: +{s_pts} pts\nTOTAL: +Rs {tot} (1 Lot Each)")
tg("✨ Option Bond 💥 V19 LOCKED BOT ON ✨\n━━━━━━━━━━━━━━━━\n✅ FINAL LOCK V19\n📦 15m Box + 5m Entry\n📊 Andar Support=CALL | Andar Resistance=PUT\n📊 Bahar Upar Toda=CALL | Bahar Neeche Toda=PUT\n📸 Ab Har Signal PHOTO ke saath aayega\n👀 NIFTY + SENSEX ONLY")
print("BOT V19 LOCKED STARTED", datetime.now(IST))
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
