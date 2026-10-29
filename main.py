import yfinance as yf
import os, requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

STOCKS = ["^NSEI","^BSESN","RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS"]
LAST_SIGNAL = {}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def rsi_calc(s, p=14):
    d = s.diff()
    g = d.where(d>0,0).ewm(alpha=1/p).mean()
    l = (-d.where(d<0,0)).ewm(alpha=1/p).mean()
    rs = g/l
    return 100 - (100/(1+rs))

def get_pattern_5m(df):
    if len(df)<4: return "NO"
    o,h,l,c = map(float, df.iloc[-1][["Open","High","Low","Close"]])
    po,ph,pl,pc = map(float, df.iloc[-2][["Open","High","Low","Close"]])
    p2o,p2h,p2l,p2c = map(float, df.iloc[-3][["Open","High","Low","Close"]])
    body = abs(c-o)
    if body==0: body=0.01
    lower = min(o,c)-l
    upper = h-max(o,c)
    rsi = float(rsi_calc(df["Close"]).iloc[-1])
    if pc<po and c>o and c>=po and o<=pc and rsi>50: return f"BULLISH ENGULFING - RSI {rsi:.0f}"
    if pc>po and c<o and o>=pc and c<=po and rsi<50: return f"BEARISH ENGULFING - RSI {rsi:.0f}"
    if lower>body*2.2 and upper<body*0.6 and rsi<45: return f"HAMMER at Support - RSI {rsi:.0f}"
    if lower>body*2.0 and upper<body*0.7 and rsi>52: return f"HAMMER - BULLISH - RSI {rsi:.0f}"
    if upper>body*2.2 and lower<body*0.6 and rsi>55: return f"SHOOTING STAR at Resistance - RSI {rsi:.0f}"
    if upper>body*2.0 and lower<body*0.7 and rsi<48: return f"SHOOTING STAR - BEARISH - RSI {rsi:.0f}"
    if p2c < p2o and abs(pc-p2o)<body and c>po and c>p2o: return f"MORNING STAR - RSI {rsi:.0f}"
    if p2c > p2o and abs(pc-p2o)<body and c<po and c<p2o: return f"EVENING STAR - RSI {rsi:.0f}"
    return "NO"

def get_trend_15m(df):
    if len(df)<20: return "NO TREND", 50
    close = float(df.iloc[-1]["Close"])
    high_5d = float(df["High"].tail(50).max())
    low_5d = float(df["Low"].tail(50).min())
    rsi = float(rsi_calc(df["Close"]).iloc[-1])
    ema20 = float(df["Close"].ewm(span=20).mean().iloc[-1])
    if close >= high_5d*0.993 and close>ema20 and rsi>58: return f"15M DAY HIGH BREAKOUT", rsi
    if close <= low_5d*1.007 and close<ema20 and rsi<42: return f"15M DAY LOW BREAKDOWN", rsi
    if close>ema20 and rsi>55: return "15M UPTREND", rsi
    if close<ema20 and rsi<45: return "15M DOWNTREND", rsi
    return "15M SIDEWAYS", rsi

def scan(stock):
    try:
        df15 = yf.download(stock, period="10d", interval="15m", progress=False, auto_adjust=True)
        df5 = yf.download(stock, period="5d", interval="5m", progress=False, auto_adjust=True)
        if len(df15)<25 or len(df5)<25: return
        trend15, rsi15 = get_trend_15m(df15)
        pattern5 = get_pattern_5m(df5)
        if pattern5=="NO": return
        is_buy = "BULLISH" in pattern5 or "HAMMER" in pattern5 or "MORNING" in pattern5
        is_sell = "BEARISH" in pattern5 or "SHOOTING" in pattern5 or "EVENING" in pattern5
        now = datetime.now()
        if stock in LAST_SIGNAL:
            if (now - LAST_SIGNAL[stock]).seconds < 2700: return
        if is_buy and ("UPTREND" in trend15 or "HIGH BREAK" in trend15):
            LAST_SIGNAL[stock]=now
            send_telegram(f"🧈 MAKHAN BUY {stock}\n📌 {pattern5}\n📈 {trend15} (RSI {rsi15:.0f})\n⏰ {now.strftime('%d-%m %H:%M')}\n👉 CE Buy - Niche se Upar")
        elif is_sell and ("DOWNTREND" in trend15 or "LOW BREAK" in trend15):
            LAST_SIGNAL[stock]=now
            send_telegram(f"🧈 MAKHAN SELL {stock}\n📌 {pattern5}\n📉 {trend15} (RSI {rsi15:.0f})\n⏰ {now.strftime('%d-%m %H:%M')}\n👉 PE Buy - Upar se Niche")
        elif is_buy and rsi15>60:
            LAST_SIGNAL[stock]=now
            send_telegram(f"⚡ FAST BUY {stock}\n📌 {pattern5}\n📈 {trend15}\n⏰ {now.strftime('%d-%m %H:%M')}")
        elif is_sell and rsi15<40:
            LAST_SIGNAL[stock]=now
            send_telegram(f"⚡ FAST SELL {stock}\n📌 {pattern5}\n📉 {trend15}\n⏰ {now.strftime('%d-%m %H:%M')}")
    except Exception as e:
        print(e)

def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        ex.map(scan, STOCKS)

if __name__=="__main__":
    main()
