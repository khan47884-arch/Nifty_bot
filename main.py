import yfinance as yf
import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram secrets missing")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
        print("Message sent")
    except Exception as e:
        print(f"Error: {e}")

def is_strong_candle(last_candle):
    try:
        o = float(last_candle['Open'])
        c = float(last_candle['Close'])
        h = float(last_candle['High'])
        l = float(last_candle['Low'])
        body = abs(c - o)
        rng = h - l
        if rng == 0:
            return False
        return body > (rng * 0.6)
    except:
        return False

def check_stock(name, df_5m, df_daily):
    try:
        if df_5m.empty or df_daily.empty:
            return None
        last_2_days = df_daily.tail(2)
        support = float(last_2_days['Low'].min())
        resistance = float(last_2_days['High'].max())
        last_candle = df_5m.tail(1).iloc[0]
        
        curr_close = float(last_candle['Close'])
        is_bullish = float(last_candle['Close']) > float(last_candle['Open'])
        is_bearish = float(last_candle['Close']) < float(last_candle['Open'])
        strong = is_strong_candle(last_candle)

        if curr_close > support and (float(last_candle['Low']) <= support * 1.002):
            return f"✅ *{name} SUPPORT BOUNCE* ✅\nSupport: {support} | Close: {curr_close}"
        if curr_close < resistance and (float(last_candle['High']) >= resistance * 0.998):
            return f"🔴 *{name} RESISTANCE REJECT* 🔴\nResistance: {resistance} | Close: {curr_close}"
        if curr_close > resistance and is_bullish and strong:
            return f"🚀 *{name} BREAKOUT* 🚀\nResistance broken: {resistance}"
        if curr_close < support and is_bearish and strong:
            return f"💥 *{name} BREAKDOWN* 💥\nSupport broken: {support}"
        return None
    except Exception as e:
        print(f"Error in {name}: {e}")
        return None

# Download data
nifty_5m = yf.download("^NSEI", period="5d", interval="5m", progress=False)
nifty_daily = yf.download("^NSEI", period="10d", interval="1d", progress=False)
sensex_5m = yf.download("^BSESN", period="5d", interval="5m", progress=False)
sensex_daily = yf.download("^BSESN", period="10d", interval="1d", progress=False)

signals = []
for s in [check_stock("NIFTY", nifty_5m, nifty_daily), check_stock("SENSEX", sensex_5m, sensex_daily)]:
    if s:
        signals.append(s)

if signals:
    send_telegram("\n\n".join(signals))

send_telegram("TEST SUCCESSFUL - Bot Telegram se connected hai boss")
