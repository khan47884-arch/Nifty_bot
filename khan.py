import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, time
import pytz
IST = pytz.timezone('Asia/Kolkata')

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

INDEX_SYMBOLS = {"SENSEX": "^BSESN", "BANKNIFTY": "^NSEBANK"}

SENT_FILE = "sent.txt"

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE) as f:
            return set(f.read().splitlines())
    return set()

def save_sent(key):
    with open(SENT_FILE, "a") as f:
        f.write(key + "\n")

def send_telegram(msg, key=None):
    if key:
        sent = load_sent()
        if key in sent:
            return False
    if not BOT_TOKEN or not CHAT_ID:
        print(msg)
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        if r.status_code == 200:
            if key:
                save_sent(key)
            return True
    except Exception as e:
        print("Telegram Error:", e)
    return False

def send_telegram_photo(photo_bytes, caption, key=None):
    if key:
        sent = load_sent()
        if key in sent:
            return False
    if not BOT_TOKEN or not CHAT_ID:
        print(caption)
        return False
    try:
        files = {'photo': ('chart.png', photo_bytes, 'image/png')}
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={"chat_id": CHAT_ID, "caption": caption}, files=files, timeout=30)
        print("TG PHOTO:", r.status_code)
        if r.status_code == 200 and key:
            save_sent(key)
            return True
    except Exception as e:
        print("TG Photo Fail", e)
    return False

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calc_vwap(df):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    return (tp * df['Volume']).cumsum() / (df['Volume'].cumsum() + 1e-9)

