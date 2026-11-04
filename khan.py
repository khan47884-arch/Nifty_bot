import yfinance as yf, requests, os, time
from datetime import datetime
import pytz
IST = pytz.timezone('Asia/Kolkata')
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m):
    try: requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id":CHAT,"text":m}, timeout=20)
    except: pass
STOCKS = ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","BHARTIARTL","ITC","LT","AXISBANK","KOTAKBANK","BAJFINANCE","MARUTI","TITAN","SUNPHARMA","WIPRO","ULTRACEMCO","ONGC","NTPC","HCLTECH","ADANIENT","M&M","POWERGRID","JSWSTEEL","HINDALCO","TRENT","COALINDIA"]
def get_nse_oi(symbol):
    try:
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
        headers = {"User-Agent": "Mozilla/5.0","Referer": "https://www.nseindia.com/"}
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=headers, timeout=10)
        time.sleep(0.6)
        r = s.get(url, headers=headers, timeout=10).json()
        spot = r["records"]["underlyingValue"]
        strikes = [x["strikePrice"] for x in r["records"]["data"] if "CE" in x]
        if not strikes: return None
        atm = min(strikes, key=lambda x: abs(x-spot))
        for item in r["records"]["data"]:
            if item["strikePrice"] == atm:
                return {"spot":spot,"atm":atm,"ce_chg":item.get("CE",{}).get("pchangeinOpenInterest",0),"pe_chg":item.get("PE",{}).get("pchangeinOpenInterest",0)}
    except: return None
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
try:
    nifty = yf.download("^NSEI", period="1d", interval="1d", progress=False, auto_adjust=True)
    nifty_trend = float(((nifty["Close"].iloc[-1] - nifty["Open"].iloc[-1])/nifty["Open"].iloc[-1])*100)
except: nifty_trend = 0
for sym in STOCKS:
    try:
        yf_sym = sym + ".NS"
        df_d = yf.download(yf_sym, period="2d", interval="1d", progress=False, auto_adjust=True)
        df_15 = yf.download(yf_sym, period="1d", interval="15m", progress=False, auto_adjust=True)
        if len(df_d) < 2 or len(df_15) < 3: continue
        prev_close = float(df_d["Close"].iloc[-2])
        curr = float(df_15["Close"].iloc[-1])
        pct = ((curr-prev_close)/prev_close)*100
        df_15["RSI"] = calculate_rsi(df_15["Close"])
        rsi = float(df_15["RSI"].iloc[-1])
        df_15["VWAP"] = (df_15["High"]+df_15["Low"]+df_15["Close"]).div(3).rolling(10).mean()
        vwap = float(df_15["VWAP"].iloc[-1])
        avg_vol = float(df_15["Volume"].iloc[-10:-1].mean())
        curr_vol = float(df_15["Volume"].iloc[-1])
        vol_ratio = curr_vol/avg_vol if avg_vol>0 else 1
        or_high = float(df_15["High"].iloc[0:2].max())
        or_low = float(df_15["Low"].iloc[0:2].min())
        if abs(pct) < 2.0: continue
        nse = get_nse_oi(sym)
        if not nse: continue
        is_long = pct >= 2.0 and nse["ce_chg"] >= 5.0 and curr > or_high
        is_short = pct <= -2.0 and nse["pe_chg"] >= 5.0 and curr < or_low
        if not (is_long or is_short): continue
        is_platinum = False
        if is_long and vol_ratio >= 1.5 and curr > vwap and rsi >= 60: is_platinum = True
        if is_short and vol_ratio >= 1.5 and curr < vwap and rsi <= 40: is_platinum = True
        sl = float(df_15["Low"].iloc[-1]) if is_long else float(df_15["High"].iloc[-1])
        target = curr + (curr-sl)*2 if is_long else curr - (sl-curr)*2
        stamp = datetime.now(IST).strftime('%I:%M %p')
        if is_platinum:
            if is_long:
                tg(f"💎 KHAN SAHAB PLATINUM 💎\n━━━━━━━━━━━━━━━\n{sym} {pct:.1f}% UP | CE OI {nse['ce_chg']:.1f}% UP\nVol {vol_ratio:.1f}x | RSI {rsi:.0f} | VWAP OK\nOR {or_high:.0f} Break | Nifty {nifty_trend:.1f}%\n💰 {sym} {nse['atm']} CE BUY\n🛑 SL {sl:.0f} 🎯 {target:.0f}\n⏰ {stamp}\n🔥 RARE SIGNAL")
            else:
                tg(f"💎 KHAN SAHAB PLATINUM 💎\n━━━━━━━━━━━━━━━\n{sym} {pct:.1f}% DOWN | PE OI {nse['pe_chg']:.1f}% UP\nVol {vol_ratio:.1f}x | RSI {rsi:.0f}\n💰 {sym} {nse['atm']} PE BUY\n🛑 SL {sl:.0f} 🎯 {target:.0f}\n⏰ {stamp}")
        else:
            if vol_ratio >= 1.2:
                if is_long:
                    tg(f"🔹 KHAN SAAB DIAMOND 🔹\n━━━━━━━━━━━━━━━\n{sym} {pct:.1f}% UP | CE OI {nse['ce_chg']:.1f}% UP\nVol {vol_ratio:.1f}x | RSI {rsi:.0f}\n💰 {sym} {nse['atm']} CE BUY\n🛑 SL {sl:.0f} 🎯 {target:.0f}\n⏰ {stamp}")
                else:
                    tg(f"🔹 KHAN SAAB DIAMOND 🔹\n━━━━━━━━━━━━━━━\n{sym} {pct:.1f}% DOWN | PE OI {nse['pe_chg']:.1f}% UP\n💰 {sym} {nse['atm']} PE BUY\n🛑 SL {sl:.0f} 🎯 {target:.0f}\n⏰ {stamp}")
        time.sleep(1)
    except Exception as e:
        print(f"{sym} {e}")
