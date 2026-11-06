import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime, time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SYMBOLS = [
    "RELIANCE.NS","HDFCBANK.NS","SBIN.NS","ICICIBANK.NS","TCS.NS",
    "INFY.NS","BHEL.NS","BEL.NS","TITAN.NS","ADANIENT.NS",
    "ADANIPORTS.NS","TATAMOTORS.NS","TATASTEEL.NS","BHARTIARTL.NS","ITC.NS",
    "LT.NS","BAJAJFINSV.NS","MARUTI.NS","HAL.NS","ONGC.NS",
    "COALINDIA.NS","NTPC.NS","POWERGRID.NS","HINDALCO.NS","VEDL.NS"
]

SENT_FILE = "sent.txt"

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE) as f:
            return set(f.read().splitlines())
    return set()

def save_sent(key):
    with open(SENT_FILE, "a") as f:
        f.write(key + "\n")

def send_telegram(msg, key):
    sent = load_sent()
    if key in sent:
        return False
    today_str = key.split("_")[0]
    today_count = sum(1 for k in sent if k.startswith(today_str))
    if today_count >= 3:
        return False
    if not BOT_TOKEN or not CHAT_ID:
        print(msg)
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        if r.status_code == 200:
            save_sent(key)
            return True
    except Exception as e:
        print("Telegram Error:", e)
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