def clean_df(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    try:
        df['Datetime'] = df['Datetime'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    except: pass
    return df

def get_index_strike(name, entry):
    if name=="SENSEX": return int(round(entry/100)*100)
    if name=="BANKNIFTY": return int(round(entry/100)*100)
    return int(round(entry/5)*5)

def detect_index_breakout(df5):
    try:
        if len(df5) < 20: return None, None, None, ""
        data = df5.reset_index(drop=True)
        curr = data.iloc[-1]
        curr_close = float(curr['Close'])
        for box_len in [8, 7, 6, 5]:
            box = data.iloc[-1-box_len:-1]
            if len(box) < 5: continue
            box_high = float(box['High'].max())
            box_low = float(box['Low'].min())
            box_range = box_high - box_low
            if box_range <= 0: continue
            before = data.iloc[-1-box_len-8:-1-box_len]
            if len(before) < 5: continue
            move_high = float(before['High'].max())
            move_low = float(before['Low'].min())
            move_range = move_high - move_low
            if move_range < box_range * 1.8: continue
            if box_range > move_range * 0.5: continue
            move_start = float(before.iloc[0]['Close'])
            move_end = float(before.iloc[-1]['Close'])
            move_up = move_end > move_start
            if curr_close > box_high and move_up:
                return "CALL", box_high, box_low, f"Pehla Move UP + Box {box_low:.0f}-{box_high:.0f} me Ruka + Box Tod ke UPAR Breakout"
            if curr_close < box_low and not move_up:
                return "PUT", box_high, box_low, f"Pehla Move DOWN + Box {box_low:.0f}-{box_high:.0f} me Ruka + Box Tod ke NEECHE Breakdown"
            if curr_close > box_high:
                return "CALL", box_high, box_low, f"Box {box_low:.0f}-{box_high:.0f} me Consolidation + Box Tod ke UPAR Breakout"
            if curr_close < box_low:
                return "PUT", box_high, box_low, f"Box {box_low:.0f}-{box_high:.0f} me Consolidation + Box Tod ke NEECHE Breakdown"
            return None, box_high, box_low, ""
        return None, None, None, ""
    except Exception as e:
        print("Index Box Fail", e)
        return None, None, None, ""

def make_index_chart(df5, name, box_high, box_low, entry, typ, candle_name):
    d = df5.tail(60).copy().reset_index(drop=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    fig.patch.set_facecolor('white')
    for i, row in d.iterrows():
        o, h, l, c = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])
        col = 'green' if c >= o else 'red'
        ax1.plot([i, i], [l, h], color=col, linewidth=1)
        ax1.add_patch(plt.Rectangle((i-0.35, min(o, c)), 0.7, abs(c-o)+0.1, color=col, alpha=0.9))
    if box_high is not None and box_low is not None:
        ax1.axhline(box_high, color='blue', linewidth=1.5, linestyle='-', label=f'Box High {box_high:.1f}')
        ax1.axhline(box_low, color='blue', linewidth=1.5, linestyle='-', label=f'Box Low {box_low:.1f}')
        ax1.fill_between([-1, len(d)], box_low, box_high, color='orange', alpha=0.12)
    ax1.axhline(entry, color='black', linewidth=1.5, linestyle='-', label=f'Breakout {entry:.1f}')
    ax1.plot([len(d)-1], [entry], marker='o', markersize=14, markerfacecolor='none', markeredgecolor='orange', markeredgewidth=2)
    ax1.set_title(f"{name} 5m | {typ} | {candle_name} | Box Breakout", fontsize=11, fontweight='bold')
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
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

SIGNAL_COUNT = 0

def check_index(name, sym):
    global SIGNAL_COUNT
    try:
        df5 = yf.download(sym, period="2d", interval="5m", progress=False, auto_adjust=False)
        if df5.empty or len(df5) < 30: return
        df5 = clean_df(df5)
        today = datetime.now(IST).date()
        df5 = df5[df5['Datetime'].dt.date == today].copy()
        if len(df5) < 30: return
        df5['VWAP'] = calc_vwap(df5)
        df5['EMA9'] = df5['Close'].ewm(span=9, adjust=False).mean()
        df5['AvgVol'] = df5['Volume'].rolling(window=20).mean()
        df5['RSI'] = calc_rsi(df5['Close'], 14)
        curr = df5.iloc[-1]; prev_c = df5.iloc[-2]
        o = float(curr['Open']); last_price = float(curr['Close'])
        po = float(prev_c['Open']); pc = float(prev_c['Close'])
        vwap = float(curr['VWAP']); ema9 = float(curr['EMA9']); vol_now = float(curr['Volume']); vol_avg = float(curr['AvgVol']) if not np.isnan(curr['AvgVol']) else vol_now
        vol_strong = vol_now > vol_avg * 1.2
        rsi = float(curr['RSI']) if not np.isnan(curr['RSI']) else 50
        rsi_prev = float(df5.iloc[-2]['RSI']) if not np.isnan(df5.iloc[-2]['RSI']) else 50
        rsi_up = rsi > rsi_prev
        rsi_down = rsi < rsi_prev
        ema_vwap_up = last_price > ema9 and last_price > vwap
        ema_vwap_down = last_price < ema9 and last_price < vwap
        body = abs(last_price - o)
        h = float(curr['High']); l = float(curr['Low']); rng = h - l if h > l else 1
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
        bullish = (bull_engulf or hammer or strong_bull or first_green)
        bearish = (bear_engulf or shoot_star or strong_bear or first_red)
        side, box_high, box_low, reason = detect_index_breakout(df5)
        if side is None: return
        if side == "CALL" and not (ema_vwap_up and rsi_up): return
        if side == "PUT" and not (ema_vwap_down and rsi_down): return
        if side == "CALL" and not bullish and last_price <= o: return
        if side == "PUT" and not bearish and last_price >= o: return
        candle_key = str(curr['Datetime'].strftime("%Y-%m-%d_%H:%M"))
        strike = get_index_strike(name, last_price)
        if side == "CALL":
            SIGNAL_COUNT += 1
            caption = f"👑👑 Khan Sahab/Kohinoor 👑👑\n━━━━━━━━━━━━━━━━━━\n\n📦 BOX READY - BREAKOUT CONFIRM\n\n🟢 CALL - {strike}-CE\n\n📊 15m Trend: UP\n📊 RSI: {rsi:.0f} - Momentum Strong\n✅ EMA 9 Verify - Candle EMA ke UPAR CLOSE\n✅ VWAP se UPAR - Buyer Full Control\n🕯️ Candle: {candle_name}\n📐 Pattern: Move + Consolidation + Breakout\n💥 {reason}\n📊 Volume {'TEZ' if vol_strong else 'OK'} ✅\n\n💰 Entry: {strike}-CE\n━━━━━━━━━━━━━━━━━━"
            img = make_index_chart(df5, name, box_high, box_low, last_price, "CALL", candle_name)
            send_telegram_photo(img, caption, f"{candle_key}_{name}_INDEX_CALL")
        if side == "PUT":
            SIGNAL_COUNT += 1
            caption = f"👑👑 Khan Sahab/Kohinoor 👑👑\n━━━━━━━━━━━━━━━━━━\n\n📦 BOX READY - BREAKOUT CONFIRM\n\n🔴 PUT - {strike}-PE\n\n📊 15m Trend: DOWN\n📊 RSI: {rsi:.0f} - Momentum Strong\n✅ EMA 9 Verify - Candle EMA ke NEECHE CLOSE\n✅ VWAP se NEECHE - Seller Full Control\n🕯️ Candle: {candle_name}\n📐 Pattern: Move + Consolidation + Breakout\n💥 {reason}\n📊 Volume {'TEZ' if vol_strong else 'OK'} ✅\n\n💰 Entry: {strike}-PE\n━━━━━━━━━━━━━━━━━━"
            img = make_index_chart(df5, name, box_high, box_low, last_price, "PUT", candle_name)
            send_telegram_photo(img, caption, f"{candle_key}_{name}_INDEX_PUT")
    except Exception as e:
        print(f"Error Index {name}: {e}")

if __name__ == "__main__":
    print("Khan Sahab Started -", datetime.now(IST))
    for name, sym in INDEX_SYMBOLS.items():
        check_index(name, sym)
    print("Done - Total Signal:", SIGNAL_COUNT)
