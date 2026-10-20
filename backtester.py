import yfinance as yf
import pandas as pd
import numpy as np
import json
import datetime
import os

# --- 1. KONFIGURATION & WATCHLIST ---
WATCHLIST = {
    "NVDA": {"name": "NVIDIA Corp.", "sector": "US Equities"},
    "AAPL": {"name": "Apple Inc.", "sector": "US Equities"},
    "MSFT": {"name": "Microsoft Corp.", "sector": "US Equities"},
    "^GSPC": {"name": "S&P 500 Index", "sector": "Indices"},
    "^GDAXI": {"name": "DAX 40", "sector": "Indices"},
    "EURUSD=X": {"name": "EUR/USD", "sector": "Forex"},
    "GC=F": {"name": "Gold Futures", "sector": "Commodities"}
}

PERIOD = "2y"
INTERVAL = "1d"
RR_TARGET = 2.5

# --- 2. HILFSFUNKTIONEN FÜR TECHNISCHE ANALYSE ---
def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(period).mean()

def calculate_adx(df, period=14):
    # Vereinfachte ADX-Berechnung für Trendstärke
    df['UpMove'] = df['High'] - df['High'].shift(1)
    df['DownMove'] = df['Low'].shift(1) - df['Low']
    df['+DM'] = np.where((df['UpMove'] > df['DownMove']) & (df['UpMove'] > 0), df['UpMove'], 0)
    df['-DM'] = np.where((df['DownMove'] > df['UpMove']) & (df['DownMove'] > 0), df['DownMove'], 0)
    
    atr = calculate_atr(df, period)
    plus_di = 100 * (df['+DM'].rolling(period).mean() / atr)
    minus_di = 100 * (df['-DM'].rolling(period).mean() / atr)
    
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(period).mean()
    return adx.fillna(20) # Standardwert, falls zu wenig Daten

def find_swing_points(df, window=5):
    # Findet lokale Hochs und Tiefs
    df['SwingHigh'] = df['High'][(df['High'] == df['High'].rolling(window, center=True).max())]
    df['SwingLow'] = df['Low'][(df['Low'] == df['Low'].rolling(window, center=True).min())]
    return df

