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

SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN"}
already_sent = set()
box_data = {}
system_built = False
exit_sent = False

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def build_box():
    global box_data
    box_data = {}
    msg = "Option Bond 💥\nNIFTY + SENSEX BOX READY\n"
    for name, sym in SYMBOLS.items():
        try:
            df15 = yf.download(sym, period="1d", interval="15m", progress=False, auto_adjust=True)
            df15.columns = [c[0] if isinstance(c, tuple) else c for c in df15.columns]
            box_high = float(df15["High"].iloc[0:3].max())
            box_low = float(df15["Low"].iloc[0:3].min())
            box_data[name] = (box_high, box_low)
            msg += f"{name} BOX: {box_low:.0f} - {box_high:.0f}\n"
        except: pass
    tg(msg)

def get_strike(name, entry):
    if name == "NIFTY": return int(round(entry / 50) * 50)
    else: return int(round(entry / 100) * 100)

def get_level(side, rsi):
    if side == "Bullish":
        if rsi >= 60:
            return "Platinum", "Target -100+ Platinum ✅"
        else:
            return "Diamond", "Target -60+ Diamond ✅"
    else:
        if rsi <= 40:
            return "Platinum", "Target -100+ Platinum ✅"
        else:
            return "Diamond", "Target -60+ Diamond ✅"

def detect_pattern(df):
    if len(df) < 3: return None, None
    c1 = df.iloc[-3]; c2 = df.iloc[-2]; c3 = df.iloc[-1]
    def vals(c): return float(c["Open"]), float(c["Close"]), float(c["High"]), float(c["Low"])
    o1, cl1, h1, l1 = vals(c1); o2, cl2, h2, l2 = vals(c2); o3, cl3, h3, l3 = vals(c3)
    body3 = abs(cl3 - o3); range3 = h3 - l3
    if range3 == 0: return None, None
    upper_wick3 = h3 - max(o3, cl3); lower_wick3 = min(o3, cl3) - l3
    is_green3 = cl3 > o3; is_red3 = cl3 < o3
    if is_green3 and lower_wick3 > body3*2 and upper_wick3 < body3*0.5: return "HAMMER", "Bullish"
    if is_green3 and upper_wick3 > body3*2 and lower_wick3 < body3*0.5: return "INVERTED HAMMER", "Bullish"
    if body3 < range3*0.1 and lower_wick3 > range3*0.7: return "DRAGONFLY DOJI", "Bullish"
    if cl1 < o1 and abs(cl2-o2) < abs(cl1-o1)*0.4 and is_green3 and cl3 > (o1+cl1)/2: return "MORNING STAR", "Bullish"
    if cl1 > o1 and cl2 > o2 and is_green3 and cl2 > cl1 and cl3 > cl2: return "THREE WHITE SOLDIERS", "Bullish"
    if is_red3 and upper_wick3 > body3*2 and lower_wick3 < body3*0.5: return "SHOOTING STAR", "Bearish"
    if is_red3 and lower_wick3 > body3*2 and upper_wick3 < body3*0.5: return "HANGING MAN", "Bearish"
    if body3 < range3*0.1 and upper_wick3 > range3*0.7: return "GRAVESTONE DOJI", "Bearish"
    if cl1 > o1 and abs(cl2-o2) < abs(cl1-o1)*0.4 and is_red3 and cl3 < (o1+cl1)/2: return "EVENING STAR", "Bearish"
    if cl1 < o1 and cl2 < o2 and is_red3 and cl2 < cl1 and cl3 < cl2: return "THREE BLACK CROWS", "Bearish"
    return None, None

def check_one(name, sym):
    if name not in box_data: return
    try:
        box_high, box_low = box_data[name]
        df15 = yf.download(sym, period="1d", interval="15m", progress=False, auto_adjust=True)
        df5 = yf.download(sym, period="1d", interval="5m", progress=False, auto_adjust=True)
        if len(df15) < 5 or len(df5) < 5: return
        for df in [df15, df5]:
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df15["VWAP"] = (df15["High"]+df15["Low"]+df15["Close"]).div(3).rolling(10).mean()
        vwap = float(df15["VWAP"].iloc[-1])
        df15["RSI"] = calc_rsi(df15["Close"])
        rsi = float(df15["RSI"].iloc[-1])
        last_15 = df15.iloc[-1]
        last_close = float(last_15["Close"]); last_low = float(last_15["Low"]); last_high = float(last_15["High"])
        c_entry = df5.iloc[-1]
        entry_close = float(c_entry["Close"])
        # 15 MIN TIMEFRAME KO TOUCH KARKE POLICE CANDLE - 15 MIN PE PATTERN CHECK
        pattern, side = detect_pattern(df15)
        if not pattern: return
        key = name + "_" + str(df15.index[-1]) + "_" + pattern
        if key in already_sent: return
        touched_support = last_low <= box_low * 1.001
        touched_res = last_high >= box_high * 0.999
        touched_15 = touched_support or touched_res or last_close > box_high or last_close < box_low
        if not touched_15: return
        if side == "Bullish" and last_close > vwap:
            strike = get_strike(name, entry_close)
            level, target_line = get_level(side, rsi)
            msg = f"Option Bond 💥 {level}\n{name}\n{pattern} - Bullish ✅\nRSI+{rsi:.0f}\nVwap+✅\nEntry {strike}-CE\nVerify Buy Khan Sahab\n{target_line}"
            tg(msg); already_sent.add(key); return
        if side == "Bearish" and last_close < vwap:
            strike = get_strike(name, entry_close)
            level, target_line = get_level(side, rsi)
            msg = f"Option Bond 💥 {level}\n{name}\n{pattern} - Bearish ✅\nRSI+{rsi:.0f}\nVwap+✅\nEntry {strike}-PE\nVerify Buy Khan Sahab\n{target_line}"
            tg(msg); already_sent.add(key); return
    except Exception as e:
        print(name, "check fail", e)

tg("Option Bond 💥\nBOT ON Khan Sahab")
print("BOT STARTED", datetime.now(IST))
start_time = time.time()
while True:
    now = datetime.now(IST)
    if now.weekday() < 5 and ((now.hour == 10 and now.minute >= 0) or now.hour > 10) and not system_built:
        build_box(); system_built = True
    is_market = now.weekday() < 5 and ((now.hour == 10 and now.minute >= 0) or (now.hour > 10 and now.hour < 15) or (now.hour == 15 and now.minute <= 15))
    if is_market and system_built:
        for name, sym in SYMBOLS.items():
            check_one(name, sym); time.sleep(1)
    if now.weekday() < 5 and now.hour == 15 and now.minute >= 15 and not exit_sent:
        tg("Option Bond 💥\n3:15 HO GAYA Khan Sahab\nTrade Kaat Do")
        exit_sent = True; break
    if time.time() - start_time > 20000: break
    time.sleep(60)
