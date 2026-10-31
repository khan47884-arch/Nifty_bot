import yfinance as yf, pytz, requests, os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m):
 try:
  ist=pytz.timezone('Asia/Kolkata')
  s=datetime.now(ist).strftime("%d-%b %I:%M %p IST")
  requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",data={"chat_id":CHAT,"text":f"{m}\n\nSTAMP:{s}\nV7 LONG+SHORT"},timeout=30)
 except: pass
STOCKS=["RVNL.NS","IRFC.NS","SJVN.NS","NHPC.NS","NBCC.NS","HUDCO.NS","IRCON.NS","RAILTEL.NS","TITAGARH.NS","JUPITERWAGONS.NS","TEXRAIL.NS","BHEL.NS","BDL.NS","BEL.NS","MAZDOCK.NS","COCHINSHIP.NS","HAL.NS","GRSE.NS","BEML.NS","PRAJIND.NS","BHARATFORG.NS","ASHOKLEY.NS","MOTHERSON.NS","ENDURANCE.NS","SONACOMS.NS","UNOMINDA.NS","SANDHAR.NS","JWL.NS","CRAFTSMAN.NS","WELCORP.NS","RATNAMANI.NS","JINDALSTEL.NS","SAIL.NS","NATIONALUM.NS","NMDC.NS","HINDZINC.NS","HINDCOPPER.NS","JSL.NS","JSWENERGY.NS","TORNTPOWER.NS","CESC.NS","POWERGRID.NS","NTPC.NS","TATAPOWER.NS","SUZLON.NS","INOXWIND.NS","BORORENEW.NS","KPIL.NS","KEC.NS","KALPATPOWR.NS","CDSL.NS","BSE.NS","ANGELONE.NS","MCX.NS","IEX.NS","CAMS.NS","KFINTECH.NS","MOTILALOFS.NS","IIFL.NS","NUVAMA.NS","ANANDRATHI.NS","DIXON.NS","KAYNES.NS","SYRMA.NS","AMBER.NS","PGEL.NS","CGPOWER.NS","KEI.NS","RRKABEL.NS","APARINDS.NS","POLYCAB.NS","VOLTAS.NS","BLUESTARCO.NS","WHIRLPOOL.NS","CROMPTON.NS","HAVELLS.NS","KALYANKJIL.NS","PCJEWELLER.NS","KAJARIACER.NS","TANLA.NS","SAFARI.NS","CERA.NS","KPRMILL.NS","TRIDENT.NS","WELSPUNLIV.NS","ARVIND.NS","PAGEIND.NS","RAYMOND.NS","VBL.NS","VARUNBEV.NS","PATANJALI.NS","AWL.NS","AFFLE.NS","ROUTE.NS","KPITTECH.NS","PERSISTENT.NS","COFORGE.NS","BSOFT.NS","ZENSAR.NS","CYIENT.NS","INTELLECT.NS","MASTEK.NS","TATAELXSI.NS","TATATECH.NS","DEEPAKNTR.NS","ATUL.NS","NAVINFLUOR.NS","FINEORG.NS","CLEAN.NS","AARTIIND.NS","VINATIORGA.NS","BALAMINES.NS","CHAMBLFERT.NS","COROMANDEL.NS","FACT.NS","GNFC.NS","CHALET.NS","LEMONTREE.NS","EIHOTEL.NS","INDHOTEL.NS","INDIANB.NS","UNIONBANK.NS","BANKINDIA.NS","CENTRALBK.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","EQUITASBNK.NS","BANDHANBNK.NS","CREDITACC.NS","M&MFIN.NS","POONAWALLA.NS","LTF.NS","PNBHOUSING.NS","AAVAS.NS","HOMEFIRST.NS","MASFIN.NS","BRIGADE.NS","SOBHA.NS","LODHA.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS","PHOENIXLTD.NS","GLENMARK.NS","LAURUSLABS.NS","GRANULES.NS","SYNGENE.NS","LALPATHLAB.NS","MAXHEALTH.NS","FORTIS.NS","MEDANTA.NS","KIMS.NS","GLAND.NS","HFCL.NS","IDEA.NS","ZOMATO.NS","PAYTM.NS","NYKAA.NS","OIL.NS","GSPL.NS","PETRONET.NS","IGL.NS","MGL.NS","GUJGASLTD.NS","BALKRISIND.NS","MRF.NS","APOLLOTYRE.NS","CEAT.NS","BATAINDIA.NS","DABUR.NS","MARICO.NS","GODREJCP.NS","BRITANNIA.NS","TATACONSUM.NS","JUBLFOOD.NS","INDIGO.NS","IRB.NS","NCC.NS","ASTRAL.NS","FINCABLES.NS","JINDALSAW.NS","WELSPUNIND.NS","HINDPETRO.NS","BPCL.NS","IOC.NS","GAIL.NS","ONGC.NS","VEDL.NS","COALINDIA.NS","UPL.NS","PIIND.NS","SRF.NS","LUPIN.NS","CIPLA.NS","SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS","MANKIND.NS","CUMMINSIND.NS","BOSCHLTD.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","TVSMOTOR.NS","ULTRACEMCO.NS","GRASIM.NS","AMBUJACEM.NS","ACC.NS","JKCEMENT.NS","ASIANPAINT.NS","BERGEPAINT.NS","PIDILITIND.NS","ABB.NS","SIEMENS.NS","THERMAX.NS","SCHAEFFLER.NS","TITAN.NS","DMART.NS","TRENT.NS","INDIAMART.NS","OFSS.NS","LTIM.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","MUTHOOTFIN.NS","CHOLAFIN.NS","SHRIRAMFIN.NS","RECLTD.NS","PFC.NS","INDUSINDBK.NS","KOTAKBANK.NS","AXISBANK.NS","AUBANK.NS","LICI.NS","YESBANK.NS","HDFCAMC.NS","DELHIVERY.NS","TATACHEM.NS","ALKEM.NS","TORNTPHARM.NS","MTARTECH.NS","ADANIENT.NS","ADANIPORTS.NS","ADANIGREEN.NS","ADANIPOWER.NS","ATGL.NS","APOLLOHOSP.NS","AUROPHARMA.NS","BIOCON.NS","DALBHARAT.NS","ESCORTS.NS","EXIDEIND.NS","HDFCBANK.NS","HINDALCO.NS","HINDUNILVR.NS","ICICIBANK.NS","ICICIGI.NS","IRCTC.NS","ITC.NS","JSWSTEEL.NS","LT.NS","M&M.NS","MARUTI.NS","NESTLEIND.NS","RELIANCE.NS","SBIN.NS","TATAMOTORS.NS","TATASTEEL.NS","TCS.NS","BAJAJFINANCE.NS"]
def cap(s):
 try:
  v=yf.Ticker(s).fast_info.market_cap
  return v/1e7 if v else 0
 except: return 0
