import yfinance as yf, pandas as pd, requests, os
from datetime import datetime
import pytz
IST = pytz.timezone('Asia/Kolkata')
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m):
    try: requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id":CHAT,"text":m}, timeout=20)
    except: pass

STOCKS=["RVNL","IRFC","TITAGARH","TEXRAIL","BHEL","SUZLON","SJVN","NHPC","ADANIENT","ADANIPOWER","ADANIGREEN","TATAPOWER","ZOMATO","PAYTM","NYKAA","DELHIVERY","TATAMOTORS","M&M","BAJAJ-AUTO","EICHERMOT","HEROMOTOCO","TVSMOTOR","ASHOKLEY","BAJAJFINSV","BAJFINANCE","SBIN","AXISBANK","KOTAKBANK","INDUSINDBK","FEDERALBNK","AUBANK","ADANIPORTS","CONCOR","IRCON","RAILTEL","JUPITERWAG","MUTHOOTFIN","MANAPPURAM","MOTILALOFS","ANGELONE","BSE","CDSL","MCX","JSWENERGY","TORNTPOWER","DIVISLAB","MANKIND","APOLLOHOSP","MAXHEALTH","FORTIS","DIXON","AMBER","KAYNES","HAVELLS","VOLTAS","POLYCAB","KEI","ASTRAL","APLAPOLLO","VBL","INDIGO","NBCC","NCC","LT","SIEMENS","ABB","CUMMINSIND","THERMAX","BHARATFORG","MOTHERSON","BOSCHLTD","HAL","BEL","BDL","MAZDOCK","COCHINSHIP","HFCL","TATACOMM","TATAELXSI","KPITTECH","LTTS","PFC","REC","IREDA","HUDCO","IRCTC","TATATECH","HDFCAMC","COFORGE","PERSISTENT","ELECON","TRIVENI","PRAJIND","AIAENG","IEX","CESC","JSWINFRA","ADANIENSOL","CHOLAFIN","SHRIRAMFIN","WAAREERTL","PREMIERENE","VIKRAMSOLR","INOXWIND","KPIGREEN","NETWEB","ZAGGLE","E2E","PGEL","KPRMILL","CRAFTSMAN","SUPREMEIND","NUVAMA","360ONE","NEULANDLAB","SYNGENE","APARINDS","RRKABEL","CGPOWER","POWERINDIA"]

def nifty_ok():
    try:
        n = yf.download("^NSEI", period="1y", interval="1d", progress=False, auto_adjust=True)
        if len(n)<210: return True
        if isinstance(n.columns, pd.MultiIndex): n.columns=n.columns.get_level_values(0)
        sma200 = n["Close"].rolling(200).mean().iloc[-1]
        curr = float(n["Close"].iloc[-1])
        return curr > float(sma200)
    except: return True

MARKET_OK = nifty_ok()

def detect_wave3_start(w):
    try:
        if len(w) < 30: return False
        closes = w["Close"].values
        low_idx = closes[-30:-10].argmin()
        w0 = float(closes[-30+low_idx])
        w1 = float(max(closes[-30+low_idx:]))
        w1_idx = list(closes).index(w1) if w1 in closes else -20
        segment = closes[w1_idx:]
        if len(segment) < 5: return False
        w2 = float(min(segment[:10]))
        wave1_len = w1 - w0
        if wave1_len <= 0: return False
        retrace2 = (w1 - w2) / wave1_len
        curr = float(closes[-1]); prev = float(closes[-2])
        if 0.38 <= retrace2 <= 0.62 and prev <= w1 and curr > w1 and curr <= w1 * 1.08:
            return True
        return False
    except: return False

