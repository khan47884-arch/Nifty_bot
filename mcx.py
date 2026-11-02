import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SYMBOLS = {
    "GOLDMINI": "GC=F",
    "SILVERM": "SI=F"
}

def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_symbol(name, yf_sym):
    df_15 = yf.download(yf_sym, period="5d", interval="15m", progress=False)
    if len(df_15) < 50: return None
    df_15.columns = [c[0] if isinstance(c, tuple) else c for c in df_15.columns]
    df_15['EMA20'] = df_15['Close'].ewm(span=20).mean()
    df_15['EMA50'] = df_15['Close'].ewm(span=50).mean()
    df_15['RSI'] = get_rsi(df_15['Close'])
    last_15 = df_15.iloc[-1]
    rsi_15 = float(last_15['RSI'])
    trend_15 = "UP" if last_15['EMA20'] > last_15['EMA50'] else "DOWN"
    
    df_5 = yf.download(yf_sym, period="2d", interval="5m", progress=False)
    df_5.columns = [c[0] if isinstance(c, tuple) else c for c in df_5.columns]
    last_5 = df_5.iloc[-1]
    prev_5 = df_5.iloc[-2]
    breakout_up = last_5['Close'] > prev_5['High']
    breakdown_down = last_5['Close'] < prev_5['Low']
    
    buy_max = 70 if name == "SILVERM" else 65
    if trend_15 == "UP" and 50 <= rsi_15 <= buy_max and breakout_up:
        return f"🟢 {name} BUY | 15m UP RSI {rsi_15:.1f} | 5m BO {last_5['Close']:.1f}"
    if trend_15 == "DOWN" and 35 <= rsi_15 <= 50 and breakdown_down:
        return f"🔴 {name} SELL | 15m DOWN RSI {rsi_15:.1f} | 5m BD {last_5['Close']:.1f}"
    return None

def send_tg(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist).strftime("%d %b %I:%M %p")
signals = []
for name, sym in SYMBOLS.items():
    res = check_symbol(name, sym)
    if res:
        signals.append(res)

if signals:
    final_msg = f"<b>MCX ENTRY | {now}</b>\n\n" + "\n\n".join(signals)
    send_tg(final_msg)
    print(final_msg)
else:
    print(f"No Entry at {now}")
