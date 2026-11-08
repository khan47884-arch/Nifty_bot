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
    "ADANIPORTS.NS","TATAMOTORS.NS","TATASTEEL.NS","BHARTIARTL.NS","M&M.NS",
    "LT.NS","BAJAJFINSV.NS","MARUTI.NS","HAL.NS","ONGC.NS",
    "BAJFINANCE.NS","NTPC.NS","POWERGRID.NS","HINDALCO.NS","VEDL.NS"
]

QTY = 500
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

def clean_df(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    try:
        df['Datetime'] = df['Datetime'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    except: pass
    return df

def get_nifty_trend_15m():
    try:
        df = yf.download("^NSEI", period="2d", interval="15m", progress=False, auto_adjust=False)
        if df.empty: return "NEUTRAL"
        df = clean_df(df)
        today = sorted(df['Datetime'].dt.date.unique())[-1]
        df = df[df['Datetime'].dt.date == today].copy()
        if len(df) < 5: return "NEUTRAL"
        df['VWAP'] = calc_vwap(df)
        last_close = float(df['Close'].iloc[-1])
        last_vwap = float(df['VWAP'].iloc[-1])
        if last_close > last_vwap: return "UP"
        if last_close < last_vwap: return "DOWN"
        return "NEUTRAL"
    except:
        return "NEUTRAL"

def check_wave3_15m(df15):
    try:
        if len(df15) < 12:
            return None
        closes = df15['Close'].values
        highs = df15['High'].values
        lows = df15['Low'].values
        w1_low = float(np.min(lows[-12:-8]))
        w1_high = float(np.max(highs[-10:-5]))
        w2_low = float(np.min(lows[-5:-1]))
        curr_close = float(closes[-1])
        wave1_move = w1_high - w1_low
        if wave1_move > 0:
            pullback_pct = (w1_high - w2_low) / wave1_move * 100
            if 40 <= pullback_pct <= 70 and curr_close > w1_high:
                return "UP"
        w1_high_d = float(np.max(highs[-12:-8]))
        w1_low_d = float(np.min(lows[-10:-5]))
        w2_high_d = float(np.max(highs[-5:-1]))
        wave1_move_d = w1_high_d - w1_low_d
        if wave1_move_d > 0:
            pullback_pct_d = (w2_high_d - w1_low_d) / wave1_move_d * 100
            if 40 <= pullback_pct_d <= 70 and curr_close < w1_low_d:
                return "DOWN"
        return None
    except:
        return None

def check_stock(symbol, nifty_trend):
    try:
        df5 = yf.download(symbol, period="5d", interval="5m", progress=False, auto_adjust=False)
        if df5.empty or len(df5) < 30:
            return
        df5 = clean_df(df5)
        all_dates = sorted(df5['Datetime'].dt.date.unique())
        today = all_dates[-1]
        today_df = df5[df5['Datetime'].dt.date == today].copy()
        if len(today_df) < 10 and len(all_dates) >= 2:
            today = all_dates[-2]
            today_df = df5[df5['Datetime'].dt.date == today].copy()
        prev_df = df5[df5['Datetime'].dt.date < today]
        if today_df.empty or prev_df.empty or len(today_df) < 10:
            return
        df15 = yf.download(symbol, period="5d", interval="15m", progress=False, auto_adjust=False)
        if df15.empty: return
        df15 = clean_df(df15)
        df15_today = df15[df15['Datetime'].dt.date == today].copy()
        if len(df15_today) < 3:
            df15_today = df15.tail(10).copy()
        df15_today['VWAP'] = calc_vwap(df15_today)
        df15_today['EMA20'] = df15_today['Close'].ewm(span=20, adjust=False).mean()
        last_15 = df15_today.iloc[-1]
        trend_15_up = float(last_15['Close']) > float(last_15['VWAP']) and float(last_15['Close']) > float(last_15['EMA20'])
        trend_15_down = float(last_15['Close']) < float(last_15['VWAP']) and float(last_15['Close']) < float(last_15['EMA20'])
        wave = check_wave3_15m(df15_today)
        if wave is None:
            return
        if wave == "UP" and not (trend_15_up and nifty_trend == "UP"):
            return
        if wave == "DOWN" and not (trend_15_down and nifty_trend == "DOWN"):
            return
        prev_close = float(prev_df['Close'].iloc[-1])
        day_open = float(today_df['Open'].iloc[0])
        gap = (day_open - prev_close) / prev_close * 100
        box_df = today_df[(today_df['Datetime'].dt.time >= time(9,15)) & (today_df['Datetime'].dt.time < time(9,30))]
        if box_df.empty: return
        box_high = float(box_df['High'].max())
        box_low = float(box_df['Low'].min())
        if box_high <= box_low: return
        today_df['EMA20'] = today_df['Close'].ewm(span=20, adjust=False).mean()
        today_df['VWAP'] = calc_vwap(today_df)
        today_df['RSI'] = calc_rsi(today_df['Close'], 14)
        today_df['VolAvg'] = today_df['Volume'].rolling(20).mean()
        after_df = today_df[today_df['Datetime'].dt.time >= time(9,30)]
        if after_df.empty or len(after_df) < 3: return
        after_df = after_df[after_df['High'] > after_df['Low']]
        if len(after_df) < 3: return
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
        candle_key = str(last['Datetime'].strftime("%Y-%m-%d_%H:%M"))
        clean = symbol.replace(".NS","")
        vwap_dist = abs(close - vwap) / vwap * 100
        if (vwap_dist < 0.10) and (45 <= rsi <= 55):
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
        call_break = (close - box_high) / box_high * 100
        put_break = (box_low - close) / box_low * 100
        if call_break > 0.8 or put_break > 0.8:
            return
        vol_ratio = vol / (vol_avg + 1e-9)
        min_risk = close * 0.002
        is_pro_bull = (wave == "UP" and trend_15_up and nifty_trend == "UP"
                       and abs(gap) >= 2.0 and vol_ratio >= 2.0 and rsi >= 65 and touched_call
                       and close > box_high and close > vwap and close > ema20
                       and call_break > 0.2)
        is_pro_bear = (wave == "DOWN" and trend_15_down and nifty_trend == "DOWN"
                       and abs(gap) >= 2.0 and vol_ratio >= 2.0 and rsi <= 35 and touched_put
                       and close < box_low and close < vwap and close < ema20
                       and put_break > 0.2)
        if is_pro_bull:
            sl = prev_low
            risk = close - sl
            if risk < min_risk: risk = min_risk; sl = close - risk
            t1 = close + (risk * 1)
            t2 = close + (risk * 2)
            msg = f"""👑 PRO KOHINOOR 👑
🟢 FUTURE: {clean} - LONG
📍 NIFTY 15 MIN: UP ⬆️ - VWAP Ke Upar
💰 BUY FUT @ {close:.2f} | Qty: {QTY} Share - FULL LOT
🛑 SL @ {sl:.2f} - Prev Candle Low
🎯 T1 @ {t1:.2f} - 50% BOOK
🎯 T2 @ {t2:.2f} - Baaki | SL to Entry"""
            send_telegram(msg, f"{candle_key}_{clean}_PRO_KOHINOOR_LONG")
        elif is_pro_bear:
            sl = prev_high
            risk = sl - close
            if risk < min_risk: risk = min_risk; sl = close + risk
            t1 = close - (risk * 1)
            t2 = close - (risk * 2)
            msg = f"""👑 PRO KOHINOOR 👑
🔴 FUTURE: {clean} - SHORT
📍 NIFTY 15 MIN: DOWN ⬇️ - VWAP Ke Neeche
💰 SELL FUT @ {close:.2f} | Qty: {QTY} Share - FULL LOT
🛑 SL @ {sl:.2f} - Prev Candle High
🎯 T1 @ {t1:.2f} - 50% BOOK
🎯 T2 @ {t2:.2f} - Baaki | SL to Entry"""
            send_telegram(msg, f"{candle_key}_{clean}_PRO_KOHINOOR_SHORT")
    except Exception as e:
        print(f"Error {symbol}: {e}")

if __name__ == "__main__":
    print("PRO KOHINOOR Started -", datetime.now())
    nifty = get_nifty_trend_15m()
    print("NIFTY 15 MIN Trend:", nifty)
    for sym in SYMBOLS:
        check_stock(sym, nifty)
    print("Done")
