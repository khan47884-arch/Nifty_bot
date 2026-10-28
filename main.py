import yfinance as yf
import pandas as pd
import os, requests, time
from datetime import datetime

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","LT.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","KOTAKBANK.NS","CIPLA.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","WIPRO.NS","HCLTECH.NS","SUNPHARMA.NS","ULTRACEMCO.NS","TITAN.NS","BAJFINANCE.NS"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(e)

def check_stock(symbol):
    try:
        df = yf.download(symbol, period="60d", interval="1d", progress=False)
        if len(df) < 50:
            return None
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        close = float(df['Close'].iloc[-1])
        ema20 = float(df['EMA20'].iloc[-1])
        ema50 = float(df['EMA50'].iloc[-1])
        if close > ema20 and ema20 > ema50:
            return f"✅ {symbol.replace('.NS','')} - ELITE BUY | Price: {close:.2f}"
        if close < ema20:
            return f"🔻 {symbol.replace('.NS','')} - WEAK | Price: {close:.2f}"
    except:
        return None
    return None

signals = []
for s in STOCKS:
    res = check_stock(s)
    if res:
        signals.append(res)
    time.sleep(0.3)

date_str = datetime.now().strftime("%d-%m-%Y %H:%M")
if signals:
    msg = f"🚀 BOND 007 - NIFTY SCAN 🚀\n📅 {date_str}\n\n" + "\n".join(signals)
else:
    msg = f"📊 BOND 007 - NIFTY SCAN\n📅 {date_str}\n\nNo strong signals today."

print(msg)
send_telegram(msg)
