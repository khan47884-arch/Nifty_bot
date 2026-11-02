import yfinance as yf, pandas as pd, requests, os
from datetime import datetime
import pytz
IST=pytz.timezone('Asia/Kolkata')
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m):
 try:requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",data={"chat_id":CHAT,"text":m},timeout=20)
 except:pass
MCX={
"GOLDMINI":{"sym":"GC=F","price":139780,"sl":300,"tg":600,"lot":"0.10 x 10 = 1 LOT"},
"SILVERM":{"sym":"SI=F","price":185404,"sl":600,"tg":1200,"lot":"0.10 x 10 = 1 LOT"},
"CRUDE":{"sym":"CL=F","price":5800,"sl":40,"tg":80,"lot":"0.10 x 10 = 1 LOT"}
}
FOUND=False
for NAME,I in MCX.items():
 try:
  df=yf.download(I["sym"],period="3d",interval="5m",progress=False,auto_adjust=True)
  df15=yf.download(I["sym"],period="10d",interval="15m",progress=False,auto_adjust=True)
  if len(df)<80 or len(df15)<50:continue
  if isinstance(df.columns,pd.MultiIndex):df.columns=df.columns.get_level_values(0)
  if isinstance(df15.columns,pd.MultiIndex):df15.columns=df15.columns.get_level_values(0)
  df["TP"]=(df["High"]+df["Low"]+df["Close"])/3
  df["VWAP"]=(df["TP"]*df["Volume"]).cumsum()/df["Volume"].cumsum()
  df15["E20"]=df15["Close"].ewm(span=20).mean()
  df15["E50"]=df15["Close"].ewm(span=50).mean()
  df["ATR"]=(df["High"]-df["Low"]).rolling(14).mean()
  df["VA"]=df["Volume"].rolling(20).mean()
  d=df["Close"].diff()
  g=d.where(d>0,0).rolling(14).mean()
  l=-d.where(d<0,0).rolling(14).mean()
  df["RSI"]=100-(100/(1+g/l))
  c=df.iloc[-1];p=df.iloc[-2];c15=df15.iloc[-1]
  close=float(c["Close"]);vwap=float(c["VWAP"]);atr=float(c["ATR"]);rsi=float(c["RSI"])
  volx=float(c["Volume"]/c["VA"]) if float(c["VA"])>0 else 1
  last10_low=float(df["Low"].iloc[-11:-1].min())
  last10_high=float(df["High"].iloc[-11:-1].max())
  bull_sweep=float(c["Low"])<last10_low and close>last10_low
  bear_sweep=float(c["High"])>last10_high and close<last10_high
  vwap_up=close>vwap
  vwap_down=close<vwap
  trend_up=float(c15["Close"])>float(c15["E20"])>float(c15["E50"])
  trend_down=float(c15["Close"])<float(c15["E20"])<float(c15["E50"])
  real_buy=close>float(p["High"])+atr*0.3
  real_sell=close<float(p["Low"])-atr*0.3
  vol_ok=volx>1.5
  rsi_buy=55<=rsi<=78
  rsi_sell=22<=rsi<=45
  stamp=datetime.now(IST).strftime('%d-%b %I:%M %p')
  if (bull_sweep or (vwap_up and trend_up and real_buy)) and vol_ok and rsi_buy:
   tg(f"🟡 {NAME} FUTURE BUY 🟢\n━━━━━━━━━━━━━━━\n💰 {NAME} BUY @ {I['price']}\n📦 {I['lot']}\n✅ {'LIQ SWEEP + ' if bull_sweep else ''}VWAP UP | 15M UP\n🧹 Sweep Low: {last10_low:.2f} | RSI:{rsi:.0f} Vol:x{volx:.1f}\n🛑 SL:{I['sl']} | 🎯 {I['tg']}\n⏰ {stamp}\n🚀 MCX BRAHMASTRA")
   FOUND=True
  elif (bear_sweep or (vwap_down and trend_down and real_sell)) and vol_ok and rsi_sell:
   tg(f"🔵 {NAME} FUTURE SELL 🔴\n━━━━━━━━━━━━━━━\n💰 {NAME} SELL @ {I['price']}\n📦 {I['lot']}\n✅ {'LIQ SWEEP + ' if bear_sweep else ''}VWAP DOWN | 15M DOWN\n🧹 Sweep High: {last10_high:.2f} | RSI:{rsi:.0f} Vol:x{volx:.1f}\n🛑 SL:{I['sl']} | 🎯 {I['tg']}\n⏰ {stamp}\n💨 MCX BRAHMASTRA")
   FOUND=True
 except:continue
if not FOUND:
 tg(f"✨ MCX BRAHMASTRA ✨\nAaj GOLDMINI/SILVERM/CRUDE me koi Sweep/Setup nahi\nGOLDMINI:139780 | SILVERM:185404\n⏰ {datetime.now(IST).strftime('%d-%b %I:%M %p IST')}")