FOUND_PLATINUM=False
FOUND_DIAMOND=False
SIGNAL_COUNT=0
MAX_SIGNALS=5
for SYM in STOCKS:
    if SIGNAL_COUNT>=MAX_SIGNALS: break
    try:
        tk = yf.Ticker(f"{SYM}.NS")
        info = tk.info or {}
        # V11.1 FIX - Mcap 0Cr Bug
        mcap = info.get("marketCap", 0) or 0
        if not mcap or mcap == 0:
            try: mcap = float(tk.fast_info.get("marketCap", 0) or 0)
            except: pass
        if not mcap or mcap == 0:
            try:
                q = tk.quarterly_balance_sheet
                mcap = 0
            except: pass
        promoter = (info.get("heldPercentInsiders", 0) or 0)*100
        inst_hold = (info.get("heldPercentInstitutions", 0) or 0)*100
        pe = info.get("trailingPE", 999) or 999
        if pe is None or pe > 200: pe = 999
        # V11.1 FIX - Debt 999 Bug - None / bada value aaye to 0 mano
        de_raw = info.get("debtToEquity", None)
        if de_raw is None: de = 0.0
        else:
            try: de = float(de_raw)
            except: de = 0.0
            if de > 10 or de < 0: de = 0.0
        roe = (info.get("returnOnEquity", 0) or 0)*100
        sales_g = (info.get("revenueGrowth", 0) or 0)*100
        profit_g = (info.get("earningsGrowth", 0) or 0)*100
        try:
            fin = tk.financials
            rev = fin.loc["Total Revenue"].dropna().values[::-1]
            net = fin.loc["Net Income"].dropna().values[::-1]
            if len(rev) >= 3 and len(net) >= 3 and rev[-3] > 0 and net[-3] > 0:
                sales_cagr = ((rev[-1]/rev[-3])**(1/2)-1)*100
                profit_cagr = ((net[-1]/net[-3])**(1/2)-1)*100
            else:
                sales_cagr = sales_g; profit_cagr = profit_g
        except:
            sales_cagr = sales_g; profit_cagr = profit_g
        bhel_turnaround = (profit_cagr >= 20 and sales_cagr >= 15)
        ocf = 1
        try:
            cf = tk.cashflow
            if "Operating Cash Flow" in cf.index:
                ocf = cf.loc["Operating Cash Flow"].dropna().values[0]
        except: pass
        m = yf.download(f"{SYM}.NS", period="6mo", interval="1mo", progress=False, auto_adjust=True)
        if len(m) < 3: continue
        if isinstance(m.columns, pd.MultiIndex): m.columns=m.columns.get_level_values(0)
        prev_m = m.iloc[-2]
        m_high = float(prev_m["High"]); m_low = float(prev_m["Low"])
        w = yf.download(f"{SYM}.NS", period="6mo", interval="1wk", progress=False, auto_adjust=True)
        if len(w) < 10: continue
        if isinstance(w.columns, pd.MultiIndex): w.columns=w.columns.get_level_values(0)
        w["VA"] = w["Volume"].rolling(10).mean()
        w["EMA20"] = w["Close"].ewm(span=20).mean()
        delta = w["Close"].diff()
        gain = delta.where(delta>0,0).rolling(14).mean()
        loss = -delta.where(delta<0,0).rolling(14).mean()
        w["RSI"] = 100-(100/(1+(gain/loss)))
        c = w.iloc[-1]; prev_w = w.iloc[-2]
        close = float(c["Close"]); vol = float(c["Volume"]); va = float(c["VA"])
        ema20 = float(c["EMA20"]); rsi = float(c["RSI"])
        volx = vol/va if va>0 else 0
        breakout = close > m_high and float(prev_w["Close"]) <= m_high
        tech_ok = volx >= 1.5 and close > ema20 and 55 < rsi < 78
        is_wave3_start = detect_wave3_start(w)
        if is_wave3_start:
            elliott_txt = "🌊 Wave 3 STARTING ✅ BONUS - Abhi Tezi Shuru Hui"
        else:
            elliott_txt = "🌊 Wave 3 Starting - No Bonus"
        score = 0
        if 800_0000000 <= mcap <= 20000_0000000: score += 1
        if promoter >= 50: score += 1
        if inst_hold >= 10: score += 1
        if sales_cagr >= 20 and profit_cagr >= 20: score += 1
        if de <= 0.5: score += 1
        if roe >= 15: score += 1
        if ocf > 0: score += 1
        if 0 < pe <= 40: score += 1
        if breakout: score += 1
        if tech_ok: score += 1
        if score == 10 and MARKET_OK:
            tag = "💎 PLATINUM MULTIBAGGER 💎"
            hold = "LONG TERM - 5-7 Saal - PLATINUM"
            FOUND_PLATINUM=True
        elif score >= 7 and is_wave3_start and bhel_turnaround and MARKET_OK:
            tag = "💎 PLATINUM MULTIBAGGER 💎 [Wave 3 START + BHEL TYPE]"
            hold = "LONG TERM - 5-7 Saal - PLATINUM (BHEL TYPE)"
            FOUND_PLATINUM=True
        elif score >= 7:
            tag = "💠 DIAMOND SHORT TERM 💠"
            hold = "SHORT TERM - 2-4 Hafte - DIAMOND"
            if not MARKET_OK:
                hold = "SHORT TERM - DIAMOND ONLY (Nifty 200 se neeche - Market Weak)"
            FOUND_DIAMOND=True
        else:
            continue
        SIGNAL_COUNT+=1
        stamp=datetime.now(IST).strftime('%d-%b %I:%M %p IST')
        sl = max(m_low*0.97, float(c["Low"])*0.97)
        risk = close - sl
        t1 = close + risk*2; t2 = close + risk*4
        qty_1lakh = int(2000 / risk) if risk>0 else 0
        msg=f"{tag}\n━━━━━━━━━━━━━━━\n🏢 {SYM}\n💰 ENTRY: Rs {close:.0f} (Monthly High {m_high:.0f} Break)\n🛡️ SL: Rs {sl:.0f} (Monthly Low {m_low:.0f})\n🎯 T1: Rs {t1:.0f} | T2: Rs {t2:.0f}\n━━━━━━━━━━━━━━━\n⭐ SCORE: {score}/10 | {hold}\n{elliott_txt}\n📊 Mcap {mcap/10000000:.0f}Cr | P/E {pe:.0f} | ROE {roe:.0f}% | Debt {de:.2f}\n👑 Promoter {promoter:.0f}% | FII/DII {inst_hold:.0f}%\n📈 Sales CAGR {sales_cagr:.0f}% | Profit CAGR {profit_cagr:.0f}% | BHEL Turnaround: {'YES' if bhel_turnaround else 'NO'}\n📊 Vol x{volx:.1f} | RSI {rsi:.0f} | Cash Flow +ve\n📊 Market: {'Nifty 200 se Upar ✅' if MARKET_OK else 'Nifty 200 se Neeche ⚠️'}\n━━━━━━━━━━━━━━━\n📌 V11.1 PLAN - TRAILING + PARTIAL:\n✅ T1 pe 50% BOOK KARO, SL ko ENTRY pe le aao - FREE TRADE\n✅ T2 pe SL ko T1 pe le jao - Ab LOSS nahi hoga\n✅ RISK 2% RULE: 1 Lakh Capital pe Max Qty {qty_1lakh} share - Risk 2000 se zyada nahi\n✅ MAX 5 POSITION: Ye {SIGNAL_COUNT}/5 Signal Hai\n⏰ {stamp}\n🚀 V11.1 FINAL 120 DONE"
        tg(msg)
    except: continue
if not FOUND_PLATINUM and not FOUND_DIAMOND:
    tg(f"✨ V11.1 FINAL 120 DONE ✨\nAaj koi PLATINUM ya DIAMOND nahi - Koi 7/10 pass nahi hua\nMarket: {'Nifty 200 se Upar ✅' if MARKET_OK else 'Nifty 200 se Neeche ⚠️ - Isliye NO PLATINUM'}\n⏰ {datetime.now(IST).strftime('%d-%b %I:%M %p IST')}")
