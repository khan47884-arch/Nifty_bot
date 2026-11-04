import yfinance as yf
import requests
import os
from datetime import datetime
import pytz
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYMBOLS = {"GOLDMINI": "GC=F", "SILVERM": "SI=F", "CRUDEOIL": "CL=F"}
def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)
def to_mcx_price(name, comex_price, usdinr):
    if name == "GOLDMINI": return (comex_price * usdinr / 31.1035) * 10
    elif name == "SILVERM": return (comex_price * usdinr / 31.1035) * 1000 * 1.18
    else: return comex_price * usdinr
def get_usdinr():
    try:
        df = yf.download("INR=X", period="1d", interval="1m", progress=False)
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        p = float(df['Close'].iloc[-1])
        return p if 80 < p < 100 else 88.5
    except: return 88.5
def check_symbol(name, yf_sym, usdinr):
    df15 = yf.download(yf_sym, period="5d", interval="15m", progress=False)
    if len(df15) < 50: return None
    df15.columns = [c[0] if isinstance(c, tuple) else c for c in df15.columns]
    df15['RSI'] = get_rsi(df15['Close'], 14)
    df15['EMA20'] = df15['Close'].ewm(span=20).mean()
    df15['EMA50'] = df15['Close'].ewm(span=50).mean()
    df15['VWAP'] = (df15['Close'] * df15['Volume']).cumsum() / df15['Volume'].cumsum()
    df15['VolAvg'] = df15['Volume'].rolling(20).mean()
    df5 = yf.download(yf_sym, period="2d", interval="5m", progress=False)
    if len(df5) < 30: return None
    df5.columns = [c[0] if isinstance(c, tuple) else c for c in df5.columns]
    df5['RSI'] = get_rsi(df5['Close'], 14)
    df5['EMA20'] = df5['Close'].ewm(span=20).mean()
    df5['VWAP'] = (df5['Close'] * df5['Volume']).cumsum() / df5['Volume'].cumsum()
    df5['VolAvg'] = df5['Volume'].rolling(20).mean()
    last15 = df15.iloc[-1]
    prev15 = df15.iloc[-2]
    last5 = df5.iloc[-1]
    if float(last15['VolAvg']) == 0 or float(last5['VolAvg']) == 0: return None
    vol15 = float(last15['Volume'] / last15['VolAvg'])
    vol5 = float(last5['Volume'] / last5['VolAvg'])
    if vol15 < 1.5 or vol5 < 1.2: return None
    rsi15 = float(last15['RSI'])
    rsi5 = float(last5['RSI'])
    if rsi15 < 5 or rsi15 > 95: return None
    if rsi15 > 70 or rsi15 < 25: return None
    vwap15 = float(last15['VWAP'])
    vwap5 = float(last5['VWAP'])
    ema20_15 = float(last15['EMA20'])
    ema50_15 = float(last15['EMA50'])
    support = float(df15['Low'].tail(20).min())
    resistance = float(df15['High'].tail(20).max())
    open_p = float(last15['Open']); close_p = float(last15['Close'])
    high_p = float(last15['High']); low_p = float(last15['Low'])
    body = abs(close_p - open_p)
    if body == 0: return None
    upper_wick = high_p - max(close_p, open_p)
    lower_wick = min(close_p, open_p) - low_p
    range_p = high_p - low_p
    if range_p == 0 or range_p < body*0.5: return None
    is_hammer = lower_wick > body*2.2 and lower_wick > upper_wick*1.5 and close_p > open_p
    is_bull_eng = close_p > open_p and prev15['Close'] < prev15['Open'] and close_p > prev15['Open'] and open_p < prev15['Close']
    is_shooting = upper_wick > body*2.2 and upper_wick > lower_wick*1.5 and close_p < open_p
    is_bear_eng = close_p < open_p and prev15['Close'] > prev15['Open'] and close_p < prev15['Open'] and open_p > prev15['Close']
    signal = None; candle_name = ""
    if is_hammer: candle_name="Hammer"; signal="BUY"
    elif is_bull_eng: candle_name="Bullish Engulfing"; signal="BUY"
    elif is_shooting: candle_name="Shooting Star"; signal="SELL"
    elif is_bear_eng: candle_name="Bearish Engulfing"; signal="SELL"
    else: return None
    if signal=="BUY":
        if not (close_p > ema20_15 and ema20_15 > ema50_15): return None
        if not (float(last5['Close']) > vwap5 and close_p > vwap15): return None
        if rsi5 < 30: return None
    else:
        if not (close_p < ema20_15 and ema20_15 < ema50_15): return None
        if not (float(last5['Close']) < vwap5 and close_p < vwap15): return None
        if rsi5 > 70: return None
    if name == "CRUDEOIL": pts=60; t2_extra=20; t3_extra=40
    elif name == "GOLDMINI": pts=150; t2_extra=150; t3_extra=300
    else: pts=1000; t2_extra=1000; t3_extra=2000
    ist = pytz.timezone('Asia/Kolkata')
    dt = datetime.now(ist).strftime("%d-%m %H:%M")
    mcx_price = to_mcx_price(name, close_p, usdinr)
    mcx_sl_low = to_mcx_price(name, low_p, usdinr)
    mcx_sl_high = to_mcx_price(name, high_p, usdinr)
    mcx_sup = to_mcx_price(name, support, usdinr)
    mcx_res = to_mcx_price(name, resistance, usdinr)
    if signal=="BUY":
        return f"""💎💎 DIAMOND BUY
📅 {dt} | 👉 UP TREND CONFIRM
📊 {name} 15M Support @ {mcx_sup:.0f} | 5M RSI:{rsi5:.1f} Vol:{vol5:.1f}x VWAP:UP
📈 RSI15:{rsi15:.1f} | Vol15:{vol15:.1f}x
🕯️ {candle_name} ✅ + Vol Spike ✅
🎯 ENTRY: {name} @ {mcx_price:.0f}
🛑 SL: {mcx_sl_low:.0f}
🎯 T1: {mcx_price+pts:.0f} (+{pts}) | T2: {mcx_price+pts+t2_extra:.0f} | T3: {mcx_price+pts+t3_extra:.0f}"""
    else:
        return f"""💎💎 DIAMOND SELL
📅 {dt} | 👉 DOWN TREND CONFIRM
📊 {name} 15M Resistance @ {mcx_res:.0f} | 5M RSI:{rsi5:.1f} Vol:{vol5:.1f}x VWAP:DOWN
📈 RSI15:{rsi15:.1f} | Vol15:{vol15:.1f}x
🕯️ {candle_name} ✅ + Vol Spike ✅
🎯 ENTRY: {name} @ {mcx_price:.0f}
🛑 SL: {mcx_sl_high:.0f}
🎯 T1: {mcx_price-pts:.0f} (-{pts}) | T2: {mcx_price-pts-t2_extra:.0f} | T3: {mcx_price-pts-t3_extra:.0f}"""
def send_tg(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
usdinr = get_usdinr()
msgs=[]
for n,s in SYMBOLS.items():
    m=check_symbol(n,s,usdinr)
    if m: msgs.append(m)
ist=pytz.timezone('Asia/Kolkata')
now=datetime.now(ist).strftime("%d-%m %I:%M %p")
if msgs:
    for m in msgs: send_tg(m)
else:
    send_tg(f"⚪ FLAT - No Strong Signal | {now}\nVol/RSI/Trend confirm nahi hua, isliye skip\nNext 5 min me")
