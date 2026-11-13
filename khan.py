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
        requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id": CHAT, "text": m}, timeout=20)
    except Exception as e: print("TG ERR", e)

def tg_photo(photo_bytes, caption):
    try:
        files = {'photo': ('chart.png', photo_bytes, 'image/png')}
        requests.post(f"https://api.telegram.org/bot{BOT}/sendPhoto", data={"chat_id": CHAT, "caption": caption}, files=files, timeout=30)
    except Exception as e: print("PHOTO ERR", e)

SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN"}
already_sent = set()
daily_trades = []
exit_sent = False
last_day = None

def clean_df(df):
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()
    df['Dt'] = pd.to_datetime(df.iloc[:,0])
    try: df['Dt'] = df['Dt'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    except: pass
    return df

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def get_15m_box(sym):
    try:
        today = datetime.now(IST).date()
        df15 = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
        df15 = clean_df(df15); df15 = df15[df15['Dt'].dt.date==today]
        if len(df15) < 1: return None, None
        first = df15.iloc[0]
        return float(first['High']), float(first['Low'])
    except: return None, None

def get_strike(name, entry):
    if name=="NIFTY": return int(round(entry/50)*50)
    if name=="SENSEX": return int(round(entry/100)*100)
    return int(round(entry/5)*5)

def make_chart(df5, name, top, bottom, entry, typ):
    d = df5.tail(60).copy().reset_index(drop=True)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    for i, row in d.iterrows():
        o, h, l, c = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])
        col = 'green' if c >= o else 'red'
        ax1.plot([i, i], [l, h], color=col, linewidth=1)
        ax1.add_patch(plt.Rectangle((i-0.35, min(o, c)), 0.7, abs(c-o)+0.1, color=col, alpha=0.9))
    ax1.plot(d['EMA9'].values, color='orange', linewidth=1.2, label='EMA 9')
    ax1.plot(d['EMA20'].values, color='purple', linewidth=1.2, label='EMA 20')
    ax1.axhline(top, color='blue', linewidth=1.5, label=f'BOX TOP {top:.1f}')
    ax1.axhline(bottom, color='blue', linewidth=1.5, label=f'BOX BOTTOM {bottom:.1f}')
    ax1.axhline(entry, color='black', linewidth=1.5, label=f'Entry {entry:.1f}')
    ax1.set_title(f"{name} 5m | {typ} | RECLAIM + HAMMER | Entry {entry:.1f}", fontsize=11, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()
    buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=150); plt.close(); buf.seek(0)
    return buf.getvalue()

def is_hammer(row):
    o,h,l,c = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])
    body = abs(c-o)
    lower = min(o,c) - l
    upper = h - max(o,c)
    if body == 0: body = 0.5
    return lower > 1.5*body and upper < body

def is_shooting(row):
    o,h,l,c = float(row['Open']), float(row['High']), float(row['Low']), float(row['Close'])
    body = abs(c-o)
    lower = min(o,c) - l
    upper = h - max(o,c)
    if body == 0: body = 0.5
    return upper > 1.5*body and lower < body

