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
    "SILVERM": "SI=F",
    "CRUDEOIL": "CL=F"
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
    rsi_15 = last_15['RSI']
    trend_15 = "UP" if last_15['EMA20'] > last_15['EMA50'] else "DOWN"
    
    df_5 = yf.download(yf_sym, period="2d", interval="5m", progress=False)
    df_5.columns = [c[0] if isinstance(c, tuple) else c for c in df_5.columns]
    df_5['VWAP'] = (df_5['Close'] * df_5['Volume']).cumsum() / df_5['Volume'].cumsum()
    last_5 = df_5.iloc[-1]
    
    if 50 <= rsi_15 <= 65:
        if trend_15 == "UP" and last_5['Close'] > last_5['VWAP']:
            return f"🟢 {name} BUY | 15m RSI {rsi_15:.1f} (50-65) | 15m UP | 5m VWAP Entry"
        elif trend_15 == "DOWN" and last_5['Close'] < last_5['VWAP']:
            return f"🔴 {name} SELL | 15m RSI {rsi_15:.1f} (50-65) | 15m DOWN | 5m VWAP Entry"
    
    return f"⚪ {name} - RSI {rsi_15:.1f} | Trend {trend_15} - Wait"

def send_tg(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist).strftime("%d %b %I:%M %p")
final_msg = f"<b>MCX 15M-5M | {now}</b>\nRSI 50-65 Filter\n\n"
has_signal = False
for name, sym in SYMBOLS.items():
    res = check_symbol(name, sym)
    if res:
        final_msg += res + "\n\n"
        if "BUY" in res or "SELL" in res: has_signal = True

if not has_signal:
    final_msg += "No Entry - RSI 50-65 bahar."

send_tg(final_msg)
print(final_msg)
