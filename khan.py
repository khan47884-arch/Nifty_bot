//@version=6
indicator("KHAN SAHAB PLATINUM + DIAMOND", overlay=true)

// ===== INPUTS =====
boxStart = input.time(timestamp("09:15"), "Box Start")
boxEnd = input.time(timestamp("09:30"), "Box End")
gapLimit = input.float(2.0, "Gap % Limit")
rsiLen = input.int(14, "RSI Length")
emaLen = input.int(20, "EMA Length")

// ===== PREV DAY CLOSE & GAP =====
prevClose = request.security(syminfo.tickerid, "D", close[1], lookahead=barmerge.lookahead_on)
dayOpen = request.security(syminfo.tickerid, "D", open, lookahead=barmerge.lookahead_on)
gapPct = (dayOpen - prevClose) / prevClose * 100

// ===== BOX 9:15-9:30 =====
var float boxHigh = na
var float boxLow = na
var bool boxDone = false
t = time
inBox = t >= boxStart and t < boxEnd

if inBox and not boxDone
    boxHigh := na(boxHigh) ? high : math.max(boxHigh, high)
    boxLow := na(boxLow) ? low : math.min(boxLow, low)
if t >= boxEnd and not boxDone
    boxDone := true

plot(boxDone ? boxHigh : na, "BOX HIGH", color.orange, 2)
plot(boxDone ? boxLow : na, "BOX LOW", color.orange, 2)

// ===== INDICATORS =====
ema20 = ta.ema(close, emaLen)
vwapVal = ta.vwap(close)
rsiVal = ta.rsi(close, rsiLen)
volAvg = ta.sma(volume, 20)

// ===== CONDITIONS =====
isPlatinum = math.abs(gapPct) >= gapLimit
isDiamond = math.abs(gapPct) < gapLimit

// PLATINUM - Seedha BOX Breakout
platCall = boxDone and isPlatinum and close > boxHigh and close > vwapVal
platPut = boxDone and isPlatinum and close < boxLow and close < vwapVal

// DIAMOND - Retrace + Double Touch
// Price neeche aake VWAP + EMA20 dono ko touch kiya
touchedBoth = math.abs(low - vwapVal) < close * 0.0005 and math.abs(low - ema20) < close * 0.0005
touchedBothUp = math.abs(high - vwapVal) < close * 0.0005 and math.abs(high - ema20) < close * 0.0005

var bool diamondTouchCall = false
var bool diamondTouchPut = false
if boxDone and isDiamond and touchedBoth
    diamondTouchCall := true
if boxDone and isDiamond and touchedBothUp
    diamondTouchPut := true

volOk = volume > volAvg
diaCall = boxDone and isDiamond and diamondTouchCall and close > boxHigh and volOk
diaPut = boxDone and isDiamond and diamondTouchPut and close < boxLow and volOk

// ===== TRUSTED =====
trustedBull = close > vwapVal and close > ema20 and rsiVal > 50 and volOk
trustedBear = close < vwapVal and close < ema20 and rsiVal < 50 and volOk

// ===== SIGNALS =====
callSignal = platCall or diaCall
putSignal = platPut or diaPut

isPlatSignal = platCall or platPut
signalType = isPlatSignal ? "PLATINUM" : "DIAMOND"
trustedTxt = callSignal and trustedBull ? "🟢 TRUSTED BULLISH 🟢" : putSignal and trustedBear ? "🔴 TRUSTED BEARISH 🔴" : ""

// ===== PLOT SIGNALS =====
plotshape(callSignal, "CALL", shape.labelup, location.belowbar, color.green, text="CALL", textcolor=color.white, size=size.normal)
plotshape(putSignal, "PUT", shape.labeldown, location.abovebar, color.red, text="PUT", textcolor=color.white, size=size.normal)

// ===== TABLE - COPY PASTE KE LIYE SIGNAL INFO =====
var table info = table.new(position.top_right, 1, 7, bgcolor=color.new(color.black, 80))
if barstate.islast
    table.cell(info, 0, 0, trustedTxt, text_color=color.white, text_size=size.normal)
    table.cell(info, 0, 1, "KHAN SAHAB " + signalType, text_color=color.yellow, text_size=size.normal)
    table.cell(info, 0, 2, "SHARE: " + syminfo.ticker + " | GAP: " + str.tostring(gapPct, "#.##") + "%", text_color=color.white)
    table.cell(info, 0, 3, "BOX: " + str.tostring(boxLow, "#.##") + " - " + str.tostring(boxHigh, "#.##"), text_color=color.white)
    table.cell(info, 0, 4, "VWAP: " + str.tostring(vwapVal, "#.##") + " | 20 EMA: " + str.tostring(ema20, "#.##"), text_color=color.white)
    table.cell(info, 0, 5, "RSI: " + str.tostring(rsiVal, "#.##"), text_color=color.white)
    table.cell(info, 0, 6, callSignal ? "BUY @ " + str.tostring(close, "#.##") + " | SL " + str.tostring(boxHigh - (boxHigh - boxLow), "#.##") : putSignal ? "BUY @ " + str.tostring(close, "#.##") + " | SL " + str.tostring(boxLow + (boxHigh - boxLow), "#.##") : "WAIT...", text_color=color.white)

// ===== ALERTS - TELEGRAM KE LIYE =====
alertcondition(callSignal, "KHAN CALL", "TRUSTED BULLISH - {{ticker}} CALL - BOX {{ticker}} - RSI")
alertcondition(putSignal, "KHAN PUT", "TRUSTED BEARISH - {{ticker}} PUT - BOX {{ticker}} - RSI")
