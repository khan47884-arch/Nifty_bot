import yfinance as yf
import requests
import os
import json
import time
from datetime import datetime
import pytz
import pandas as pd

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FILE = "last_trade.json"
IST = pytz.timezone('Asia/Kolkata')

def send_tg(msg):
    if not BOT_TOKEN or not CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        return r.status_code == 200
    except:
        return False

def can_send(strike, side):
    try:
        if not os.path.exists(FILE):
            return True
        with open(FILE, 'r') as f:
            data = json.load(f)
        key = f"{strike}_{side}"
        last = data.get(key, 0)
        return (time.time() - last) > 300
    except:
        return True

def save_sent(strike, side):
    try:
        data = {}
        if os.path.exists(FILE):
            with open(FILE, 'r') as f:
                data = json.load(f)
        data[f"{strike}_{side}"] = time.time()
        with open(FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def run_for(symbol, name, step):
    try:
        df = yf.download(symbol, period="2d", interval="5m", progress=False)
        if df.empty or len(df) < 50:
            print(f"{name} No Data")
            return False
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        closes = df['Close'].tolist()
        last_price = float(closes[-1])
        recent_high = max(closes[-20:-1])
        recent_low = min(closes[-20:-1])
        side = None
        tier = ""
        if last_price > recent_high:
            side = "CE"
            tier = "GOLD BOND"
        elif last_price < recent_low:
            side = "PE"
            tier = "DIAMOND BOND"
        else:
            print(f"{name} No Breakout - {last_price}")
            return False
        strike = int(round(last_price / step) * step)
        if not can_send(strike, side):
            print(f"{name} {strike} {side} Blocked")
            return False
        now_str = datetime.now(IST).strftime('%d-%m %H:%M')
        msg = f"💣 {name} OPTION BOND [{tier}]\n\n"
        msg += f"{name} {strike} {side} BUY\n"
        msg += f"Price {last_price:.2f}\n"
        msg += f"Time {now_str} IST\n"
        msg += f"5M BREAKOUT {side} SIDE\n"
        msg += f"SL {recent_low if side=='CE' else recent_high:.2f}"
        if send_tg(msg):
            save_sent(strike, side)
            print(f"SENT {name} {strike} {side}")
            return True
        return False
    except Exception as e:
        print(f"Error in {name}: {e}")
        return False

if __name__ == "__main__":
    n = run_for("^NSEI", "NIFTY", 50)
    time.sleep(3)
    s = run_for("^BSESN", "SENSEX", 100)
    if not n and not s:
        now_str = datetime.now(IST).strftime('%H:%M')
        test_msg = f"📊 BOND 007 SCAN {now_str}\nNo BOND Setup - Market WAIT\nNIFTY & SENSEX Scanning Active ✅"
        send_tg(test_msg)
        print("No trade - active msg sent")
