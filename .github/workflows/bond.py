import warnings
warnings.filterwarnings("ignore")
import yfinance as yf, requests, os, time
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for i in range(0, len(msg), 3900):
        try: 
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg[i:i+3900]}, timeout=25)
            time.sleep(1)
        except: pass

STOCKS = [
"RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","MARUTI.NS","TATAMOTORS.NS","M&M.NS","BAJFINANCE.NS","KOTAKBANK.NS","AXISBANK.NS","ASIANPAINT.NS","TITAN.NS","HINDALCO.NS","TATASTEEL.NS","JSWSTEEL.NS","ULTRACEMCO.NS","SUNPHARMA.NS","NTPC.NS","POWERGRID.NS","ONGC.NS","ADANIENT.NS","ADANIPORTS.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","COALINDIA.NS","BPCL.NS","BRITANNIA.NS","EICHERMOT.NS","GRASIM.NS","HINDUNILVR.NS","CIPLA.NS","DIVISLAB.NS","DRREDDY.NS","APOLLOHOSP.NS","BAJAJFINSV.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","INDUSINDBK.NS","SBILIFE.NS","HDFCLIFE.NS","JSWENERGY.NS","TATACONSUM.NS","TRENT.NS",
"POLYCAB.NS","PERSISTENT.NS","COFORGE.NS","LTIM.NS","MPHASIS.NS","LTTS.NS","HAL.NS","BEL.NS","BDL.NS","MAZDOCK.NS","COCHINSHIP.NS","RVNL.NS","IRFC.NS","IRCTC.NS","TATAPOWER.NS","NHPC.NS","SJVN.NS","PFC.NS","RECLTD.NS","TATACOMM.NS","INDIGO.NS","DIXON.NS","CGPOWER.NS","BHEL.NS","CUMMINSIND.NS","ABB.NS","SIEMENS.NS","VOLTAS.NS","BLUESTARCO.NS","HAVELLS.NS","KEI.NS","APARINDS.NS","ASTRAL.NS","CROMPTON.NS","VGUARD.NS","MOTHERSON.NS","BOSCHLTD.NS","TVSMOTOR.NS","ASHOKLEY.NS","BHARATFORG.NS","MRF.NS","BALKRISIND.NS","BATAINDIA.NS","RELAXO.NS","PAGEIND.NS","RAYMOND.NS","SAFARI.NS","DMART.NS","ABFRL.NS","VEDL.NS","SAIL.NS","JINDALSTEL.NS","HINDCOPPER.NS","NATIONALUM.NS","JSL.NS","NMDC.NS","OIL.NS","GAIL.NS","PETRONET.NS","IGL.NS","MGL.NS","GSPL.NS","LUPIN.NS","ZYDUSLIFE.NS","ALKEM.NS","IPCALAB.NS","AUROPHARMA.NS","GLENMARK.NS","BIOCON.NS","LAURUSLABS.NS","SYNGENE.NS","MANKIND.NS","FORTIS.NS","MAXHEALTH.NS","MEDANTA.NS","CERA.NS","KAJARIACER.NS","BERGEPAINT.NS","PIDILITIND.NS","SRF.NS","AARTIIND.NS","DEEPAKNTR.NS","ATUL.NS","VINATIORGA.NS","PIIND.NS","UPL.NS","COROMANDEL.NS","CHAMBLFERT.NS","LTF.NS","CHOLAFIN.NS","MUTHOOTFIN.NS","CREDITACC.NS","M&MFIN.NS","BAJAJHLDNG.NS","HDFCAMC.NS","CDSL.NS","BSE.NS","MCX.NS","ANGELONE.NS","CAMS.NS","KFINTECH.NS","MOTILALOFS.NS","NUVAMA.NS","360ONE.NS","DALBHARAT.NS","ACC.NS","AMBUJACEM.NS","JKCEMENT.NS","RAMCOCEM.NS","SHREECEM.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS","LODHA.NS","BRIGADE.NS","SOBHA.NS","PHOENIXLTD.NS","NBCC.NS","HUDCO.NS","IRB.NS","GMRINFRA.NS","CONCOR.NS","TITAGARH.NS","JWL.NS","TEXRAIL.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","AUBANK.NS","BANDHANBNK.NS","KARURVYSYA.NS","RBLBANK.NS","EQUITASBNK.NS","UJJIVANSFB.NS","INDIAMART.NS","AFFLE.NS","NAUKRI.NS","MAPMYINDIA.NS","TANLA.NS","ROUTE.NS","KPITTECH.NS","TATAELXSI.NS","NYKAA.NS","ZOMATO.NS","PAYTM.NS","PBFINTECH.NS","DELHIVERY.NS","VBL.NS","VARUNBEV.NS","DABUR.NS","MARICO.NS","GODREJCP.NS","COLPAL.NS","HONASA.NS","JUBLFOOD.NS","DEVYANI.NS","DOMS.NS","KPRMILL.NS","WELSPUNLIV.NS",
"SUZLON.NS","IDEA.NS","YESBANK.NS","JPOWER.NS","JPPOWER.NS","JPASSOCIAT.NS","RENUKA.NS","ALOKINDS.NS","NCC.NS","IRCON.NS","RAILTEL.NS","RITES.NS","BEML.NS","GRSE.NS","PRAJIND.NS","TRIVENI.NS","JINDALSAW.NS","WELCORP.NS","RATNAMANI.NS","ELECON.NS","JYOTICNC.NS","KAYNES.NS","AMBER.NS","PGEL.NS","SYRMA.NS","INOXWIND.NS","BORORENEW.NS","WAAREEENER.NS","PREMIERENE.NS","KPIGREEN.NS","ADANIPOWER.NS","ADANIGREEN.NS","ADANIENSOL.NS","ATGL.NS","IEX.NS","CESC.NS","TORNTPOWER.NS","MRPL.NS","CHENNPETRO.NS","FACT.NS","RCF.NS","GNFC.NS","GSFC.NS","DEEPAKFERT.NS","ZUARI.NS","SUMICHEM.NS","FINOLEXIND.NS","SUPREMEIND.NS","PNBHOUSING.NS","AAVAS.NS","CANFINHOME.NS","HOMEFIRST.NS","APTUS.NS","FIVE-STAR.NS","MASFIN.NS","BANKINDIA.NS","MAHABANK.NS","CENTRALBK.NS","INDIANB.NS","UCOBANK.NS","IOB.NS","UNIONBANK.NS","HDFCAMC.NS","UTIAMC.NS","ANANDRATHI.NS","LICI.NS","SBICARD.NS","ICICIGI.NS","STARHEALTH.NS","GLAND.NS","JBCHEPHARM.NS","NATCOPHARM.NS","METROPOLIS.NS","LALPATHLAB.NS","RAINBOW.NS","VIJAYA.NS","ASTERDM.NS","POLYMED.NS","AJANTPHARM.NS","TORNTPHARM.NS","GRANULES.NS","HINDWAREAP.NS","GREENPANEL.NS","CENTURYPLY.NS","KANSAINER.NS","INDIGOPNTS.NS","BALRAMCHIN.NS","EIDPARRY.NS","AVANTIFEED.NS","HEIDELBERG.NS","INDIACEM.NS","BIRLACORPN.NS","TATASTLLP.NS","SAIL.NS","JSL.NS","ASHOKLEY.NS","ESCORTS.NS","EXIDEIND.NS","AMARAJABAT.NS","APOLLOTYRE.NS","CEAT.NS","ENDURANCE.NS","UNOMINDA.NS","SONACOMS.NS","CRAFTSMAN.NS","TIINDIA.NS","HONAUT.NS","SKFINDIA.NS","GRINDWELL.NS","AIAENG.NS","VA_TECH.NS","ISGEC.NS","LAKSHMIMACH.NS","VOLTAS.NS","WHIRLPOOL.NS","TTKPRESTIG.NS","METROBRAND.NS","KALYANKJIL.NS","SENC0.NS","ARVIND.NS","VTL.NS","GOKEX.NS","VIPIND.NS","CAMPUS.NS","BAJAJCON.NS","JYOTHYLAB.NS","CCL.NS","RADICO.NS","SULA.NS","MCDOWELL-N.NS","MANYAVAR.NS","INTELLECT.NS","BSOFT.NS","SONATSOFTW.NS","CYIENT.NS","ZENSARTECH.NS","OFSS.NS","HAPPSTMNDS.NS","SPICEJET.NS","AEGISLOG.NS","GESHIP.NS","SCI.NS"
]

