import yfinance as yf
import requests, os, time, datetime
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        for i in range(0, len(msg), 3500):
            requests.post(url, data={"chat_id": CHAT_ID, "text": msg[i:i+3500]})
            time.sleep(1)
    except: pass

def is_strong(row, type="green"):
    try:
        body = abs(float(row['Close'])-float(row['Open']))
        rng = float(row['High'])-float(row['Low'])
        if rng==0 or body/rng<0.6: return False
        if type=="green": return float(row['Close'])>float(row['Open'])
        if type=="red": return float(row['Close'])<float(row['Open'])
    except: return False
    return False

def check_nifty_sensex():
    for symbol, name in [("^NSEI","NIFTY"),("^BSESN","SENSEX")]:
        try:
            daily = yf.download(symbol, period="5d", interval="1d", auto_adjust=True, progress=False)
            if len(daily)<3: continue
            prev_high = float(daily['High'].iloc[-2])
            prev_low = float(daily['Low'].iloc[-2])
            intraday = yf.download(symbol, period="1d", interval="5m", auto_adjust=True, progress=False)
            if len(intraday)<3: continue
            open_today = float(intraday['Open'].iloc[0])
            curr_row = intraday.iloc[-1]
            curr = float(curr_row['Close'])
            if open_today>prev_high and curr>prev_high and is_strong(curr_row,"green"):
                send_telegram(f"🔥 {name} BIWI ALERT\nUpar khula, Kaali Line {prev_high:.2f} tod ke upar\nPrice: {curr:.2f}")
            if open_today>prev_high and curr<prev_high and is_strong(curr_row,"red"):
                send_telegram(f"🔻 {name} SI ALERT\nUpar se khula, Kaali Line {prev_high:.2f} tod ke neeche\nPrice: {curr:.2f}")
            if open_today<prev_low and curr<prev_low and is_strong(curr_row,"red"):
                send_telegram(f"🔻 {name} SI ALERT\nNiche se khula, Kaali Line {prev_low:.2f} tod ke niche\nPrice: {curr:.2f}")
            if open_today<prev_low and curr>prev_low and is_strong(curr_row,"green"):
                send_telegram(f"🔥 {name} BIWI ALERT\nNiche se khula, Kaali Line {prev_low:.2f} pe Support\nPrice: {curr:.2f}")
        except: pass

STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","LT.NS","ITC.NS","KOTAKBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","WIPRO.NS","AXISBANK.NS","HCLTECH.NS","ULTRACEMCO.NS","TITAN.NS","BAJAJFINSV.NS","ADANIENT.NS"]

def check_stock(stock):
    try:
        df = yf.download(stock, period="250d", interval="1d", auto_adjust=True, progress=False)
        if len(df)<200: return None
        df['50ma']=df['Close'].rolling(50).mean()
        df['200ma']=df['Close'].rolling(200).mean()
        if df['50ma'].iloc[-2]<df['200ma'].iloc[-2] and df['50ma'].iloc[-1]>df['200ma'].iloc[-1]:
            return f"✅ GOLDEN CROSS: {stock} Price {float(df['Close'].iloc[-1]):.2f}"
    except: pass
    return None

def check_equity():
    if datetime.datetime.now().hour < 10:
        return
    results=[]
    with ThreadPoolExecutor(max_workers=15) as ex:
        for r in ex.map(check_stock, STOCKS):
            if r: results.append(r)
    if results:
        msg = "🔥 NIFTY 1000 GOLDEN CROSS 🔥\n\n" + "\n".join(results)
        send_telegram(msg)

check_nifty_sensex()
check_equity()