def check_one(name, sym):
    try:
        top, bottom = get_15m_box(sym)
        if top is None: return
        now = datetime.now(IST)
        if now.hour == 9 and now.minute < 30:
            return
        today = now.date()
        df5 = yf.download(sym, period="2d", interval="5m", progress=False, auto_adjust=True)
        df5 = clean_df(df5); df5 = df5[df5['Dt'].dt.date==today]
        if len(df5) < 5: return
        df5["EMA9"] = df5["Close"].ewm(span=9, adjust=False).mean()
        df5["EMA20"] = df5["Close"].ewm(span=20, adjust=False).mean()
        df5["RSI"] = calc_rsi(df5["Close"])
        curr = df5.iloc[-1]; prev_c = df5.iloc[-2]; prev2 = df5.iloc[-3]
        last_price = float(curr['Close']); pc = float(prev_c['Close'])
        ema9 = float(curr['EMA9']); ema20 = float(curr['EMA20'])
        rsi = float(curr['RSI']) if not pd.isna(curr['RSI']) else 50
        body = abs(float(curr['Close']) - float(curr['Open']))
        is_green = float(curr['Close']) > float(curr['Open'])
        is_red = float(curr['Close']) < float(curr['Open'])

        # CALL: Support pe Hammer / Bullish candle + Upar Closing
        support_broken_then_reclaim = float(prev2['Low']) < bottom or float(prev_c['Low']) < bottom
        hammer_near = is_hammer(prev_c) or is_hammer(prev2) or is_hammer(curr)
        call_trigger = support_broken_then_reclaim and last_price > bottom and pc <= bottom + 5 and last_price > ema9 and is_green and rsi > 50 and (hammer_near or body > 5)
        call_breakout = pc <= top and last_price > top and is_green and rsi > 50 and last_price > ema9

        # PUT: Resistance pe Shooting / Bearish candle + Neeche Closing
        resistance_broken_then_reclaim = float(prev2['High']) > top or float(prev_c['High']) > top
        shooting_near = is_shooting(prev_c) or is_shooting(prev2) or is_shooting(curr)
        put_trigger = resistance_broken_then_reclaim and last_price < top and pc >= top - 5 and last_price < ema9 and is_red and rsi < 50 and (shooting_near or body > 5)
        put_breakdown = pc >= bottom and last_price < bottom and is_red and rsi < 50 and last_price < ema9

        if call_trigger or call_breakout:
            key = f"{today}_{name}_CALL_{str(curr['Dt'])}"
            if key not in already_sent:
                strike = get_strike(name, last_price)
                sl = round(bottom - 5, 1) if call_trigger else round(top - 5, 1)
                caption = f"👑👑 Khan Sahab/Kohinoor 👑👑\n━━━━━━━━━━━━━━━━━━\n\n📦 SUPPORT RECLAIM + HAMMER\n\n🟢 CALL - {strike}-CE\n\n📊 Price: {last_price:.2f}\n📊 Box TOP: {top:.2f} | BOTTOM: {bottom:.2f}\n📊 EMA 9: {ema9:.1f} | EMA 20: {ema20:.1f}\n📊 RSI: {rsi:.0f}\n\n💰 Entry: {strike}-CE\n🛑 SL: {sl}\n🎯 Target: {round(last_price + (last_price - sl)*2, 1)}\n━━━━━━━━━━━━━━━━━━"
                tg_photo(make_chart(df5, name, top, bottom, last_price, "CALL"), caption)
                already_sent.add(key); daily_trades.append([name,"CALL",last_price]); return
        if put_trigger or put_breakdown:
            key = f"{today}_{name}_PUT_{str(curr['Dt'])}"
            if key not in already_sent:
                strike = get_strike(name, last_price)
                sl = round(top + 5, 1) if put_trigger else round(bottom + 5, 1)
                caption = f"👑👑 Khan Sahab/Kohinoor 👑👑\n━━━━━━━━━━━━━━━━━━\n\n📦 RESISTANCE RECLAIM + SHOOTING\n\n🔴 PUT - {strike}-PE\n\n📊 Price: {last_price:.2f}\n📊 Box TOP: {top:.2f} | BOTTOM: {bottom:.2f}\n📊 EMA 9: {ema9:.1f} | EMA 20: {ema20:.1f}\n📊 RSI: {rsi:.0f}\n\n💰 Entry: {strike}-PE\n🛑 SL: {sl}\n🎯 Target: {round(last_price - (sl - last_price)*2, 1)}\n━━━━━━━━━━━━━━━━━━"
                tg_photo(make_chart(df5, name, top, bottom, last_price, "PUT"), caption)
                already_sent.add(key); daily_trades.append([name,"PUT",last_price]); return
    except Exception as e: print(name, e)

print("BOT STARTED - AUTO MODE", datetime.now(IST))
tg("✅ BOT STARTED - AUTO MODE\nRoz subah khud chalega, chhutti pe band rahega")

while True:
    try:
        now = datetime.now(IST)
        today = now.date()

        # Roz naya din aaye to reset
        if last_day != today:
            already_sent.clear()
            daily_trades.clear()
            exit_sent = False
            last_day = today
            print("NEW DAY RESET", today)

        is_weekday = now.weekday() < 5
        is_market = is_weekday and ((now.hour==9 and now.minute>=30) or (now.hour>9 and now.hour<15) or (now.hour==15 and now.minute<=15))

        if is_market:
            for name,sym in SYMBOLS.items():
                check_one(name,sym); time.sleep(1)

        if is_weekday and now.hour==15 and now.minute>=15 and not exit_sent:
            lines=""
            for t in daily_trades: lines+=f"{t[0]} {t[1]} @ {t[2]:.2f}\n"
            if not lines: lines="Aaj koi Trade nahi bana - NO TRADE\n"
            tg(f"📊 DAILY REPORT 📊\n{lines}Total: {len(daily_trades)}")
            exit_sent=True

        if not is_weekday:
            print("WEEKEND - SLEEPING", now)
            time.sleep(3600)
        elif not is_market:
            time.sleep(60)
        else:
            time.sleep(30)

    except Exception as e:
        print("Loop Error", e); time.sleep(30)
