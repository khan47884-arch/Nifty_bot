import os
import requests
import yfinance as yf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

try:
    daily = yf.Ticker("^NSEI").history(period="5d", interval="1d")
    hist = yf.Ticker("^NSEI").history(period="5d", interval="15m")

    prev_high = daily['High'].iloc[-2]
    prev_low = daily['Low'].iloc[-2]
    live = hist['Close'].iloc[-1]
    last2 = hist['Close'].iloc[-2:].values

    if last2[0] > prev_high and last2[1] > prev_high:
        send(f"🚀 *CONFIRM BUY SIGNAL*\n\nKal ka HIGH: {prev_high:.2f}\nLive Price: {live:.2f}\n✅ 2 Candle Confirm Hai - Fake Nahi")

    elif last2[0] < prev_low and last2[1] < prev_low:
        send(f"🔻 *CONFIRM SELL SIGNAL*\n\nKal ka LOW: {prev_low:.2f}\nLive Price: {live:.2f}\n✅ 2 Candle Confirm Hai - Fake Nahi")

    else:
        print(f"No Break - Live {live:.2f}")

except Exception as e:
    print(e)
