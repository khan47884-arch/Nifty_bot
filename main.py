Ye lo *FINAL 507 ELITE BOND* wala - same logic bas 507 stocks:
import yfinance as yf
import os, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","LT.NS","SBIN.NS","ITC.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","SUNPHARMA.NS","ULTRACEMCO.NS","TITAN.NS","ASIANPAINT.NS","HCLTECH.NS","WIPRO.NS","CIPLA.NS","NTPC.NS","POWERGRID.NS","ONGC.NS","COALINDIA.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","GRASIM.NS","BAJAJFINSV.NS","ADANIENT.NS","ADANIPORTS.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","M&M.NS","TATAMOTORS.NS","BRITANNIA.NS","NESTLEIND.NS","APOLLOHOSP.NS","DRREDDY.NS","DIVISLAB.NS","INDUSINDBK.NS","SBILIFE.NS","HDFCLIFE.NS","TECHM.NS","LTIM.NS","HINDUNILVR.NS","BPCL.NS","SHRIRAMFIN.NS","TRENT.NS","HAL.NS","BEL.NS","BDL.NS","MAZDOCK.NS","COCHINSHIP.NS","BHEL.NS","IRCTC.NS","IRFC.NS","RVNL.NS","IRCON.NS","ZOMATO.NS","PAYTM.NS","DMART.NS","VBL.NS","TATACONSUM.NS","PIDILITIND.NS","INDIGO.NS","TATAPOWER.NS","ADANIGREEN.NS","ADANIPOWER.NS","SUZLON.NS","NHPC.NS","IOC.NS","GAIL.NS","VEDL.NS","SAIL.NS","NMDC.NS","JINDALSTEL.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","UNIONBANK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","AUBANK.NS","BANDHANBNK.NS","YESBANK.NS","CHOLAFIN.NS","MUTHOOTFIN.NS","HDFCAMC.NS","ICICIPRULI.NS","LICI.NS","ANGELONE.NS","BSE.NS","CDSL.NS","PFC.NS","RECLTD.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PHOENIXLTD.NS","INDHOTEL.NS","ASHOKLEY.NS","BHARATFORG.NS","MOTHERSON.NS","BOSCHLTD.NS","MRF.NS","BALKRISIND.NS","APOLLOTYRE.NS","TVSMOTOR.NS","POLYCAB.NS","HAVELLS.NS","CUMMINSIND.NS","ABB.NS","SIEMENS.NS","HINDZINC.NS","SRF.NS","ATGL.NS","IGL.NS","MGL.NS","PETRONET.NS","JUBLFOOD.NS","NAUKRI.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS","LTF.NS","MANAPPURAM.NS","MFSL.NS","ICICIGI.NS","SBICARD.NS","ABCAPITAL.NS","TORNTPHARM.NS","LAURUSLABS.NS","GLENMARK.NS","BIOCON.NS","AUROPHARMA.NS","ALKEM.NS","IPCALAB.NS","LUPIN.NS","ZYDUSLIFE.NS","TATACOMM.NS","CONCOR.NS","AIAENG.NS","DEEPAKNTR.NS","PIIND.NS","COROMANDEL.NS","UPL.NS","CHAMBLFERT.NS","BALRAMCHIN.NS","DABUR.NS","MARICO.NS","GODREJCP.NS","COLPAL.NS","HINDPETRO.NS","EXIDEIND.NS","AMARAJABAT.NS","ESCORTS.NS","TIINDIA.NS","VOLTAS.NS","BLUESTARCO.NS","KAYNES.NS","DIXON.NS","AMBER.NS","SYNGENE.NS","TATAELXSI.NS","KPITTECH.NS","LTTS.NS","TATAINVEST.NS","JSWENERGY.NS","TORNTPOWER.NS","ADANIENSOL.NS","NTPCGREEN.NS","ACC.NS","AMBUJACEM.NS","ASTRAL.NS","ATUL.NS","BAJAJHLDNG.NS","BATAINDIA.NS","BERGEPAINT.NS","BEML.NS","BIRLACORPN.NS","BLUEDART.NS","BOROSIL.NS","BRIGADE.NS","BSOFT.NS","CANFINHOME.NS","CAPLIPOINT.NS","CARBORUNDA.NS","CASTROLIND.NS","CCL.NS","CEATLTD.NS","CENTRALBK.NS","CENTURYPLY.NS","CERA.NS","CESC.NS","CGCL.NS","CHALET.NS","CROMPTON.NS","CUB.NS","CYIENT.NS","DALBHARAT.NS","DATAPATTNS.NS","DCBBANK.NS","DEEPAKFERT.NS","DELHIVERY.NS","DELTACORP.NS","DEVYANI.NS","DODLA.NS","EASEMYTRIP.NS","EIDPARRY.NS","EIHOTEL.NS","ELGIEQUIP.NS","EMAMILTD.NS","ENDURANCE.NS","ENGINERSIN.NS","EQUITASBNK.NS","ERIS.NS","FDC.NS","FINEORG.NS","FINCABLES.NS","FINPIPE.NS","FIVESTAR.NS","FLUOROCHEM.NS","FORTIS.NS","FSL.NS","GALAXYSURF.NS","GARDENREACH.NS","GICRE.NS","GILLETTE.NS","GLAND.NS","GMMPFAUDLR.NS","GMRINFRA.NS","GODFRYPHLP.NS","GRANULES.NS","GRAPHITE.NS","GRINDWELL.NS","GRINFRA.NS","GRSE.NS","GSFC.NS","GSPL.NS","GULFOILLUB.NS","HAPPSTMNDS.NS","HATSUN.NS","HBLPOWER.NS","HCG.NS","HEG.NS","HEIDELBERG.NS","HIKAL.NS","HOMEFIRST.NS","HONASA.NS","HONAUT.NS","HUDCO.NS","IBULHSGFIN.NS","IEX.NS","IFBIND.NS","INDIACEM.NS","INDIAMART.NS","INDIANB.NS","INDIGOPNTS.NS","INDUSTOWER.NS","INFIBEAM.NS","INOXWIND.NS","INTELLECT.NS","IOB.NS","IOLCP.NS","IONEXCHANG.NS","IRB.NS","ISEC.NS","ITI.NS","J&KBANK.NS","JAMNAAUTO.NS","JBCHEPHARM.NS","JINDALSAW.NS","JISLJALEQS.NS","JKCEMENT.NS","JKLAKSHMI.NS","JKPAPER.NS","JKTYRE.NS","JMFINANCIL.NS","JSL.NS","JSWHL.NS","JSWINFRA.NS","JUBLINGREA.NS","JUBLPHARMA.NS","JUSTDIAL.NS","JYOTHYLAB.NS","KAJARIACER.NS","KALYANKJIL.NS","KANSAINER.NS","KARURVYSYA.NS","KCP.NS","KEC.NS","KEI.NS","KFINTECH.NS","KHADIM.NS","KIMS.NS","KIOCL.NS","KNRCON.NS","KPRMILL.NS","KRBL.NS","KSB.NS","KTKBANK.NS","L&TFH.NS","LALPATHLAB.NS","LAOPALA.NS","LAXMIMACH.NS","LEMONTREE.NS","LICHSGFIN.NS","LINDEINDIA.NS","LUMAXIND.NS","LUXIND.NS","M&MFIN.NS","MAHABANK.NS","MAHINDCIE.NS","MAHLIFE.NS","MAHLOG.NS","MAHSEAMLES.NS","MANYAVAR.NS","MAPMYINDIA.NS","MARKSANS.NS","MCDOWELL-N.NS","MCX.NS","MEDANTA.NS","METROBRAND.NS","METROPOLIS.NS","MHRIL.NS","MIDHANI.NS","MINDACORP.NS","MIRZAINT.NS","MOIL.NS","MOTILALOFS.NS","MUKANDLTD.NS","NACLIND.NS","NAM-INDIA.NS","NATCOPHARM.NS","NATIONALUM.NS","NAVINFLUOR.NS","NAZARA.NS","NBCC.NS","NCC.NS","NDTV.NS","NETWORK18.NS","NEULANDLAB.NS","NEWGEN.NS","NH.NS","NIACL.NS","NLCINDIA.NS","NOCIL.NS","OCCL.NS","OFSS.NS","OIL.NS","OLECTRA.NS","ORIENTCEM.NS","ORIENTELEC.NS","PAISALO.NS","PATANJALI.NS","PCBL.NS","PITTIENG.NS","PNBHOUSING.NS","PNCINFRA.NS","POLYMED.NS","POLYPLEX.NS","POWERMECH.NS","PRAJIND.NS","PRESTIGE.NS","PRINCEPIPE.NS","PRSMJOHNSN.NS","PSB.NS","PSPPROJECT.NS","PTC.NS","PVRINOX.NS","QUESS.NS","RADICO.NS","RAILTEL.NS","RAIN.NS","RAJESHEXPO.NS","RALLIS.NS","RAMCOCEM.NS","RAMCOIND.NS","RANEHOLDIN.NS","RATNAMANI.NS","RAYMOND.NS","RBA.NS","RBLBANK.NS","RCF.NS","REDINGTON.NS","RELAXO.NS","RELIGARE.NS","REPCOHOME.NS","RITES.NS","RKFORGE.NS","ROLEXRINGS.NS","ROSSARI.NS","ROUTE.NS","RPGLIFE.NS","RTNINDIA.NS","SAFARI.NS","SANDHAR.NS","SANGHIIND.NS","SANOFI.NS","SAPPHIRE.NS","SAREGAMA.NS","SASKEN.NS","SCHAEFFLER.NS","SCI.NS","SEQUENT.NS","SFL.NS","SHANKARA.NS","SHARDACROP.NS","SHAREINDIA.NS","SHILPAMED.NS","SHK.NS","SHOPERSTOP.NS","SHREECEM.NS","SHREERAMA.NS","SHYAMMETL.NS","SILGO.NS","SIS.NS","SJVN.NS","SKFINDIA.NS","SOBHA.NS","SOLARINDS.NS","SONACOMS.NS","SONATSOFTW.NS","SPANDANA.NS","SRM.NS","STAR.NS","STARCEMENT.NS","STARHEALTH.NS","STLTECH.NS","STOVEKRAFT.NS","SUBEXLTD.NS","SUDARSCHEM.NS","SUMICHEM.NS","SUNCLAYLTD.NS","SUNDARMFIN.NS","SUNDRMFAST.NS","SUNFLAG.NS","SUNTV.NS","SUPRAJIT.NS","SUPREMEIND.NS","SURYAROSNI.NS","SWSOLAR.NS","SYMPHONY.NS","SYRMA.NS","TANLA.NS","TARC.NS","TATACHEM.NS","TATAMETALI.NS","TATATECH.NS","TCI.NS","TCIEXP.NS","TCNSBRANDS.NS","TCPLPACK.NS","TDPOWERSYS.NS","TEAMLEASE.NS","TEJASNET.NS","TEXRAIL.NS","THERMAX.NS","THYROCARE.NS","TI.NS","TIDEWATER.NS","TIMETECHNO.NS","TIMKEN.NS","TIPSINDLTD.NS","TMB.NS","TNPL.NS","TRIDENT.NS","TRITURBINE.NS","TRIVENI.NS","TTKPRESTIG.NS","TV18BRDCST.NS","UBL.NS","UFLEX.NS","UJJIVAN.NS","UJJIVANSFB.NS","UNIONBANK.NS","UNITECH.NS","UNOMINDA.NS","UTIAMC.NS","V2RETAIL.NS","VAIBHAVGBL.NS","VAKRANGEE.NS","VARROC.NS","VGUARD.NS","VINATIORGA.NS","VIPIND.NS","VIPULLTD.NS","VISAKAIND.NS","VMART.NS","VOLTAMP.NS","VRLLOG.NS","VSTIND.NS","WABAG.NS","WELCORP.NS","WELENT.NS","WELSPUNLIV.NS","WESTLIFE.NS","WHIRLPOOL.NS","WINDMACHIN.NS","WIPRO.NS","WOCKHARDT.NS","XPROINDIA.NS","ZEEL.NS","ZENSARTECH.NS","ZYDUSWELL.NS"]

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
    return float(cl.iloc[-1]), float(cl.ewm(20).mean().iloc[-1]), float(cl.ewm(50).mean().iloc[-1])

