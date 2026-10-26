import yfinance as yf
import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def is_strong_candle(c):
    body = abs(float(c['Close']) - float(c['Open']))
    rng = float(c['High']) - float(c['Low'])
    return (body / rng) > 0.6 if rng != 0 else False

def check_stock(name, data_5m, data_daily):
    if data_5m.empty or data_daily.empty:
        return None
    last_candle = data_5m.iloc[-1]
    last_20_vol_avg = data_5m['Volume'].iloc[-21:-1].mean()
    curr_vol = float(last_candle['Volume'])
    if curr_vol < (last_20_vol_avg * 1.5):
        return None
    last_2_days = data_daily.iloc[-3:-1]
    support = float(last_2_days['Low'].min())
    resistance = float(last_2_days['High'].max())
    curr_close = float(last_candle['Close'])
    is_bullish = float(last_candle['Close']) > float(last_candle['Open'])
    is_bearish = float(last_candle['Close']) < float(last_candle['Open'])
    strong = is_strong_candle(last_candle)
    if curr_close > support and (float(last_candle['Low']) <= support * 1.003) and is_bullish and strong:
        return f"✅ *{name} SUPPORT BOUNCE + REAL VOLUME* ✅\nSupport: {support:.2f}\nCurrent: {curr_close:.2f}\nVolume: {curr_vol:.0f} (1.5x)"
    if curr_close < resistance and (float(last_candle['High']) >= resistance * 0.997) and is_bearish and strong:
        return f"🔴 *{name} RESISTANCE REJECT + REAL VOLUME* 🔴\nResistance: {resistance:.2f}\nCurrent: {curr_close:.2f}\nVolume: {curr_vol:.0f} (1.5x)"
    if curr_close > resistance and is_bullish and strong:
        return f"🚀 *{name} BREAKOUT + VOLUME* 🚀\n{resistance:.2f} -> {curr_close:.2f}"
    if curr_close < support and is_bearish and strong:
        return f"💥 *{name} BREAKDOWN + VOLUME* 💥\n{support:.2f} -> {curr_close:.2f}"
    return None

nifty_5m = yf.download("^NSEI", period="5d", interval="5m", progress=False)
nifty_daily = yf.download("^NSEI", period="10d", interval="1d", progress=False)
sensex_5m = yf.download("^BSESN", period="5d", interval="5m", progress=False)
sensex_daily = yf.download("^BSESN", period="10d", interval="1d", progress=False)

signals = []
for s in [check_stock("NIFTY", nifty_5m, nifty_daily), check_stock("SENSEX", sensex_5m, sensex_daily)]:
    if s:
        signals.append(s)

if signals:
    send_telegram("\n\n".join(signals))
