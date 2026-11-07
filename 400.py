import yfinance as yf, pytz, requests, os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")

def tg(m):
 try:
  ist=pytz.timezone('Asia/Kolkata')
  s=datetime.now(ist).strftime("%d-%b %I:%M %p IST")
  requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",data={"chat_id":CHAT,"text":f"{m}\n\nSTAMP:{s}\nV11.5 PLATINUM"},timeout=30)
 except: pass

LONG_TERM_120 = ["RVNL.NS","IRFC.NS","SJVN.NS","NHPC.NS","NBCC.NS","HUDCO.NS","IRCON.NS","RAILTEL.NS","TITAGARH.NS","JUPITERWAGONS.NS","TEXRAIL.NS","BHEL.NS","BDL.NS","BEL.NS","MAZDOCK.NS","COCHINSHIP.NS","HAL.NS","GRSE.NS","BEML.NS","PRAJIND.NS","BHARATFORG.NS","ASHOKLEY.NS","MOTHERSON.NS","ENDURANCE.NS","SONACOMS.NS","UNOMINDA.NS","SANDHAR.NS","JWL.NS","CRAFTSMAN.NS","WELCORP.NS","RATNAMANI.NS","JINDALSTEL.NS","SAIL.NS","NATIONALUM.NS","NMDC.NS","HINDZINC.NS","HINDCOPPER.NS","JSL.NS","JSWENERGY.NS","TORNTPOWER.NS","CESC.NS","POWERGRID.NS","NTPC.NS","TATAPOWER.NS","SUZLON.NS","INOXWIND.NS","BORORENEW.NS","KPIL.NS","KEC.NS","KALPATPOWR.NS","CDSL.NS","BSE.NS","ANGELONE.NS","MCX.NS","IEX.NS","CAMS.NS","KFINTECH.NS","MOTILALOFS.NS","IIFL.NS","NUVAMA.NS","ANANDRATHI.NS","DIXON.NS","KAYNES.NS","SYRMA.NS","AMBER.NS","PGEL.NS","CGPOWER.NS","KEI.NS","RRKABEL.NS","APARINDS.NS","POLYCAB.NS","VOLTAS.NS","BLUESTARCO.NS","WHIRLPOOL.NS","CROMPTON.NS","HAVELLS.NS","KALYANKJIL.NS","PCJEWELLER.NS","KAJARIACER.NS","TANLA.NS","SAFARI.NS","CERA.NS","KPRMILL.NS","TRIDENT.NS","WELSPUNLIV.NS","ARVIND.NS","PAGEIND.NS","RAYMOND.NS","VBL.NS","VARUNBEV.NS","PATANJALI.NS","AWL.NS","AFFLE.NS","ROUTE.NS","KPITTECH.NS","PERSISTENT.NS","COFORGE.NS","BSOFT.NS","ZENSAR.NS","CYIENT.NS","INTELLECT.NS","MASTEK.NS","TATAELXSI.NS","TATATECH.NS","DEEPAKNTR.NS","ATUL.NS","NAVINFLUOR.NS","FINEORG.NS","CLEAN.NS","AARTIIND.NS","VINATIORGA.NS","BALAMINES.NS","CHAMBLFERT.NS","COROMANDEL.NS","FACT.NS","GNFC.NS","CHALET.NS","LEMONTREE.NS","EIHOTEL.NS","INDHOTEL.NS"]