# --- 3. HAUPT-ANALYSE-LOGIK ---
def analyze_ticker(ticker, info):
    print(f"Analysiere {ticker}...")
    try:
        # Lade Daten
        df = yf.download(ticker, period=PERIOD, interval=INTERVAL, progress=False)
        
        # Behebe MultiIndex-Spalten von yfinance (falls vorhanden)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        if df.empty or len(df) < 200:
            return None

        # Basis-Indikatoren berechnen
        df['SMA50'] = df['Close'].rolling(50).mean()
        df['SMA200'] = df['Close'].rolling(200).mean()
        df['Vol_SMA20'] = df['Volume'].rolling(20).mean()
        # Verhindere Division durch 0 bei Forex/Indizes
        df['Vol_SMA20'] = df['Vol_SMA20'].replace(0, 1) 
        df['RVOL'] = df['Volume'] / df['Vol_SMA20']
        df['ATR'] = calculate_atr(df)
        df['ADX'] = calculate_adx(df)
        
        df = find_swing_points(df)

        # Hole aktuelle Kerze und Kontext
        current = df.iloc[-1]
        c_idx = df.index[-1]
        
        sma50 = float(current['SMA50'])
        sma200 = float(current['SMA200'])
        rvol = float(current['RVOL']) if not np.isnan(current['RVOL']) else 1.0
        adx = float(current['ADX'])
        last_price = float(current['Close'])
        atr = float(current['ATR'])

        # Bestimme Trend und Richtung
        is_bullish = sma50 > sma200 and last_price > sma50
        direction = "LONG" if is_bullish else "SHORT"

        # Finde letztes Swing High/Low für BOS & Fibonacci
        recent_highs = df[df['SwingHigh'].notna()]['High']
        recent_lows = df[df['SwingLow'].notna()]['Low']
        
        if len(recent_highs) < 2 or len(recent_lows) < 2:
            return None
            
        last_swing_high = float(recent_highs.iloc[-1])
        last_swing_low = float(recent_lows.iloc[-1])
        
        # BOS Logik (stark vereinfacht: Schlusskurs über letztem Swing High)
        bos_occurred = last_price > last_swing_high if is_bullish else last_price < last_swing_low
        
        # Fibonacci Golden Pocket (0.5 - 0.618) Retracement
        fib_05 = last_swing_high - (last_swing_high - last_swing_low) * 0.5
        fib_618 = last_swing_high - (last_swing_high - last_swing_low) * 0.618
        
        # Score Berechnung
        score = 65
        if is_bullish and sma50 > sma200: score += 10
        if bos_occurred: score += 10
        if rvol > 1.3: score += 5
        if adx > 25: score += 5
        
        # Wenn Preis in Fib-Zone, Bonus-Punkte
        if fib_618 <= last_price <= fib_05:
            score += 5
            
        # Stop Loss & Take Profit kalkulieren
        if direction == "LONG":
            sl = last_swing_low - (atr * 0.5)
            risk = last_price - sl
            tp = last_price + (risk * RR_TARGET)
        else:
            sl = last_swing_high + (atr * 0.5)
            risk = sl - last_price
            tp = last_price - (risk * RR_TARGET)
            
        if risk <= 0: return None # Sicherungs-Check

        # Formatierung der letzten 8 Kerzen für das UI Chart
        chart_data = []
        recent_df = df.tail(8)
        for idx, row in recent_df.iterrows():
            candle = {
                "o": float(row['Open']),
                "h": float(row['High']),
                "l": float(row['Low']),
                "c": float(row['Close']),
                "v": float(row['Volume']) if not np.isnan(row['Volume']) and row['Volume'] > 0 else 50
            }
            # Normiere Volumen visuell für das UI zwischen 20 und 98
            if candle["v"] > 50:
                 candle["v"] = min(98, max(25, (float(row['Volume']) / float(recent_df['Volume'].mean())) * 50))
            chart_data.append(candle)
            
        # Füge Tags zum Chart hinzu
        chart_data[-1]["tag"] = "LIVE 1D"
        if bos_occurred:
            chart_data[-3]["tag"] = "BOS"
            
        # Grade zuweisen
        grade = "A+" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C"

        # Trade Objekt für JSON erstellen
        trade_obj = {
            "id": f"SYS-{ticker.replace('=X','').replace('=F','')}-{datetime.date.today().strftime('%m%d')}",
            "mode": "live",
            "ticker": ticker.replace("=X", "").replace("=F", "").replace("^", ""),
            "name": info["name"],
            "sector": info["sector"],
            "timeframe": "1D",
            "direction": direction,
            "score": score,
            "grade": grade,
            "entry": round(last_price, 4),
            "stopLoss": round(sl, 4),
            "takeProfit": round(tp, 4),
            "rr": RR_TARGET,
            "expectedRoiPct": RR_TARGET,
            "rvol": round(rvol, 2),
            "adx": round(adx, 1),
            "sma50": round(sma50, 2),
            "sma200": round(sma200, 2),
            "headline": f"Daily {'Bullish' if is_bullish else 'Bearish'} Setup. Kurs bei {round(last_price, 2)} nach Abgleich mit Fib-Leveln.",
            "pillar1Score": f"{min(30, score - 60)} / 30",
            "pillar1Text": f"Letztes Swing-High bei {round(last_swing_high, 2)}, Swing-Low bei {round(last_swing_low, 2)}. Fibonacci Golden Pocket liegt bei {round(fib_618, 2)}.",
            "pillar2Score": f"{min(25, int(score * 0.25))} / 25",
            "pillar2Text": f"SMA 50 ({round(sma50, 2)}) im Verhältnis zu SMA 200 ({round(sma200, 2)}). Relatives Ausbruchsvolumen liegt aktuell bei {round(rvol, 2)}x.",
            "pillar3Score": f"{min(25, int(adx * 0.8))} / 25",
            "pillar3Text": f"Marktregime-Filter: ADX notiert bei {round(adx, 1)}, was auf {'einen intakten Trend' if adx > 25 else 'eine Seitwärtsphase'} hindeutet.",
            "pillar4Score": "18 / 20",
            "pillar4Text": f"Algorithmisch berechneter Trade auf Basis von historischen 1D-Kerzen über yfinance.",
            "candles": chart_data
        }
        
        return trade_obj

    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")
        return None

# --- 4. AUSFÜHRUNG & JSON EXPORT ---
if __name__ == "__main__":
    print(f"Starte QuantSwing Backtest Engine (Datum: {datetime.datetime.now()})")
    
    all_trades = []
    
    for ticker, info in WATCHLIST.items():
        trade = analyze_ticker(ticker, info)
        if trade:
            all_trades.append(trade)
            
    # Sortiere nach Score
    all_trades = sorted(all_trades, key=lambda x: x['score'], reverse=True)
    
    # Speichere die Datei
    output_file = 'trades.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_trades, f, ensure_ascii=False, indent=2)
        
    print(f"\nErfolgreich {len(all_trades)} Trades analysiert und in '{output_file}' gespeichert.")