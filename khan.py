import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime, time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SYMBOLS = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "KOTAKBANK.NS","SBIN.NS","AXISBANK.NS","LT.NS","TITAN.NS",
    "ITC.NS","HINDUNILVR.NS","BAJFINANCE.NS","MARUTI.NS","TATAMOTORS.NS",
    "TATASTEEL.NS","ONGC.NS","POWERGRID.NS","NTPC.NS","SUNPHARMA.NS",
    "ADANIENT.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","ULTRACEMCO.NS"
]

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print(msg)
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print("Telegram Error:", e)

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
        df = yf.download(symbol, period="2d", interval="5m", progress=False, auto_adjust=False)
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
        today = df['Datetime'].dt.date.max()
        today_df = df[df['Datetime'].dt.date == today].copy()
        prev_df = df[df['Datetime'].dt.date < today]
        if today_df.empty or prev_df.empty:
            return
        prev_close = float(prev_df['Close'].iloc[-1])
        day_open = float(today_df['Open'].iloc[0])
        gap = (day_open - prev_close) / prev_close * 100
        box_df = today_df[(today_df['Datetime'].dt.time >= time(9,15)) & (today_df['Datetime'].dt.time < time(9,30))]
        if box_df.empty:
            return
        box_high = float(box_df['High'].max())
        box_low = float(box_df['Low'].min())
        today_df['EMA20'] = today_df['Close'].ewm(span=20, adjust=False).mean()
        today_df['VWAP'] = calc_vwap(today_df)
        today_df['RSI'] = calc_rsi(today_df['Close'], 14)
        today_df['VolAvg'] = today_df['Volume'].rolling(20).mean()
        after_df = today_df[today_df['Datetime'].dt.time >= time(9,30)]
        if after_df.empty:
            return
        last = after_df.iloc[-1]
        close = float(last['Close'])
        low = float(last['Low'])
        high = float(last['High'])
        ema20 = float(last['EMA20'])
        vwap = float(last['VWAP'])
        rsi = float(last['RSI']) if not np.isnan(last['RSI']) else 50
        vol = float(last['Volume'])
        vol_avg = float(last['VolAvg']) if not np.isnan(last['VolAvg']) else vol
        vol_ok = vol > vol_avg
        clean = symbol.replace(".NS","")
        trusted_bull = close > vwap and close > ema20 and rsi > 50 and vol_ok
        trusted_bear = close < vwap and close < ema20 and rsi < 50 and vol_ok
        if abs(gap) >= 2.0:
            if close > box_high and close > vwap:
                trusted = "🟢 TRUSTED BULLISH 🟢\n" if trusted_bull else ""
                msg = f"""{trusted}💎 KHAN SAHAB PLATINUM 💎
📌 SHARE: {clean} - CALL
📊 GAP: {gap:.2f}%
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP: {vwap:.2f} - UPAR ✅
📍 20 EMA: {ema20:.2f} - UPAR ✅
📈 RSI: {rsi:.0f}
💰 BUY @ {close:.2f} | SL {box_high:.2f} | TARGET {close + (box_high-box_low):.2f}"""
                send_telegram(msg)
            elif close < box_low and close < vwap:
                trusted = "🔴 TRUSTED BEARISH 🔴\n" if trusted_bear else ""
                msg = f"""{trusted}💎 KHAN SAHAB PLATINUM 💎
📌 SHARE: {clean} - PUT
📊 GAP: {gap:.2f}%
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP: {vwap:.2f} - NEECHE ✅
📍 20 EMA: {ema20:.2f} - NEECHE ✅
📈 RSI: {rsi:.0f}
💰 BUY @ {close:.2f} | SL {box_low:.2f} | TARGET {close - (box_high-box_low):.2f}"""
                send_telegram(msg)
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
        if touched_call and close > box_high and vol_ok:
            trusted = "🟢 TRUSTED BULLISH 🟢\n" if trusted_bull else ""
            msg = f"""{trusted}🔹 KHAN SAHAB DIAMOND 🔹
📌 SHARE: {clean} - CALL - Retest + Double Touch
📊 GAP: {gap:.2f}%
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP + 20 EMA Touch ✅
📈 RSI: {rsi:.0f}
💰 BUY @ {close:.2f} | SL {box_low:.2f} | TARGET {close + (box_high-box_low):.2f}"""
            send_telegram(msg)
        elif touched_put and close < box_low and vol_ok:
            trusted = "🔴 TRUSTED BEARISH 🔴\n" if trusted_bear else ""
            msg = f"""{trusted}🔹 KHAN SAHAB DIAMOND 🔹
📌 SHARE: {clean} - PUT - Retest + Double Touch
📊 GAP: {gap:.2f}%
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP + 20 EMA Touch ✅
📈 RSI: {rsi:.0f}
💰 BUY @ {close:.2f} | SL {box_high:.2f} | TARGET {close - (box_high-box_low):.2f}"""
            send_telegram(msg)
    except Exception as e:
        print(f"Error {symbol}: {e}")

if __name__ == "__main__":
    print("Khan Bot Started -", datetime.now())
    for sym in SYMBOLS:
        check_stock(sym)
    print("Done")
