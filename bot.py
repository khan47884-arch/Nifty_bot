import yfinance as yf, pytz, requests, os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

BOT = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")

def tg(m):
    try:
        ist = pytz.timezone('Asia/Kolkata')
        s = datetime.now(ist).strftime("%d-%b %I:%M %p IST")
        requests.post(
            f"https://api.telegram.org/bot{BOT}/sendMessage",
            data={"chat_id": CHAT, "text": f"{m}\n\nSTAMP:{s}\nV1.0 MOMENTUM"},
            timeout=30
        )
    except:
        pass

STOCKS = ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","M&M.NS","TATAMOTORS.NS","TITAN.NS","RELIANCE.NS","INFY.NS","TCS.NS","LT.NS","AXISBANK.NS","KOTAKBANK.NS","BAJFINANCE.NS","MARUTI.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","TVSMOTOR.NS","ULTRACEMCO.NS","GRASIM.NS","ASIANPAINT.NS","SUNPHARMA.NS","CIPLA.NS","DIVISLAB.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","ONGC.NS","NTPC.NS","POWERGRID.NS","TATAPOWER.NS","COALINDIA.NS","BEL.NS","HAL.NS","DLF.NS","GODREJPROP.NS","TRENT.NS","DMART.NS","ZOMATO.NS","PAYTM.NS","INDIGO.NS","VEDL.NS","BPCL.NS","IOC.NS","GAIL.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS","LTIM.NS","SBILIFE.NS","HDFCLIFE.NS"]

def chk(s):
    try:
        df = yf.download(s, period="6mo", interval="1d", progress=False, auto_adjust=True)
        if len(df) < 60:
            return None
        df.columns = [x[0] if isinstance(x, tuple) else x for x in df.columns]
        c = df['Close'].iloc[-1]
        vol = df['Volume'].iloc[-1]
        if (c * vol) < 50000000:
            return None
        ema10 = df['Close'].ewm(span=10).mean().iloc[-1]
        ema20 = df['Close'].ewm(span=20).mean().iloc[-1]
        ema50 = df['Close'].ewm(span=50).mean().iloc[-1]
        if not (c > ema10 > ema20 > ema50):
            return None
        delta = df['Close'].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain.iloc[-1] / max(loss.iloc[-1], 0.01)
        rsi = 100 - (100 / (1 + rs))
        if rsi < 50 or rsi > 68:
            return None
        tr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        atr_pct = (tr / c) * 100
        if atr_pct < 1.0 or atr_pct > 3.5:
            return None
        high5 = df['High'].iloc[-6:-1].max()
        dist_high = ((high5 - c) / high5) * 100
        if dist_high > 1.5:
            return None
        va = df['Volume'].iloc[-20:-1].mean()
        vol_x = vol / max(va, 1)
        if vol_x < 1.2:
            return None
        box_low = df['Low'].iloc[-21:-1].min()
        box_high = df['High'].iloc[-21:-1].max()
        if c <= box_high:
            return None
        score = 0
        if rsi >= 55 and rsi <= 65: score += 3
        if vol_x > 1.8: score += 3
        elif vol_x > 1.5: score += 2
        if atr_pct >= 1.5 and atr_pct <= 2.5: score += 2
        if dist_high < 0.5: score += 2
        if score < 6:
            return None
        sl = box_low * 0.98
        risk = c - sl
        t1 = c + risk * 2
        t2 = c + risk * 3.5
        qty = int(25000 / c)
        if qty < 1: qty = 1
        return {"symbol": s.replace(".NS",""), "c": c, "rsi": rsi, "atr": atr_pct, "score": score, "vol_x": vol_x, "sl": sl, "t1": t1, "t2": t2, "qty": qty, "box_low": box_low, "box_high": box_high}
    except:
        return None

with ThreadPoolExecutor(max_workers=8) as ex:
    res = [x for x in ex.map(chk, STOCKS) if x]

res.sort(key=lambda x: x["score"], reverse=True)

if not res:
    tg("👑👑 Khan Sahab/Kohinoor 👑👑\n___________________________\n\n📦 DAILY BREAKOUT - NO SETUP\n\nAaj koi Momentum setup nahi, paisa bach gaya.\nKal 3:30 pe fir scan hoga.")
else:
    top = res[0]
    msg1 = f"""👑👑 Khan Sahab/Kohinoor 👑👑
___________________________

🔥 KAL KA SECTOR - NAZAR RAKHO

No.1 Sector: {top['symbol']} wala Sector - Aaj sabse tez bhaga
Nazar Rakhne Wale Sher:
1. {top['symbol']} - 5 Din High ke paas hai
2. Baaki sher kal ke scan me aayenge

Baaki sector me kal haath mat lagana"""
    msg2 = f"""👑👑 Khan Sahab/Kohinoor 👑👑
___________________________

📦 DAILY BREAKOUT - CONFIRM

🟢 STOCK - {top['symbol']}

📊 Daily Trend: UP
📊 RSI: {top['rsi']:.0f} - Momentum Strong
✅ EMA 10 > 20 > 50 Verify - Candle EMA ke UPAR CLOSE
✅ VWAP se UPAR - Buyer Full Control
🕯️ Candle: Strong Bull Candle
📐 Pattern: Move + Consolidation + Breakout
💥 Box {top['box_low']:.0f}-{top['box_high']:.0f} me Consolidation + Box Tod ke UPAR Breakout
📊 Volume OK ✅ x{top['vol_x']:.1f}

💰 Entry: {top['c']:.0f}
🛑 SL: {top['sl']:.0f}
🎯 Target 1: {top['t1']:.0f} - 2-3 Din me
🎯 Target 2: {top['t2']:.0f} - 4-5 Din me
⏰ TIME STOP: 3 Din me Target 1 na aaye to EXIT
📦 Qty: {top['qty']} Share (25k)
🔥 Score: {top['score']}/10"""
    tg(msg1)
    tg(msg2)
