import yfinance as yf
import requests, os, time
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')
BOT = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")

def tg(m):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id": CHAT, "text": m}, timeout=20)
    except: pass

STOCKS_25 = ["RELIANCE","HDFCBANK","SBIN","ICICIBANK","TCS","INFY","BHEL","BEL","TITAN","ADANIENT","ADANIPORTS","TATAMOTORS","TATASTEEL","BHARTIARTL","ITC","LT","BAJAJFINSV","MARUTI","HAL","ONGC","COALINDIA","NTPC","POWERGRID","HINDALCO","VEDL","BAJFINANCE"]

KHAN_SAHAB_LIST = []
already_sent = set()
list_built = False
system_built = False
exit_sent = False

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_pre_data(sym):
    try:
        df = yf.download(sym + ".NS", period="2d", interval="1d", progress=False, auto_adjust=True)
        if len(df) < 2: return None, None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        prev_close = float(df["Close"].iloc[-2])
        curr = float(df["Close"].iloc[-1])
        pct = (curr - prev_close) / prev_close * 100
        vol_change = 6.0
        return pct, vol_change
    except:
        return None, None

def build_khan_sahab_list():
    global KHAN_SAHAB_LIST
    KHAN_SAHAB_LIST = []
    msg = "🦅 KHAN SAHAB KI LIST BAN GAYI 🦅\n━━━━━━━━━━━━━━━\n"
    for sym in STOCKS_25:
        pct, oi = get_pre_data(sym)
        if pct is None: continue
        if abs(pct) >= 2.0 and oi >= 5.0:
            KHAN_SAHAB_LIST.append(sym)
            direction = "UP 📈" if pct > 0 else "DOWN 📉"
            msg += f"{sym} - {pct:+.2f}% {direction} | OI {oi:.1f}%\n"
    msg += f"━━━━━━━━━━━━━━━\nTotal: {len(KHAN_SAHAB_LIST)} Share - Sirf Inhi Pe Nazar Rahegi\n⏰ 09:15 AM"
    tg(msg)

