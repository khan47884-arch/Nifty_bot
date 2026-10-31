import yfinance as yf,requests,os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m):
 try: requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",data={"chat_id":CHAT,"text":m},timeout=20)
 except: pass
STOCKS=["RVNL.NS","IRFC.NS","SJVN.NS","NHPC.NS","NBCC.NS","HUDCO.NS","IRCON.NS","RAILTEL.NS","TITAGARH.NS","JUPITERWAGONS.NS","TEXRAIL.NS","BHEL.NS","BDL.NS","BEL.NS","MAZDOCK.NS","COCHINSHIP.NS","HAL.NS","GRSE.NS","BEML.NS","PRAJIND.NS","BHARATFORG.NS","ASHOKLEY.NS","MOTHERSON.NS","ENDURANCE.NS","SONACOMS.NS","UNOMINDA.NS","SANDHAR.NS","JWL.NS","CRAFTSMAN.NS","WELCORP.NS","RATNAMANI.NS","JINDALSTEL.NS","SAIL.NS","NATIONALUM.NS","NMDC.NS","HINDZINC.NS","HINDCOPPER.NS","JSL.NS","JSWENERGY.NS","TORNTPOWER.NS","CESC.NS","POWERGRID.NS","NTPC.NS","TATAPOWER.NS","SUZLON.NS","INOXWIND.NS","BORORENEW.NS","KPIL.NS","KEC.NS","KALPATPOWR.NS","CDSL.NS","BSE.NS","ANGELONE.NS","MCX.NS","IEX.NS","CAMS.NS","KFINTECH.NS","MOTILALOFS.NS","IIFL.NS","NUVAMA.NS","ANANDRATHI.NS","DIXON.NS","KAYNES.NS","SYRMA.NS","AMBER.NS","PGEL.NS","CGPOWER.NS","KEI.NS","RRKABEL.NS","APARINDS.NS","POLYCAB.NS","VOLTAS.NS","BLUESTARCO.NS","WHIRLPOOL.NS","CROMPTON.NS","HAVELLS.NS","KALYANKJIL.NS","PCJEWELLER.NS","KAJARIACER.NS","TANLA.NS","SAFARI.NS","CERA.NS","KPRMILL.NS","TRIDENT.NS","WELSPUNLIV.NS","ARVIND.NS","PAGEIND.NS","RAYMOND.NS","VBL.NS","VARUNBEV.NS","PATANJALI.NS","AWL.NS","AFFLE.NS","ROUTE.NS","KPITTECH.NS","PERSISTENT.NS","COFORGE.NS","BSOFT.NS","ZENSAR.NS","CYIENT.NS","INTELLECT.NS","MASTEK.NS","TATAELXSI.NS","TATATECH.NS","DEEPAKNTR.NS","ATUL.NS","NAVINFLUOR.NS","FINEORG.NS","CLEAN.NS","AARTIIND.NS","VINATIORGA.NS","BALAMINES.NS","CHAMBLFERT.NS","COROMANDEL.NS","FACT.NS","GNFC.NS","CHALET.NS","LEMONTREE.NS","EIHOTEL.NS","INDHOTEL.NS","INDIANB.NS","UNIONBANK.NS","BANKINDIA.NS","CENTRALBK.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","EQUITASBNK.NS","BANDHANBNK.NS","CREDITACC.NS","M&MFIN.NS","POONAWALLA.NS","LTF.NS","PNBHOUSING.NS","AAVAS.NS","HOMEFIRST.NS","MASFIN.NS","BRIGADE.NS","SOBHA.NS","LODHA.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS","PHOENIXLTD.NS","GLENMARK.NS","LAURUSLABS.NS","GRANULES.NS","SYNGENE.NS","LALPATHLAB.NS","MAXHEALTH.NS","FORTIS.NS","MEDANTA.NS","KIMS.NS","GLAND.NS","HFCL.NS","IDEA.NS","ZOMATO.NS","PAYTM.NS","NYKAA.NS","OIL.NS","GSPL.NS","PETRONET.NS","IGL.NS","MGL.NS","GUJGASLTD.NS","BALKRISIND.NS","MRF.NS","APOLLOTYRE.NS","CEAT.NS","BATAINDIA.NS","DABUR.NS","MARICO.NS","GODREJCP.NS","BRITANNIA.NS","TATACONSUM.NS","JUBLFOOD.NS","INDIGO.NS","IRB.NS","NCC.NS","ASTRAL.NS","FINCABLES.NS","JINDALSAW.NS","WELSPUNIND.NS","HINDPETRO.NS","BPCL.NS","IOC.NS","GAIL.NS","ONGC.NS","VEDL.NS","COALINDIA.NS","UPL.NS","PIIND.NS","SRF.NS","LUPIN.NS","CIPLA.NS","SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS","MANKIND.NS","CUMMINSIND.NS","BOSCHLTD.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","TVSMOTOR.NS","ULTRACEMCO.NS","GRASIM.NS","AMBUJACEM.NS","ACC.NS","JKCEMENT.NS","ASIANPAINT.NS","BERGEPAINT.NS","PIDILITIND.NS","ABB.NS","SIEMENS.NS","THERMAX.NS","SCHAEFFLER.NS","TITAN.NS","DMART.NS","TRENT.NS","INDIAMART.NS","OFSS.NS","LTIM.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","MUTHOOTFIN.NS","CHOLAFIN.NS","SHRIRAMFIN.NS","RECLTD.NS","PFC.NS","INDUSINDBK.NS","KOTAKBANK.NS","AXISBANK.NS","AUBANK.NS","NBCC.NS","HUDCO.NS","KEI.NS","RRKABEL.NS","ASTRAL.NS","PAGEIND.NS","RAYMOND.NS","VBL.NS","OFSS.NS","BSOFT.NS","ZENSAR.NS","CYIENT.NS","INTELLECT.NS","MASTEK.NS","ATUL.NS","TATACHEM.NS","GLENMARK.NS","LAURUSLABS.NS","ALKEM.NS","TORNTPHARM.NS","ABB.NS","SIEMENS.NS","CROMPTON.NS","WHIRLPOOL.NS","AMBER.NS","BEML.NS","COCHINSHIP.NS","LICI.NS","CAMS.NS","KFINTECH.NS","MOTILALOFS.NS","IIFL.NS","EQUITASBNK.NS","BANDHANBNK.NS","CREDITACC.NS","M&MFIN.NS","POONAWALLA.NS","INDIAMART.NS","EIHOTEL.NS","CHALET.NS","LEMONTREE.NS","AFFLE.NS","ROUTE.NS","KPIL.NS","KEC.NS","LTF.NS","PNBHOUSING.NS","AAVAS.NS","CENTRALBK.NS","BANKINDIA.NS","YESBANK.NS","HDFCAMC.NS","WELCORP.NS","ARVIND.NS","GRANULES.NS","SYNGENE.NS","LALPATHLAB.NS","MAXHEALTH.NS","FORTIS.NS","CRAFTSMAN.NS","ENDURANCE.NS","RATNAMANI.NS","NMDC.NS","OIL.NS","GSPL.NS","INOXWIND.NS","HFCL.NS","IDEA.NS","AWL.NS","SOBHA.NS","BRIGADE.NS","LODHA.NS","CLEAN.NS","MEDANTA.NS","KIMS.NS","GLAND.NS","APARINDS.NS","DELHIVERY.NS","SAFARI.NS","CERA.NS","KPRMILL.NS","MASFIN.NS","NUVAMA.NS","IRCON.NS","RAILTEL.NS","BDL.NS","MTARTECH.NS","PGEL.NS","PCJEWELLER.NS","KAJARIACER.NS","BORORENEW.NS"]
NIFTY=yf.download("^NSEI",period="1mo",interval="1d",progress=False,auto_adjust=True,threads=False)
NIFTY_RET=(NIFTY['Close'].iloc[-1]/NIFTY['Close'].iloc[-22]-1)*100 if len(NIFTY)>22 else 0
def get_cap(sym):
 try:
  mc=yf.Ticker(sym).fast_info.market_cap
  return mc/1e7 if mc else 5000
 except: return 5000
