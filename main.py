import yfinance as yf, requests, yaml
from datetime import datetime
import pytz

with open('option.yml','r') as f:
    cfg = yaml.safe_load(f)

def send_tg(pattern, rsi5, strike, sl, t1, t2, t3, tag, volx, vwap_ok):
    token = cfg['telegram']['bot_token']
    chat_id = cfg['telegram']['chat_id']
    now = datetime.now().strftime("%d-%m %H:%M")
    vwap_txt = "VWAP UP ✅" if vwap_ok else "VWAP DOWN ❌"
    
    if "DIAMOND" in tag:
        stamp = "💎💎💎 DIAMOND BOMB - PAKKA BOND"
        note = "👉 HOLD TILL T2/T3 - Pattern Confirm"
    else:
        stamp = "🥇 GOLD RUNNER - LAMBA JAYEGA"
        note = "👉 T1 pe 50% BOOK, Baki Trail"

    msg = f"""{stamp}
━━━━━━━━━━━━━━
📅 {now} | {pattern} (5M)
📊 15M Trend: UP ✅ | {vwap_txt}
📈 RSI 5M: {rsi5} | Vol 5M: {volx}x

🎯 STRIKE: {strike} CE

🛑 SL: {sl} pts (ATR BASED)
🎯 TGT1: {t1} pts (1:2)
🎯 TGT2: {t2} pts (1:3)
🎯 TGT3: {t3} pts (1:4) - RUNNER

{note}
━━━━━━━━━━━━━━"""

    requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                  data={"chat_id": chat_id, "text": msg}, timeout=10)

def get_15m_trend():
    d15 = yf.download("^NSEI", interval="15m", period="5d", auto_adjust=True, progress=False)
    d15.columns = [c[0] if isinstance(c, tuple) else c for c in d15.columns]
    close = d15['Close']
    ema20 = close.ewm(span=20).mean().iloc[-1]
    ema50 = close.ewm(span=50).mean().iloc[-1]
    delta = close.diff()
    rsi = 100 - (100 / (1 + delta.where(delta>0,0).ewm(alpha=1/14).mean() / -delta.where(delta<0,0).ewm(alpha=1/14).mean().replace(0,0.001)))
    return float(close.iloc[-1]) > float(ema20) > float(ema50), int(float(rsi.iloc[-1]))

def run():
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    if not (9 <= now_ist.hour <= 15):
        return
    if now_ist.hour == 9 and now_ist.minute < 35:
        return
    if now_ist.hour == 15 and now_ist.minute > 15:
        return

    df5 = yf.download("^NSEI", interval="5m", period="2d", auto_adjust=True, progress=False).tail(100)
    df5.columns = [c[0] if isinstance(c, tuple) else c for c in df5.columns]
    if len(df5) < 50:
        return

    last = df5.iloc[-1]
    prev = df5.iloc[-2]
    close = df5['Close']
    high = df5['High']
    low = df5['Low']
    vol = df5['Volume']

    typical = (high + low + close)/3
    vwap = (typical * vol).cumsum() / vol.cumsum()
    vwap_ok = float(close.iloc[-1]) > float(vwap.iloc[-1])

    tr = (high - low).combine((high - close.shift()).abs(), max).combine((low - close.shift()).abs(), max)
    atr = tr.ewm(alpha=1/14).mean().iloc[-1]
    atr = float(atr)

    ema20_5 = close.ewm(span=20).mean()
    ema50_5 = close.ewm(span=50).mean()
    ema_ok_5 = float(close.iloc[-1]) > float(ema20_5.iloc[-1]) > float(ema50_5.iloc[-1])

    delta = close.diff()
    rsi5 = 100 - (100 / (1 + delta.where(delta>0,0).ewm(alpha=1/14).mean() / -delta.where(delta<0,0).ewm(alpha=1/14).mean().replace(0,0.001)))
    rsi5_val = int(float(rsi5.iloc[-1]))

    v20 = vol.ewm(span=20).mean()
    volx = float(vol.iloc[-1])/float(v20.iloc[-1]) if float(v20.iloc[-1])>0 else 1

    body = abs(float(last['Close']) - float(last['Open']))
    wick_low = float(min(float(last['Close']), float(last['Open'])) - float(last['Low']))
    is_pin = wick_low > body*1.8 and float(last['Close']) > float(last['Open'])
    is_engulf = float(prev['Close']) < float(prev['Open']) and float(last['Close']) > float(prev['Open'])
    is_W = abs(float(df5['Low'].tail(30).iloc[-3]) - float(df5['Low'].tail(30).min())) < float(last['Close'])*0.002

    pattern = "W PATTERN" if is_W else "BULLISH PIN BAR" if is_pin else "BULLISH ENGULFING" if is_engulf else None
    trend_15, rsi15 = get_15m_trend()

    is_gold = ema_ok_5 and vwap_ok and 50 <= rsi5_val <= 70 and volx > 1.0 and trend_15
    is_diamond = pattern and ema_ok_5 and vwap_ok and volx > 1.3 and 52 <= rsi5_val <= 70 and trend_15

    if not (is_gold or is_diamond):
        return

    sl_pts = max(25, min(50, int(atr*1.2)))
    t1_pts = sl_pts*2
    t2_pts = sl_pts*3
    t3_pts = sl_pts*4

    strike = round(int(float(last['Close'])) / 50) * 50
    tag = "💎💎 DIAMOND FINAL" if is_diamond else "🥇 GOLD FINAL"
    pat = pattern if pattern else "VWAP+EMA SETUP"
    send_tg(pat, rsi5_val, strike, sl_pts, t1_pts, t2_pts, t3_pts, tag, round(volx,1), vwap_ok)

if __name__ == "__main__":
    run()
