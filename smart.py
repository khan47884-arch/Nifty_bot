import yfinance as yf, pytz, requests, os, json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m):
 try:
  ist=pytz.timezone('Asia/Kolkata')
  s=datetime.now(ist).strftime("%d-%b %I:%M %p IST")
  requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",data={"chat_id":CHAT,"text":f"{m}\n\nSTAMP:{s}\nV12.1 SMART MONEY + DII/FII"},timeout=30)
 except: pass
LONG_TERM_120 = ["RVNL.NS","IRFC.NS","SJVN.NS","NHPC.NS","NBCC.NS","HUDCO.NS","IRCON.NS","RAILTEL.NS","TITAGARH.NS","JUPITERWAGONS.NS","TEXRAIL.NS","BHEL.NS","BDL.NS","BEL.NS","MAZDOCK.NS","COCHINSHIP.NS","HAL.NS","GRSE.NS","BEML.NS","PRAJIND.NS","BHARATFORG.NS","ASHOKLEY.NS","MOTHERSON.NS","ENDURANCE.NS","SONACOMS.NS","UNOMINDA.NS","SANDHAR.NS","JWL.NS","CRAFTSMAN.NS","WELCORP.NS","RATNAMANI.NS","JINDALSTEL.NS","SAIL.NS","NATIONALUM.NS","NMDC.NS","HINDZINC.NS","HINDCOPPER.NS","JSL.NS","JSWENERGY.NS","TORNTPOWER.NS","CESC.NS","POWERGRID.NS","NTPC.NS","TATAPOWER.NS","SUZLON.NS","INOXWIND.NS","BORORENEW.NS","KPIL.NS","KEC.NS","KALPATPOWR.NS","CDSL.NS","BSE.NS","ANGELONE.NS","MCX.NS","IEX.NS","CAMS.NS","KFINTECH.NS","MOTILALOFS.NS","IIFL.NS","NUVAMA.NS","ANANDRATHI.NS","DIXON.NS","KAYNES.NS","SYRMA.NS","AMBER.NS","PGEL.NS","CGPOWER.NS","KEI.NS","RRKABEL.NS","APARINDS.NS","POLYCAB.NS","VOLTAS.NS","BLUESTARCO.NS","WHIRLPOOL.NS","CROMPTON.NS","HAVELLS.NS","KALYANKJIL.NS","PCJEWELLER.NS","KAJARIACER.NS","TANLA.NS","SAFARI.NS","CERA.NS","KPRMILL.NS","TRIDENT.NS","WELSPUNLIV.NS","ARVIND.NS","PAGEIND.NS","RAYMOND.NS","VBL.NS","VARUNBEV.NS","PATANJALI.NS","AWL.NS","AFFLE.NS","ROUTE.NS","KPITTECH.NS","PERSISTENT.NS","COFORGE.NS","BSOFT.NS","ZENSAR.NS","CYIENT.NS","INTELLECT.NS","MASTEK.NS","TATAELXSI.NS","TATATECH.NS","DEEPAKNTR.NS","ATUL.NS","NAVINFLUOR.NS","FINEORG.NS","CLEAN.NS","AARTIIND.NS","VINATIORGA.NS","BALAMINES.NS","CHAMBLFERT.NS","COROMANDEL.NS","FACT.NS","GNFC.NS","CHALET.NS","LEMONTREE.NS","EIHOTEL.NS","INDHOTEL.NS"]
NEW_100 = ["INDIANB.NS","UNIONBANK.NS","BANKINDIA.NS","CENTRALBK.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","EQUITASBNK.NS","BANDHANBNK.NS","CREDITACC.NS","M&MFIN.NS","POONAWALLA.NS","LTF.NS","PNBHOUSING.NS","AAVAS.NS","HOMEFIRST.NS","MASFIN.NS","BRIGADE.NS","SOBHA.NS","LODHA.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS","PHOENIXLTD.NS","HFCL.NS","IDEA.NS","ZOMATO.NS","PAYTM.NS","NYKAA.NS","OIL.NS","GSPL.NS","PETRONET.NS","IGL.NS","MGL.NS","GUJGASLTD.NS","BALKRISIND.NS","MRF.NS","APOLLOTYRE.NS","CEAT.NS","JUBLFOOD.NS","INDIGO.NS","IRB.NS","NCC.NS","ASTRAL.NS","FINCABLES.NS","JINDALSAW.NS","WELSPUNIND.NS","HINDPETRO.NS","BPCL.NS","IOC.NS","GAIL.NS","ONGC.NS","VEDL.NS","COALINDIA.NS","UPL.NS","PIIND.NS","SRF.NS","LUPIN.NS","CIPLA.NS","SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS","MANKIND.NS","CUMMINSIND.NS","BOSCHLTD.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","TVSMOTOR.NS","ULTRACEMCO.NS","GRASIM.NS","AMBUJACEM.NS","ACC.NS","JKCEMENT.NS","ASIANPAINT.NS","BERGEPAINT.NS","PIDILITIND.NS","ABB.NS","SIEMENS.NS","THERMAX.NS","SCHAEFFLER.NS","TITAN.NS","DMART.NS","TRENT.NS","INDIAMART.NS","OFSS.NS","LTIM.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","CHOLAFIN.NS","SHRIRAMFIN.NS","RECLTD.NS","PFC.NS"]
STOCKS = list(dict.fromkeys(LONG_TERM_120 + NEW_100))
STOCK_NAMES = set([s.replace(".NS","") for s in STOCKS])
def bulk_deals():
 try:
  headers={"User-Agent":"Mozilla/5.0","Accept":"application/json","Accept-Language":"en-US,en;q=0.9"}
  s=requests.Session()
  s.get("https://www.nseindia.com",headers=headers,timeout=15)
  r=s.get("https://www.nseindia.com/api/corporates-bulk-deals?index=equities&symbol=",headers=headers,timeout=20)
  data=r.json().get("data",[])
  out=[]
  for d in data:
   sym=d.get("symbol","").upper()
   name=d.get("clientName","")
   qty=d.get("quantityTraded",0)
   if sym in STOCK_NAMES:
    big = any(k in name.upper() for k in ["FUND","MUTUAL","FII","FOREIGN","INSURANCE","LIC","SBI","HDFC","ICICI","AXIS","KOTAK","NIPPON","ADITYA","UTI","MORGAN","GOLDMAN","BLACKROCK","FIDELITY","HSBC","CITI","JP MORGAN"])
    tag = "🔥 BADA CLIENT" if big else "Bulk Deal"
    out.append(f"🏦 {tag} {sym} - {name} Qty {qty}")
  return out[:10]
 except Exception as e:
  return []
