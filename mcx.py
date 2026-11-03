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
    if name == "GOLDMINI": return (comex_price * usdinr / 31.1035) * 10
    elif name == "SILVERM": return (comex_price * usdinr / 31.1035) * 1000 * 1.02
    else: return comex_price * usdinr

def get_usdinr():
    try:
        df = yf.download("INR=X", period="1d", interval="1m", progress=False)
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        price = float(df['Close'].iloc[-1])
        if price < 80 or price > 100: return 88.5
        return price
    except: return 88.5

def check_symbol(name, yf_sym, usdinr):
    df15 = yf.download(yf_sym, period="5d", interval="15m", progress=False)
    if len(df15) < 50: return None
    df15.columns = [c[0] if isinstance(c, tuple) else c for c in df15.columns]
    df15['RSI5'] = get_rsi(df15['Close'], 5)
    df15['EMA20'] = df15['Close'].ewm(span=20).mean()
    df15['EMA50'] = df15['Close'].ewm(span=50).mean()
    df15['VWAP'] = (df15['Close'] * df15['Volume']).cumsum() / df15['Volume'].cumsum()
    df15['VolAvg'] = df15['Volume'].rolling(20).mean()

    df5 = yf.download(yf_sym, period="2d", interval="5m", progress=False)
    if len(df5) < 30: return None
    df5.columns = [c[0] if isinstance(c, tuple) else c for c in df5.columns]
    df5['RSI5'] = get_rsi(df5['Close'], 5)
    df5['EMA20'] = df5['Close'].ewm(span=20).mean()
    df5['VWAP'] = (df5['Close'] * df5['Volume']).cumsum() / df5['Volume'].cumsum()
    df5['VolAvg'] = df5['Volume'].rolling(20).mean()

    last15 = df15.iloc[-1]
    last5 = df5.iloc[-1]

    support = float(df15['Low'].tail(20).min())
    resistance = float(df15['High'].tail(20).max())
    
    open_p = float(last15['Open']); close_p = float(last15['Close'])
    high_p = float(last15['High']); low_p = float(last15['Low'])
    body = abs(close_p - open_p)
    upper_wick = high_p - max(close_p, open_p)
    lower_wick = min(close_p, open_p) - low_p
    range_p = high_p - low_p
    if range_p == 0: return None

    vol15 = float(last15['Volume'] / last15['VolAvg']) if last15['VolAvg'] > 0 else 1.0
    rsi15 = float(last15['RSI5'])
    rsi5 = float(last5['RSI5'])
    vol5 = float(last5['Volume'] / last5['VolAvg']) if last5['VolAvg'] > 0 else 1.0

    trend_up = last15['EMA20'] > last15['EMA50']
    trend_up_5 = last5['EMA20'] > df5['EMA20'].iloc[-2] if len(df5)>2 else True
    vwap_up_5 = float(last5['Close']) > float(last5['VWAP'])

    is_hammer = lower_wick > body*2 and lower_wick > upper_wick and close_p > open_p
    is_inv_hammer = upper_wick > body*2 and close_p > open_p
    is_bull_eng = close_p > open_p and df15.iloc[-2]['Close'] < df15.iloc[-2]['Open']
    is_shooting = upper_wick > body*2 and upper_wick > lower_wick and close_p < open_p
    is_bear_eng = close_p < open_p and df15.iloc[-2]['Close'] > df15.iloc[-2]['Open']

    candle_name = ""
    signal = None
    if is_hammer: candle_name="Hammer"; signal="BUY"
    elif is_inv_hammer: candle_name="Inverted Hammer"; signal="BUY"
    elif is_bull_eng: candle_name="Bullish Engulfing"; signal="BUY"
    elif is_shooting: candle_name="Shooting Star"; signal="SELL"
    elif is_bear_eng: candle_name="Bearish Engulfing"; signal="SELL"

    if signal and vol15 >= 2.0 and vol5 >= 1.5 and vwap_up_5:
        quality="PLATINUM"; pts=2000; emoji="💎💎💎 PLATINUM BOMB"
    elif signal and vol15 >= 1.5:
        quality="DIAMOND"; pts=1500; emoji="💎💎 DIAMOND BOMB"
    elif signal:
        quality="GOLD"; pts=800; emoji="🪙 GOLD BOMB"
    else:
        return None

    ist = pytz.timezone('Asia/Kolkata')
    dt = datetime.now(ist).strftime("%d-%m %H:%M")
    mcx_price = to_mcx_price(name, close_p, usdinr)
    mcx_sl_low = to_mcx_price(name, low_p, usdinr)
    mcx_sl_high = to_mcx_price(name, high_p, usdinr)
    mcx_sup = to_mcx_price(name, support, usdinr)
    mcx_res = to_mcx_price(name, resistance, usdinr)
    trend_txt = "UP TREND + TREND CONFIRM" if trend_up else "DOWN TREND + TREND CONFIRM"
    confirm_txt = f"5M RSI:{rsi5:.1f} Vol:{vol5:.1f}x VWAP:{'UP' if vwap_up_5 else 'DOWN'} Trend:{'UP' if trend_up_5 else 'DOWN'}"

    if signal=="BUY":
        return f"""{emoji} BUY
📅 {dt} | 👉 {trend_txt}
📊 {name} MCX 15M Support @ {mcx_sup:.0f} | 5M Confirm: {confirm_txt}
📈 RSI15:{rsi15:.1f} | Vol15:{vol15:.1f}x | Quality: {quality}
🕯️ {candle_name} ✅ + Volume Spike ✅ (15M Candle se Entry, 5M se Confirm)
🎯 ENTRY: {name} @ {mcx_price:.0f} Rs
🛑 SL: {mcx_sl_low:.0f} Rs
🎯 T1: {mcx_price+pts:.0f} (+{pts}) | T2: {mcx_price+pts+500:.0f} | T3: {mcx_price+pts+1000:.0f}
💡 T1 pe 50% book"""
    else:
        return f"""{emoji} SELL
📅 {dt} | 👉 {trend_txt}
📊 {name} MCX 15M Resistance @ {mcx_res:.0f} | 5M Confirm: {confirm_txt}
📈 RSI15:{rsi15:.1f} | Vol15:{vol15:.1f}x | Quality: {quality}
🕯️ {candle_name} ✅ + Volume Spike ✅ (15M Candle se Entry, 5M se Confirm)
🎯 ENTRY: {name} @ {mcx_price:.0f} Rs
🛑 SL: {mcx_sl_high:.0f} Rs
🎯 T1: {mcx_price-pts:.0f} (-{pts}) | T2: {mcx_price-pts-500:.0f} | T3: {mcx_price-pts-1000:.0f}
💡 T1 pe 50% book"""

def send_tg(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})

usdinr = get_usdinr()
msgs = []
for n, s in SYMBOLS.items():
    m = check_symbol(n, s, usdinr)
    if m: msgs.append(m)

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist).strftime("%d-%m %I:%M %p")

if msgs:
    for m in msgs: send_tg(m)
else:
    msg = f"⚪ 5 MIN SCAN - Flat Market | {now}\n15M me koi strong candle nahi bani\nSupport/Resistance pe fight nahi hui\nNext scan 5 min me"
    send_tg(msg)
