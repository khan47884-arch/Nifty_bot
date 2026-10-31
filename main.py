import yfinance as yf
import requests
import yaml
from datetime import datetime

with open('option.yml','r') as f:
    cfg = yaml.safe_load(f)

def send_tg(pattern, rsi, strike, sl, tgt1, tgt2):
    token = cfg['telegram']['bot_token']
    chat_id = cfg['telegram']['chat_id']
    now = datetime.now().strftime("%d-%m %H:%M")
    msg = f"""🎩 OPTION BOND - NIFTY [5M/15M]
📅 {now}
📊 {pattern} VERIFY (5M)
📈 RSI: {rsi}
🎯 STRIKE: {strike} CE
🛑 SL: {sl} pts
🎯 TGT: {tgt1} pts (1:2) | {tgt2} pts
👉 {strike} CE BUY - Pakka Bond"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def check_patterns(df_5m):
    last = df_5m.iloc[-1]
    prev = df_5m.iloc[-2]
    body = abs(float(last['Close']) - float(last['Open']))
    wick_low = float(min(last['Close'], last['Open']) - last['Low'])
    is_Pin = wick_low > body * 2 and float(last['Close']) > float(last['Open'])
    is_Engulf = float(prev['Close']) < float(prev['Open']) and float(last['Close']) > float(last['Open'])
    is_W = float(df_5m['Low'].iloc[-2]) == float(df_5m['Low'].min()) and float(last['Close']) > float(prev['High'])
    if is_W: return "W PATTERN"
    if is_Pin: return "BULLISH PIN BAR"
    if is_Engulf: return "BULLISH ENGULFING"
    return None

def get_15m_trend():
    data_15 = yf.download("^NSEI", interval="15m", period="5d", auto_adjust=True)
    close = data_15['Close']
    ema20 = close.ewm(span=20).mean().iloc[-1]
    delta = close.diff()
    gain = delta.where(delta > 0, 0).ewm(com=13).mean()
    loss = -delta.where(delta < 0, 0).ewm(com=13).mean()
    rsi_series = 100 - (100 / (1 + gain / loss.replace(0, 0.01)))
    return float(close.iloc[-1]) > float(ema20) and int(float(rsi_series.iloc[-1])) > 52, int(float(rsi_series.iloc[-1]))

def run():
    df_5m = yf.download("^NSEI", interval="5m", period="1d", auto_adjust=True).tail(15)
    df_5m.columns = [c[0] if isinstance(c, tuple) else c for c in df_5m.columns]
    pattern = check_patterns(df_5m)
    trend_up, rsi_val = get_15m_trend()
    if pattern and trend_up:
        index_price = int(float(df_5m['Close'].iloc[-1]))
        strike = round(index_price / 50) * 50
        send_tg(pattern, rsi_val, strike, 30, 60, 90)


        return float(close.iloc[-1]) > float(ema20.iloc[-1]) and int(float(rsi_series.iloc[-1])) > 52, int(float(rsi_series.iloc[-1]))
