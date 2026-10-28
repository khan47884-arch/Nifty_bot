import yfinance as yf
import os, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","LT.NS","SBIN.NS","ITC.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","SUNPHARMA.NS","ULTRACEMCO.NS","TITAN.NS","ASIANPAINT.NS","HCLTECH.NS","WIPRO.NS","CIPLA.NS","NTPC.NS","POWERGRID.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","GRASIM.NS","BAJAJFINSV.NS","ADANIENT.NS","ADANIPORTS.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","M&M.NS","TATAMOTORS.NS","BRITANNIA.NS","NESTLEIND.NS","APOLLOHOSP.NS","DRREDDY.NS","DIVISLAB.NS","INDUSINDBK.NS","SBILIFE.NS","HDFCLIFE.NS","TECHM.NS","LTIM.NS","HINDUNILVR.NS","BPCL.NS","SHRIRAMFIN.NS","TRENT.NS","HAL.NS","BEL.NS","BDL.NS","MAZDOCK.NS","COCHINSHIP.NS","BHEL.NS","IRCTC.NS","IRFC.NS","RVNL.NS","IRCON.NS","ZOMATO.NS","PAYTM.NS","DMART.NS","VBL.NS","TATACONSUM.NS","PIDILITIND.NS","INDIGO.NS","TATAPOWER.NS","ADANIGREEN.NS","ADANIPOWER.NS","SUZLON.NS","NHPC.NS","IOC.NS","GAIL.NS","VEDL.NS","SAIL.NS","NMDC.NS","JINDALSTEL.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","UNIONBANK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","AUBANK.NS","BANDHANBNK.NS","YESBANK.NS","CHOLAFIN.NS","MUTHOOTFIN.NS","HDFCAMC.NS","ICICIPRULI.NS","LICI.NS","ANGELONE.NS","BSE.NS","CDSL.NS","PFC.NS","RECLTD.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PHOENIXLTD.NS","INDHOTEL.NS","ASHOKLEY.NS","BHARATFORG.NS","MOTHERSON.NS","BOSCHLTD.NS","MRF.NS","BALKRISIND.NS","APOLLOTYRE.NS","TVSMOTOR.NS","POLYCAB.NS","HAVELLS.NS","CUMMINSIND.NS","ABB.NS","SIEMENS.NS","HINDZINC.NS","SRF.NS","ATGL.NS","IGL.NS","MGL.NS","PETRONET.NS","JUBLFOOD.NS","NAUKRI.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS","LTF.NS","MANAPPURAM.NS","MFSL.NS","ICICIGI.NS","SBICARD.NS","ABCAPITAL.NS","TORNTPHARM.NS","LAURUSLABS.NS","GLENMARK.NS","BIOCON.NS","AUROPHARMA.NS","ALKEM.NS","IPCALAB.NS","LUPIN.NS","ZYDUSLIFE.NS","TATACOMM.NS","CONCOR.NS","AIAENG.NS","DEEPAKNTR.NS","PIIND.NS","COROMANDEL.NS","UPL.NS","CHAMBLFERT.NS","BALRAMCHIN.NS","DABUR.NS","MARICO.NS","GODREJCP.NS","COLPAL.NS","HINDPETRO.NS","EXIDEIND.NS","AMARAJABAT.NS","ESCORTS.NS","TIINDIA.NS","VOLTAS.NS","BLUESTARCO.NS","KAYNES.NS","DIXON.NS","AMBER.NS","SYNGENE.NS","TATAELXSI.NS","KPITTECH.NS","LTTS.NS","JSWENERGY.NS","TORNTPOWER.NS"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for i in range(0, len(msg), 3900):
        try: requests.post(url, data={"chat_id": CHAT_ID, "text": msg[i:i+3900]}, timeout=25)
        except: pass

def get_pattern(df):
    if len(df)<3: return "NO PATTERN"
    o,h,l,c = map(float, df.iloc[-1][["Open","High","Low","Close"]])
    po,ph,pl,pc = map(float, df.iloc[-2][["Open","High","Low","Close"]])
    body = abs(c-o)
    lower = min(o,c)-l
    upper = h-max(o,c)
    if len(df)>=3 and df.iloc[-3]["Close"]>df.iloc[-3]["Open"] and df.iloc[-2]["Close"]>df.iloc[-2]["Open"] and c>o: return "THREE WHITE SOLDIERS"
    if len(df)>=3 and df.iloc[-3]["Close"]<df.iloc[-3]["Open"] and df.iloc[-2]["Close"]<df.iloc[-2]["Open"] and c<o: return "THREE BLACK CROWS"
    if pc<po and c>o and c>=po and o<=pc: return "BULLISH ENGULFING"
    if pc>po and c<o and o>=pc and c<=po: return "BEARISH ENGULFING"
    if lower>body*2 and upper<body*0.5 and c>o: return "HAMMER"
    if upper>body*2 and lower<body*0.5: return "INVERTED HAMMER" if c>o else "SHOOTING STAR"
    return "NO PATTERN"

