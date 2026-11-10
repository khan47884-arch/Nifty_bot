import yfinance as yf
import pandas as pd
import numpy as np
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
LOT = {"NIFTY": 65, "SENSEX": 20}
already_sent = set()
daily_trades = []
exit_sent = False
def clean_df(df):
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()
    df['Dt'] = pd.to_datetime(df.iloc[:,0])
    try: df['Dt'] = df['Dt'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    except: pass
    return df
def calc_vwap(df):
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    return (tp * df['Volume']).cumsum() / df['Volume'].cumsum()
def calc_supertrend(df, period=10, mult=3):
    df = df.copy()
    df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(abs(df['High'] - df['Close'].shift(1)), abs(df['Low'] - df['Close'].shift(1))))
    df['ATR'] = df['TR'].rolling(window=period).mean()
    df['BU'] = (df['High'] + df['Low']) / 2 + (mult * df['ATR'])
    df['BL'] = (df['High'] + df['Low']) / 2 - (mult * df['ATR'])
    fu = [0]*len(df); fl = [0]*len(df); tr = [1]*len(df)
    for i in range(1, len(df)):
        fu[i] = df['BU'].iloc[i] if df['Close'].iloc[i-1] > fu[i-1] or fu[i-1]==0 else min(df['BU'].iloc[i], fu[i-1])
        fl[i] = df['BL'].iloc[i] if df['Close'].iloc[i-1] < fl[i-1] or fl[i-1]==0 else max(df['BL'].iloc[i], fl[i-1])
        if tr[i-1]==1 and df['Close'].iloc[i] < fl[i]: tr[i] = -1
        elif tr[i-1]==-1 and df['Close'].iloc[i] > fu[i]: tr[i] = 1
        else: tr[i] = tr[i-1]
    return tr
def get_15m_levels(sym):
    try:
        today = datetime.now(IST).date()
        df15 = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
        df15 = clean_df(df15); df15 = df15[df15['Dt'].dt.date==today]
        if len(df15) < 1: return None, None
        first = df15.iloc[0]
        return float(first['High']), float(first['Low'])
    except Exception as e:
        print("15m Level Fail", e)
        return None, None
def get_strike(name, entry):
    return int(round(entry/50)*50) if name=="NIFTY" else int(round(entry/100)*100)
