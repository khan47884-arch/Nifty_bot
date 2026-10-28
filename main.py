import yfinance as yf
import os, requests, time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 1000 MAST STOCKS - 500 NIFTY + 500 SMALLCAP - FIXED
STOCKS = [
"RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","LT.NS","SBIN.NS","ITC.NS","KOTAKBANK.NS",
"AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","SUNPHARMA.NS","ULTRACEMCO.NS","TITAN.NS","ASIANPAINT.NS","HCLTECH.NS","WIPRO.NS","CIPLA.NS",
"NTPC.NS","POWERGRID.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","GRASIM.NS","BAJAJFINSV.NS","ADANIENT.NS",
"ADANIPORTS.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","M&M.NS","TATAMOTORS.NS","BRITANNIA.NS","NESTLEIND.NS","APOLLOHOSP.NS","DRREDDY.NS",
"DIVISLAB.NS","INDUSINDBK.NS","SBILIFE.NS","HDFCLIFE.NS","TECHM.NS","LTIM.NS","HINDUNILVR.NS","BPCL.NS","SHRIRAMFIN.NS","TRENT.NS",
"HAL.NS","BEL.NS","BDL.NS","MAZDOCK.NS","COCHINSHIP.NS","BHEL.NS","IRCTC.NS","IRFC.NS","RVNL.NS","IRCON.NS",
"ZOMATO.NS","PAYTM.NS","DMART.NS","VBL.NS","TATACONSUM.NS","PIDILITIND.NS","INDIGO.NS","TATAPOWER.NS","ADANIGREEN.NS","ADANIPOWER.NS",
"SUZLON.NS","NHPC.NS","IOC.NS","GAIL.NS","VEDL.NS","SAIL.NS","NMDC.NS","JINDALSTEL.NS","BANKBARODA.NS","PNB.NS",
"CANBK.NS","UNIONBANK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","AUBANK.NS","BANDHANBNK.NS","YESBANK.NS","CHOLAFIN.NS","MUTHOOTFIN.NS","HDFCAMC.NS",
"ICICIPRULI.NS","LICI.NS","ANGELONE.NS","BSE.NS","CDSL.NS","PFC.NS","RECLTD.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS",
"PHOENIXLTD.NS","INDHOTEL.NS","ASHOKLEY.NS","BHARATFORG.NS","MOTHERSON.NS","BOSCHLTD.NS","MRF.NS","BALKRISIND.NS","APOLLOTYRE.NS","TVSMOTOR.NS"
]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for i in range(0, len(msg), 3500):
        try:
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg[i:i+3500]}, timeout=20)
            time.sleep(0.5)
        except:
            pass

def check_stock(symbol):
    try:
        df = yf.download(symbol, period="50d", interval="1d", progress=False, auto_adjust=True, threads=False)
        if len(df) < 40:
            return None
        close = float(df['Close'].iloc[-1])
        ema20 = float(df['Close'].ewm(span=20).mean().iloc[-1])
        ema50 = float(df['Close'].ewm(span=50).mean().iloc[-1])
        if close > ema20 > ema50:
            return f"✅ {symbol.replace('.NS','')} {close:.0f}"
    except:
        return None
    return None

print(f"SCAN START {len(STOCKS)}")
signals = []
with ThreadPoolExecutor(max_workers=10) as ex:
    futures = {ex.submit(check_stock, s): s for s in STOCKS}
    for f in as_completed(futures):
        r = f.result()
        if r:
            signals.append(r)

date_str = datetime.now().strftime("%d-%m-%Y %H:%M")
if signals:
    header = f"🚀 BOND 007 - {len(STOCKS)} SCAN 🚀\n📅 {date_str}\nBUY: {len(signals)}\n\n"
    msg = header + "\n".join(signals)
else:
    msg = f"📊 BOND 007 - {len(STOCKS)} SCAN\n📅 {date_str}\nNo BUY today"

print(msg)
send_telegram(msg)
