import yfinance as yf
import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def is_strong(row, type="green"):
    try:
        body = abs(float(row['Close']) - float(row['Open']))
        rng = float(row['High']) - float(row['Low'])
        if rng == 0 or body/rng < 0.6: return False
        if type == "green": return float(row['Close']) > float(row['Open'])
        if type == "red": return float(row['Close']) < float(row['Open'])
    except: return False
    return False

def check(symbol, name):
    daily = yf.download(symbol, period="10d", interval="1d", progress=False, auto_adjust=True)
    prev_high = float(daily['High'].iloc[-2])
    prev_low = float(daily['Low'].iloc[-2])
    intraday = yf.download(symbol, period="2d", interval="5m", progress=False, auto_adjust=True)
    if len(intraday) < 3: return f"{name}: No Data"
    curr_row = intraday.iloc[-1]
    prev_row = intraday.iloc[-2]
    curr = float(curr_row['Close'])
    SL_POINT = 60 if "SENSEX" in name else 30
    entry = curr
    t1_gap = SL_POINT * 1.5
    t2_gap = SL_POINT * 3
    if curr > prev_high and is_strong(curr_row, "green"):
        return f"🚀 CONFIRM BUY {name}\nEntry: {entry:.2f}\nSL: {entry-SL_POINT:.2f} ({SL_POINT} pts)\nT1: {entry+t1_gap:.2f} | T2: {entry+t2_gap:.2f}\nReason: High {prev_high:.2f} Break"
    if curr < prev_high and float(prev_row['High']) >= prev_high*0.999 and is_strong(curr_row, "red"):
        return f"🔻 TOP SE SELL {name}\nEntry: {entry:.2f}\nSL: {entry+SL_POINT:.2f} ({SL_POINT} pts)\nT1: {entry-t1_gap:.2f} | T2: {entry-t2_gap:.2f}\nReason: High {prev_high:.2f} Fail"
    if curr > prev_low and curr < prev_low*1.008 and is_strong(curr_row, "green"):
        return f"🚀 SUPPORT BOUNCE BUY {name}\nEntry: {entry:.2f}\nSL: {entry-SL_POINT:.2f} ({SL_POINT} pts)\nT1: {entry+t1_gap:.2f} | T2: {entry+t2_gap:.2f}\nReason: Low {prev_low:.2f} se Bounce"
    if curr < prev_low and is_strong(curr_row, "red"):
        return f"🔻 CONFIRM SELL {name}\nEntry: {entry:.2f}\nSL: {entry+SL_POINT:.2f} ({SL_POINT} pts)\nT1: {entry-t1_gap:.2f} | T2: {entry-t2_gap:.2f}\nReason: Low {prev_low:.2f} Break"
    return f"Wait {name} - {curr:.2f}"

msg_nifty = check("^NSEI", "NIFTY")
msg_sensex = check("^BSESN", "SENSEX")
final = f"{msg_nifty}\n\n{msg_sensex}"
print(final)
send_telegram(final)