def chk(s):
 try:
  df=yf.download(s,period="3mo",interval="1d",progress=False,auto_adjust=True)
  if len(df)<50: return None
  df.columns=[x[0] if isinstance(x,tuple) else x for x in df.columns]
  c=df['Close'].iloc[-1]
  vol=df['Volume'].iloc[-1]; va=df['Volume'].iloc[-20:-1].mean()
  v_ratio=vol/max(va,1)
  ema20=df['Close'].ewm(span=20).mean().iloc[-1]
  high52=df['Close'].iloc[-50:].max()
  chg=(c-df['Close'].iloc[-2])/df['Close'].iloc[-2]*100
  score=0; reason=[]
  if v_ratio>2.5: score+=3; reason.append(f"Vol x{v_ratio:.1f} BADA PAISA")
  elif v_ratio>1.8: score+=2; reason.append(f"Vol x{v_ratio:.1f}")
  if chg>2 and c>ema20: score+=2; reason.append(f"+{chg:.1f}% Bhaag raha")
  if c>high52*0.98: score+=3; reason.append("52W High ke paas - BREAKOUT")
  if c>ema20: score+=1
  if score<5: return None
  verdict="🚀 LAMBA JAYEGA - PRE-OPEN ME NAZAR RAKHO" if score>=7 else "⚡ TEZ HAI - Nazar rakho"
  sl=c*0.97; t1=c*1.05; t2=c*1.12
  return (score, f"💎 SMART {s.replace('.NS','')} Rs{c:.0f} Score{score}/9\n{verdict}\n{', '.join(reason)}\nSL {sl:.0f} TGT {t1:.0f}/{t2:.0f}")
 except: return None
with ThreadPoolExecutor(max_workers=10) as ex:
 res=[x for x in ex.map(chk,STOCKS) if x]
res.sort(key=lambda x: x[0], reverse=True)
top=[r[1] for r in res[:5]]
bulk=bulk_deals()
msg=""
if bulk:
 msg+="🏦 DII / FII / MF BULK DEAL - TUMHARI LIST ME:\n"+"\n".join(bulk)+"\n\n"
if top:
 msg+=f"💎 V12.1 SMART MONEY - 280 ME SE BADA PAISA:\n\n"+"\n\n".join(top)
if not msg:
 msg="💎 V12.1 SMART MONEY - Aaj 280 me kahi bada paisa nahi ghusa, aaram karo"
tg(msg)
