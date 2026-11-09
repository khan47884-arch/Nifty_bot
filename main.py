import yfinance as yf
import pandas as pd
import requests, os, time
from datetime import datetime
import pytz
IST = pytz.timezone('Asia/Kolkata')
BOT = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")

def tg(m):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id": CHAT, "text": m}, timeout=20)
        print("TG:", r.status_code)
    except Exception as e: print("TG Fail", e)

SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN"}
box_data = {}
touched = {}
already_sent = set()
watch_sent = {}
system_built = False
exit_sent = False
last_box_date = None

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calc_vwap_daily(df):
    df = df.copy()
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['TPV'] = df['TP'] * df['Volume']
    df['VWAP'] = df.groupby(df['Dt'].dt.date)['TPV'].cumsum() / df.groupby(df['Dt'].dt.date)['Volume'].cumsum()
    df = df.drop(columns=['TP','TPV'])
    return df

def clean_df(df):
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()
    dt_col = df.columns[0]
    df['Dt'] = pd.to_datetime(df[dt_col])
    try:
        df['Dt'] = df['Dt'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    except: pass
    return df

def build_box():
    global box_data, touched, last_box_date
    box_data = {}; touched = {}
    today = datetime.now(IST).date()
    last_box_date = today
    msg = "✨ Option Bond 💥 V12 BOX READY ✨\n━━━━━━━━━━━━━━━━\n⏰ 9:15 - 9:30 BOX VERIFIED ✅\n"
    for name, sym in SYMBOLS.items():
        bh = None; bl = None
        for attempt in range(3):
            try:
                df = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
                df = clean_df(df)
                df = df[df['Dt'].dt.date == today]
                box_candle = df[(df['Dt'].dt.hour == 9) & (df['Dt'].dt.minute == 15)]
                if box_candle.empty:
                    box_candle = df.iloc[[0]]
                bh = float(box_candle["High"].iloc[0])
                bl = float(box_candle["Low"].iloc[0])
                break
            except Exception as e:
                print(name, f"Box Try {attempt+1} Fail", e)
                time.sleep(2)
        if bh is not None and bl is not None:
            box_data[name] = (bh, bl)
            touched[name] = False
            msg += f"📊 {name} BOX [15m]: {bl:.0f} - {bh:.0f}\n"
            print(name, "BOX 15m", bl, bh)
        else:
            msg += f"📊 {name} BOX: ❌ FAIL - Data nahi mila, 1 min me phir try hoga\n"
            print(name, "BOX FAIL")
    msg += "━━━━━━━━━━━━━━━━\n👑 V12: 15m Box + 15m Trend + Liquidity Sweep + Retest + Reclaim\n📦 BOX 15m | 📈 TREND 15m | ⚡ WORK 5m\n👀 Reclaim ban raha hoga to WATCH message aayega"
    tg(msg)

def get_strike(name, entry):
    if name == "NIFTY": return int(round(entry / 50) * 50)
    else: return int(round(entry / 100) * 100)

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

def detect_sweep(df5, box_low, box_high, direction):
    if len(df5) < 5: return False
    recent = df5.tail(6)
    if direction == "CALL":
        swept = any(float(r['Low']) < box_low for _, r in recent.iterrows())
        back_inside = float(df5.iloc[-1]['Close']) > box_low
        return swept and back_inside
    else:
        swept = any(float(r['High']) > box_high for _, r in recent.iterrows())
        back_inside = float(df5.iloc[-1]['Close']) < box_high
        return swept and back_inside

def check_one(name, sym):
    if name not in box_data:
        print(f"{name} BOX nahi bana - SKIP")
        return
    try:
        box_high, box_low = box_data[name]
        today = datetime.now(IST).date()
        df15 = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
        df15 = clean_df(df15)
        df15 = df15[df15['Dt'].dt.date == today]
        if len(df15) < 5:
            print(f"{name} 15m data kam hai {len(df15)}")
            return
        df15 = calc_vwap_daily(df15)
        df15["EMA20"] = df15["Close"].ewm(span=20, adjust=False).mean()
        df15["EMA50"] = df15["Close"].ewm(span=50, adjust=False).mean()
        last15 = df15.iloc[-1]
        close15 = float(last15['Close']); vwap15 = float(last15['VWAP']); ema20_15 = float(last15['EMA20']); ema50_15 = float(last15['EMA50'])
        if close15 > vwap15 and close15 > ema20_15 and ema20_15 > ema50_15:
            trend = "UPTREND"
        elif close15 < vwap15 and close15 < ema20_15 and ema20_15 < ema50_15:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"
        print(f"{name} [15m] TREND:{trend} Close15:{close15:.0f} Box:{box_low:.0f}-{box_high:.0f}")
        df5 = yf.download(sym, period="2d", interval="5m", progress=False, auto_adjust=True)
        df5 = clean_df(df5)
        df5 = df5[df5['Dt'].dt.date == today]
        if len(df5) < 5:
            print(f"{name} 5m data kam hai {len(df5)}")
            return
        df5 = calc_vwap_daily(df5)
        df5["EMA20"] = df5["Close"].ewm(span=20, adjust=False).mean()
        df5["RSI"] = calc_rsi(df5["Close"])
        after_box = df5[df5['Dt'].dt.time >= pd.to_datetime("09:30").time()].copy()
        for _, row in after_box.iterrows():
            low = float(row['Low']); high = float(row['High'])
            v = float(row['VWAP']); e = float(row['EMA20']); c = float(row['Close'])
            tol = c * 0.0005
            if (low - tol <= v <= high + tol) and (low - tol <= e <= high + tol):
                touched[name] = True
                break
        last5 = df5.iloc[-1]
        close5 = float(last5['Close'])
        vwap5 = float(last5['VWAP']); ema5 = float(last5['EMA20']); rsi5 = float(last5['RSI'])
        candle_time = str(last5['Dt'])
        is_retest = touched[name]
        pattern, p_side = detect_pattern(df5)
        print(f"{name} [5m] Close:{close5:.0f} VWAP:{vwap5:.0f} EMA:{ema5:.0f} RSI:{rsi5:.0f} Retest:{is_retest} Pattern:{pattern} Trend:{trend}")
        if name == "NIFTY":
            t1, t2, t3, buf = "+100", "+150", "+200", 10
        else:
            t1, t2, t3, buf = "+200", "+300", "+400", 20
        if box_low <= close5 <= box_high:
            went_below = False
            went_above = False
            if len(after_box) > 0:
                went_below = float(after_box['Low'].min()) < box_low
                went_above = float(after_box['High'].max()) > box_high
            print(f"{name} INSIDE BOX - WentBelow:{went_below} WentAbove:{went_above}")
            if went_below or went_above:
                now_hm = datetime.now(IST).strftime("%H")
                watch_key = f"{today}_{name}_WATCH_{now_hm}_{'CALL' if went_below else 'PUT'}"
                if watch_key not in watch_sent:
                    if went_below:
                        cond = f"VWAP:{'✅' if close5>vwap5 else '❌'} EMA:{'✅' if close5>ema5 else '❌'} RSI:{rsi5:.0f} {'✅' if rsi5>50 else '❌'}"
                        wmsg = f"👀 RECLAIM WATCH - {name}\n━━━━━━━━━━━━━━━━\n📦 BOX: {box_low:.0f} - {box_high:.0f}\n📍 Abhi Price: {close5:.0f} - BOX ke ANDAR\n🔽 Neeche gaya tha, wapas andar aaya ✅\n📈 TREND [15m]: {trend}\n📊 {cond}\n⏳ Confirm hote hi CALL Trade aayega - Ready raho Khan Sahab\n━━━━━━━━━━━━━━━━"
                    else:
                        cond = f"VWAP:{'✅' if close5<vwap5 else '❌'} EMA:{'✅' if close5<ema5 else '❌'} RSI:{rsi5:.0f} {'✅' if rsi5<50 else '❌'}"
                        wmsg = f"👀 RECLAIM WATCH - {name}\n━━━━━━━━━━━━━━━━\n📦 BOX: {box_low:.0f} - {box_high:.0f}\n📍 Abhi Price: {close5:.0f} - BOX ke ANDAR\n🔼 Upar gaya tha, wapas andar aaya ✅\n📉 TREND [15m]: {trend}\n📊 {cond}\n⏳ Confirm hote hi PUT Trade aayega - Ready raho Khan Sahab\n━━━━━━━━━━━━━━━━"
                    tg(wmsg); watch_sent[watch_key] = True
            allow_call_reclaim = True if name == "SENSEX" else (trend != "DOWNTREND")
            allow_put_reclaim = True if name == "SENSEX" else (trend != "UPTREND")
            if went_below and close5 > vwap5 and close5 > ema5 and rsi5 > 50 and allow_call_reclaim:
                sweep_r = detect_sweep(df5, box_low, box_high, "CALL")
                pattern_ok_r = (pattern is not None and p_side == "Bullish")
                key = f"{today}_{name}_RECLAIM_CALL_{candle_time}"
                if key not in already_sent:
                    strike = get_strike(name, close5)
                    sl = int(box_low - buf)
                    pat_txt = f"🕯️ {pattern} BONUS ✅" if pattern_ok_r else "🕯️ Pattern - No Bonus"
                    msg = f"👑 PRO KOHINOOR - RECLAIM 👑\n✨ Option Bond 💥 V12 ✨\n━━━━━━━━━━━━━━━━\n📊 {name} - CALL\n📦 15m BOX: {box_low:.0f} - {box_high:.0f}\n📈 TREND [15m]: {trend}\n🧹 Liquidity Sweep: {'✅' if sweep_r else '❌'} - Neeche gaya, wapas andar aaya\n{pat_txt}\n📍 VWAP [5m]: {vwap5:.0f} - UPAR ✅\n📍 20 EMA [5m]: {ema5:.0f} - UPAR ✅\n📈 RSI [5m]: {rsi5:.0f} - 50 se Upar ✅\n━━━━━━━━━━━━━━━━\n💰 Entry {strike}-CE\n🛑 SL: {sl}\n📦 Qty: HALF LOT\n✅ Verify Buy Khan Sahab\n🎯 Target {t1} - HALF LOT\n━━━━━━━━━━━━━━━━"
                    tg(msg); already_sent.add(key)
                return
            if went_above and close5 < vwap5 and close5 < ema5 and rsi5 < 50 and allow_put_reclaim:
                sweep_r = detect_sweep(df5, box_low, box_high, "PUT")
                pattern_ok_r = (pattern is not None and p_side == "Bearish")
                key = f"{today}_{name}_RECLAIM_PUT_{candle_time}"
                if key not in already_sent:
                    strike = get_strike(name, close5)
                    sl = int(box_high + buf)
                    pat_txt = f"🕯️ {pattern} BONUS ✅" if pattern_ok_r else "🕯️ Pattern - No Bonus"
                    msg = f"👑 PRO KOHINOOR - RECLAIM 👑\n✨ Option Bond 💥 V12 ✨\n━━━━━━━━━━━━━━━━\n📊 {name} - PUT\n📦 15m BOX: {box_low:.0f} - {box_high:.0f}\n📉 TREND [15m]: {trend}\n🧹 Liquidity Sweep: {'✅' if sweep_r else '❌'} - Upar gaya, wapas andar aaya\n{pat_txt}\n📍 VWAP [5m]: {vwap5:.0f} - NEECHE ✅\n📍 20 EMA [5m]: {ema5:.0f} - NEECHE ✅\n📈 RSI [5m]: {rsi5:.0f} - 50 se Neeche ✅\n━━━━━━━━━━━━━━━━\n💰 Entry {strike}-PE\n🛑 SL: {sl}\n📦 Qty: HALF LOT\n✅ Verify Buy Khan Sahab\n🎯 Target {t1} - HALF LOT\n━━━━━━━━━━━━━━━━"
                    tg(msg); already_sent.add(key)
                return
            print(f"{name} BOX ke ANDAR hai - NO SIGNAL (No Reclaim)")
            return
        if close5 > box_high and close5 > vwap5 and close5 > ema5:
            sweep = detect_sweep(df5, box_low, box_high, "CALL")
            pattern_ok = (pattern is not None and p_side == "Bullish")
            trend_point = 1 if (trend == "UPTREND" or (name == "SENSEX" and trend == "SIDEWAYS")) else 0
            if trend == "DOWNTREND":
                print(f"{name} CALL Block - Trend DOWNTREND"); return
            score = trend_point + int(sweep) + int(is_retest or pattern_ok)
            if score == 3:
                level = "👑👑👑 3 PRO 👑👑👑"; qty = "FULL LOT ✅"; target_line = f"🎯 Target {t1} / {t2} / {t3} - FULL LOT\n🧹 Sweep ✅ + Trend ✅ + Retest/Pattern ✅"; tag = "PRO3"
            elif score == 2:
                level = "👑👑 2 PLATINUM 👑👑"; qty = "HALF LOT"; target_line = f"🎯 Target {t1} - HALF LOT\n🧹 Sweep:{sweep} | Trend:{trend}"; tag = "PLAT2"
            else:
                print(f"{name} CALL Score {score}/3 - NO TRADE V12"); return
            key = f"{today}_{name}_CALL_{tag}_{candle_time}"
            if key not in already_sent:
                strike = get_strike(name, close5)
                sl = int(box_low - buf)
                pat_txt = f"🕯️ {pattern} BONUS ✅" if pattern_ok else "🕯️ Pattern - No Bonus"
                msg = f"{level}\n✨ Option Bond 💥 V12 ✨\n━━━━━━━━━━━━━━━━\n📊 {name} - CALL\n📦 15m BOX: {box_low:.0f} - {box_high:.0f}\n📈 TREND [15m]: {trend} ✅\n🧹 Liquidity Sweep: {'✅' if sweep else '❌'}\n{pat_txt}\n📍 VWAP [5m]: {vwap5:.0f} - UPAR ✅\n📍 20 EMA [5m]: {ema5:.0f} - UPAR ✅\n📈 RSI [5m]: {rsi5:.0f}\n💥 Breakout [5m]: {box_high:.0f} ke UPAR ✅\n━━━━━━━━━━━━━━━━\n💰 Entry {strike}-CE\n🛑 SL: {sl}\n📦 Qty: {qty}\n✅ Verify Buy Khan Sahab\n{target_line}\n━━━━━━━━━━━━━━━━"
                tg(msg); already_sent.add(key)
        elif close5 < box_low and close5 < vwap5 and close5 < ema5:
            sweep = detect_sweep(df5, box_low, box_high, "PUT")
            pattern_ok = (pattern is not None and p_side == "Bearish")
            trend_point = 1 if (trend == "DOWNTREND" or (name == "SENSEX" and trend == "SIDEWAYS")) else 0
            if trend == "UPTREND":
                print(f"{name} PUT Block - Trend UPTREND"); return
            score = trend_point + int(sweep) + int(is_retest or pattern_ok)
            if score == 3:
                level = "👑👑👑 3 PRO 👑👑👑"; qty = "FULL LOT ✅"; target_line = f"🎯 Target {t1} / {t2} / {t3} - FULL LOT\n🧹 Sweep ✅ + Trend ✅ + Retest/Pattern ✅"; tag = "PRO3"
            elif score == 2:
                level = "👑👑 2 PLATINUM 👑👑"; qty = "HALF LOT"; target_line = f"🎯 Target {t1} - HALF LOT\n🧹 Sweep:{sweep} | Trend:{trend}"; tag = "PLAT2"
            else:
                print(f"{name} PUT Score {score}/3 - NO TRADE V12"); return
            key = f"{today}_{name}_PUT_{tag}_{candle_time}"
            if key not in already_sent:
                strike = get_strike(name, close5)
                sl = int(box_high + buf)
                pat_txt = f"🕯️ {pattern} BONUS ✅" if pattern_ok else "🕯️ Pattern - No Bonus"
                msg = f"{level}\n✨ Option Bond 💥 V12 ✨\n━━━━━━━━━━━━━━━━\n📊 {name} - PUT\n📦 15m BOX: {box_low:.0f} - {box_high:.0f}\n📉 TREND [15m]: {trend} ✅\n🧹 Liquidity Sweep: {'✅' if sweep else '❌'}\n{pat_txt}\n📍 VWAP [5m]: {vwap5:.0f} - NEECHE ✅\n📍 20 EMA [5m]: {ema5:.0f} - NEECHE ✅\n📈 RSI [5m]: {rsi5:.0f}\n💥 Breakout [5m]: {box_low:.0f} ke NEECHE ✅\n━━━━━━━━━━━━━━━━\n💰 Entry {strike}-PE\n🛑 SL: {sl}\n📦 Qty: {qty}\n✅ Verify Buy Khan Sahab\n{target_line}\n━━━━━━━━━━━━━━━━"
                tg(msg); already_sent.add(key)
    except Exception as e: print(name, "check fail", e)

tg("✨ Option Bond 💥 V12 BOT ON ✨\n━━━━━━━━━━━━━━━━\n✅ Khan Sahab V12 Ready Hai\n📦 NIFTY + SENSEX ONLY\n📦 BOX 15m MUST\n📈 TREND 15m MUST\n🧹 LIQUIDITY SWEEP MUST\n⚡ WORK 5m MUST\n👑 3 PRO = FULL LOT | 👑 2 PLATINUM = HALF LOT\n🔄 RECLAIM = HALF LOT - Neeche gaya wapas andar / Upar gaya wapas andar\n👀 RECLAIM WATCH = Har ghante 1 baar, ban raha hai to pehle se pata chalega\n❌ BOX ke ANDAR bina Reclaim ke koi signal nahi")
print("BOT STARTED", datetime.now(IST))
start_time = time.time()
while True:
    now = datetime.now(IST)
    is_trading_day = (now.weekday() < 5)
    if is_trading_day and ((now.hour == 9 and now.minute >= 15) or (now.hour > 9 and now.hour < 15) or (now.hour == 15 and now.minute <= 15)):
        if last_box_date != now.date():
            build_box(); system_built = True
    is_market = is_trading_day and ((now.hour == 9 and now.minute >= 30) or (now.hour > 9 and now.hour < 15) or (now.hour == 15 and now.minute <= 15))
    if is_market and system_built:
        for name, sym in SYMBOLS.items():
            check_one(name, sym); time.sleep(1)
    if is_trading_day and now.hour == 15 and now.minute >= 15 and not exit_sent:
        tg("✨ Option Bond 💥 EXIT ✨\n━━━━━━━━━━━━━━━━\n⏰ 3:15 HO GAYA Khan Sahab\n❌ Trade Kaat Do\n━━━━━━━━━━━━━━━━")
        exit_sent = True; break
    if time.time() - start_time > 20000: break
    time.sleep(60)