def atr(d, n=14):
    return float((d["High"]-d["Low"]).rolling(n).mean().iloc[-1])

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
        price, e20, e50 = get_ema(d)
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
        return f"""💣 BOND 007 - {conf} CONFIRMED 💣
📈 {s.replace('.NS','')} @ {price:.0f}
M:{mp} | W:{wp} | D:{dp}
⚡ GOLDEN CROSS | {dhdl}
📊 NIFTY:{'BULL' if nifty_bull else 'BEAR'} SENSEX:{'BULL' if sensex_bull else 'BEAR'}
━━━━━━━━━━━━
🎯 ENTRY: {entry:.0f}
🛑 SL: {sl:.0f}
✅ T1: {t1:.0f} | T2: {t2:.0f} | T3: {t3:.0f}
💰 R:R 1:{reward/risk if risk>0 else 0:.1f}
"""
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
    header=f"🚀 BOND 007 - ELITE 507 BOND 🚀\n📅 {date_str}\n📊 NIFTY:{'BULLISH' if nifty_bull else 'BEARISH'} | Found: {len(results)} BOND\n----------------------------------------\n\n"
    final=header+"\n\n".join(results[:12])
else:
    final=f"📊 BOND 007 - 507 SCAN\n📅 {date_str}\nNo 3/3 BOND today - Market WAIT\nNIFTY:{'BULL' if nifty_bull else 'BEAR'}"

print(final)
send_telegram(final)
