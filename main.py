import yfinance as yf
import os, requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","^NSEI","^BSESN"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for i in range(0, len(msg), 3900):
        try: requests.post(url, data={"chat_id": CHAT_ID, "text": msg[i:i+3900]})
        except: pass

def rsi_calc(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_pattern(df):
    if len(df)<3: return "NO PATTERN"
    o,h,l,c = map(float, df.iloc[-1][["Open","High","Low","Close"]])
    po,ph,pl,pc = map(float, df.iloc[-2][["Open","High","Low","Close"]])
    body = abs(c-o)
    lower = min(o,c)-l
    upper = h-max(o,c)
    if len(df)>=3 and df.iloc[-3]["Close"] < df.iloc[-3]["Open"] and pc < df.iloc[-3]["Low"]:
        if c > po: return "MORNING STAR - BULLISH"
    if len(df)>=3 and df.iloc[-3]["Close"] > df.iloc[-3]["Open"] and pc > df.iloc[-3]["High"]:
        if c < po: return "EVENING STAR - BEARISH"
    if pc<po and c>o and c>=po and o<=pc: return "BULLISH ENGULFING"
    if pc>po and c<o and o>=pc and c<=po: return "BEARISH ENGULFING"
    if lower>body*2 and upper<body*0.5: return "HAMMER - BULLISH"
    if upper>body*2 and lower<body*0.5: return "SHOOTING STAR - BEARISH"
    return "NO PATTERN"

def get_big_pattern_15m(df):
    if len(df)<2: return "NO BIG PATTERN"
    last_close = float(df.iloc[-1]["Close"])
    day_high = float(df["High"].max())
    day_low = float(df["Low"].min())
    rsi = float(rsi_calc(df["Close"]).iloc[-1])
    if last_close >= day_high * 0.998 and rsi > 60:
        return f"DAY HIGH BREAK 15M - RSI {rsi:.1f}"
    if last_close <= day_low * 1.002 and rsi < 40:
        return f"DAY LOW BREAK 15M - RSI {rsi:.1f}"
    return "NO BIG PATTERN"

def scan_stock(stock):
    try:
        df15 = yf.download(stock, period="5d", interval="15m", progress=False)
        df5 = yf.download(stock, period="2d", interval="5m", progress=False)
        if len(df15)<20 or len(df5)<20: return
        big = get_big_pattern_15m(df15)
        small = get_pattern(df5)
        rsi5 = float(rsi_calc(df5["Close"]).iloc[-1])
        if "DAY HIGH BREAK" in big and "BULLISH" in small:
            send_telegram(f"🚀 FAST BUY {stock}\n{big}\n5M: {small}\nRSI: {rsi5:.1f}\nTime: {datetime.now().strftime('%H:%M')}")
        elif "DAY LOW BREAK" in big and "BEARISH" in small:
            send_telegram(f"🔻 FAST SELL {stock}\n{big}\n5M: {small}\nRSI: {rsi5:.1f}\nTime: {datetime.now().strftime('%H:%M')}")
    except Exception as e:
        print(f"Error {stock}: {e}")

def main():
    with ThreadPoolExecutor(max_workers=5) as exe:
        exe.map(scan_stock, STOCKS)

if __name__ == "__main__":
    main()
