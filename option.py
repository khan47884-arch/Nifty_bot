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

def get_rsi(series, p=14):
    d = series.diff()
    g = d.where(d > 0, 0).rolling(p).mean()
    l = -d.where(d < 0, 0).rolling(p).mean()
    rs = g / l
    return 100 - (100 / (1 + rs))

def run_for(symbol, name, step):
    try:
        df = yf.download(symbol, period="10d", interval="5m", progress=False, threads=False, auto_adjust=True)
        if df.empty or len(df) < 100:
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
        last_price = float(last['Close'])
        rsi = float(last['RSI'])
        ema20 = float(last['EMA20'])
        ema50 = float(last['EMA50'])
        ema200 = float(last['EMA200'])
        vwap = float(last['VWAP'])
        vol = float(last['Volume'] / last['VolAvg']) if last['VolAvg'] > 0 else 0
        recent_high = max(closes[-21:-1])
        recent_low = min(closes[-21:-1])
        side = None
        if last_price > recent_high:
            side = "CE"
        elif last_price < recent_low:
            side = "PE"
        else:
            return False
        if vol < 1.8:
            return False
        if side == "CE" and rsi > 72:
            return False
        if side == "PE" and rsi < 28:
            return False
        tier = "GOLD BOND"
        if vol >= 2.0 and 35 < rsi < 68:
            tier = "DIAMOND BOND"
        trend_up = last_price > ema20 and ema20 > ema50 and last_price > ema200 and last_price > vwap
        trend_down = last_price < ema20 and ema20 < ema50 and last_price < ema200 and last_price < vwap
        if side == "CE" and trend_up and vol >= 2.2 and 40 < rsi < 65:
            tier = "PLATINUM BOND"
        if side == "PE" and trend_down and vol >= 2.2 and 35 < rsi < 60:
            tier = "PLATINUM BOND"
        strike = int(round(last_price / step) * step)
        now_str = datetime.now(IST).strftime('%d-%m %I:%M')
        msg = f"💣 {name} OPTION BOND [{tier}]\n📅 {now_str} | RSI:{rsi:.1f} Vol:{vol:.1f}x\n\n{name} {strike} {side} BUY\nPrice {last_price:.2f}\n5M BREAKOUT {side} SIDE\nSL {recent_low if side=='CE' else recent_high:.2f}\n🎯 T1 pe 50% book"
        if send_tg(msg):
            return True
        return False
    except:
        return False

if __name__ == "__main__":
    n = run_for("^NSEI", "NIFTY", 50)
    time.sleep(2)
    s = run_for("^BSESN", "SENSEX", 100)
