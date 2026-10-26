import yfinance as yf
import requests, os, time, datetime
from concurrent.futures import ThreadPoolExecutor

if datetime.datetime.now().hour < 10:
    print("Market time hai, screener abhi nahi chalega")
    exit()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        for i in range(0, len(msg), 3500):
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg[i:i+3500]}, timeout=15)
            time.sleep(1)
    except: pass

# NIFTY 1000 FULL LIST - 600+ TOP LIQUID
STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","TITAN.NS","BAJFINANCE.NS","MARUTI.NS","TATAMOTORS.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","ADANIENT.NS","ADANIPORTS.NS","ADANIPOWER.NS","ADANIGREEN.NS","ADANIENSOL.NS","POLYCAB.NS","PERSISTENT.NS","COFORGE.NS","LTIM.NS","MPHASIS.NS","LTTS.NS","HAL.NS","BEL.NS","MAZDOCK.NS","RVNL.NS","IRFC.NS","IRCTC.NS","SJVN.NS","NHPC.NS","TATAPOWER.NS","NTPC.NS","POWERGRID.NS","SUZLON.NS","JIOFIN.NS","CDSL.NS","BSE.NS","ANGELONE.NS","MCX.NS","IEX.NS","ZOMATO.NS","PAYTM.NS","NYKAA.NS","DIXON.NS","CGPOWER.NS","BHEL.NS","COALINDIA.NS","ONGC.NS","VEDL.NS","HINDZINC.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS","MANKIND.NS","LUPIN.NS","CIPLA.NS","SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS","CUMMINSIND.NS","ASHOKLEY.NS","MOTHERSON.NS","BOSCHLTD.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","TVSMOTOR.NS","ULTRACEMCO.NS","GRASIM.NS","AMBUJACEM.NS","ACC.NS","JKCEMENT.NS","ASIANPAINT.NS","BERGEPAINT.NS","PIDILITIND.NS","HAVELLS.NS","VOLTAS.NS","BLUESTARCO.NS","KAYNES.NS","SYRMA.NS","TATAELXSI.NS","TATATECH.NS","TATACOMM.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","ICICIPRULI.NS","ICICIGI.NS","MUTHOOTFIN.NS","MANAPPURAM.NS","CHOLAFIN.NS","SHRIRAMFIN.NS","RECLTD.NS","PFC.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","INDUSINDBK.NS","KOTAKBANK.NS","AXISBANK.NS","AUBANK.NS","DMART.NS","TRENT.NS","KALYANKJIL.NS","TITAGARH.NS","JINDALSTEL.NS","SAIL.NS","NATIONALUM.NS","JSWENERGY.NS","TORNTPOWER.NS","INDIANB.NS","UNIONBANK.NS","BHARATFORG.NS","M&M.NS","SRF.NS","DEEPAKNTR.NS","NAVINFLUOR.NS","UPL.NS","PIIND.NS","COROMANDEL.NS","CHAMBLFERT.NS","FACT.NS","HINDPETRO.NS","BPCL.NS","IOC.NS","GAIL.NS","PETRONET.NS","IGL.NS","MGL.NS","GUJGASLTD.NS","BALKRISIND.NS","MRF.NS","APOLLOTYRE.NS","CEAT.NS","BATAINDIA.NS","PATANJALI.NS","DABUR.NS","MARICO.NS","GODREJCP.NS","HINDUNILVR.NS","BRITANNIA.NS","NESTLEIND.NS","TATACONSUM.NS","VARUNBEV.NS","JUBLFOOD.NS","INDIGO.NS","IRB.NS","NBCC.NS","HUDCO.NS","NCC.NS","KEI.NS","RRKABEL.NS","ASTRAL.NS","SUPREMEIND.NS","PAGEIND.NS","RAYMOND.NS","VBL.NS","OFSS.NS","BSOFT.NS","ZENSAR.NS","CYIENT.NS","INTELLECT.NS","MASTEK.NS","HONASA.NS","ATUL.NS","VINATIORGA.NS","TATACHEM.NS","GLENMARK.NS","LAURUSLABS.NS","IPCALAB.NS","ALKEM.NS","TORNTPHARM.NS","ABB.NS","SIEMENS.NS","ABBOTINDIA.NS","SCHAEFFLER.NS","TIMKEN.NS","SKFINDIA.NS","THERMAX.NS","CROMPTON.NS","WHIRLPOOL.NS","AMBER.NS","AIAENG.NS","BEML.NS","COCHINSHIP.NS","GARDENREACH.NS","PRAJIND.NS","LICHSGFIN.NS","LICI.NS","GICRE.NS","STARHEALTH.NS","SBICARD.NS","CAMS.NS","KFINTECH.NS","360ONE.NS","ANANDRATHI.NS","MOTILALOFS.NS","IIFL.NS","EQUITASBNK.NS","UJJIVANSFB.NS","BANDHANBNK.NS","CREDITACC.NS","M&MFIN.NS","POONAWALLA.NS","INDIAMART.NS","EIHOTEL.NS","CHALET.NS","LEMONTREE.NS","AFFLE.NS","ROUTE.NS","KPIL.NS","KALPATPOWR.NS","KEC.NS","LTF.NS","PNBHOUSING.NS","CANFINHOME.NS","AAVAS.NS","CENTRALBK.NS","BANKINDIA.NS","MAHABANK.NS","IOB.NS","YESBANK.NS","HDFCAMC.NS","UTIAMC.NS","WELCORP.NS","ARVIND.NS","JUBLINGREA.NS","GRANULES.NS","NATCOPHARM.NS","SYNGENE.NS","MEDPLUS.NS","METROPOLIS.NS","LALPATHLAB.NS","MAXHEALTH.NS","FORTIS.NS","APOLLOHOSP.NS","CRAFTSMAN.NS","ENDURANCE.NS","MINDACORP.NS","MAHSEAMLES.NS","RATNAMANI.NS","GMDCLTD.NS","MOIL.NS","HINDCOPPER.NS","NMDC.NS","OIL.NS","GSPL.NS","INOXWIND.NS","HFCL.NS","TATACOMM.NS","IDEA.NS","BHARTIHEXA.NS","AWL.NS","GODREJAGRO.NS","BALRAMCHIN.NS","EIDPARRY.NS","TRIVENI.NS","SWANENERGY.NS","GMRINFRA.NS","SOBHA.NS","BRIGADE.NS","LODHA.NS","HEIDELBERG.NS","INDIACEM.NS","RAMCOCEM.NS","CLEAN.NS","FINEORG.NS","AETHER.NS","MEDANTA.NS","KIMS.NS","GLAND.NS","APARINDS.NS","HONAUT.NS","ELGIEQUIP.NS","MMFL.NS","DELHIVERY.NS","BLUEDART.NS","SHREECEM.NS","JKLAKSHMI.NS","JKPAPER.NS","VIPIND.NS","SAFARI.NS","CERA.NS","VGUARD.NS","DOLLAR.NS","KPRMILL.NS","SPANDANA.NS","MASFIN.NS","NUVAMA.NS","IRCON.NS","RAILTEL.NS","BDL.NS","MTARTECH.NS","PGEL.NS","PCJEWELLER.NS","KAJARIACER.NS","BORORENEW.NS","TTKPRESTIG.NS","WELSPUNLIV.NS","UFLEX.NS","EPL.NS","GRINDWELL.NS","ULTRACEMCO.NS","SUZLON.NS","INOXWIND.NS"]

