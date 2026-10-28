import yfinance as yf
import os, requests, time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","LT.NS","SBIN.NS","ITC.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","SUNPHARMA.NS","ULTRACEMCO.NS","TITAN.NS","ASIANPAINT.NS","HCLTECH.NS","WIPRO.NS","CIPLA.NS","NTPC.NS","POWERGRID.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","GRASIM.NS","BAJAJFINSV.NS","ADANIENT.NS","ADANIPORTS.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","M&M.NS","TATAMOTORS.NS","BRITANNIA.NS","NESTLEIND.NS","APOLLOHOSP.NS","DRREDDY.NS","DIVISLAB.NS","INDUSINDBK.NS","SBILIFE.NS","HDFCLIFE.NS","TECHM.NS","LTIM.NS","HINDUNILVR.NS","BPCL.NS","SHRIRAMFIN.NS","TRENT.NS","HAL.NS","BEL.NS","BDL.NS","MAZDOCK.NS","COCHINSHIP.NS","BHEL.NS","IRCTC.NS","IRFC.NS","RVNL.NS","IRCON.NS","ZOMATO.NS","PAYTM.NS","DMART.NS","VBL.NS","TATACONSUM.NS","PIDILITIND.NS","INDIGO.NS","TATAPOWER.NS","ADANIGREEN.NS","ADANIPOWER.NS","SUZLON.NS","NHPC.NS","IOC.NS","GAIL.NS","VEDL.NS","SAIL.NS","NMDC.NS","JINDALSTEL.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","UNIONBANK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","AUBANK.NS","BANDHANBNK.NS","YESBANK.NS","CHOLAFIN.NS","MUTHOOTFIN.NS","HDFCAMC.NS","ICICIPRULI.NS","LICI.NS","ANGELONE.NS","BSE.NS","CDSL.NS","PFC.NS","RECLTD.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PHOENIXLTD.NS","INDHOTEL.NS","ASHOKLEY.NS","BHARATFORG.NS","MOTHERSON.NS","BOSCHLTD.NS","MRF.NS","BALKRISIND.NS","APOLLOTYRE.NS","TVSMOTOR.NS","POLYCAB.NS","HAVELLS.NS","CUMMINSIND.NS","ABB.NS","SIEMENS.NS","HINDZINC.NS","SRF.NS","ATGL.NS","IGL.NS","MGL.NS","PETRONET.NS","JUBLFOOD.NS","NAUKRI.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS","LTF.NS","MANAPPURAM.NS","MFSL.NS","ICICIGI.NS","SBICARD.NS","ABCAPITAL.NS","TORNTPHARM.NS","LAURUSLABS.NS","GLENMARK.NS","BIOCON.NS","AUROPHARMA.NS","ALKEM.NS","IPCALAB.NS","LUPIN.NS","ZYDUSLIFE.NS","TATACOMM.NS","CONCOR.NS","AIAENG.NS","DEEPAKNTR.NS","PIIND.NS","COROMANDEL.NS","UPL.NS","CHAMBLFERT.NS","BALRAMCHIN.NS","DABUR.NS","MARICO.NS","GODREJCP.NS","COLPAL.NS","HINDPETRO.NS","EXIDEIND.NS","AMARAJABAT.NS","ESCORTS.NS","TIINDIA.NS","VOLTAS.NS","BLUESTARCO.NS","KAYNES.NS","DIXON.NS","AMBER.NS","SYNGENE.NS","TATAELXSI.NS","KPITTECH.NS","LTTS.NS","TATAINVEST.NS","JSWENERGY.NS","TORNTPOWER.NS","ADANIENSOL.NS","NTPCGREEN.NS"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for i in range(0, len(msg), 3500):
        try:
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg[i:i+3500]}, timeout=20)
            time.sleep(0.3)
        except: pass

def check(s):
    try:
        df = yf.download(s, period="50d", interval="1d", progress=False, auto_adjust=True, threads=False)
        if len(df) < 40: return None
        c = float(df['Close'].iloc[-1]); e20 = float(df['Close'].ewm(span=20).mean().iloc[-1]); e50 = float(df['Close'].ewm(span=50).mean().iloc[-1])
        if c > e20 > e50: return f"✅ {s.replace('.NS','')} {c:.0f}"
    except: return None

sigs=[]
with ThreadPoolExecutor(max_workers=15) as ex:
    for f in as_completed([ex.submit(check, s) for s in STOCKS]):
        r=f.result()
        if r: sigs.append(r)

msg = f"🚀 BOND 007 - {len(STOCKS)} SCAN\n📅 {datetime.now().strftime('%d-%m %H:%M')}\nBUY: {len(sigs)}\n\n" + "\n".join(sigs) if sigs else f"No BUY today - {len(STOCKS)} scanned"
print(msg)
send_telegram(msg)
