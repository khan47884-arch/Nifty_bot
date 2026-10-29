name: Backtest
on: workflow_dispatch
jobs:
  backtest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install yfinance pandas
      - run: |
          python - << 'PY'
          import yfinance as yf, pandas as pd
          def rsi(s, p=14):
              d=s.diff(); g=d.where(d>0,0).ewm(alpha=1/p).mean(); l=(-d.where(d<0,0)).ewm(alpha=1/p).mean()
              return 100-(100/(1+(g/l)))
          for SYMBOL in ["^NSEI","^BSESN"]:
              df=yf.download(SYMBOL,period="6mo",interval="15m",auto_adjust=True,progress=False)
              df.dropna(inplace=True)
              df["EMA20"]=df["Close"].ewm(span=20).mean()
              df["EMA50"]=df["Close"].ewm(span=50).mean()
              df["RSI"]=rsi(df["Close"])
              trades=[]
              for i in range(100,len(df)-10):
                  o,h,l,c=map(float,df.iloc[i][["Open","High","Low","Close"]])
                  po,ph,pl,pc=map(float,df.iloc[i-1][["Open","High","Low","Close"]])
                  body=abs(c-o)
                  if body==0: body=0.01
                  lower=min(o,c)-l; upper=h-max(o,c)
                  pat=""; bull=False; bear=False
                  if pc<po and c>o and c>=po and o<=pc: pat="BULLISH ENGULFING"; bull=True
                  elif lower>body*2 and upper<body*0.6: pat="HAMMER"; bull=True
                  elif lower>body*2.2: pat="BULLISH PIN BAR"; bull=True
                  elif pc>po and c<o and o>=pc and c<=po: pat="BEARISH ENGULFING"; bear=True
                  elif upper>body*2 and lower<body*0.6: pat="SHOOTING STAR"; bear=True
                  elif upper>body*2.2: pat="BEARISH PIN BAR"; bear=True
                  if pat=="": continue
                  ema20=float(df.iloc[i]["EMA20"]); ema50=float(df.iloc[i]["EMA50"]); rsi_val=float(df.iloc[i]["RSI"])
                  up= c>ema20 and c>ema50 and rsi_val>52
                  down= c<ema20 and c<ema50 and rsi_val<48
                  sl= min(l,pl) if bull else max(h,ph)
                  risk= abs(c-sl)
                  if risk==0: continue
                  tgt1= c + risk*1.5 if bull else c - risk*1.5
                  sig=None
                  if bull and up: sig="CE"
                  elif bear and down: sig="PE"
                  else: continue
                  res="No Hit"; pnl=0
                  for j in range(i+1,min(i+11,len(df))):
                      fh=float(df.iloc[j]["High"]); fl=float(df.iloc[j]["Low"])
                      if sig=="CE":
                          if fl<=sl: res="SL"; pnl=-risk; break
                          if fh>=tgt1: res="TGT1"; pnl=risk*1.5; break
                      else:
                          if fh>=sl: res="SL"; pnl=-risk; break
                          if fl<=tgt1: res="TGT1"; pnl=risk*1.5; break
                  trades.append([str(df.index[i]),pat,sig,round(c,1),round(sl,1),round(tgt1,1),res,round(pnl,1)])
              dft=pd.DataFrame(trades,columns=["Date","Pattern","Type","Entry","SL","TGT1","Result","PnL"])
              print(f"\n===== {SYMBOL} BACKTEST =====")
              print(f"Total: {len(dft)}")
              if len(dft)>0:
                  wins=len(dft[dft["Result"]=="TGT1"]); losses=len(dft[dft["Result"]=="SL"])
                  print(f"Win {wins} Loss {losses} Win% {wins/len(dft)*100:.1f}% PnL {dft['PnL'].sum():.1f} pts")
                  print(dft.tail(15).to_string(index=False))
          PY