def get_ema(d):
    cl = d["Close"]
    return float(cl.iloc[-1]), float(cl.ewm(20).mean().iloc[-1]), float(cl.ewm(50).mean().iloc[-1]), float(cl.ewm(200).mean().iloc[-1])

def atr(d, n=14):
    hl = d["High"]-d["Low"]
    return float(hl.rolling(n).mean().iloc[-1])

try:
    nifty = yf.download("^NSEI", period="3mo", interval="1d", progress=False, auto_adjust=True)
    sensex = yf.download("^BSESN", period="3mo", interval="1d", progress=False, auto_adjust=True)
    nifty_bull = float(nifty["Close"].iloc[-1]) > float(nifty["Close"].ewm(20).mean().iloc[-1])
    sensex_bull = float(sensex["Close"].iloc[-1]) > float(sensex["Close"].ewm(20).mean().iloc[-1])
except:
    nifty_bull, sensex_bull = True, True

def analyze(s):
    try:
        d = yf.download(s, period="1y", interval="1d", progress=False, auto_adjust=True)
        w = yf.download(s, period="2y", interval="1wk", progress=False, auto_adjust=True)
        m = yf.download(s, period="5y", interval="1mo", progress=False, auto_adjust=True)
        if len(d)<50 or len(w)<20 or len(m)<12: return None
        dp, wp, mp = get_pattern(d), get_pattern(w), get_pattern(m)
        price, e20, e50, e200 = get_ema(d)
        atr_val = atr(d)
        dh = float(d["High"].iloc[-1]); dl = float(d["Low"].iloc[-1])
        prev_h = float(d["High"].iloc[-2])
        gc = price>e20>e50
        if not gc: return None
        bull_p = ["BULLISH ENGULFING","HAMMER","INVERTED HAMMER","THREE WHITE SOLDIERS"]
        if not (dp in bull_p or wp in bull_p): return None
        entry = price
        sl = min(dl, e20*0.98)
        t1 = entry + atr_val*2
        t2 = entry + atr_val*4
        t3 = entry + atr_val*6
        risk = entry-sl
        reward = t1-entry
        conf = "3/3" if (dp in bull_p and wp in bull_p and mp in bull_p) else "2/3"
        dhdl = "DH BREAKOUT" if dh>prev_h else "AT DH" if price>=dh*0.98 else "MID"
        msg = f"""💣 BOND 007 - {conf} CONFIRMED 💣
📈 {s.replace('.NS','')} @ {price:.0f}
M:{mp} | W:{wp} | D:{dp}
⚡ GOLDEN CROSS | {dhdl}
📊 NIFTY:{'BULL' if nifty_bull else 'BEAR'} SENSEX:{'BULL' if sensex_bull else 'BEAR'}
━━━━━━━━━━━━
🎯 ENTRY: {entry:.0f}
🛑 SL: {sl:.0f} ({-risk/entry*100:.1f}%)
✅ T1: {t1:.0f}
✅ T2: {t2:.0f}
🚀 T3: {t3:.0f}
💰 R:R 1:{reward/risk if risk>0 else 0:.1f}
"""
        return msg
    except:
        return None

results=[]
with ThreadPoolExecutor(max_workers=10) as ex:
    futs=[ex.submit(analyze,s) for s in STOCKS]
    for f in as_completed(futs):
        r=f.result()
        if r: results.append(r)

date_str=datetime.now().strftime("%d-%m-%Y %H:%M")
if results:
    header=f"🚀 BOND 007 - ELITE BOND SCAN 🚀\n📅 {date_str}\n📊 NIFTY:{'BULLISH' if nifty_bull else 'BEARISH'} | Found: {len(results)} BOND\n----------------------------------------\n\n"
    final=header+"\n\n".join(results[:15])
else:
    final=f"📊 BOND 007 - {len(STOCKS)} SCAN\n📅 {date_str}\nNo 3/3 BOND today - Market WAIT\nNIFTY:{'BULL' if nifty_bull else 'BEAR'}"

print(final)
send_telegram(final)
