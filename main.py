import os
import requests
import yfinance as yf

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

try:
    nifty = yf.Ticker("^NSEI").history(period="2d")
    nifty_close = round(nifty['Close'].iloc[-1])
    nifty_prev = round(nifty['Close'].iloc[-2])
    brent = round(yf.Ticker("BZ=F").history(period="1d")['Close'].iloc[-1], 2)
    mcx_est = round(brent * 83.5 * 7.43)
except:
    nifty_close = 22500
    nifty_prev = 22650
    brent = 117.38
    mcx_est = 9783

diff = nifty_close - nifty_prev
if diff > 0:
    nifty_signal = f"Gap Up (+{round(diff)})"
else:
    nifty_signal = f"Gap Down ({round(diff)})"

nifty_sup = round(nifty_close * 0.99)
nifty_res = round(nifty_close * 1.01)

if brent > 115:
    crude_signal = "HIGH - Sell on Rise"
    crude_level = "Res: 9827 / 10000"
else:
    crude_signal = "Buy on Dip 9550"
    crude_level = "Tgt: 10000 | SL: 9400"

msg = f"DAILY MARKET ALERT\n\nNIFTY 50: {nifty_close} ({diff})\nSignal: {nifty_signal}\nSupport: {nifty_sup} | Resistance: {nifty_res}\n\nCRUDE OIL (MCX EST): {mcx_est}\nBrent: ${brent}\nSignal: {crude_signal}\nLevel: {crude_level}"
