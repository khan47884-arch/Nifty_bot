import yfinance as yf
import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def is_strong(row, type="green"):
    try:
        body = abs(float(row['Close']) - float(row['Open']))
        rng = float(row['High']) - float(row['Low'])
        if rng == 0 or body/rng < 0.6:
            return False
        if type == "green":
            return float(row['Close']) > float(row['Open'])
        if type == "red":
            return float(row['Close']) < float(row['Open'])
    except:
        return False
    return False

def check(symbol, name):
    try:
        daily = yf.download(symbol, period="5d", interval="1d", auto_adjust=True, progress=False)
        if len(daily) < 3:
            return None
        prev_high = float(daily['High'].iloc[-2])
        prev_low = float(daily['Low'].iloc[-2])

        intraday = yf.download(symbol, period="1d", interval="5m", auto_adjust=True, progress=False)
        if len(intraday) < 3:
            return None
        
        open_today = float(intraday['Open'].iloc[0])
        curr_row = intraday.iloc[-1]
        curr = float(curr_row['Close'])

        if open_today > prev_high and curr > prev_high and is_strong(curr_row, "green"):
            return f"🔥 {name} BIWI ALERT\nUpar khula, Kaali Line {prev_high:.2f} tod ke upar\nPrice: {curr:.2f}"

        if open_today > prev_high and curr < prev_high and is_strong(curr_row, "red"):
            return f"🔻 {name} SI ALERT\nUpar se khula, Kaali Line {prev_high:.2f} tod ke neeche\nPrice: {curr:.2f}"

        if open_today < prev_low and curr < prev_low and is_strong(curr_row, "red"):
            return f"🔻 {name} SI ALERT\nNiche se khula, Kaali Line {prev_low:.2f} tod ke niche\nPrice: {curr:.2f}"

        if open_today < prev_low and curr > prev_low and is_strong(curr_row, "green"):
            return f"🔥 {name} BIWI ALERT\nNiche se khula, Kaali Line {prev_low:.2f} pe Support leke upar\nPrice: {curr:.2f}"

    except:
        pass
    return None

symbols = [("^NSEI", "NIFTY"), ("^BSESN", "SENSEX")]

for sym, name in symbols:
    signal = check(sym, name)
    if signal:
        send_telegram(signal)
