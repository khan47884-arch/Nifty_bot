# V13 BACKTEST V3 - 60 DAYS ONLY - Yahoo 5m/15m 60 din se jyada nahi deta
import yfinance as yf
import pandas as pd
SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN"}
LOT = {"NIFTY": 65, "SENSEX": 20}
def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))
def clean_df(df):
    if df is None or len(df)==0: return df
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()
    df['Dt'] = pd.to_datetime(df.iloc[:,0])
    try:
        df['Dt'] = df['Dt'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    except:
        pass
    return df
def gv(c):
    return float(c["Open"]), float(c["Close"]), float(c["High"]), float(c["Low"])
def is_hammer(c):
    o,cl,h,l=gv(c)
    body=abs(cl-o); rng=h-l
    return rng!=0 and cl>o and (min(o,cl)-l)>body*2 and (h-max(o,cl))<body*0.5
def is_inv_hammer(c):
    o,cl,h,l=gv(c)
    body=abs(cl-o); rng=h-l
    return rng!=0 and cl>o and (h-max(o,cl))>body*2 and (min(o,cl)-l)<body*0.5
def is_dragonfly(c):
    o,cl,h,l=gv(c)
    body=abs(cl-o); rng=h-l
    return rng!=0 and body<rng*0.1 and (min(o,cl)-l)>rng*0.7
def is_shooting(c):
    o,cl,h,l=gv(c)
    body=abs(cl-o); rng=h-l
    return rng!=0 and cl<o and (h-max(o,cl))>body*2 and (min(o,cl)-l)<body*0.5
def is_hanging(c):
    o,cl,h,l=gv(c)
    body=abs(cl-o); rng=h-l
    return rng!=0 and cl<o and (min(o,cl)-l)>body*2 and (h-max(o,cl))<body*0.5
def is_grave(c):
    o,cl,h,l=gv(c)
    body=abs(cl-o); rng=h-l
    return rng!=0 and body<rng*0.1 and (h-max(o,cl))>rng*0.7
def detect_bonus(df):
    if len(df) < 20: return None, None
    d = df.tail(20)
    highs = d["High"].values; lows = d["Low"].values; closes = d["Close"].values
    l1 = min(lows[:8]); l2 = min(lows[-8:]); mid_high = max(highs[8:12])
    if abs(l1-l2) < (max(highs)-min(lows))*0.08 and closes[-1] > mid_high:
        return "DOUBLE BOTTOM (Bonus)", "Bullish"
    h1 = max(highs[:8]); h2 = max(highs[-8:]); mid_low = min(lows[8:12])
    if abs(h1-h2) < (max(highs)-min(lows))*0.08 and closes[-1] < mid_low:
        return "DOUBLE TOP (Bonus)", "Bearish"
    if abs(max(highs[-6:])-max(highs[:6])) < (max(highs)-min(lows))*0.08 and min(lows[-6:]) > min(lows[:6]) and closes[-1] > max(highs[-6:]):
        return "ASCENDING TRIANGLE (Bonus)", "Bullish"
    if abs(min(lows[-6:])-min(lows[:6])) < (max(highs)-min(lows))*0.08 and max(highs[-6:]) < max(highs[:6]) and closes[-1] < min(lows[-6:]):
        return "DESCENDING TRIANGLE (Bonus)", "Bearish"
    if closes[5] > closes[0]*1.001 and closes[-1] > max(highs[-5:-1]):
        return "BULLISH FLAG (Bonus)", "Bullish"
    if closes[5] < closes[0]*0.999 and closes[-1] < min(lows[-5:-1]):
        return "BEARISH FLAG (Bonus)", "Bearish"
    if max(highs[:5]) > max(highs[-5:]) and min(lows[:5]) > min(lows[-5:]) and (max(highs[-5:])-min(lows[-5:])) < (max(highs[:5])-min(lows[:5]))*0.6 and closes[-1] > max(highs[-3:]):
        return "FALLING WEDGE (Bonus)", "Bullish"
    if max(highs[:5]) < max(highs[-5:]) and min(lows[:5]) < min(lows[-5:]) and (max(highs[-5:])-min(lows[-5:])) < (max(highs[:5])-min(lows[:5]))*0.6 and closes[-1] < min(lows[-3:]):
        return "RISING WEDGE (Bonus)", "Bearish"
    if len(d)>=15:
        left = max(highs[2:5]); head = max(highs[6:9]); right = max(highs[10:13])
        if head > left and head > right and abs(left-right) < (head-min(lows))*0.1 and closes[-1] < min(lows[5:12]):
            return "HEAD & SHOULDERS (Bonus)", "Bearish"
        l_left = min(lows[2:5]); l_head = min(lows[6:9]); l_right = min(lows[10:13])
        if l_head < l_left and l_head < l_right and abs(l_left-l_right) < (max(highs)-l_head)*0.1 and closes[-1] > max(highs[5:12]):
            return "INV. HEAD & SHOULDERS (Bonus)", "Bullish"
    if (max(highs[-3:])-min(lows[-3:])) < (max(highs[:5])-min(lows[:5]))*0.4:
        if closes[-1] > max(highs[-4:]): return "SYMMETRICAL TRIANGLE UP (Bonus)", "Bullish"
        if closes[-1] < min(lows[-4:]): return "SYMMETRICAL TRIANGLE DOWN (Bonus)", "Bearish"
    return None, None
def detect_main(df5):
    if len(df5)<3: return None,None
    c1=df5.iloc[-3]; c2=df5.iloc[-2]; c3=df5.iloc[-1]
    o1,cl1,h1,l1=gv(c1); o2,cl2,h2,l2=gv(c2); o3,cl3,h3,l3=gv(c3)
    if is_hammer(c3): return "HAMMER", "Bullish"
    if is_inv_hammer(c3): return "INVERTED HAMMER", "Bullish"
    if is_dragonfly(c3): return "DRAGONFLY DOJI", "Bullish"
    if cl1<o1 and abs(cl2-o2)<abs(cl1-o1)*0.4 and cl3>o3 and cl3>(o1+cl1)/2: return "MORNING STAR", "Bullish"
    if is_shooting(c3): return "SHOOTING STAR", "Bearish"
    if is_hanging(c3): return "HANGING MAN", "Bearish"
    if is_grave(c3): return "GRAVESTONE DOJI", "Bearish"
    if cl1>o1 and abs(cl2-o2)<abs(cl1-o1)*0.4 and cl3<o3 and cl3<(o1+cl1)/2: return "EVENING STAR", "Bearish"
    return None,None
all_trades = []
dbg = {"trend_ok":0, "pattern_ok":0, "vol_fail":0, "break_fail":0}
for name, sym in SYMBOLS.items():
    print(f"Loading {name} 60d...")
    df15 = yf.download(sym, period="60d", interval="15m", progress=False, auto_adjust=True)
    df15 = clean_df(df15)
    df15['TP'] = (df15['High']+df15['Low']+df15['Close'])/3
    df15['TPV'] = df15['TP']*df15['Volume']
    df15['VWAP'] = df15.groupby(df15['Dt'].dt.date)['TPV'].cumsum() / df15.groupby(df15['Dt'].dt.date)['Volume'].cumsum()
    df15["EMA20"]=df15["Close"].ewm(span=20, adjust=False).mean()
    df15["EMA50"]=df15["Close"].ewm(span=50, adjust=False).mean()
    df5 = yf.download(sym, period="60d", interval="5m", progress=False, auto_adjust=True)
    df5 = clean_df(df5)
    df5["RSI"]=calc_rsi(df5["Close"])
    print(f"{name} 15m rows {len(df15)} 5m rows {len(df5)}")
    for date, day15 in df15.groupby(df15['Dt'].dt.date):
        day5 = df5[df5['Dt'].dt.date==date].reset_index(drop=True)
        if len(day5)<25: continue
        box = day15[(day15['Dt'].dt.hour==9) & (day15['Dt'].dt.minute==15)]
        if box.empty: continue
        box_high=float(box["High"].iloc[0]); box_low=float(box["Low"].iloc[0])
        for i in range(22, len(day5)-1):
            curr = day5.iloc[i]; prev = day5.iloc[i-1]; nxt = day5.iloc[i+1]
            if curr['Dt'].hour==9 and curr['Dt'].minute<30: continue
            if curr['Dt'].hour>=15: continue
            c15_row = day15[day15['Dt']<=curr['Dt']]
            if c15_row.empty: continue
            last15=c15_row.iloc[-1]
            c15=float(last15['Close']); v15=float(last15['VWAP']); e20=float(last15['EMA20']); e50=float(last15['EMA50'])
            if c15>v15 and c15>e20 and e20>e50: trend="UPTREND"
            elif c15<v15 and c15<e20 and e20<e50: trend="DOWNTREND"
            else: continue
            dbg["trend_ok"]+=1
            pat, side = detect_main(day5.iloc[i-2:i+1])
            if pat is None: pat, side = detect_bonus(day5.iloc[i-19:i+1])
            if pat is None: continue
            dbg["pattern_ok"]+=1
            vol_ok = float(curr['Volume']) >= 1.5*float(prev['Volume']) if float(prev['Volume'])>0 else False
            if not vol_ok:
                dbg["vol_fail"]+=1
                continue
            rsi5=float(curr['RSI'])
            tgt_pts=100 if name=="NIFTY" else 200
            if trend=="UPTREND" and side=="Bullish" and float(nxt['High'])>float(prev['High']):
                entry=float(nxt['Close']); sl=float(prev['Low']); target=entry+tgt_pts
                res="TARGET"; pnl=tgt_pts*LOT[name]
                for _, f in day5.iloc[i+2:i+12].iterrows():
                    if float(f['Low'])<=sl: res="SL"; pnl=-round((entry-sl)*LOT[name]); break
                    if float(f['High'])>=target: res="TARGET"; break
                else: res="OPEN"; pnl=0
                all_trades.append([str(date), str(curr['Dt'].time())[:5], name, "CALL", pat, f"RSI {rsi5:.0f}", round(entry), round(sl), round(target), res, pnl, f"BOX {box_low:.0f}-{box_high:.0f}"])
                break
            elif trend=="DOWNTREND" and side=="Bearish" and float(nxt['Low'])<float(prev['Low']):
                entry=float(nxt['Close']); sl=float(prev['High']); target=entry-tgt_pts
                res="TARGET"; pnl=tgt_pts*LOT[name]
                for _, f in day5.iloc[i+2:i+12].iterrows():
                    if float(f['High'])>=sl: res="SL"; pnl=-round((sl-entry)*LOT[name]); break
                    if float(f['Low'])<=target: res="TARGET"; break
                else: res="OPEN"; pnl=0
                all_trades.append([str(date), str(curr['Dt'].time())[:5], name, "PUT", pat, f"RSI {rsi5:.0f}", round(entry), round(sl), round(target), res, pnl, f"BOX {box_low:.0f}-{box_high:.0f}"])
                break
            else:
                dbg["break_fail"]+=1
                continue
print("========== V13 V3 - 60 DIN BACKTEST ==========")
for t in all_trades: print(t)
print(f"DEBUG Trend OK: {dbg['trend_ok']} Pattern OK: {dbg['pattern_ok']} Vol Fail 1.5x: {dbg['vol_fail']} Break Fail: {dbg['break_fail']}")
n_rs = sum([x[10] for x in all_trades if x[2]=="NIFTY"])
s_rs = sum([x[10] for x in all_trades if x[2]=="SENSEX"])
win = sum([1 for x in all_trades if x[9]=="TARGET"])
slc = sum([1 for x in all_trades if x[9]=="SL"])
print(f"Total Trades: {len(all_trades)} | TARGET: {win} | SL: {slc} | Win%: {round(win/len(all_trades)*100,1) if all_trades else 0}%")
print(f"NIFTY Net: Rs {n_rs}")
print(f"SENSEX Net: Rs {s_rs}")
print(f"TOTAL NET: Rs {n_rs+s_rs} (1 Lot Each - NIFTY x65 | SENSEX x20)")
