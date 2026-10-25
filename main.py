import requests, os, yfinance as yf
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

#FETCH LIVE
try:
    nifty = yf.Ticker("^NSEI").history(period="5d")
    nifty_close = round(nifty['Close'].iloc[-1], 2)
    nifty_prev = round(nifty['Close'].iloc[-2], 2)
    brent = round(yf.Ticker("BZ=F").history(period="1d")['Close'].iloc[-1], 2)
    mcx_est = round(brent * 83.5 * 7.33 / 159)
except:
    nifty_close = 22500
    nifty_prev = 22650
    brent = 117.38
    mcx_est = 9783
#
NIFTY SIGNAL
diff = nifty_close - nifty_prev
if diff > 0:
    nifty_signal = f"🟢 Gap Up (+{round(diff,1)}) - Sell on Rise"
else:
    nifty_signal = f"🔴 Gap Down ({round(diff,1)}) - Buy on Dip"

nifty_sup = round(nifty_close * 0.99)
nifty_res = round(nifty_close * 1.01)

CRUDE SIGNAL
if brent > 115:
#    crude_signal = "🔴 HIGH - Sell near 9800-9850"
    crude_level = "Res: 9827 / 10000 | Sup: 9550"
else:
    crude_signal = "🟢 Buy on Dip 9550-9600"
    crude_level = "Target: 10000 | SL: 9496"

now = datetime.now().strftime('%d %b %Y, %a %I:%M %p')

msg = f"""📊 *NIFTY + CRUDE LIVE - {now}*

*NIFTY 50:*
Price: {nifty_close} ({'+' if diff>0 else ''}{round(diff,1)})
Signal: {nifty_signal}
Support: {nifty_sup} | Resistance: {nifty_res}

*CRUDE OIL:*
Brent: ${brent} | MCX Est: Rs {mcx_est}
Signal: {crude_signal}
Level: {crude_level}

*Final Plan:*
Nifty: {nifty_signal}
Crude: {crude_signal}
