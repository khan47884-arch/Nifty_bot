import yfinance as yf
import requests
import os
from concurrent.futures import ThreadPoolExecutor

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TELEGRAM_BOT_TOKEN: return
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                      data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
    except: pass

STOCKS = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","TITAN.NS","BAJFINANCE.NS","MARUTI.NS","TATAMOTORS.NS","TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","ADANIENT.NS","ADANIPORTS.NS","POLYCAB.NS","PERSISTENT.NS","COFORGE.NS","HAL.NS","BEL.NS","MAZDOCK.NS","RVNL.NS","IRFC.NS","IRCTC.NS","SJVN.NS","NHPC.NS","TATAPOWER.NS","NTPC.NS","POWERGRID.NS","SUZLON.NS","CDSL.NS","BSE.NS","ANGELONE.NS","MCX.NS","IEX.NS","ZOMATO.NS","PAYTM.NS","NYKAA.NS","DIXON.NS","CGPOWER.NS","BHEL.NS","COALINDIA.NS","ONGC.NS","VEDL.NS","DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS","MANKIND.NS","LUPIN.NS","CIPLA.NS","SUNPHARMA.NS","DIVISLAB.NS","DRREDDY.NS","CUMMINSIND.NS","ASHOKLEY.NS","MOTHERSON.NS","BOSCHLTD.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","TVSMOTOR.NS","ULTRACEMCO.NS","GRASIM.NS","AMBUJACEM.NS","ACC.NS","JKCEMENT.NS","ASIANPAINT.NS","BERGEPAINT.NS","PIDILITIND.NS","HAVELLS.NS","VOLTAS.NS","BLUESTARCO.NS","KAYNES.NS","SYRMA.NS","TATAELXSI.NS","TATATECH.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","MUTHOOTFIN.NS","CHOLAFIN.NS","SHRIRAMFIN.NS","RECLTD.NS","PFC.NS","BANKBARODA.NS","PNB.NS","CANBK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS","INDUSINDBK.NS","KOTAKBANK.NS","AXISBANK.NS","AUBANK.NS","DMART.NS","TRENT.NS","KALYANKJIL.NS","TITAGARH.NS","JINDALSTEL.NS","SAIL.NS","NATIONALUM.NS","JSWENERGY.NS","TORNTPOWER.NS","INDIANB.NS","UNIONBANK.NS","BHARATFORG.NS","M&M.NS","SRF.NS","DEEPAKNTR.NS","NAVINFLUOR.NS","UPL.NS","PIIND.NS","COROMANDEL.NS","CHAMBLFERT.NS","FACT.NS","HINDPETRO.NS","BPCL.NS","IOC.NS","GAIL.NS","PETRONET.NS","IGL.NS","MGL.NS","GUJGASLTD.NS","BALKRISIND.NS","MRF.NS","APOLLOTYRE.NS","CEAT.NS","BATAINDIA.NS","PATANJALI.NS","DABUR.NS","MARICO.NS","GODREJCP.NS","BRITANNIA.NS","TATACONSUM.NS","VARUNBEV.NS","JUBLFOOD.NS","INDIGO.NS","IRB.NS","NBCC.NS","HUDCO.NS","NCC.NS","KEI.NS","RRKABEL.NS","ASTRAL.NS","PAGEIND.NS","RAYMOND.NS","VBL.NS","OFSS.NS","BSOFT.NS","ZENSAR.NS","CYIENT.NS","INTELLECT.NS","MASTEK.NS","ATUL.NS","TATACHEM.NS","GLENMARK.NS","LAURUSLABS.NS","ALKEM.NS","TORNTPHARM.NS","ABB.NS","SIEMENS.NS","SCHAEFFLER.NS","THERMAX.NS","CROMPTON.NS","WHIRLPOOL.NS","AMBER.NS","BEML.NS","COCHINSHIP.NS","LICI.NS","CAMS.NS","KFINTECH.NS","MOTILALOFS.NS","IIFL.NS","EQUITASBNK.NS","BANDHANBNK.NS","CREDITACC.NS","M&MFIN.NS","POONAWALLA.NS","INDIAMART.NS","EIHOTEL.NS","CHALET.NS","LEMONTREE.NS","AFFLE.NS","ROUTE.NS","KPIL.NS","KEC.NS","LTF.NS","PNBHOUSING.NS","AAVAS.NS","CENTRALBK.NS","BANKINDIA.NS","YESBANK.NS","HDFCAMC.NS","WELCORP.NS","ARVIND.NS","GRANULES.NS","SYNGENE.NS","LALPATHLAB.NS","MAXHEALTH.NS","FORTIS.NS","CRAFTSMAN.NS","ENDURANCE.NS","RATNAMANI.NS","NMDC.NS","OIL.NS","GSPL.NS","INOXWIND.NS","HFCL.NS","IDEA.NS","AWL.NS","SOBHA.NS","BRIGADE.NS","LODHA.NS","CLEAN.NS","MEDANTA.NS","KIMS.NS","GLAND.NS","APARINDS.NS","DELHIVERY.NS","SAFARI.NS","CERA.NS","KPRMILL.NS","MASFIN.NS","NUVAMA.NS","IRCON.NS","RAILTEL.NS","BDL.NS","MTARTECH.NS","PGEL.NS","PCJEWELLER.NS","KAJARIACER.NS","BORORENEW.NS"]