def scan_single(sym):
    try:
        df = yf.download(sym, period="1y", interval="1d", progress=False, auto_adjust=True, threads=False)
        if len(df) < 210: return None
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['EMA200'] = df['Close'].ewm(span=200).mean()
        df['Vol20'] = df['Volume'].rolling(20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        cross_found = False
        cross_day = 0
        for i in range(1, 6):
            if df['EMA50'].iloc[-i-1] < df['EMA200'].iloc[-i-1] and df['EMA50'].iloc[-i] > df['EMA200'].iloc[-i]:
                cross_found = True
                cross_day = i
                break
        if not cross_found: return None
        last = df.iloc[-1]
        if not (last['Close'] > last['EMA50'] > last['EMA200']): return None
        if last['Volume'] < last['Vol20'] * 1.8: return None
        if not (55 <= last['RSI'] <= 78): return None
        day_range = last['High'] - last['Low']
        if day_range == 0: return None
        if (last['Close'] - last['Low']) / day_range < 0.7: return None
        sl = float(df['Low'].iloc[-10:].min()) * 0.98
        slp = (last['Close'] - sl) / last['Close'] * 100
        if not (2.5 <= slp <= 6.5): return None
        if df['EMA50'].iloc[-1] <= df['EMA50'].iloc[-5]: return None
        price = float(last['Close'])
        cap_type = "LARGE" if sym in STOCKS[:50] else "MID" if sym in STOCKS[50:250] else "SMALL BOOM"
        return f"🔥 {cap_type} {sym.replace('.NS','')} ({cross_day}d)\nENTRY: {price:.0f} | SL: {sl:.0f} ({slp:.1f}%)\nVOL: {last['Volume']/last['Vol20']:.1f}x | RSI: {last['RSI']:.0f}\nT1:{price*1.12:.0f} T2:{price*1.25:.0f} T3:{price*1.45:.0f} 🚀"
    except: return None

found=[]
with ThreadPoolExecutor(max_workers=10) as ex:
    for r in ex.map(scan_single, list(set(STOCKS))):
        if r: found.append(r)

if not found:
    msg = "⚪ Aaj ELITE moka nahi mila [600+ MIX SCAN] - Bot OK hai"
else:
    msg = f"💎💥 ELITE 600 MIX SCAN - {len(found)} BOOM STOCK 💥💎\nLARGE+MID+SMALL\n\n" + "\n\n---\n\n".join(found[:20])

print(msg)
send_telegram(msg)
