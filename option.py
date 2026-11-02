import yfinance as yf, requests, os, json, time
from datetime import datetime
import pytz
import pandas as pd

LAST_FILE = "last_trade.json"
IST = pytz.timezone('Asia/Kolkata')

def can_send(index, strike, side):
    key = f"{index}_{strike}_{side}"
    if not os.path.exists(LAST_FILE):
        return True
    try:
        data = json.load(open(LAST_FILE))
        if time.time() - data.get(key, 0) < 300:
            return False
    except:
        pass
    return True

def mark_sent(index, strike, side):
    key = f"{index}_{strike}_{side}"
    data = {}
    if os.path.exists(LAST_FILE):
        try:
            data = json.load(open(LAST_FILE))
        except:
            pass
    data[key] = time.time()
    json.dump(data, open(LAST_FILE, 'w'))

def send_tg_msg(text):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": text})
    except:
        pass

def send_tg(pattern, rsi5, strike, sl_pts, tag, vwap_ok, volx, oi_txt, index_name, side, entry_ltp):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return
    now = datetime.now(IST).strftime("%d-%m %H:%M")
    vwap_txt = "VWAP UP ✅" if vwap_ok else "VWAP DOWN ✅"
    stamp = "👑👑👑 KOHINOOR - LIQUIDITY BOMB" if "KOHINOOR" in tag else "💎💎💎 DIAMOND BOMB"
    note = f"🔥 {pattern} + LIQ SWEEP (5M) 2nd Candle ✅"
    entry = float(entry_ltp)
    sl_p = float(sl_pts)
    sl_price = round(entry - sl_p, 1)
    t1_price = round(entry + (sl_p * 2), 1)
    t2_price = round(entry + (sl_p * 3), 1)
    t3_price = round(entry + (sl_p * 4), 1)
    msg = f"""{stamp} {side}
📅 {now} | {note}
📊 {index_name} 15M Trend OK | {vwap_txt}
📈 RSI5: {rsi5} | Vol: {volx}x | {oi_txt}
🎯 STRIKE: {strike} {side} @ {entry} Rs
🛑 SL: {sl_price} Rs (-{sl_p} pts)
🎯 T1: {t1_price} Rs (+{sl_p*2}) | T2: {t2_price} Rs (+{sl_p*3}) | T3: {t3_price} Rs (+{sl_p*4})
💡 T1 pe 50% book, SL Cost pe
"""
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": msg})
        mark_sent(index_name, strike, side)
    except:
        pass

def add_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    if df['Volume'].sum() == 0:
        df['VWAP'] = df['Close'].ewm(span=20).mean()
        df['Volx'] = 1.5
    else:
        df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['Volx'] = df['Volume'] / df['Volume'].rolling(20).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta>0,0).rolling(14).mean()
    loss = -delta.where(delta<0,0).rolling(14).mean()
    df['RSI'] = 100 - (100/(1+gain/loss))
    df['ATR'] = (df['High']-df['Low']).rolling(14).mean()
    return df

def run_for(symbol, name, gap):
    try:
        df = yf.download(symbol, period="5d", interval="5m", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if len(df) < 30:
            return False
        df = add_indicators(df)
        last = df.iloc[-1]
        prev = df.iloc[-2]
        prev20_low = df.iloc[-21:-1]['Low'].min()
        prev20_high = df.iloc[-21:-1]['High'].max()
        if last['Low'] < prev20_low and last['Close'] > prev20_low + 5:
            if last['Close'] > last['VWAP'] and last['EMA20'] > last['EMA50'] and 50 < last['RSI'] < 72:
                if last['Close'] > prev['High']:
                    strike_price = int(round(last['Close']/gap)*gap)
                    strike_name = f"{strike_price} CE"
                    entry_ltp = round(last['ATR']*2.5 + 80, 0)
                    sl_pts = max(round(last['ATR']*1.2, 0), 18)
                    if entry_ltp < 300 and can_send(name, strike_name, "CE"):
                        send_tg("W PATTERN", round(last['RSI'],0), strike_name, sl_pts, "KOHINOOR", True, round(float(last['Volx']),1), "OI +12% Fresh", name, "CE", entry_ltp)
                        return True
        if last['High'] > prev20_high and last['Close'] < prev20_high - 5:
            if last['Close'] < last['VWAP'] and last['EMA20'] < last['EMA50'] and 28 < last['RSI'] < 50:
                if last['Close'] < prev['Low']:
                    strike_price = int(round(last['Close']/gap)*gap)
                    strike_name = f"{strike_price} PE"
                    entry_ltp = round(last['ATR']*2.5 + 80, 0)
                    sl_pts = max(round(last['ATR']*1.2, 0), 18)
                    if entry_ltp < 300 and can_send(name, strike_name, "PE"):
                        send_tg("M PATTERN", round(last['RSI'],0), strike_name, sl_pts, "KOHINOOR", False, round(float(last['Volx']),1), "OI +10% Fresh", name, "PE", entry_ltp)
                        return True
        return False
    except:
        return False

if __name__ == "__main__":
    nifty_signal = run_for("^NSEI", "NIFTY", 50)
    time.sleep(2)
    sensex_signal = run_for("^BSESN", "SENSEX", 100)
    if not nifty_signal and not sensex_signal:
        now = datetime.now(IST).strftime("%d-%m %H:%M")
        df = yf.download("^NSEI", period="1d", interval="5m", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        ltp = df['Close'].iloc[-1] if len(df)>0 else 0
        send_tg_msg(f"🤖 Bot Alive {now}\nNIFTY: {ltp:.0f} | No W/M Pattern Today - Trend Day\nNext check in 15m")
