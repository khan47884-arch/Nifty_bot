import yfinance as yf, pandas as pd, requests, os
from datetime import datetime
import pytz
IST = pytz.timezone('Asia/Kolkata')
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m):
    try: requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id":CHAT,"text":m}, timeout=20)
    except: pass

STOCKS=["RVNL","IRFC","TITAGARH","TEXRAIL","BHEL","SUZLON","SJVN","NHPC","TATASTEEL","JSWSTEEL","SAIL","ADANIENT","ADANIPOWER","ADANIGREEN","TATAPOWER","ZOMATO","PAYTM","NYKAA","DELHIVERY","TRIDENT","NTPC","COALINDIA","POWERGRID","ONGC","RELIANCE","TCS","INFY","WIPRO","HCLTECH","TECHM","LTIM","TATAMOTORS","MARUTI","M&M","BAJAJ-AUTO","EICHERMOT","HEROMOTOCO","TVSMOTOR","ASHOKLEY","BAJAJFINSV","BAJFINANCE","SBIN","ICICIBANK","HDFCBANK","AXISBANK","KOTAKBANK","INDUSINDBK","FEDERALBNK","BANDHANBNK","IDFCFIRSTB","PNB","BANKBARODA","CANBK","UNIONBANK","INDIANB","YESBANK","AUBANK","RBLBANK","EQUITASBNK","UJJIVANSFB","HDFCLIFE","SBILIFE","ICICIPRULI","LICI","ADANIPORTS","CONCOR","IRCON","RAILTEL","JUPITERWAG","TITAN","ITC","BRITANNIA","NESTLEIND","HINDUNILVR","DABUR","MARICO","GODREJCP","COLPAL","MUTHOOTFIN","MANAPPURAM","IIFL","MOTILALOFS","ANGELONE","BSE","CDSL","MCX","VEDL","HINDALCO","NATIONALUM","HINDZINC","JSWENERGY","TORNTPOWER","SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","LUPIN","AUROPHARMA","ALKEM","BIOCON","LAURUSLABS","GLENMARK","IPCALAB","ZYDUSLIFE","MANKIND","APOLLOHOSP","MAXHEALTH","FORTIS","DLF","GODREJPROP","OBEROIRL","PRESTIGE","BRIGADE","SOBHA","LODHA","DIXON","AMBER","KAYNES","CROMPTON","HAVELLS","VOLTAS","BLUESTARCO","POLYCAB","KEI","ASTRAL","APLAPOLLO","JINDALSTEL","WELCORP","VBL","UBL","MCDOWELL-N","RADICO","INDIGO","GMRINFRA","IRB","NBCC","NCC","LT","SIEMENS","ABB","CUMMINSIND","THERMAX","BHARATFORG","MOTHERSON","BOSCHLTD","HAL","BEL","BDL","MAZDOCK","COCHINSHIP","BHARTIARTL","IDEA","HFCL","TATACOMM","TATAELXSI","KPITTECH","LTTS","ULTRACEMCO","ACC","AMBUJACEM","JKCEMENT","RAMCOCEM","SHREECEM","GRASIM","PIDILITIND","ASIANPAINT","BERGERPAINT","ATUL","AARTIIND","DEEPAKNTR","NAVINFLUOR","SRF","UPL","PIIND","COROMANDEL","CHAMBLFERT","BATAINDIA","RELAXO","KALYANKJIL","PAGEIND","TRENT","DMART","ABFRL","SAFARI","HINDCOPPER","MOIL","NMDC","HINDPETRO","BPCL","IOC","GAIL","IGL","MGL","PETRONET","OIL","PFC","REC","IREDA","HUDCO","IRCTC","JPOWER","TATATECH","HDFCAMC","NAM-INDIA","UTIAMC","OFSS","COFORGE","PERSISTENT","MPHASIS","TATACONSUM","JUBLFOOD","DEVYANI","SAPPHIRE","WESTLIFE","SENCO","TANLA","AFFLE","NAUKRI","INDIAMART","JUSTDIAL","INTELLECT","BSOFT","MASTEK","ZENSAR","CYIENT","SONATSOFTW","ELECON","TRIVENI","PRAJIND","AIAENG","CARBORUNDU","GRINDWELL","HINDOILEXP","GSPL","GUJGAS","IEX","CESC","JSWINFRA","ADANIENSOL","TORNTPHARM","ABBOTINDIA","SANOFI","PFIZER","AJANTPHARM","GRANULES","JBCHEPHARM","ENDURANCE","MINDACORP","SONACOMS","BALKRISIND","MRF","APOLLOTYRE","CEAT","BAJAJHLDNG","CHOLAFIN","SHRIRAMFIN","LTF","M&MFIN","CUB","KARURVYSYA","CITYUNION","DCBBANK","IDBI","BANKINDIA","MAHABANK","CENTRALBK","UCOBANK","IOB","PSB","J&KBANK","INDIACEM","HEIDELBERG","PRISMJOHN","ORIENTCEM","SAGCEM","DELTACORP","NAZARA","EASEMYTRIP","ALOKIND","JAIPRAKPOW","GOLDBEES","SILVERBEES","NIFTYBEES","BANKBEES"]

