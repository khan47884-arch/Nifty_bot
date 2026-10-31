import yfinance as yf,requests,os
from concurrent.futures import ThreadPoolExecutor
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m):
 try: requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",data={"chat_id":CHAT,"text":m},timeout=10)
 except: pass
STOCKS=["RVNL.NS","IRFC.NS","SJVN.NS","NHPC.NS","NBCC.NS","HUDCO.NS","IRCON.NS","RAILTEL.NS","TITAGARH.NS","JUPITERWAGONS.NS","TEXRAIL.NS","BHEL.NS","BDL.NS","BEL.NS","MAZDOCK.NS","COCHINSHIP.NS","HAL.NS","BHARATFORG.NS","ASHOKLEY.NS","MOTHERSON.NS","ENDURANCE.NS","SONACOMS.NS","JWL.NS","CRAFTSMAN.NS","WELCORP.NS","JINDALSTEL.NS","SAIL.NS","NATIONALUM.NS","NMDC.NS","JSWENERGY.NS","TORNTPOWER.NS","CESC.NS","SUZLON.NS","INOXWIND.NS","BORORENEW.NS","CDSL.NS","BSE.NS","ANGELONE.NS","MCX.NS","IEX.NS","CAMS.NS","KFINTECH.NS","MOTILALOFS.NS","IIFL.NS","DIXON.NS","KAYNES.NS","SYRMA.NS","AMBER.NS","CGPOWER.NS","KEI.NS","RRKABEL.NS","APARINDS.NS","KALYANKJIL.NS","PCJEWELLER.NS","KAJARIACER.NS","DELHIVERY.NS","CERA.NS","KPRMILL.NS","TRIDENT.NS","WELSPUNIND.NS","VBL.NS","PATANJALI.NS","AWL.NS","AFFLE.NS","ROUTE.NS","KPITTECH.NS","PERSISTENT.NS","COFORGE.NS","BSOFT.NS","ZENSAR.NS","CYIENT.NS","INTELLECT.NS","MASTEK.NS","DEEPAKNTR.NS","ATUL.NS","NAVINFLUOR.NS","FINEORG.NS","CLEAN.NS","AARTIIND.NS","CHAMBLFERT.NS","COROMANDEL.NS","FACT.NS","CHALET.NS","LEMONTREE.NS","EIHOTEL.NS","INDIANB.NS","UNIONBANK.NS","BANKINDIA.NS","CENTRALBK.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","EQUITASBNK.NS","BANDHANBNK.NS","CREDITACC.NS","M&MFIN.NS","POONAWALLA.NS","LTF.NS","PNBHOUSING.NS","AAVAS.NS","MASFIN.NS","NUVAMA.NS","BRIGADE.NS","SOBHA.NS","LODHA.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS","GLENMARK.NS","LAURUSLABS.NS","GRANULES.NS","SYNGENE.NS","MAXHEALTH.NS","FORTIS.NS","MEDANTA.NS","HFCL.NS","IDEA.NS","ZOMATO.NS","PAYTM.NS","NYKAA.NS","OIL.NS","GSPL.NS","PETRONET.NS","IGL.NS","MGL.NS","GUJGASLTD.NS"]
def get_cap(sym):
 try: return yf.Ticker(sym).fast_info.market_cap/1e7
 except: return 0
def ham(c):
 try:
  o,h,l,cl=float(c['Open']),float(c['High']),float(c['Low']),float(c['Close']); rng=h-l
  if rng==0: return False
  body=abs(cl-o); low=min(o,cl)-l; return low>=body*1.8 and cl>o and body/rng<0.5
 except: return False
def eng(c,p):
 try: return float(p['Close'])<float(p['Open']) and float(c['Close'])>float(c['Open']) and float(c['Open'])<float(p['Close']) and float(c['Close'])>float(p['Open'])
 except: return False
def rsi(s):
 d=s.diff(); g=d.where(d>0,0).ewm(alpha=1/14).mean(); l=-d.where(d<0,0).ewm(alpha=1/14).mean(); return 100-(100/(1+g/l))
def scan(sym):
 try:
  cap=get_cap(sym)
  if cap<1000 or cap>20000: return None
  d=yf.download(sym,period="1y",interval="1d",progress=False,auto_adjust=True,threads=False)
  m=yf.download(sym,period="5y",interval="1mo",progress=False,auto_adjust=True,threads=False)
  w=yf.download(sym,period="2y",interval="1wk",progress=False,auto_adjust=True,threads=False)
  n=yf.download("^NSEI",period="1mo",interval="1d",progress=False,auto_adjust=True,threads=False)
  if len(d)<210 or len(m)<24 or len(w)<30 or len(n)<22: return None
  d['E20']=d['Close'].ewm(span=20).mean(); d['E50']=d['Close'].ewm(span=50).mean(); d['E200']=d['Close'].ewm(span=200).mean(); d['V20']=d['Volume'].ewm(span=20).mean()
  cur=d.iloc[-1]; pre=d.iloc[-2]; pr=float(cur['Close'])
  if not (pr>float(cur['E20'])>float(cur['E50'])>float(cur['E200'])): return None
  hm=ham(cur); en=eng(cur,pre); vol=float(cur['Volume'])>float(cur['V20'])*1.5
  if not ((hm or en) and vol): return None
  rm=float(rsi(m['Close']).iloc[-1]); rw=float(rsi(w['Close']).iloc[-1]); rwp=float(rsi(w['Close']).iloc[-2])
  if not (35<rm<52): return None
  if not (rwp<32 and 25<rw<42): return None
  lows=m['Low'].iloc[-3:].values
  if (max(lows)-min(lows))>(pr*0.08): return None
  low10=float(d['Low'].iloc[-10:].min()); sl=min(low10,float(cur['E200']))*0.98; slp=((pr-sl)/pr)*100
  if slp>7 or slp<0.3: return None
  rs=(d['Close'].iloc[-1]/d['Close'].iloc[-22]-1)*100; rn=(n['Close'].iloc[-1]/n['Close'].iloc[-22]-1)*100
  if rs<(rn+5): return None
  rr=(pr*1.15-pr)/(pr-sl) if (pr-sl)>0 else 0
  if rr<2: return None
  return f"💎 {sym.replace('.NS','')} Rs{pr:.0f} Cap{cap:.0f}Cr EMA{float(cur['E20']):.0f} {'Ham' if hm else 'Eng'} Vol{float(cur['Volume'])/float(cur['V20']):.1f}x RSI M{rm:.0f} W{rw:.0f} SL{slp:.1f}% N+{rs-rn:.1f}% RR{rr:.1f}"
 except: return None
if __name__=="__main__":
 f=[]
 with ThreadPoolExecutor(max_workers=10) as ex:
  for r in ex.map(scan,STOCKS):
   if r: f.append(r)
 if f:
  f=list(dict.fromkeys(f))
  tg(f"💎💎 REAL DIAMOND - {len(f)} STOCK 💎💎\n\n"+"\n\n".join(f[:10]))
