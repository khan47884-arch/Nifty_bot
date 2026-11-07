import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime, time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SYMBOLS = [
    "RELIANCE.NS","HDFCBANK.NS","SBIN.NS","ICICIBANK.NS","TCS.NS",
    "INFY.NS","BHEL.NS","BEL.NS","TITAN.NS","ADANIENT.NS",
    "ADANIPORTS.NS","TATAMOTORS.NS","TATASTEEL.NS","BHARTIARTL.NS","M&M.NS",
    "LT.NS","BAJAJFINSV.NS","MARUTI.NS","HAL.NS","ONGC.NS",
    "BAJFINANCE.NS","NTPC.NS","POWERGRID.NS","HINDALCO.NS","VEDL.NS"
]

LOT_SIZE = {
    "RELIANCE":250, "HDFCBANK":550, "SBIN":1500, "ICICIBANK":1375, "TCS":175,
    "INFY":400, "BHEL":5250, "BEL":3150, "TITAN":375, "ADANIENT":300,
    "ADANIPORTS":1000, "TATAMOTORS":1425, "TATASTEEL":5500, "BHARTIARTL":950, "M&M":1250,
    "LT":300, "BAJAJFINSV":500, "MARUTI":75, "HAL":300, "ONGC":3850,
    "BAJFINANCE":500, "NTPC":3000, "POWERGRID":3000, "HINDALCO":2100, "VEDL":3000
}

SENT_FILE = "sent.txt"

def load_sent():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE) as f:
            return set(f.read().splitlines())
    return set()

def save_sent(key):
    with open(SENT_FILE, "a") as f:
        f.write(key + "\n")

def send_telegram(msg, key):
    sent = load_sent()
    if key in sent:
        return False
    if not BOT_TOKEN or not CHAT_ID:
        print(msg)
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        if r.status_code == 200:
            save_sent(key)
            return True
    except Exception as e:
        print("Telegram Error:", e)
    return False

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def calc_vwap(df):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    return (tp * df['Volume']).cumsum() / (df['Volume'].cumsum() + 1e-9)