FOUND_PLATINUM=False
FOUND_DIAMOND=False
for SYM in STOCKS:
    try:
        tk = yf.Ticker(f"{SYM}.NS")
        info = tk.info or {}
        mcap = info.get("marketCap", 0) or 0
        promoter = (info.get("heldPercentInsiders", 0) or 0)*100
        inst_hold = (info.get("heldPercentInstitutions", 0) or 0)*100
        pe = info.get("trailingPE", 999) or 999
        de = info.get("debtToEquity", 999) or 999
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
        if score == 10:
            tag = "💎 PLATINUM MULTIBAGGER 💎"
            hold = "LONG TERM - 5-7 Saal - PLATINUM"
            FOUND_PLATINUM=True
        elif score >= 7:
            tag = "💠 DIAMOND SHORT TERM 💠"
            hold = "SHORT TERM - 2-4 Hafte - DIAMOND"
            FOUND_DIAMOND=True
        else:
            continue
        stamp=datetime.now(IST).strftime('%d-%b %I:%M %p IST')
        sl = max(m_low*0.97, float(c["Low"])*0.97)
        risk = close - sl
        t1 = close + risk*2; t2 = close + risk*4
        msg=f"{tag}\n━━━━━━━━━━━━━━━\n🏢 {SYM}\n💰 ENTRY: Rs {close:.0f} (Monthly High {m_high:.0f} Break)\n🛡️ SL: Rs {sl:.0f} (Monthly Low {m_low:.0f})\n🎯 T1: Rs {t1:.0f} | T2: Rs {t2:.0f}\n━━━━━━━━━━━━━━━\n⭐ SCORE: {score}/10 | {hold}\n📊 Mcap {mcap/10000000:.0f}Cr | P/E {pe:.0f} | ROE {roe:.0f}% | Debt {de:.2f}\n👑 Promoter {promoter:.0f}% | FII/DII {inst_hold:.0f}%\n📈 Sales CAGR {sales_cagr:.0f}% | Profit CAGR {profit_cagr:.0f}%\n📊 Vol x{volx:.1f} | RSI {rsi:.0f} | Cash Flow +ve\n⏰ {stamp}\n🚀 V8 FINAL DONE"
        tg(msg)
    except: continue
if not FOUND_PLATINUM and not FOUND_DIAMOND:
    tg(f"✨ V8 FINAL DONE ✨\nAaj koi PLATINUM ya DIAMOND nahi - Koi 7/10 pass nahi hua\n⏰ {datetime.now(IST).strftime('%d-%b %I:%M %p IST')}")