def check_stock(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="5m", progress=False, auto_adjust=False)
        if df.empty or len(df) < 30:
            return
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        try:
            df['Datetime'] = df['Datetime'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        except:
            pass
        all_dates = sorted(df['Datetime'].dt.date.unique())
        today = all_dates[-1]
        today_df = df[df['Datetime'].dt.date == today].copy()
        if len(today_df) < 10 and len(all_dates) >= 2:
            today = all_dates[-2]
            today_df = df[df['Datetime'].dt.date == today].copy()
        prev_df = df[df['Datetime'].dt.date < today]
        if today_df.empty or prev_df.empty or len(today_df) < 10:
            return
        prev_close = float(prev_df['Close'].iloc[-1])
        day_open = float(today_df['Open'].iloc[0])
        gap = (day_open - prev_close) / prev_close * 100
        box_df = today_df[(today_df['Datetime'].dt.time >= time(9,15)) & (today_df['Datetime'].dt.time < time(9,30))]
        if box_df.empty:
            return
        box_high = float(box_df['High'].max())
        box_low = float(box_df['Low'].min())
        if box_high <= box_low:
            return
        today_df['EMA20'] = today_df['Close'].ewm(span=20, adjust=False).mean()
        today_df['VWAP'] = calc_vwap(today_df)
        today_df['RSI'] = calc_rsi(today_df['Close'], 14)
        today_df['VolAvg'] = today_df['Volume'].rolling(20).mean()
        after_df = today_df[today_df['Datetime'].dt.time >= time(9,30)]
        if after_df.empty or len(after_df) < 3:
            return
        after_df = after_df[after_df['High'] > after_df['Low']]
        if len(after_df) < 3:
            return
        last = after_df.iloc[-1]
        prev_candle = after_df.iloc[-2]
        close = float(last['Close'])
        prev_low = float(prev_candle['Low'])
        prev_high = float(prev_candle['High'])
        ema20 = float(last['EMA20'])
        vwap = float(last['VWAP'])
        rsi = float(last['RSI']) if not np.isnan(last['RSI']) else 50
        vol = float(last['Volume'])
        vol_avg = float(last['VolAvg']) if not np.isnan(last['VolAvg']) else vol
        vol_ok = vol > (vol_avg * 1.5)
        if not vol_ok:
            return
        clean = symbol.replace(".NS","")
        date_str = str(today)
        call_break = (close - box_high) / box_high * 100
        put_break = (box_low - close) / box_low * 100
        call_too_far = call_break > 0.8
        put_too_far = put_break > 0.8
        trusted_bull = close > vwap and close > ema20 and rsi > 60 and vol_ok
        trusted_bear = close < vwap and close < ema20 and rsi < 40 and vol_ok
        min_risk = close * 0.002
        if abs(gap) >= 2.0:
            if close > box_high and trusted_bull and call_break > 0.2 and not call_too_far:
                sl = prev_low
                risk = close - sl
                if risk < min_risk:
                    risk = min_risk
                    sl = close - risk
                target = close + (risk * 2)
                msg = f"""🟢 TRUSTED BULLISH 🟢
💎 KHAN SAHAB PLATINUM 💎
📌 SHARE: {clean} - CALL
📊 GAP: {gap:.2f}%
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP: {vwap:.2f} - UPAR ✅
📍 20 EMA: {ema20:.2f} - UPAR ✅
📈 RSI: {rsi:.0f}
💰 BUY @ {close:.2f} | SL {sl:.2f} | TARGET {target:.2f}"""
                send_telegram(msg, f"{date_str}_{clean}_PLAT_CALL")
            elif close < box_low and trusted_bear and put_break > 0.2 and not put_too_far:
                sl = prev_high
                risk = sl - close
                if risk < min_risk:
                    risk = min_risk
                    sl = close + risk
                target = close - (risk * 2)
                msg = f"""🔴 TRUSTED BEARISH 🔴
💎 KHAN SAHAB PLATINUM 💎
📌 SHARE: {clean} - PUT
📊 GAP: {gap:.2f}%
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP: {vwap:.2f} - NEECHE ✅
📍 20 EMA: {ema20:.2f} - NEECHE ✅
📈 RSI: {rsi:.0f}
💰 BUY @ {close:.2f} | SL {sl:.2f} | TARGET {target:.2f}"""
                send_telegram(msg, f"{date_str}_{clean}_PLAT_PUT")
            return
        touched_call = False
        touched_put = False
        for _, row in after_df.iterrows():
            l = float(row['Low']); h = float(row['High'])
            v = float(row['VWAP']); e = float(row['EMA20']); c = float(row['Close'])
            if abs(l - v) < c*0.0005 and abs(l - e) < c*0.0005:
                touched_call = True
            if abs(h - v) < c*0.0005 and abs(h - e) < c*0.0005:
                touched_put = True
        if touched_call and close > box_high and trusted_bull and call_break > 0.2 and not call_too_far:
            sl = prev_low
            risk = close - sl
            if risk < min_risk:
                risk = min_risk
                sl = close - risk
            target = close + (risk * 2)
            msg = f"""🟢 TRUSTED BULLISH 🟢
🔹 KHAN SAHAB DIAMOND 🔹
📌 SHARE: {clean} - CALL - Retest + Double Touch
📊 GAP: {gap:.2f}%
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP + 20 EMA Touch ✅
📈 RSI: {rsi:.0f}
💰 BUY @ {close:.2f} | SL {sl:.2f} | TARGET {target:.2f}"""
            send_telegram(msg, f"{date_str}_{clean}_DIA_CALL")
        elif touched_put and close < box_low and trusted_bear and put_break > 0.2 and not put_too_far:
            sl = prev_high
            risk = sl - close
            if risk < min_risk:
                risk = min_risk
                sl = close + risk
            target = close - (risk * 2)
            msg = f"""🔴 TRUSTED BEARISH 🔴
🔹 KHAN SAHAB DIAMOND 🔹
📌 SHARE: {clean} - PUT - Retest + Double Touch
📊 GAP: {gap:.2f}%
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP + 20 EMA Touch ✅
📈 RSI: {rsi:.0f}
💰 BUY @ {close:.2f} | SL {sl:.2f} | TARGET {target:.2f}"""
            send_telegram(msg, f"{date_str}_{clean}_DIA_PUT")
    except Exception as e:
        print(f"Error {symbol}: {e}")

if __name__ == "__main__":
    print("Khan Bot Started -", datetime.now())
    for sym in SYMBOLS:
        check_stock(sym)
    print("Done")