def get_nifty_trend():
    try:
        df = yf.download("^NSEI", period="2d", interval="5m", progress=False, auto_adjust=False)
        if df.empty: return "NEUTRAL"
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        try:
            df['Datetime'] = df['Datetime'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        except: pass
        today = sorted(df['Datetime'].dt.date.unique())[-1]
        df = df[df['Datetime'].dt.date == today].copy()
        if len(df) < 5: return "NEUTRAL"
        df['VWAP'] = calc_vwap(df)
        last_close = float(df['Close'].iloc[-1])
        last_vwap = float(df['VWAP'].iloc[-1])
        if last_close > last_vwap: return "UP"
        if last_close < last_vwap: return "DOWN"
        return "NEUTRAL"
    except:
        return "NEUTRAL"

def check_stock(symbol, nifty_trend):
    try:
        df = yf.download(symbol, period="5d", interval="5m", progress=False, auto_adjust=False)
        if df.empty or len(df) < 30:
            return
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        try:
            df['Datetime'] = df['Datetime'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
        except: pass
        all_dates = sorted(df['Datetime'].dt.date.unique())
        today = all_dates[-1]
        today_df = df[df['Datetime'].dt.date == today].copy()
        if len(today_df) < 10 and len(all_dates) >= 2:
            today = all_dates[-2]
            today_df = df[df['Datetime'].dt.date == today].copy()
        prev_df = df[df['Datetime'].dt.date < today]
        if today_df.empty or prev_df.empty or len(today_df) < 10:
            return
        prev_close = float(prev_df['Close'].iloc[-1])
        day_open = float(today_df['Open'].iloc[0])
        gap = (day_open - prev_close) / prev_close * 100
        box_df = today_df[(today_df['Datetime'].dt.time >= time(9,15)) & (today_df['Datetime'].dt.time < time(9,30))]
        if box_df.empty: return
        box_high = float(box_df['High'].max())
        box_low = float(box_df['Low'].min())
        if box_high <= box_low: return

        today_df['EMA20'] = today_df['Close'].ewm(span=20, adjust=False).mean()
        today_df['VWAP'] = calc_vwap(today_df)
        today_df['RSI'] = calc_rsi(today_df['Close'], 14)
        today_df['VolAvg'] = today_df['Volume'].rolling(20).mean()
        after_df = today_df[today_df['Datetime'].dt.time >= time(9,30)]
        if after_df.empty or len(after_df) < 3: return
        after_df = after_df[after_df['High'] > after_df['Low']]
        if len(after_df) < 3: return

        last = after_df.iloc[-1]
        prev_candle = after_df.iloc[-2]
        close = float(last['Close'])
        prev_low = float(prev_candle['Low'])
        prev_high = float(prev_candle['High'])
        ema20 = float(last['EMA20'])
        vwap = float(last['VWAP'])
        rsi = float(last['RSI']) if not np.isnan(last['RSI']) else 50
        vol = float(last['Volume'])
        vol_avg = float(last['VolAvg']) if not np.isnan(last['VolAvg']) else vol
        last_time = str(last['Datetime'].strftime("%H:%M"))
        candle_key = str(last['Datetime'].strftime("%Y-%m-%d_%H:%M"))

        clean = symbol.replace(".NS","")
        lot = LOT_SIZE.get(clean, 0)

        vwap_dist = abs(close - vwap) / vwap * 100
        is_sideways = (vwap_dist < 0.10) and (45 <= rsi <= 55)
        if is_sideways:
            print(f"{clean} SIDEWAYS - No Trade - VWAP Dist {vwap_dist:.2f}% RSI {rsi:.0f}")
            return

        touched_call = False
        touched_put = False
        for _, row in after_df.iterrows():
            l = float(row['Low']); h = float(row['High'])
            v = float(row['VWAP']); e = float(row['EMA20']); c = float(row['Close'])
            if abs(l - v) < c*0.0005 and abs(l - e) < c*0.0005:
                touched_call = True
            if abs(h - v) < c*0.0005 and abs(h - e) < c*0.0005:
                touched_put = True

        call_break = (close - box_high) / box_high * 100
        put_break = (box_low - close) / box_low * 100
        if call_break > 0.8 or put_break > 0.8:
            return

        vol_ratio = vol / (vol_avg + 1e-9)
        min_risk = close * 0.002

        is_pro_bull = (abs(gap) >= 2.0 and vol_ratio >= 2.0 and rsi >= 65 and touched_call
                       and close > box_high and close > vwap and close > ema20
                       and nifty_trend == "UP" and call_break > 0.2)
        is_pro_bear = (abs(gap) >= 2.0 and vol_ratio >= 2.0 and rsi <= 35 and touched_put
                       and close < box_low and close < vwap and close < ema20
                       and nifty_trend == "DOWN" and put_break > 0.2)

        is_plat_bull = (vol_ratio >= 1.5 and rsi >= 60 and touched_call
                        and close > box_high and close > vwap and close > ema20
                        and nifty_trend == "UP" and call_break > 0.2)
        is_plat_bear = (vol_ratio >= 1.5 and rsi <= 40 and touched_put
                        and close < box_low and close < vwap and close < ema20
                        and nifty_trend == "DOWN" and put_break > 0.2)

        if is_pro_bull:
            sl = prev_low
            risk = close - sl
            if risk < min_risk: risk = min_risk; sl = close - risk
            t1 = close + (risk * 1)
            t2 = close + (risk * 2)
            msg = f"""👑👑 PRO PLATINUM 👑👑
🟢 FUTURE: {clean} - LONG (BUY FUTURE)
📊 GAP: {gap:.2f}% | Vol: {vol_ratio:.1f}x | RSI: {rsi:.0f}
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP: {vwap:.2f} - UPAR ✅ | 20 EMA: {ema20:.2f} - UPAR ✅
📍 NIFTY: UP ✅ | Retest ✅ | Time: {last_time}
💰 BUY FUT @ {close:.2f} | Lot: {lot}
🛑 SL {sl:.2f}
🎯 T1 {t1:.2f} - 50% BOOK ✅
🎯 T2 {t2:.2f} - Baaki | SL to Entry"""
            send_telegram(msg, f"{candle_key}_{clean}_PRO_LONG")

        elif is_pro_bear:
            sl = prev_high
            risk = sl - close
            if risk < min_risk: risk = min_risk; sl = close + risk
            t1 = close - (risk * 1)
            t2 = close - (risk * 2)
            msg = f"""👑👑 PRO PLATINUM 👑👑
🔴 FUTURE: {clean} - SHORT (SELL FUTURE)
📊 GAP: {gap:.2f}% | Vol: {vol_ratio:.1f}x | RSI: {rsi:.0f}
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP: {vwap:.2f} - NEECHE ✅ | 20 EMA: {ema20:.2f} - NEECHE ✅
📍 NIFTY: DOWN ✅ | Retest ✅ | Time: {last_time}
💰 SELL FUT @ {close:.2f} | Lot: {lot}
🛑 SL {sl:.2f}
🎯 T1 {t1:.2f} - 50% BOOK ✅
🎯 T2 {t2:.2f} - Baaki | SL to Entry"""
            send_telegram(msg, f"{candle_key}_{clean}_PRO_SHORT")

        elif is_plat_bull:
            sl = prev_low
            risk = close - sl
            if risk < min_risk: risk = min_risk; sl = close - risk
            t1 = close + (risk * 1)
            t2 = close + (risk * 2)
            msg = f"""💎 PLATINUM 💎
🟢 FUTURE: {clean} - LONG (BUY FUTURE)
📊 GAP: {gap:.2f}% | Vol: {vol_ratio:.1f}x | RSI: {rsi:.0f}
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP: {vwap:.2f} - UPAR ✅ | 20 EMA: {ema20:.2f} - UPAR ✅
📍 NIFTY: UP ✅ | Retest ✅ | Time: {last_time}
💰 BUY FUT @ {close:.2f} | Lot: {lot}
🛑 SL {sl:.2f}
🎯 T1 {t1:.2f} - 50% BOOK ✅
🎯 T2 {t2:.2f} - Baaki | SL to Entry"""
            send_telegram(msg, f"{candle_key}_{clean}_PLAT_LONG")

        elif is_plat_bear:
            sl = prev_high
            risk = sl - close
            if risk < min_risk: risk = min_risk; sl = close + risk
            t1 = close - (risk * 1)
            t2 = close - (risk * 2)
            msg = f"""💎 PLATINUM 💎
🔴 FUTURE: {clean} - SHORT (SELL FUTURE)
📊 GAP: {gap:.2f}% | Vol: {vol_ratio:.1f}x | RSI: {rsi:.0f}
📦 BOX: {box_low:.2f} - {box_high:.2f}
📍 VWAP: {vwap:.2f} - NEECHE ✅ | 20 EMA: {ema20:.2f} - NEECHE ✅
📍 NIFTY: DOWN ✅ | Retest ✅ | Time: {last_time}
💰 SELL FUT @ {close:.2f} | Lot: {lot}
🛑 SL {sl:.2f}
🎯 T1 {t1:.2f} - 50% BOOK ✅
🎯 T2 {t2:.2f} - Baaki | SL to Entry"""
            send_telegram(msg, f"{candle_key}_{clean}_PLAT_SHORT")

    except Exception as e:
        print(f"Error {symbol}: {e}")

if __name__ == "__main__":
    print("Khan Future V2 Started -", datetime.now())
    nifty = get_nifty_trend()
    print("NIFTY Trend:", nifty)
    for sym in SYMBOLS:
        check_stock(sym, nifty)
    print("Done")