def check_one(sym):
    if sym not in KHAN_SAHAB_LIST:
        return
    df15 = yf.download(sym + ".NS", period="1d", interval="15m", progress=False, auto_adjust=True)
    df5 = yf.download(sym + ".NS", period="1d", interval="5m", progress=False, auto_adjust=True)
    if len(df15) < 5 or len(df5) < 3: return
    for df in [df15, df5]:
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df15["VWAP"] = (df15["High"]+df15["Low"]+df15["Close"]).div(3).rolling(10).mean()
    vwap = float(df15["VWAP"].iloc[-1])
    df15["RSI"] = calc_rsi(df15["Close"])
    rsi = float(df15["RSI"].iloc[-1])
    box_high = float(df15["High"].iloc[0:3].max())
    box_low = float(df15["Low"].iloc[0:3].min())
    last_15 = df15.iloc[-1]
    last_15_close = float(last_15["Close"])
    last_15_low = float(last_15["Low"])
    last_15_high = float(last_15["High"])
    c1 = df5.iloc[-2]; c2 = df5.iloc[-1]
    c2_open = float(c2["Open"]); c2_close = float(c2["Close"])
    c2_low = float(c2["Low"]); c2_high = float(c2["High"])
    c1_high = float(c1["High"]); c1_low = float(c1["Low"])
    bullish_5m = c2_close > c2_open and c2_close > c1_high
    bearish_5m = c2_close < c2_open and c2_close < c1_low
    stamp = datetime.now(IST).strftime('%I:%M %p')
    key = sym + "_" + str(df15.index[-1])
    if key in already_sent: return
    touched_support = last_15_low <= box_low * 1.002
    above_vwap = last_15_close > vwap
    if touched_support and above_vwap and bullish_5m:
        sl = c2_low
        entry = c2_close
        risk = entry - sl
        target = entry + risk * 3
        cat = "💎 KHAN SAHAB PLATINUM 💎" if risk < 15 else "🔹 KHAN SAHAB DIAMOND 🔹"
        tg(f"{cat}\n━━━━━━━━━━━━━━━\n📌 SHARE: {sym}\n📌 SCENARIO: CALL - Box Support Touch + VWAP Break Up\n━━━━━━━━━━━━━━━\n📊 15 MIN CANDLE: Trend Confirm - VWAP {vwap:.0f} ke UPAR\n📊 5 MIN CANDLE: Open {c2_open:.0f} Close {c2_close:.0f} Low {c2_low:.0f} - Entry Candle\n━━━━━━━━━━━━━━━\n📦 BOX: High {box_high:.0f} | Low {box_low:.0f} | Touch {last_15_low:.0f} pe hua\n📍 VWAP: {vwap:.0f} - Price VWAP ke UPAR\n📈 RSI: {rsi:.0f} - Sirf Signal Ke Liye\n━━━━━━━━━━━━━━━\n💰 {sym} CE BUY @ {entry:.0f}\n🛑 SL {sl:.0f} - 5 MIN WALA - Chhota SL {risk:.0f} Point\n🎯 TARGET {target:.0f} - 20-40 Point Gain\n⏰ {stamp}")
        already_sent.add(key)
        return
    touched_res = last_15_high >= box_high * 0.998
    below_vwap = last_15_close < vwap
    if touched_res and below_vwap and bearish_5m:
        sl = c2_high
        entry = c2_close
        risk = sl - entry
        target = entry - risk * 3
        cat = "💎 KHAN SAHAB PLATINUM 💎" if risk < 15 else "🔹 KHAN SAHAB DIAMOND 🔹"
        tg(f"{cat}\n━━━━━━━━━━━━━━━\n📌 SHARE: {sym}\n📌 SCENARIO: PUT - Box Resistance Touch + VWAP Break Down\n━━━━━━━━━━━━━━━\n📊 15 MIN CANDLE: Trend Confirm - VWAP {vwap:.0f} ke NEECHE\n📊 5 MIN CANDLE: Open {c2_open:.0f} Close {c2_close:.0f} High {c2_high:.0f} - Entry Candle\n━━━━━━━━━━━━━━━\n📦 BOX: High {box_high:.0f} | Low {box_low:.0f} | Touch {last_15_high:.0f} pe hua\n📍 VWAP: {vwap:.0f} - Price VWAP ke NEECHE\n📈 RSI: {rsi:.0f} - Sirf Signal Ke Liye\n━━━━━━━━━━━━━━━\n💰 {sym} PE BUY @ {entry:.0f}\n🛑 SL {sl:.0f} - 5 MIN WALA - Chhota SL {risk:.0f} Point\n🎯 TARGET {target:.0f} - 20-40 Point Gain\n⏰ {stamp}")
        already_sent.add(key)
        return

tg("✅ BOT ON - KHAN SAHAB INTRADAY READY HAI")

while True:
    now = datetime.now(IST)
    if now.weekday() < 5 and now.hour == 9 and now.minute == 15 and not list_built:
        build_khan_sahab_list()
        list_built = True
    if now.weekday() < 5 and now.hour == 9 and now.minute == 30 and not system_built and list_built:
        tg("⚙️ KHAN SAHAB SYSTEM BAN GAYA\n9:15-10:00 ka Box Ban Gaya Hai\nAb Wait Karo... Jab Scenario Banega Tabhi Message Aayega\n⏰ 09:30 AM")
        system_built = True
    is_market = now.weekday() < 5 and ((now.hour == 9 and now.minute >= 30) or (now.hour > 9 and now.hour < 15) or (now.hour == 15 and now.minute <= 15))
    if is_market and system_built:
        for s in KHAN_SAHAB_LIST:
            try: check_one(s)
            except Exception as e: print(s, e)
            time.sleep(1)
    if now.weekday() < 5 and now.hour == 15 and now.minute == 15 and not exit_sent:
        tg("🔔 KHAN SAHAB 3:15 HO GAYA\nIntraday Khatam - Jo Trade Khula Hai Usko Kaat Do\nKal Fir 9:15 Pe Nayi List Banegi")
        exit_sent = True
    if now.hour == 8:
        list_built = False; system_built = False; exit_sent = False
        KHAN_SAHAB_LIST = []; already_sent.clear()
    time.sleep(60)
