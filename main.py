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
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def check_stock(name, df_5m, df_daily):
    if df_5m.empty or df_daily.empty:
        return None
    try:
        curr = float(df_5m['Close'].iloc[-1])
        res = float(df_daily['High'].tail(20).max())
        sup = float(df_daily['Low'].tail(20).min())
        if curr > res:
            return f"BREAKOUT {name} {curr:.2f} > {res:.2f}"
        if curr < sup:
            return f"BREAKDOWN {name} {curr:.2f} < {sup:.2f}"
        return None
    except:
        return None

nifty_5m = yf.download("^NSEI", period="5d", interval="15m", progress=False)
nifty_daily = yf.download("^NSEI", period="3mo", interval="1d", progress=False)
sensex_5m = yf.download("^BSESN", period="5d", interval="15m", progress=False)
sensex_daily = yf.download("^BSESN", period="3mo", interval="1d", progress=False)

signals = []
s1 = check_stock("NIFTY", nifty_5m, nifty_daily)
if s1:
    signals.append(s1)
s2 = check_stock("SENSEX", sensex_5m, sensex_daily)
if s2:
    signals.append(s2)

if len(signals) > 0:
    msg = "\n".join(signals)
    print(msg)
    send_telegram(msg)
else:
    print("No breakout today")
