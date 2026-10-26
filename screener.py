import yfinance as yf
import requests, os, time, datetime

if datetime.datetime.now().hour < 10:
    print("Market time hai, screener abhi nahi chalega")
    exit()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        for i in range(0, len(msg), 3500):
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg[i:i+3500]}, timeout=15)
            time.sleep(1)
    except: pass

STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","TITAN.NS","BAJFINANCE.NS","MARUTI.NS","TATAMOTORS.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","ADANIENT.NS","POLYCAB.NS","PERSISTENT.NS","KPITTECH.NS","HAL.NS","BEL.NS","MAZDOCK.NS","RVNL.NS","IRFC.NS","SJVN.NS","NHPC.NS","TATAPOWER.NS","SUZLON.NS","JIOFIN.NS","CDSL.NS","BSE.NS","ANGELONE.NS","MCX.NS","IEX.NS","ZOMATO.NS","DIXON.NS","CGPOWER.NS","BHEL.NS","COALINDIA.NS","NTPC.NS","ONGC.NS","VEDL.NS","DLF.NS","MANKIND.NS","LUPIN.NS","CIPLA.NS","SUNPHARMA.NS","DIVISLAB.NS","CUMMINSIND.NS","ASHOKLEY.NS"]

def is_bullish_hammer(row):
    o,h,l,c = float(row['Open']),float(row['High']),float(row['Low']),float(row['Close'])
    body = abs(c-o); rng = h-l; lower = min(o,c)-l
    if rng==0: return False
    return (lower >= body*2) and (c>o) and (body/rng < 0.4)

def is_bullish_engulfing(curr, prev):
    return (float(prev['Close'])<float(prev['Open']) and float(curr['Close'])>float(curr['Open']) and float(curr['Open'])<float(prev['Close']) and float(curr['Close'])>float(prev['Open']))

def scan(df):
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
    if len(df) < 210: return None
    cross_days = 0
    for i in range(1, 21):
        if df['EMA50'].iloc[-i-1] < df['EMA200'].iloc[-i-1] and df['EMA50'].iloc[-i] > df['EMA200'].iloc[-i]:
            cross_days = i
            break
    if cross_days == 0: return None
    curr = df.iloc[-1]; prev = df.iloc[-2]
    price = float(curr['Close']); ema50 = float(curr['EMA50']); ema200 = float(curr['EMA200'])
    low_10 = float(df['Low'].iloc[-10:].min())
    if abs(price - ema50) / ema50 > 0.04: return None
    hammer = is_bullish_hammer(curr)
    engulf = is_bullish_engulfing(curr, prev)
    body = abs(float(curr['Close'])-float(curr['Open']))
    rng = float(curr['High'])-float(curr['Low'])
    strong = (rng>0 and body/rng>0.6 and float(curr['Close'])>float(curr['Open']))
    if not (hammer or engulf or strong): return None
    sl_base = min(low_10, ema200)
    sl = sl_base * 0.98
    sl_percent = ((price - sl) / price) * 100
    if sl_percent > 8: return None
    t1 = price * 1.10; t2 = price * 1.20; t3 = price * 1.35; t4 = price * 1.50
    risk = price - sl
    rr1 = (t1-price)/risk if risk>0 else 0
    if hammer: candle_name = "BULLISH HAMMER 🔨"
    elif engulf: candle_name = "BULLISH ENGULFING 🚀"
    else: candle_name = "BULLISH GREEN CANDLE 💪"
    return f"\n🔥 {candle_name} - {cross_days} din pehle Golden Cross + EMA50 Retest\n💰 ENTRY: {price:.0f}\n🛑 SL: {sl:.0f} ({sl_percent:.1f}% Daily Low)\n🎯 T1 (1M): {t1:.0f} (+10%) RR 1:{rr1:.1f}\n🎯 T2 (2M): {t2:.0f} (+20%)\n🎯 T3 (3M): {t3:.0f} (+35%)\n🎯 T4 (4M): {t4:.0f} (+50%)"

found = []
for sym in STOCKS:
    try:
        df = yf.download(sym, period="1y", interval="1d", progress=False, auto_adjust=True)
        res = scan(df)
        if res: found.append(f"✅ {sym.replace('.NS','')} {res}\n--------------------------")
        time.sleep(0.3)
    except: continue

if not found:
    msg = "Aaj koi CONFIRM Golden Cross + Retest + Bullish Candle nahi mila."
else:
    msg = f"💥 FINAL CONFIRM LIST - {len(found)} SHARES (Daily Candle) 💥\n\n" + "\n".join(found) + "\n\nSTRATEGY: T1 pe 30% book, T4 tak hold."
print(msg)
send_telegram(msg)
