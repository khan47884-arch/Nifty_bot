import os
import requests
import yfinance as yf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)

try:
    daily = yf.Ticker("^NSEI").history(period="5d", interval="1d")
    hist = yf.Ticker("^NSEI").history(period="2d", interval="5m")

    prev_high = daily['High'].iloc[-3:-1].max()
    prev_low = daily['Low'].iloc[-3:-1].min()

    last = hist.iloc[-1]
    prev = hist.iloc[-2]
    live = last['Close']

    body = abs(last['Close'] - last['Open'])
    rang = last['High'] - last['Low']
    is_strong = (body / rang > 0.6) if rang > 0 else False

    if prev['Close'] > prev_high and last['Close'] > prev_high:
        if is_strong:
            send(f"🚀 *STRONG BUY - 5MIN BREAKOUT*\n\n2 Din High: {prev_high:.0f} Toda\nLive: {live:.0f}\nStrong Candle ✅")
        else:
            send(f"⚠️ *BREAKOUT Weak Candle*\nHigh: {prev_high:.0f} Live: {live:.0f}")

    elif prev['Close'] < prev_low and last['Close'] < prev_low:
        if is_strong:
            send(f"🔻 *STRONG SELL - 5MIN BREAKDOWN*\n\n2 Din Low: {prev_low:.0f} Toda\nLive: {live:.0f}\nStrong Candle ✅")
        else:
            send(f"⚠️ *BREAKDOWN Weak Candle*\nLow: {prev_low:.0f} Live: {live:.0f}")

except Exception as e:
    print(e)
