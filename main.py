import yfinance as yf
import os, requests
from datetime import datetime

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def rsi(s, p=14):
    d = s.diff()
    g = d.where(d>0,0).ewm(alpha=1/p).mean()
    l = (-d.where(d<0,0)).ewm(alpha=1/p).mean()
    return 100 - (100/(1+(g/l)))

def main():
    for sym, name in [("^NSEI","NIFTY"), ("^BSESN","SENSEX")]:
        try:
            df5 = yf.download(sym, period="2d", interval="5m", progress=False, auto_adjust=True)
            df15 = yf.download(sym, period="5d", interval="15m", progress=False, auto_adjust=True)
            if len(df5)<30 or len(df15)<30: continue
            o,h,l,c = map(float, df5.iloc[-1][["Open","High","Low","Close"]])
            po,ph,pl,pc = map(float, df5.iloc[-2][["Open","High","Low","Close"]])
            body = abs(c-o)
            if body==0: body=0.01
            lower = min(o,c)-l
            upper = h-max(o,c)
            rsi5 = float(rsi(df5["Close"]).iloc[-1])
            close15 = float(df15.iloc[-1]["Close"])
            ema20 = float(df15["Close"].ewm(span=20).mean().iloc[-1])
            rsi15 = float(rsi(df15["Close"]).iloc[-1])

            pattern = ""
            bullish = False
            bearish = False

            if pc < po and c > o and c >= po and o <= pc:
                pattern = "BULLISH ENGULFING"
                bullish = True
            elif pc > po and c < o and o >= pc and c <= po:
                pattern = "BEARISH ENGULFING"
                bearish = True
            elif lower > body*2 and upper < body*0.5:
                pattern = "HAMMER"
                bullish = True
            elif upper > body*2 and lower < body*0.5:
                pattern = "SHOOTING STAR"
                bearish = True
            elif lower > body*2.5:
                pattern = "BULLISH PIN BAR"
                bullish = True
            elif upper > body*2.5:
                pattern = "BEARISH PIN BAR"
                bearish = True

            if pattern == "": continue
            now = datetime.now().strftime('%d-%m-%Y %H:%M')

            if bullish and close15>ema20 and rsi15>55:
                send_telegram(f"🎩 OPTION BOND - {name} [5M/15M]\n📅 {now}\n________________________\n\n📊 {pattern} - BUY\n📈 15M Uptrend RSI {rsi15:.0f} | 5M RSI {rsi5:.0f}\n👉 CE BUY - {pattern}")
            elif bearish and close15<ema20 and rsi15<45:
                send_telegram(f"🎩 OPTION BOND - {name} [5M/15M]\n📅 {now}\n________________________\n\n📊 {pattern} - SELL\n📉 15M Downtrend RSI {rsi15:.0f} | 5M RSI {rsi5:.0f}\n👉 PE BUY - {pattern}")
        except: pass

if __name__=="__main__":
    main()
