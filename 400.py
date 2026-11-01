import yfinance as yf, pandas as pd, requests, os
from datetime import datetime
BOT=os.getenv("TELEGRAM_BOT_TOKEN")
CHAT=os.getenv("TELEGRAM_CHAT_ID")
def tg(m): requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage", data={"chat_id":CHAT,"text":m})
STOCKS=["RVNL","IRFC","TITAGARH","TEXRAIL","BHEL","SUZLON","SJVN","NHPC","TATASTEEL","JSWSTEEL","SAIL","ADANIENT","ADANIPOWER","TATAPOWER","ZOMATO","PAYTM","NYKAA","DELHIVERY","TRIDENT","NTPC","COALINDIA","POWERGRID","ONGC","RELIANCE","TCS","INFY","WIPRO","HCLTECH","TECHM","LTIM","TATAMOTORS","MARUTI","M&M","BAJAJ-AUTO","EICHERMOT","HEROMOTOCO","TVSMOTOR","ASHOKLEY","BAJAJFINSV","BAJFINANCE","SBIN","ICICIBANK","HDFCBANK","AXISBANK","KOTAKBANK","INDUSINDBK","FEDERALBNK","BANDHANBNK","IDFCFIRSTB","PNB","BANKBARODA","CANBK","UNIONBANK","INDIANB","YESBANK","AUBANK","RBLBANK","EQUITASBNK","UJJIVANSFB","HDFCLIFE","SBILIFE","ICICIPRULI","LICI","ADANIPORTS","CONCOR","IRCON","RAILTEL","JUPITERWAG","TITAN","ITC","BRITANNIA","NESTLEIND","HINDUNILVR","DABUR","MARICO","GODREJCP","COLPAL","MUTHOOTFIN","MANAPPURAM","IIFL","MOTILALOFS","ANGELONE","BSE","CDSL","MCX","VEDL","HINDALCO","NATIONALUM","HINDZINC","JSWENERGY","TORNTPOWER","SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","LUPIN","AUROPHARMA","ALKEM","BIOCON","LAURUSLABS","GLENMARK","IPCALAB","ZYDUSLIFE","MANKIND","APOLLOHOSP","MAXHEALTH","FORTIS","DLF","GODREJPROP","OBEROIRL","PRESTIGE","BRIGADE","SOBHA","LODHA","DIXON","AMBER","KAYNES","CROMPTON","HAVELLS","VOLTAS","BLUESTARCO","POLYCAB","KEI","ASTRAL","APLAPOLLO","JINDALSTEL","WELCORP","VBL","UBL","MCDOWELL-N","RADICO","INDIGO","GMRINFRA","IRB","NBCC","NCC","LT","SIEMENS","ABB","CUMMINSIND","THERMAX","BHARATFORG","MOTHERSON","BOSCHLTD","HAL","BEL","BDL","MAZDOCK","COCHINSHIP","BHARTIARTL","IDEA","HFCL","TATACOMM","TATAELXSI","KPITTECH","LTTS","ULTRACEMCO","ACC","AMBUJACEM","JKCEMENT","RAMCOCEM","SHREECEM","GRASIM","PIDILITIND","ASIANPAINT","BERGERPAINT","ATUL","AARTIIND","DEEPAKNTR","NAVINFLUOR","SRF","UPL","PIIND","COROMANDEL","CHAMBLFERT","BATAINDIA","RELAXO","KALYANKJIL","PAGEIND","TRENT","DMART","ABFRL","SAFARI","HINDCOPPER","MOIL","NMDC","HINDPETRO","BPCL","IOC","GAIL","IGL","MGL","PETRONET","OIL","PFC","REC","IREDA","HUDCO","IRCTC","JPOWER","ADANIGREEN","TATATECH","LT","ACC","VEDL","HINDALCO","HDFCAMC","NAM-INDIA","UTIAMC"]
FOUND=False
for SYM in STOCKS:
    try:
        df=yf.download(f"{SYM}.NS", period="6mo", interval="1d", progress=False)
        if len(df)<60: continue
        if isinstance(df.columns, pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        df["VA"]=df["Volume"].rolling(20).mean()
        df["S20"]=df["Close"].rolling(20).mean()
        df["S50"]=df["Close"].rolling(50).mean()
        c=df.iloc[-1]
        close=float(c["Close"]); low=float(c["Low"]); vol=float(c["Volume"]); va=float(c["VA"])
        body=abs(float(c["Close"])-float(c["Open"]))
        hammer=(float(c["Open"])-low) > body*1.8
        volx=vol/va if va>0 else 0
        vwap_up=close>float(c["S20"]) and float(c["S20"])>float(c["S50"])
        prev_low=float(df["Low"].iloc[-6:-1].min())
        sweep=low < prev_low and close > prev_low
        score=0
        if hammer: score+=25
        if volx>2.5: score+=25
        if vwap_up: score+=20
        if sweep: score+=30
        if score>=70:
            tg(f"KOHINOOR {score} - {SYM} Rs {close:.0f} Vol x{volx:.1f} SL {low*0.97:.0f} ENTRY {close:.0f} STAMP:{datetime.now().strftime('%d-%b %I:%M %p IST')} 400 BRAHMASTRA")
            FOUND=True
    except: continue
if not FOUND:
    tg(f"V6 ORIGINAL - Aaj koi naya Game Changer nahi STAMP:{datetime.now().strftime('%d-%b %I:%M %p IST')} V6 ORIGINAL")
