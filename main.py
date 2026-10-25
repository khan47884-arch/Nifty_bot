import os
import requests
import yfinance as yf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

try:
    nifty = yf.Ticker("^NSEI").history(period="5d")
    nifty_close = round(nifty['Close'].iloc[-1])
    nifty_prev = round(nifty['Close'].iloc[-2])
    nifty_change = nifty_close - nifty_prev

    brent = round(yf.Ticker("BZ=F").history(period="5d")['Close'].iloc[-1], 2)
    mcx_est = int(brent * 83)

    gap = "Gap Up" if nifty_change > 0 else "Gap Down"
    support = nifty_close - 225
    resistance = nifty_close + 225
    crude_signal = "HIGH - Sell on Rise" if mcx_est > 9500 else "LOW - Buy on Dip"

    msg = f"""DAILY MARKET ALERT

NIFTY 50: {nifty_close} ({nifty_change})
Signal: {gap} ({nifty_change})
Support: {support} | Resistance: {resistance}

CRUDE OIL (MCX EST): {mcx_est}
Brent: ${brent}
Signal: {crude_signal}
Level: Res: {mcx_est+50} / 10000"""

    send(msg)
    print(msg)

except Exception as e:
    print(f"Error {e}")
    # Fallback agar net fail ho
    send(f"Nifty Bot Error: {e}")