def get_cap_cr(sym):
    try:
        mcap = yf.Ticker(sym).fast_info.market_cap
        return (mcap / 1e7) if mcap else 0
    except: return 0

def is_bullish_hammer(c):
    try:
        o,h,l,cl = float(c['Open']), float(c['High']), float(c['Low']), float(c['Close'])
        rng = h-l
        if rng==0: return False
        body = abs(cl-o)
        lower = min(o,cl)-l
        return lower >= body*1.8 and cl>o and body/rng < 0.5
    except: return False

def is_bullish_engulfing(curr, prev):
    try:
        return float(prev['Close']) < float(prev['Open']) and float(curr['Close']) > float(curr['Open']) and float(curr['Open']) < float(prev['Close']) and float(curr['Close']) > float(prev['Open'])
    except: return False

def get_rsi(s):
    d=s.diff(); g=d.where(d>0,0).ewm(alpha=1/14).mean(); l=-d.where(d<0,0).ewm(alpha=1/14).mean(); return 100-(100/(1+g/l))

def scan_single(sym):
    try:
        cap = get_cap_cr(sym)
        if cap < 1000 or cap > 20000: return None
        df_d = yf.download(sym, period="1y", interval="1d", progress=False, auto_adjust=True, threads=False)
        df_m = yf.download(sym, period="5y", interval="1mo", progress=False, auto_adjust=True, threads=False)
        df_w = yf.download(sym, period="2y", interval="1wk", progress=False, auto_adjust=True, threads=False)
        nifty = yf.download("^NSEI", period="1mo", interval="1d", progress=False, auto_adjust=True, threads=False)
        if len(df_d) < 210 or len(df_m) < 24 or len(df_w) < 30 or len(nifty) < 22: return None
        df_d['EMA20'] = df_d['Close'].ewm(span=20).mean()
        df_d['EMA50'] = df_d['Close'].ewm(span=50).mean()
        df_d['EMA200'] = df_d['Close'].ewm(span=200).mean()
        df_d['VOL20'] = df_d['Volume'].ewm(span=20).mean()
        curr = df_d.iloc[-1]; prev = df_d.iloc[-2]
        price = float(curr['Close'])
        if not (price > float(curr['EMA20']) > float(curr['EMA50']) > float(curr['EMA200'])): return None
        hammer = is_bullish_hammer(curr)
        engulf = is_bullish_engulfing(curr, prev)
        vol_spike = float(curr['Volume']) > float(curr['VOL20']) * 1.5
        if not ((hammer or engulf) and vol_spike): return None
        rsi_m = float(get_rsi(df_m['Close']).iloc[-1])
        rsi_w = float(get_rsi(df_w['Close']).iloc[-1])
        rsi_w_prev = float(get_rsi(df_w['Close']).iloc[-2])
        if not (35 < rsi_m < 52): return None
        if not (rsi_w_prev < 32 and 25 < rsi_w < 42): return None
        last_3_lows = df_m['Low'].iloc[-3:].values
        if (max(last_3_lows) - min(last_3_lows)) > (price * 0.08): return None
        low_10 = float(df_d['Low'].iloc[-10:].min())
        sl = min(low_10, float(curr['EMA200'])) * 0.98
        sl_per = ((price - sl) / price) * 100
        if sl_per > 7 or sl_per < 0.3: return None
        ret_stock = (df_d['Close'].iloc[-1] / df_d['Close'].iloc[-22] - 1) * 100
        ret_nifty = (nifty['Close'].iloc[-1] / nifty['Close'].iloc[-22] - 1) * 100
        if ret_stock < (ret_nifty + 5): return None
        t1 = price * 1.15
        risk = price - sl
        reward = t1 - price
        rr = reward / risk if risk>0 else 0
        if rr < 2: return None
        return (f"💎 REAL DIAMOND {sym.replace('.NS','')} | Rs {price:.0f}\n"
                f"✅ P1 Cap {cap:.0f}Cr [1000-20000]\n"
                f"✅ P2 Price > EMA20 > EMA50 > EMA200 [{float(curr['EMA20']):.0f}>{float(curr['EMA50']):.0f}>{float(curr['EMA200']):.0f}]\n"
                f"✅ P3 {'Hammer' if hammer else 'Engulf'} + Vol {float(curr['Volume'])/float(curr['VOL20']):.1f}x\n"
                f"✅ P4 RSI M {rsi_m:.0f} + W {rsi_w:.0f} + Triple Bottom\n"
                f"✅ P5 SL {sl:.0f} ({sl_per:.1f}%) <7%\n"
                f"✅ P6 Nifty se +{ret_stock-ret_nifty:.1f}% tez\n"
                f"✅ P7 RR {rr:.1f} >2\n"
                f"--> CONFIRMED REAL DIAMOND 💎")
    except:
        return None

if __name__ == "__main__":
    found = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        for r in ex.map(scan_single, STOCKS):
            if r: found.append(r)
    if not found:
        print("Aaj koi REAL DIAMOND nahi - Skip Telegram")
    else:
        found = list(dict.fromkeys(found))
        msg = f"💎💎 REAL DIAMOND MILA - {len(found)} STOCK 💎💎\n\n" + "\n\n".join(found[:10])
        print(msg)
        send_telegram(msg)
        send_telegram("💎 TEST - Bot zinda hai, Real Diamond scanner ready hai!")