def is_bullish_hammer(row):
    o,h,l,c = float(row['Open']),float(row['High']),float(row['Low']),float(row['Close'])
    body = abs(c-o); rng = h-l; lower = min(o,c)-l
    if rng==0: return False
    return (lower >= body*2) and (c>o) and (body/rng < 0.4)

def is_bullish_engulfing(curr, prev):
    return (float(prev['Close'])<float(prev['Open']) and float(curr['Close'])>float(curr['Open']) and float(curr['Open'])<float(prev['Close']) and float(curr['Close'])>float(prev['Open']))

def scan_single(sym):
    try:
        df = yf.download(sym, period="1y", interval="1d", progress=False, auto_adjust=True)
        if len(df) < 210: return None
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
        cross_days = 0
        for i in range(1, 21):
            if df['EMA50'].iloc[-i-1] < df['EMA200'].iloc[-i-1] and df['EMA50'].iloc[-i] > df['EMA200'].iloc[-i]:
                cross_days = i
                break
        if cross_days == 0: return None
        curr = df.iloc[-1]; prev = df.iloc[-2]
        price = float(curr['Close']); ema50 = float(curr['EMA50']); ema200 = float(curr['EMA200'])
        low_10 = float(df['Low'].iloc[-10:].min())
        if abs(price - ema50) / ema50 > 0.04: return None
        hammer = is_bullish_hammer(curr)
        engulf = is_bullish_engulfing(curr, prev)
        body = abs(float(curr['Close'])-float(curr['Open']))
        rng = float(curr['High'])-float(curr['Low'])
        strong = (rng>0 and body/rng>0.6 and float(curr['Close'])>float(curr['Open']))
        if not (hammer or engulf or strong): return None
        sl_base = min(low_10, ema200)
        sl = sl_base * 0.98
        sl_percent = ((price - sl) / price) * 100
        if sl_percent > 8: return None
        t1 = price * 1.10; t4 = price * 1.50
        risk = price - sl
        rr1 = (t1-price)/risk if risk>0 else 0
        if hammer: candle_name = "BULLISH HAMMER"
        elif engulf: candle_name = "BULLISH ENGULFING"
        else: candle_name = "BULLISH GREEN"
        return f"✅ {sym.replace('.NS','')} - {candle_name} {cross_days}d ago ENTRY: {price:.0f} SL: {sl:.0f} ({sl_percent:.1f}%) T1: {t1:.0f} T4: {t4:.0f} RR:{rr1:.1f}"
    except:
        return None

found = []
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(scan_single, sym): sym for sym in STOCKS}
    for f in futures:
        res = f.result()
        if res: found.append(res)

if not found:
    msg = "Aaj koi CONFIRM Golden Cross nahi mila [NIFTY 1000 Scan]"
else:
    found = list(dict.fromkeys(found))
    msg = f"💥 NIFTY 1000 SCAN - {len(found)} SHARES 💥\n\n" + "\n".join(found[:30])
print(msg)
send_telegram(msg)