def check_one(name, sym):
    try:
        high15, low15 = get_15m_levels(sym)
        if high15 is None: return
        today = datetime.now(IST).date()
        df5 = yf.download(sym, period="2d", interval="5m", progress=False, auto_adjust=True)
        df5 = clean_df(df5); df5 = df5[df5['Dt'].dt.date==today]
        if len(df5) < 30: return
        df5["VWAP"] = calc_vwap(df5)
        df5["AvgVol"] = df5["Volume"].rolling(window=20).mean()
        st = calc_supertrend(df5)
        curr = df5.iloc[-1]; prev_c = df5.iloc[-2]
        last_price = float(curr['Close']); prev_price = float(prev_c['Close'])
        vwap = float(curr['VWAP']); vol_now = float(curr['Volume']); vol_avg = float(curr['AvgVol'])
        vol_strong = vol_now > vol_avg * 1.5
        st_now = st[-1]
        call_break_high = prev_price <= high15 and last_price > high15
        call_reclaim_low = prev_price < low15 and last_price > low15
        call_cond = (call_break_high or call_reclaim_low) and last_price > vwap and vol_strong and st_now == 1
        put_break_low = prev_price >= low15 and last_price < low15
        put_reject_high = prev_price > high15 and last_price < high15
        put_cond = (put_break_low or put_reject_high) and last_price < vwap and vol_strong and st_now == -1
        if call_cond:
            key = f"{today}_{name}_CALL_{str(curr['Dt'])}"
            if key not in already_sent:
                strike = get_strike(name, last_price)
                sl = int(low15 if call_reclaim_low else high15)
                tgt_pts = 100 if name=="NIFTY" else 200
                target = int(last_price + tgt_pts); profit_rs = tgt_pts * LOT[name]
                reason = "High Tod ke UPAR" if call_break_high else "Low se UPAR"
                msg = f"👑 CALL - V16 BEST 👑\n📊 {name} - CALL\n📈 15m Level: High {high15:.0f} / Low {low15:.0f}\n💥 {reason} ✅\n📊 VWAP {vwap:.0f} ke UPAR ✅\n📊 Volume TEZ ✅\n🟢 Supertrend GREEN ✅\n💰 Entry {strike}-CE @ {last_price:.0f}\n🛑 SL: {sl}\n🎯 Target: {target} (+{tgt_pts} pts = +Rs {profit_rs})"
                tg(msg); already_sent.add(key); daily_trades.append([name,"CALL",last_price,sl,target,tgt_pts,profit_rs]); return
        if put_cond:
            key = f"{today}_{name}_PUT_{str(curr['Dt'])}"
            if key not in already_sent:
                strike = get_strike(name, last_price)
                sl = int(high15 if put_reject_high else low15)
                tgt_pts = 100 if name=="NIFTY" else 200
                target = int(last_price - tgt_pts); profit_rs = tgt_pts * LOT[name]
                reason = "Low Tod ke NEECHE" if put_break_low else "High se NEECHE"
                msg = f"👑 PUT - V16 BEST 👑\n📊 {name} - PUT\n📉 15m Level: High {high15:.0f} / Low {low15:.0f}\n💥 {reason} ✅\n📊 VWAP {vwap:.0f} ke NEECHE ✅\n📊 Volume TEZ ✅\n🔴 Supertrend RED ✅\n💰 Entry {strike}-PE @ {last_price:.0f}\n🛑 SL: {sl}\n🎯 Target: {target} (-{tgt_pts} pts = +Rs {profit_rs})"
                tg(msg); already_sent.add(key); daily_trades.append([name,"PUT",last_price,sl,target,tgt_pts,profit_rs]); return
    except Exception as e: print(name, e)
def send_daily_report():
    n_pts=0; s_pts=0; tot=0; lines=""
    for t in daily_trades:
        name,typ,entry,sl,target,pts,rs=t
        if name=="NIFTY": n_pts+=pts
        else: s_pts+=pts
        tot+=rs; lines+=f"{name} {typ}: +{pts} pts x {LOT[name]} = +Rs {rs}\n"
    if not lines: lines="Aaj koi Trade nahi bana - NO TRADE\n"
    tg(f"📊 V16 DAILY REPORT - BEST 📊\n━━━━━━━━━━━━━━━━\n{lines}━━━━━━━━━━━━━━━━\nNIFTY Net: +{n_pts} pts\nSENSEX Net: +{s_pts} pts\nTOTAL: +Rs {tot} (1 Lot Each)")
tg("✨ Option Bond 💥 V16 BEST BOT ON ✨\n━━━━━━━━━━━━━━━━\n✅ FINAL LOCK V16\n📦 15m Level (9:15 High/Low) + 5m Trade\n📊 VWAP + Volume + Supertrend Only")
print("BOT V16 BEST STARTED", datetime.now(IST))
start_time=time.time()
while True:
    now=datetime.now(IST); is_day=(now.weekday()<5)
    is_market=is_day and ((now.hour==9 and now.minute>=30) or (now.hour>9 and now.hour<15) or (now.hour==15 and now.minute<=15))
    if is_market:
        for name,sym in SYMBOLS.items():
            check_one(name,sym); time.sleep(1)
    if is_day and now.hour==15 and now.minute>=15 and not exit_sent:
        send_daily_report(); tg("✨ Option Bond 💥 EXIT ✨\n━━━━━━━━━━━━━━━━\n⏰ 3:15 HO GAYA\n❌ Trade Kaat Do"); exit_sent=True; break
    if time.time()-start_time>30000: break
    time.sleep(60)
