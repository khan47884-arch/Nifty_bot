import requests, time, yfinance as yf
from datetime import datetime
import os
from flask import Flask
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8905559008:AAGw-oHZaIiTZ-eD3Qpei4tKCsKMUTIS--8")
CHAT_ID = os.environ.get("CHAT_ID", "2096276176")

app = Flask(__name__)
@app.route('/')
def home():
    return "Nifty Bot LIVE Hai!"

def send(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def nifty_bot():
    send("🚀 Nifty Bot Cloud par 24x7 LIVE!")
    high = low = None
    done = False
    last_date = None
    while True:
        try:
            now = datetime.now()
            if last_date != now.date():
                high = low = None
                done = False
                last_date = now.date()
            if now.weekday() >= 5:
                time.sleep(3600)
                continue
            df = yf.download("^NSEI", period="1d", interval="1m", progress=False)
            if df.empty:
                time.sleep(60)
                continue
            price = float(df['Close'].iloc[-1])
            if now.hour == 9 and 15 <= now.minute <= 30:
                if high is None: high = low = price
                high = max(high, price)
                low = min(low, price)
                if now.hour == 9 and now.minute == 30:
                    send(f"📊 Opening Range High: {high:.2f} Low: {low:.2f}")
            if high and now.hour == 9 and now.minute > 30 and not done:
                if price > high + 5:
                    send(f"🔥 BREAKOUT UP {price:.2f} > {high:.2f} BUY")
                    done = True
                elif price < low - 5:
                    send(f"🔻 BREAKDOWN {price:.2f} < {low:.2f} SELL")
                    done = True
            time.sleep(60)
        except: time.sleep(60)

threading.Thread(target=nifty_bot, daemon=True).start()
app.run(host='0.0.0.0', port=10000)