def chk(s):
 try:
  c1=cap(s)
  if c1<800 or c1>25000: return None
  df=yf.download(s,period="1y",interval="1d",progress=False,auto_adjust=True)
  if len(df)<200: return None
  df.columns=[x[0] if isinstance(x,tuple) else x for x in df.columns]
  c=df['Close'].iloc[-1]; l=df['Low'].iloc[-1]; h=df['High'].iloc[-1]; o=df['Open'].iloc[-1]
  pl20=df['Low'].iloc[-21:-1].min(); pl10=df['Low'].iloc[-11:-1].min()
  va=df['Volume'].iloc[-20:-1].mean(); vb=df['Volume'].iloc[-1]
  long = l < pl20 and c > pl20 and (h-l) > 2.5*max(abs(c-o),0.1) and vb > va*2.5 and c > df['High'].iloc[-200:-1].max()*0.92
  short = l < pl10 and c > pl10 and vb > va*1.8 and c>o
  if not (long or short): return None
  typ = "LONG" if long else "SHORT"
  sl= (pl20 if long else pl10)*0.97
  t1=c* (1.25 if long else 1.08); t2=c* (1.60 if long else 1.15)
  return (typ, f"💎 {typ} {s.replace('.NS','')} Rs{c:.0f} Cap{c1:.0f}Cr SL{sl:.0f} TGT{t1:.0f}/{t2:.0f} Vol x{vb/va:.1f}")
 except: return None
with ThreadPoolExecutor(max_workers=6) as ex:
 res=[x for x in ex.map(chk,STOCKS) if x]
longs=[r[1] for r in res if r[0]=="LONG"]; shorts=[r[1] for r in res if r[0]=="SHORT"]
msg=""
if longs: msg+=f"🔥 LONG GAME CHANGER {len(longs)}:\n"+"\n".join(longs[:10])+"\n\n"
if shorts: msg+=f"⚡ SHORT SWING {len(shorts)}:\n"+"\n".join(shorts[:10])
if not msg: msg="V7 - Aaj koi LONG/SHORT nahi"
tg(msg)