def ham(c):
 try:
  o,h,l,cl=float(c['Open']),float(c['High']),float(c['Low']),float(c['Close']); rng=h-l
  if rng==0: return False
  body=abs(cl-o); low=min(o,cl)-l; return low>=body*1.5 and cl>o and body/rng<0.6
 except: return False
def eng(c,p):
 try: return float(p['Close'])<float(p['Open']) and float(c['Close'])>float(c['Open']) and float(c['Open'])<float(p['Close']) and float(c['Close'])>float(p['Open'])
 except: return False
def rsi(s):
 d=s.diff(); g=d.where(d>0,0).ewm(alpha=1/14).mean(); l=-d.where(d<0,0).ewm(alpha=1/14).mean(); return 100-(100/(1+g/l))
def supertrend(df, period=10, mult=3):
 try:
  hl2=(df['High']+df['Low'])/2
  atr=(df['High']-df['Low']).ewm(alpha=1/period).mean()
  upper=hl2+mult*atr
  lower=hl2-mult*atr
  return float(df['Close'].iloc[-1])>float(lower.iloc[-1])
 except: return True
def scan(sym):
 try:
  cap=get_cap(sym)
  if cap<1000 or cap>25000: return None
  d=yf.download(sym,period="1y",interval="1d",progress=False,auto_adjust=True,threads=False)
  if len(d)<210: return None
  m=d.resample('ME').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'})
  w=d.resample('W').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'})
  if len(m)<24 or len(w)<30: return None
  d['E20']=d['Close'].ewm(span=20).mean(); d['E50']=d['Close'].ewm(span=50).mean(); d['E200']=d['Close'].ewm(span=200).mean(); d['V20']=d['Volume'].ewm(span=20).mean()
  cur=d.iloc[-1]; pre=d.iloc[-2]; pr=float(cur['Close'])
  if not (pr>float(cur['E20'])>float(cur['E50'])>float(cur['E200'])): return None
  if not supertrend(d): return None
  hm=ham(cur); en=eng(cur,pre); vol=float(cur['Volume'])>float(cur['V20'])*1.3
  if not ((hm or en) and vol): return None
  rm=float(rsi(m['Close']).iloc[-1]); rw=float(rsi(w['Close']).iloc[-1])
  if not (35<rm<55): return None
  if not (30<rw<50): return None
  lows=m['Low'].iloc[-3:].values
  if (max(lows)-min(lows))>(pr*0.10): return None
  low10=float(d['Low'].iloc[-10:].min()); sl=min(low10,float(cur['E200']))*0.98; slp=((pr-sl)/pr)*100
  if slp>7 or slp<0.3: return None
  rs=(d['Close'].iloc[-1]/d['Close'].iloc[-22]-1)*100
  if rs<(NIFTY_RET+3): return None
  rr=(pr*1.15-pr)/(pr-sl) if (pr-sl)>0 else 0
  if rr<2: return None
  return f"💎 V2 {sym.replace('.NS','')} Rs{pr:.0f} Cap{cap:.0f}Cr ST✅ EMA{float(cur['E20']):.0f} {'Ham' if hm else 'Eng'} Vol{float(cur['Volume'])/float(cur['V20']):.1f}x RSI M{rm:.0f} W{rw:.0f} SL{slp:.1f}% N+{rs-NIFTY_RET:.1f}% RR{rr:.1f}"
 except: return None
if __name__=="__main__":
 f=[]
 with ThreadPoolExecutor(max_workers=15) as ex:
  for r in ex.map(scan,STOCKS):
   if r: f.append(r)
 if not f:
  tg(f"⚪ Aaj koi V2 DIAMOND nahi - 360 SCAN")
 else:
  f=list(dict.fromkeys(f))
  tg(f"💎💎 V2 REAL DIAMOND - {len(f)} STOCK [360] 💎💎\n\n"+"\n\n".join(f[:20]))
