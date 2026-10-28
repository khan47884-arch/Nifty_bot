import yfinance as yf
import os, requests
from datetime import datetime

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        for i in range(0, len(msg), 3900):
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg[i:i+3900]}, timeout=20)
    except: pass

def get_oi_pcr(symbol="NIFTY"):
    try:
        headers = {"User-Agent": "Mozilla/5.0","Referer": "https://www.nseindia.com/option-chain"}
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=headers, timeout=10)
        r = s.get(f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}", headers=headers, timeout=10).json()
        ce_oi=pe_oi=ce_chg=pe_chg=0
        for item in r['records']['data']:
            if 'CE' in item: 
                ce_oi+=item['CE']['openInterest']; ce_chg+=item['CE']['changeinOpenInterest']
            if 'PE' in item: 
                pe_oi+=item['PE']['openInterest']; pe_chg+=item['PE']['changeinOpenInterest']
        pcr = pe_oi/ce_oi if ce_oi>0 else 1.1
        return ce_oi, pe_oi, ce_chg, pe_chg, round(pcr,2)
    except: return 0,0,0,0,1.10

def detect_candle(df):
    if len(df)<5: return "NO PATTERN","NEUTRAL"
    c=float(df["Close"].iloc[-1]); o=float(df["Open"].iloc[-1]); h=float(df["High"].iloc[-1]); l=float(df["Low"].iloc[-1])
    c1=float(df["Close"].iloc[-2]); o1=float(df["Open"].iloc[-2]); c2=float(df["Close"].iloc[-3]); o2=float(df["Open"].iloc[-3])
    body=abs(c-o); lower=min(o,c)-l; upper=h-max(o,c); body1=abs(c1-o1)
    if lower>body*2 and body>0 and c>o: return "HAMMER CANDLE","BULLISH"
    if upper>body*2 and c>o: return "INVERTED HAMMER","BULLISH"
    if c1<o1 and c>o and c>=o1 and o<=c1: return "BULLISH ENGULFING","BULLISH"
    if c1<o1 and c>o and o>c1 and c<o1: return "BULLISH HARAMI","BULLISH"
    if c1<o1 and c>o and o<c1 and c>(o1+c1)/2: return "PIERCING PATTERN","BULLISH"
    if len(df)>=3 and c>o and c1>o1 and c2>o2 and c>c1>c2: return "THREE WHITE SOLDIERS","BULLISH"
    if body<(h-l)*0.1 and lower>(h-l)*0.7: return "DRAGONFLY DOJI","BULLISH"
    if len(df)>=3 and c2<o2 and body1<abs(c2-o2)*0.3 and c>o: return "MORNING STAR","BULLISH"
    if upper>body*2 and c<o: return "SHOOTING STAR","BEARISH"
    if lower>body*2 and c<o: return "HANGING MAN","BEARISH"
    if c1>o1 and c<o and c<=o1 and o>=c1: return "BEARISH ENGULFING","BEARISH"
    if c1>o1 and c<o and o<c1 and c>o1: return "BEARISH HARAMI","BEARISH"
    if c1>o1 and c<o and o>c1 and c<(o1+c1)/2: return "DARK CLOUD COVER","BEARISH"
    if len(df)>=3 and c<o and c1<o1 and c2<o2: return "THREE BLACK CROWS","BEARISH"
    if body<(h-l)*0.1 and upper>(h-l)*0.7: return "GRAVESTONE DOJI","BEARISH"
    if len(df)>=3 and c2>o2 and body1<abs(c2-o2)*0.3 and c<o: return "EVENING STAR","BEARISH"
    return "NO PATTERN","NEUTRAL"

def analyze(symbol_yf, symbol_nse, name):
    try:
        d=yf.download(symbol_yf, period="3mo", interval="1d", progress=False, auto_adjust=True)
        i5=yf.download(symbol_yf, period="5d", interval="5m", progress=False, auto_adjust=True)
        i15=yf.download(symbol_yf, period="5d", interval="15m", progress=False, auto_adjust=True)
        if len(d)<20 or len(i5)<10 or len(i15)<10: return None
        spot=float(d["Close"].iloc[-1]); e20=float(d["Close"].ewm(20).mean().iloc[-1]); e50=float(d["Close"].ewm(50).mean().iloc[-1])
        low_y=float(d["Low"].iloc[-2]); high_y=float(d["High"].iloc[-2])
        p5,dir5=detect_candle(i5); p15,dir15=detect_candle(i15)
        ce_oi,pe_oi,ce_chg,pe_chg,pcr=get_oi_pcr(symbol_nse)
        bull=spot>e20>e50; bear=spot<e20
        if dir5=="NEUTRAL" and dir15=="NEUTRAL": return None
        if not (bull or bear): return None
        final="BULLISH" if (dir5=="BULLISH" or dir15=="BULLISH") and bull else "BEARISH" if (dir5=="BEARISH" or dir15=="BEARISH") and bear else "NEUTRAL"
        if final=="NEUTRAL": return None
        gap=50 if name=="NIFTY" else 100
        strike=round(spot/gap)*gap
        opt=f"{strike} {'CE BUY' if final=='BULLISH' else 'PE BUY'}"
        sl=low_y if final=="BULLISH" else high_y
        tgt1=spot+(150 if name=="NIFTY" else 300) if final=="BULLISH" else spot-(150 if name=="NIFTY" else 300)
        tgt2=spot+(300 if name=="NIFTY" else 600) if final=="BULLISH" else spot-(300 if name=="NIFTY" else 600)
        return f"💣 {name} OPTION BOND\n🎯 {name} {opt}\n🕯️ 5M:{p5}({dir5}) | 15M:{p15}({dir15})\n📊 Spot:{spot:.0f} EMA20:{e20:.0f} {'BULL ✅' if bull else 'BEAR ❌'}\n📈 PCR:{pcr} | OI:PE{pe_chg} CE{ce_chg}\n💰 Entry Spot:{spot:.0f} 🛑 SL:{sl:.0f}\n🎯 TGT1:{tgt1:.0f} TGT2:{tgt2:.0f}\n"
    except: return None

n_msg=analyze("^NSEI","NIFTY","NIFTY")
s_msg=analyze("^BSESN","NIFTY","SENSEX")

date=datetime.now().strftime("%d-%m-%Y %H:%M")
final=f"🎩 OPTION BOND - NIFTY+SENSEX [5M/15M]\n📅 {date}\n━━━━━━━━━━━━\n\n"
if n_msg: final+=n_msg+"\n━━━━━━━━━━━━\n\n"
if s_msg: final+=s_msg+"\n━━━━━━━━━━━━\n\n"
if not n_msg and not s_msg:
    final+=f"📊 No Candle BOND - WAIT\nNIFTY & SENSEX me pattern nahi bana"

print(final)
send_telegram(final)
