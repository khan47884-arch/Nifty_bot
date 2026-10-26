import yfinance as yf
import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Secrets missing")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print(e)

def check_stock(name, df_5m, df_daily):
    if df_5m.empty or df_daily.empty:
        return None
    try:
        curr_close = float(df_5m['Close'].iloc[-1])
        resistance = float(df_daily['High'].tail(20).max())
        support = float(df_daily['Low'].tail(20).min())
        is_bullish = curr_close > float(df_5m['Close'].tail(5).mean())
        is_bearish = curr_close < float(df_5m['Close'].tail(5).mean())
        if curr_close > resistance and is_bullish:
            return f"🚀 *{name} BREAKOUT* 🚀\nPrice: {curr_close:.2f} > Resistance: {resistance:.2f}"
        if curr_close < support and is_bearish:
            return f"💥 *{name} BREAKDOWN* 💥\nPrice: {curr_close:.2f} < Support: {support:.2f}"
        return None
    except Exception as e:
        print(f"{name} error {e}")
        return None

#--- MAIN ---
nifty_5m = yf.download("^NSEI", period="5d", interval="15m", progress=False)
nifty_daily = yf.download("^NSEI", period="3mo", interval="1d", progress=False)
sensex_5m = yf.download("^BSESN", period="5d", interval="15m", progress=False)
sensex_daily = yf.download("^BSESN", period="3mo", interval="1d", progress=False)

signals = []
nifty_signal = check_stock("NIFTY", nifty_5m, nifty_daily)
if nifty_signal:
    signals.append(nifty_signal)
sensex_signal = check_stock("SENSEX", sensex_5m, sensex_daily)
if sensex_signal:
    signals.append(sensex_signal)

if signals:
