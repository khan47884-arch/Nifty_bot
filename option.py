import yfinance as yf
import requests
import os
import time
from datetime import datetime
import pytz
import pandas as pd

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
IST = pytz.timezone('Asia/Kolkata')

def send_tg(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
        return r.status_code == 200
    except:
        return False

def get_rsi(s, p=14):
    d = s.diff()
    g = d.where(d > 0, 0).rolling(p).mean()
    l = -d.where(d < 0, 0).rolling(p).mean()
    rs = g / l
    return 100 - (100 / (1 + rs))

def run_for(symbol, name, step):
    try:
        df = yf.download(symbol, period="10d", interval="5m", progress=False, threads=False, auto_adjust=True)
        if df.empty or len(df) < 80:
            return False
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        df['RSI'] = get_rsi(df['Close'])
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['EMA200'] = df['Close'].ewm(span=200).mean()
        df['VolAvg'] = df['Volume'].rolling(20).mean()
        df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        last = df.iloc[-1]
        closes = df['Close'].tolist()
        highs = df['High'].tolist()
        lows = df['Low'].tolist()
        price = float(last['Close'])
        rsi = float(last['RSI'])
        ema20 = float(last['EMA20'])
        ema50 = float(last['EMA50'])
        ema200 = float(last['EMA200'])
        vwap = float(last['VWAP'])
        vol = float(last['Volume'] / last['VolAvg']) if last['VolAvg'] > 0 else 0
        recent_high = max(closes[-21:-1])
        recent_low = min(closes[-21:-1])
        range_high = max(highs[-21:-1])
        range_low = min(lows[-21:-1])
        buffer = (range_high - range_low) * 0.15
        tier = None
        side = None
        logic = ""

        # SIRF CONFIRM SIGNAL - HAR 5 MIN PE CHECK, MESSAGE SIRF CONFIRM PE
        # 1. PLATINUM BREAKOUT ONLY
        if price > recent_high and vol >= 2.2 and 40 < rsi < 65:
            if price > ema20 and ema20 > ema50 and price > ema200 and price > vwap:
                side = "CE"
                tier = "PLATINUM BOND"
                logic = f"BREAKOUT CONFIRM UP > {recent_high:.0f}"
        elif price < recent_low and vol >= 2.2 and 35 < rsi < 60:
            if price < ema20 and ema20 < ema50 and price < ema200 and price < vwap:
                side = "PE"
                tier = "PLATINUM BOND"
                logic = f"BREAKOUT CONFIRM DOWN < {recent_low:.0f}"
        # 2. TOP-BOTTOM CONFIRM
        else:
            if price >= (range_high - buffer) and rsi <= 48 and vol >= 1.5:
                side = "PE"
                tier = "TOP TO BOTTOM CONFIRM"
                logic = f"TOP SE DOWN {range_high:.0f} -> RSI DOWN {rsi:.1f}"
            elif price <= (range_low + buffer) and rsi >= 52 and vol >= 1.5:
                side = "CE"
                tier = "BOTTOM TO TOP CONFIRM"
                logic = f"BOTTOM SE UP {range_low:.0f} -> RSI UP {rsi:.1f}"
            else:
                return False

        if tier is None:
            return False

        strike = int(round(price / step) * step)
        now = datetime.now(IST).strftime('%d-%m %I:%M')
        msg = f"💣 {name} OPTION BOND [{tier}]\n📅 {now} | RSI:{rsi:.1f} Vol:{vol:.1f}x\n📊 {logic}\n\n{name} {strike} {side} BUY\nPrice {price:.2f}\n🎯 CONFIRM SIGNAL"
        return send_tg(msg)
    except:
        return False

if __name__ == "__main__":
    run_for("^NSEI", "NIFTY", 50)
    time.sleep(2)
    run_for("^BSESN", "SENSEX", 100)
