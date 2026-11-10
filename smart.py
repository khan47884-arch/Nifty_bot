# V13 BACKTEST - 3 MONTH - FINAL
import yfinance as yf, pandas as pd, numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings; warnings.filterwarnings('ignore')
print("3 Mahine ka Data Download Ho Raha Hai... 1 Min Ruko")
SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN"}
LOT = {"NIFTY": 65, "SENSEX": 20}
TARGET_PTS = {"NIFTY": 100, "SENSEX": 200}
MAX_PER_BOX = 3
def clean(df):
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()
    df['Dt'] = pd.to_datetime(df.iloc[:,0])
    try: df['Dt'] = df['Dt'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
    except: pass
    return df
def gv(c): return float(c["Open"]), float(c["Close"]), float(c["High"]), float(c["Low"])
def is_hammer(c):
    o,cl,h,l=gv(c); b=abs(cl-o); r=h-l
    return r!=0 and cl>o and (min(o,cl)-l)>b*2 and (h-max(o,cl))<b*0.5
def is_inv_hammer(c):
    o,cl,h,l=gv(c); b=abs(cl-o); r=h-l
    return r!=0 and cl>o and (h-max(o,cl))>b*2 and (min(o,cl)-l)<b*0.5
def is_dragonfly(c):
    o,cl,h,l=gv(c); b=abs(cl-o); r=h-l
    return r!=0 and b<r*0.1 and (min(o,cl)-l)>r*0.7
def is_shooting(c):
    o,cl,h,l=gv(c); b=abs(cl-o); r=h-l
    return r!=0 and cl<o and (h-max(o,cl))>b*2 and (min(o,cl)-l)<b*0.5
def get_strike(name, entry):
    return int(round(entry/50)*50) if name=="NIFTY" else int(round(entry/100)*100)
all_trades = []
for name, sym in SYMBOLS.items():
    print(f"\n{name} Ka Backtest Chal Raha Hai...")
    df15 = clean(yf.download(sym, period="3mo", interval="15m", progress=False, auto_adjust=True))
    df5 = clean(yf.download(sym, period="3mo", interval="5m", progress=False, auto_adjust=True))
    days = sorted(df5['Dt'].dt.date.unique())
    for day in days:
        d15 = df15[df15['Dt'].dt.date==day]
        d5 = df5[df5['Dt'].dt.date==day].reset_index(drop=True)
        if len(d15)<5 or len(d5)<22: continue
        boxes = []
        b1 = d15[(d15['Dt'].dt.hour==9)&(d15['Dt'].dt.minute==15)]
        if not b1.empty: boxes.append(("BOX1", float(b1["High"].iloc[0]), float(b1["Low"].iloc[0])))
        b2 = d15[(d15['Dt'].dt.hour==11)&(d15['Dt'].dt.minute==30)]
        if not b2.empty: boxes.append(("BOX2", float(b2["High"].iloc[0]), float(b2["Low"].iloc[0])))
        for box_name, bh, bl in boxes:
            if box_name=="BOX1":
                candles = d5[(d5['Dt'].dt.hour==9)&(d5['Dt'].dt.minute>=30) | (d5['Dt'].dt.hour==10) | (d5['Dt'].dt.hour==11)&(d5['Dt'].dt.minute<30)]
            else:
                candles = d5[(d5['Dt'].dt.hour==11)&(d5['Dt'].dt.minute>=30) | (d5['Dt'].dt.hour>=12)]
            candles = candles.reset_index(drop=True)
            if len(candles)<5: continue
            cnt = 0
            i = 2
            while i < len(candles)-1 and cnt < MAX_PER_BOX:
                prev = candles.iloc[i-1]; curr = candles.iloc[i]; nxt = candles.iloc[i+1]
                t15 = d15[d15['Dt']<=nxt['Dt']]
                if len(t15)<3:
                    i+=1; continue
                last15 = t15.iloc[-1]; prev15 = t15.iloc[-2]
                c15=float(last15['Close']); ph15=float(prev15['High']); pl15=float(prev15['Low'])
                if c15>ph15: trend="UPTREND"
                elif c15<pl15: trend="DOWNTREND"
                else:
                    i+=1; continue
                pat=None; side=None
                if is_hammer(nxt): pat="HAMMER"; side="Bullish"
                elif is_inv_hammer(nxt): pat="INVERTED HAMMER"; side="Bullish"
                elif is_dragonfly(nxt): pat="DRAGONFLY"; side="Bullish"
                elif is_shooting(nxt): pat="SHOOTING STAR"; side="Bearish"
                if pat is None:
                    i+=1; continue
                pv=float(prev['Volume']); cv=float(curr['Volume'])
                if pv>0 and cv>0 and cv < 2*pv:
                    i+=1; continue
                entry=float(nxt['Close']); strike=get_strike(name, entry)
                tgt_pts=TARGET_PTS[name]
                if trend=="UPTREND" and side=="Bullish" and float(nxt['High'])>float(prev['High']):
                    sl=float(prev['Low']); target=entry+tgt_pts; typ="CALL"
                elif trend=="DOWNTREND" and side=="Bearish" and float(nxt['Low'])<float(prev['Low']):
                    sl=float(prev['High']); target=entry-tgt_pts; typ="PUT"
                else:
                    i+=1; continue
                result="OPEN"; pnl_pts=0; exit_idx=None
                for j in range(i+2, len(candles)):
                    fut=candles.iloc[j]
                    if typ=="CALL":
                        if float(fut['Low'])<=sl: result="SL"; pnl_pts=-(entry-sl); exit_idx=j; break
                        if float(fut['High'])>=target: result="TARGET"; pnl_pts=tgt_pts; exit_idx=j; break
                    else:
                        if float(fut['High'])>=sl: result="SL"; pnl_pts=-(sl-entry); exit_idx=j; break
                        if float(fut['Low'])<=target: result="TARGET"; pnl_pts=tgt_pts; exit_idx=j; break
                if result=="OPEN":
                    break
                pnl_rs = pnl_pts * LOT[name] if result=="TARGET" else -abs(pnl_pts)*LOT[name]
                all_trades.append({"Date": day, "Month": pd.to_datetime(day).strftime("%Y-%m"), "Symbol": name, "Type": typ, "Box": box_name, "TradeNo": cnt+1, "Pattern": pat, "Strike": strike, "Entry": round(entry), "SL": round(sl), "Target": round(target), "Result": result, "Pts": round(pnl_pts,1), "Rs": round(pnl_rs)})
                cnt+=1
                i = exit_idx + 1
df = pd.DataFrame(all_trades)
if df.empty:
    print("Koi Trade Nahi Bana - Data Check Karo")
else:
    print("V13 BACKTEST - 3 MONTH - PURA HISAB")
    total=len(df); wins=(df['Result']=="TARGET").sum(); losses=(df['Result']=="SL").sum()
    win_pct=wins/total*100 if total else 0
    total_rs=df['Rs'].sum()
    print(f"Total Trade: {total} | Win: {wins} | Loss: {losses} | Win %: {win_pct:.1f}%")
    print(f"TOTAL P&L (1 Lot Each): Rs {total_rs:,.0f}")
    print(df.groupby("Month").agg(Trade=("Rs","count"), Win=("Result", lambda x:(x=="TARGET").sum()), Rs=("Rs","sum")))
    print(df.groupby("Box").agg(Trade=("Rs","count"), Win=("Result", lambda x:(x=="TARGET").sum()), Rs=("Rs","sum")))
    print(df.groupby("TradeNo").agg(Trade=("Rs","count"), Win=("Result", lambda x:(x=="TARGET").sum()), Rs=("Rs","sum")))
    print(df.groupby("Symbol").agg(Trade=("Rs","count"), Win=("Result", lambda x:(x=="TARGET").sum()), Rs=("Rs","sum")))
    print(df.groupby("Type").agg(Trade=("Rs","count"), Win=("Result", lambda x:(x=="TARGET").sum()), Rs=("Rs","sum")))
    print(df.tail(20).to_string(index=False))
    df['Cum'] = df['Rs'].cumsum()
    plt.figure(figsize=(12,6))
    plt.plot(df['Cum'].values, linewidth=2)
    plt.title(f"V13 Backtest 3 Month - Total Rs {total_rs:,.0f} | Win {win_pct:.1f}% | Trades {total}", fontsize=13, weight='bold')
    plt.xlabel("Trade Number"); plt.ylabel("Cumulative Rs (1 Lot)")
    plt.grid(True, alpha=0.3); plt.tight_layout(); plt.savefig("backtest.png")
    df.to_csv("V13_Backtest_3Month.csv", index=False)
    print("CSV Save Ho Gaya")
