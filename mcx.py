import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SYMBOLS = {"GOLDMINI": "GC=F", "SILVERM": "SI=F", "CRUDEOIL": "CL=F"}

def get_rsi(series, period=5):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def to_mcx_price(name, comex_price, usdinr):
    if name == "GOLDMINI":
        return (comex_price * usdinr / 31.1035) * 10
    elif name == "SILVERM":
        return (comex_price * usdinr / 31.1035) * 1000
    else:
        return comex_price * usdinr

def get_usdinr():
    try:
        df = yf.download("INR=X", period="1d", interval="1m", progress=False)
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return float(df['Close'].iloc[-1])
    except:
        return 84.0

def check_quality(df15):
    last = df15.iloc[-1]
    prev = df15.iloc[-2]
    rsi = float(last['RSI5']) if 'RSI5' in df15 else 50.0
    vol_avg = df15['Volume'].rolling(20).mean().iloc[-1]
    vol = float(last['Volume'] / vol_avg) if vol_avg > 0 else 1.0
    base_high = df15.tail(4)['High'].max()
    base_low = df15.tail(4)['Low'].min()
    is_inside = last['High'] < prev['High'] and last['Low'] > prev['Low']
    sweep = (last['High'] > base_high and last['Close'] < base_high) or (last['Low'] < base_low and last['Close'] > base_low)
    if vol >= 1.8 and is_inside and sweep:
        return "PLATINUM", 2000, rsi, vol, is_inside, sweep, base_high, base_low
    elif vol >= 1.3 and (is_inside or sweep):
        return "DIAMOND", 1500, rsi, vol, is_inside, sweep, base_high, base_low
    else:
        return "GOLD", 800, rsi, vol, is_inside, sweep, base_high, base_low

def check_symbol(name, yf_sym, usdinr):
    df15 = yf.download(yf_sym, period="5d", interval="15m", progress=False)
    if len(df15) < 50:
        return None
    df15.columns = [c[0] if isinstance(c, tuple) else c for c in df15.columns]
    df15['RSI5'] = get_rsi(df15['Close'], 5)
    df15['EMA20'] = df15['Close'].ewm(span=20).mean()
    df15['EMA50'] = df15['Close'].ewm(span=50).mean()
    df15['VWAP'] = (df15['Close'] * df15['Volume']).cumsum() / df15['Volume'].cumsum()
    quality, base_target, rsi, vol, is_inside, sweep, base_high, base_low = check_quality(df15)
    last = df15.iloc[-1]
    trend_up = last['EMA20'] > last['EMA50']
    vwap_up = last['Close'] > last['VWAP']
    df5 = yf.download(yf_sym, period="2d", interval="5m", progress=False)
    if len(df5) < 10:
        return None
    df5.columns = [c[0] if isinstance(c, tuple) else c for c in df5.columns]
    last5 = float(df5.iloc[-1]['Close'])
    if last5 <= base_high and last5 >= base_low:
        return None
    mcx_price = to_mcx_price(name, last5, usdinr)
    mcx_high = to_mcx_price(name, base_high, usdinr)
    mcx_low = to_mcx_price(name, base_low, usdinr)
    ist = pytz.timezone('Asia/Kolkata')
    dt = datetime.now(ist).strftime("%d-%m %H:%M")
    trend_txt = "UP TREND + TREND CONFIRM" if trend_up else "DOWN TREND + TREND CONFIRM"
    vwap_txt = "VWAP UP ✅" if vwap_up else "VWAP DOWN ✅"
    sweep_txt = "Liquidity Sweep ✅" if sweep else "No Sweep"
    inside_txt = "Inside Candle ✅" if is_inside else ""
    if quality == "PLATINUM":
        emoji = "💎💎💎 PLATINUM BOMB"
        t1, t2, t3 = base_target, base_target+500, base_target+1000
    elif quality == "DIAMOND":
        emoji = "💎💎 DIAMOND BOMB"
        t1, t2, t3 = base_target, base_target+300, base_target+700
    else:
        emoji = "🪙 GOLD BOMB"
        t1, t2, t3 = 800, 1000, 1200
    if last5 > base_high:
        return f"""{emoji} BUY
📅 {dt} | 👉 {trend_txt}
📊 {name} MCX 15M Trend OK | {vwap_txt}
📈 RSI5: {rsi:.1f} | Vol: {vol:.1f}x | Quality: {quality}
🕯️ {sweep_txt} {inside_txt}
🎯 ENTRY: {name} @ {mcx_price:.0f} Rs
🛑 SL: {mcx_low:.0f} Rs
🎯 T1: {mcx_price+t1:.0f} (+{t1}) | T2: {mcx_price+t2:.0f} (+{t2}) | T3: {mcx_price+t3:.0f} (+{t3})
💡 T1 pe 50% book, SL Cost pe"""
    else:
        return f"""{emoji} SELL
📅 {dt} | 👉 {trend_txt}
📊 {name} MCX 15M Trend OK | {vwap_txt}
📈 RSI5: {rsi:.1f} | Vol: {vol:.1f}x | Quality: {quality}
🕯️ {sweep_txt} {inside_txt}
🎯 ENTRY: {name} @ {mcx_price:.0f} Rs
🛑 SL: {mcx_high:.0f} Rs
🎯 T1: {mcx_price-t1:.0f} (-{t1}) | T2: {mcx_price-t2:.0f} (-{t2}) | T3: {mcx_price-t3:.0f} (-{t3})
💡 T1 pe 50% book, SL Cost pe"""

def send_tg(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})

usdinr = get_usdinr()
msgs = []
for n, s in SYMBOLS.items():
    m = check_symbol(n, s, usdinr)
    if m:
        msgs.append(m)

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist).strftime("%d-%m %I:%M %p")

if msgs:
    for m in msgs:
        send_tg(m)
        print(m)
else:
    msg = f"⚪ Aaj koi V2 DIAMOND nahi - 360 SCAN - MCX | {now}\nFlat Market - No Breakout"
    send_tg(msg)
    print(msg)
