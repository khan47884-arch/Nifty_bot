import yfinance as yf, pytz, requests, os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m):
 try:
  ist=pytz.timezone('Asia/Kolkata')
  stamp=datetime.now(ist).strftime("%d-%b-%Y %I:%M %p IST")
  final=f"{m}\n\nSTAMP: {stamp}\n385 ORIGINAL"
  requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",data={"chat_id":CHAT,"text":final},timeout=20)
 except: pass
STOCKS=["RVNL.NS","IRFC.NS","SJVN.NS","NHPC.NS","NBCC.NS","HUDCO.NS","IRCON.NS","RAILTEL.NS","TITAGARH.NS","BHEL.NS","BDL.NS","BEL.NS","MAZDOCK.NS","HAL.NS","BEML.NS","MOTHERSON.NS","JINDALSTEL.NS","SAIL.NS","NMDC.NS","SUZLON.NS","CDSL.NS","BSE.NS","ANGELONE.NS","DIXON.NS","KAYNES.NS","CGPOWER.NS","POLYCAB.NS","VBL.NS","PERSISTENT.NS","IDFCFIRSTB.NS","DLF.NS","ZOMATO.NS","ONGC.NS","SRF.NS","TITAN.NS","DMART.NS","RECLTD.NS","PFC.NS","RELIANCE.NS","TCS.NS"]
def get_cap(s):
 try:
  t=yf.Ticker(s)
  c=t.fast_info.market_cap
  return c/1e7 if c else 0
 except: return 0
def check(s):
 try:
  cap=get_cap(s)
  if cap<1000 or cap>20000: return None
  df=yf.download(s,period="3mo",interval="1d",progress=False,auto_adjust=True)
  if len(df)<50: return None
  df.columns=[c[0] if isinstance(c,tuple) else c for c in df.columns]
  c=df['Close'].iloc[-1]; l=df['Low'].iloc[-1]; h=df['High'].iloc[-1]
  prev=df['Low'].iloc[-21:-1].min()
  sweep=l < prev and c > prev
  body=abs(df['Close'].iloc[-1]-df['Open'].iloc[-1])
  hammer=(h-l) > 2*body
  vol=df['Volume'].iloc[-1] > df['Volume'].iloc[-20:-1].mean()*1.5
  if sweep and hammer and vol:
   return f"{s.replace('.NS','')} Rs {c:.0f} Cap {cap:.0f}Cr"
 except: return None
with ThreadPoolExecutor(max_workers=10) as ex:
 hits=[r for r in ex.map(check,STOCKS) if r]
if hits:
 tg(f"KAALA HEERA - {len(hits)} MILE:\n\n" + "\n".join(hits[:15]))
else:
 tg("KAALA HEERA - Aaj koi nahi")