NEW_100 = ["INDIANB.NS","UNIONBANK.NS","BANKINDIA.NS","CENTRALBK.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","EQUITASBNK.NS","BANDHANBNK.NS","CREDITACC.NS","M&MFIN.NS","POONAWALLA.NS","LTF.NS","PNBHOUSING.NS","AAVAS.NS","HOMEFIRST.NS","MASFIN.NS","BRIGADE.NS","SOBHA.NS","LODHA.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS","PHOENIXLTD.NS","HFCL.NS","IDEA.NS","ZOMATO.NS","PAYTM.NS","NYKAA.NS","OIL.NS","GSPL.NS","PETRONET.NS","IGL.NS","MGL.NS","GUJGASLTD.NS","BALKRISIND.NS","MRF.NS","APOLLOTYRE.NS","CEAT.NS","JUBLFOOD.NS","INDIGO.NS","IRB.NS","NCC.NS","ASTRAL.NS","FINCABLES.NS","JINDALSAW.NS","WELSPUNIND.NS","HINDPETRO.NS","BPCL.NS","IOC.NS","GAIL.NS","ONGC.NS","VEDL.NS","COALINDIA.NS","UPL.NS","PIIND.NS","SRF.NS","LUPIN.NS","CIPLA.NS","SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS","MANKIND.NS","CUMMINSIND.NS","BOSCHLTD.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","TVSMOTOR.NS","ULTRACEMCO.NS","GRASIM.NS","AMBUJACEM.NS","ACC.NS","JKCEMENT.NS","ASIANPAINT.NS","BERGEPAINT.NS","PIDILITIND.NS","ABB.NS","SIEMENS.NS","THERMAX.NS","SCHAEFFLER.NS","TITAN.NS","DMART.NS","TRENT.NS","INDIAMART.NS","OFSS.NS","LTIM.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","CHOLAFIN.NS","SHRIRAMFIN.NS","RECLTD.NS","PFC.NS"]

STOCKS = list(dict.fromkeys(LONG_TERM_120 + NEW_100))

def nifty_ok():
 try:
  df=yf.download("^NSEI",period="3mo",interval="1d",progress=False,auto_adjust=True)
  df.columns=[x[0] if isinstance(x,tuple) else x for x in df.columns]
  return df['Close'].iloc[-1] > df['Close'].ewm(span=50).mean().iloc[-1]
 except: return True
NIFTY_BULL = nifty_ok()

def chk(s):
 try:
  df=yf.download(s,period="1y",interval="1d",progress=False,auto_adjust=True)
  if len(df)<200: return None
  df.columns=[x[0] if isinstance(x,tuple) else x for x in df.columns]
  c=df['Close'].iloc[-1]; l=df['Low'].iloc[-1]; h=df['High'].iloc[-1]; o=df['Open'].iloc[-1]
  vol=df['Volume'].iloc[-1]
  if (c*vol) < 50000000: return None
  ema20=df['Close'].ewm(span=20).mean().iloc[-1]
  ema50=df['Close'].ewm(span=50).mean().iloc[-1]
  ema200=df['Close'].ewm(span=200).mean().iloc[-1]
  if c < ema20 or c < ema50 or c < ema200: return None
  delta=df['Close'].diff(); gain=delta.clip(lower=0).rolling(14).mean(); loss=-delta.clip(upper=0).rolling(14).mean()
  rs=gain.iloc[-1]/max(loss.iloc[-1],0.01); rsi=100-(100/(1+rs))
  if rsi < 45 or rsi > 65: return None
  tr=(df['High']-df['Low']).rolling(14).mean().iloc[-1]
  atr_pct=(tr/c)*100
  if atr_pct < 1.0 or atr_pct > 3.5: return None
  if not NIFTY_BULL: return None
  pl20=df['Low'].iloc[-21:-1].min()
  va=df['Volume'].iloc[-20:-1].mean(); vb=vol
  score=0
  if c > df['Close'].iloc[-50:].max()*0.98: score+=3
  if vb > va*1.8: score+=2
  if l < pl20 and c > pl20: score+=3
  if 50 <= rsi <= 60: score+=2
  if atr_pct >= 1.5 and atr_pct <= 2.5: score+=1
  if score < 6: return None
  sl=pl20*0.97
  risk=c-sl; t1=c+risk*2; t2=c+risk*4
  return (score, f"👑 PLATINUM LONG {s.replace('.NS','')} Rs{c:.0f} RSI{rsi:.0f} ATR{atr_pct:.1f}% Score{score}/11 SL{sl:.0f} TGT{t1:.0f}/{t2:.0f} Vol x{vb/va:.1f}")
 except: return None

with ThreadPoolExecutor(max_workers=8) as ex:
 res=[x for x in ex.map(chk,STOCKS) if x]
res.sort(key=lambda x: x[0], reverse=True)
top=[r[1] for r in res[:4]]
if top: msg=f"👑 V11.5 PLATINUM LONG-TERM TOP {len(top)}:\n"+"\n".join(top)
else: msg="👑 V11.5 PLATINUM - Aaj koi Platinum setup nahi, paisa bach gaya"
tg(msg)
