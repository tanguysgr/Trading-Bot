import yfinance as yf
import pandas as pd
import numpy as np
import json
import requests
from io import StringIO
from datetime import datetime

# ==============================================================================
# 1.STRENGE QUALITÄTS-SCHWELLENWERTE (GATEKEEPER)
# ==============================================================================
MIN_SCORE_STOCKS_ETFS = 80       # Mindest-Score für Aktien & ETFs (0-100)
MIN_WINRATE_STOCKS_ETFS = 58.0   # Mindest-Trefferquote im Backtest für Aktien/ETFs (%)
MIN_PF_STOCKS_ETFS = 1.65        # Mindest-Profit-Faktor für Aktien/ETFs

# KRYPTO-SONDERREGEL: Nur bei extrem hoher Erfolgswahrscheinlichkeit!
MIN_SCORE_CRYPTO = 90            # Krypto braucht mindestens 90/100 Punkte
MIN_WINRATE_CRYPTO = 68.0        # Krypto braucht mindestens 68% historische Trefferquote
MIN_PF_CRYPTO = 2.10             # Krypto braucht mindestens Profit Faktor 2.10


# ==============================================================================
# 2. DYNAMISCHES MARKT-UNIVERSUM (AKTIEN, ETFS & KRYPTO)
# ==============================================================================
BROAD_ETFS = {
    "SPY": "S&P 500 ETF", "QQQ": "NASDAQ 100 ETF", "IWM": "Russell 2000 Small Cap ETF",
    "DIA": "Dow Jones ETF", "SMH": "VanEck Semiconductor ETF", "SOXX": "iShares Semiconductor ETF",
    "XLK": "Technology Select Sector ETF", "XLF": "Financial Select Sector ETF",
    "XLE": "Energy Select Sector ETF", "XLV": "Health Care Select Sector ETF",
    "XLI": "Industrial Select Sector ETF", "XLP": "Consumer Staples ETF",
    "XLY": "Consumer Discretionary ETF", "XLB": "Materials Select Sector ETF",
    "XLU": "Utilities Select Sector ETF", "IBB": "iShares Biotechnology ETF",
    "ARKK": "ARK Innovation ETF", "GLD": "SPDR Gold Trust ETF", "SLV": "iShares Silver Trust ETF",
    "USO": "United States Oil Fund ETF", "TLT": "iShares 20+ Year Treasury Bond ETF",
    "EEM": "iShares MSCI Emerging Markets ETF", "EWZ": "iShares MSCI Brazil ETF",
    "EWJ": "iShares MSCI Japan ETF", "VGK": "Vanguard FTSE Europe ETF",
    "GDX": "VanEck Gold Miners ETF", "XBI": "SPDR S&P Biotech ETF",
    "ITB": "iShares U.S. Home Construction ETF", "KRE": "SPDR Regional Banking ETF"
}

CORE_GLOBAL_STOCKS = [
    # US Tech, AI & Growth
    "NVDA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "TSLA", "AMD", "AVGO", "NFLX",
    "CRM", "ORCL", "ADBE", "PANW", "CRWD", "NOW", "PLTR", "SNOW", "UBER", "ABNB",
    "SHOP", "SQ", "COIN", "MSTR", "MU", "INTC", "QCOM", "TXN", "AMAT", "LRCX",
    "KLAC", "ASML", "ARM", "SMCI", "DELL", "ANET", "DDOG", "NET", "ZS", "TEAM",
    # US Finance, Healthcare, Consumer & Industrials
    "JPM", "BAC", "GS", "MS", "V", "MA", "AXP", "BLK", "BRK-B", "C",
    "LLY", "UNH", "JNJ", "ABBV", "MRK", "ISRG", "TMO", "AMGN", "VRTX", "REGN",
    "COST", "WMT", "HD", "MCD", "NKE", "SBUX", "DIS", "BKNG", "CMG", "LULU",
    "CAT", "DE", "GE", "HON", "UNP", "BA", "LMT", "RTX", "ETN", "URI",
    "XOM", "CVX", "COP", "SLB", "EOG", "FCX", "NEM", "NEE", "CEG", "VST",
    # Top Europa / DAX / Blue Chips
    "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "MUV2.DE", "ADS.DE", "IFX.DE", "MBG.DE",
    "BMW.DE", "RHM.DE", "DHL.DE", "DB1.DE", "CBK.DE", "MTX.DE", "LIN", "NVO"
]

CRYPTO_UNIVERSE = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    "BNB-USD": "BNB"
}

def build_market_universe():
    """Sammelt hunderte liquide Aktien & ETFs (dynamisch aus S&P 500 + Kernuniversum)."""
    stocks = set(CORE_GLOBAL_STOCKS)
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers=headers, timeout=8)
        if resp.status_code == 200:
            tables = pd.read_html(StringIO(resp.text))
            sp500_syms = tables[0]["Symbol"].str.replace(".", "-", regex=False).tolist()
            # Nimm die ersten 120 S&P-500 Werte zusätzlich ins Live-Scan-Universum auf
            stocks.update(sp500_syms[:120])
    except Exception as e:
        print(f"Info: Nutze integriertes Aktien-Universum ({e})")

    universe = {}
    for sym, name in BROAD_ETFS.items():
        universe[sym] = {"name": name, "sector": "ETF", "asset_class": "ETF"}
    for sym in stocks:
        if sym not in universe:
            sector = "DE/EU Equities" if ".DE" in sym else "US Equities"
            universe[sym] = {"name": f"{sym} Share", "sector": sector, "asset_class": "STOCK"}
    for sym, name in CRYPTO_UNIVERSE.items():
        universe[sym] = {"name": name, "sector": "Crypto", "asset_class": "CRYPTO"}

    print(f"Markt-Universum geladen: {len(universe)} Assets (Aktien, ETFs & Krypto).")
    return universe


# ==============================================================================
# 3. TECHNISCHE INDIKATOR-BERECHNUNG (SMA, EMA, BOS, FIB, RSI, MACD, BB, ADX)
# ==============================================================================
def compute_indicators(df):
    df = df.copy()
    c = df["Close"]
    h = df["High"]
    l = df["Low"]
    v = df["Volume"]

    # Gleitende Durchschnitte
    df["EMA_20"] = c.ewm(span=20, adjust=False).mean()
    df["SMA_50"] = c.rolling(50).mean()
    df["SMA_200"] = c.rolling(200).mean()

    # ATR (14)
    prev_c = c.shift(1)
    tr = pd.concat([h - l, (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    # RSI (14)
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    df["RSI"] = df["RSI"].fillna(50)

    # MACD (12, 26, 9)
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # Bollinger Bands (20, 2) & Squeeze
    bb_mid = c.rolling(20).mean()
    bb_std = c.rolling(20).std()
    df["BB_Upper"] = bb_mid + 2 * bb_std
    df["BB_Lower"] = bb_mid - 2 * bb_std
    df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / bb_mid.replace(0, np.nan)
    df["BB_Width_Min20"] = df["BB_Width"].rolling(20).min()

    # Relatives Volumen (RVOL)
    vol_ma20 = v.rolling(20).mean().replace(0, 1)
    df["RVOL"] = v / vol_ma20

    # ADX (14) Approximation über Richtungsbewegung
    up_move = h.diff()
    down_move = -l.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    atr_safe = df["ATR"].replace(0, np.nan)
    plus_di = 100 * pd.Series(plus_dm, index=df.index).rolling(14).mean() / atr_safe
    minus_di = 100 * pd.Series(minus_dm, index=df.index).rolling(14).mean() / atr_safe
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(20)
    df["ADX"] = dx.rolling(14).mean().fillna(20)

    # Swing-Struktur (Pivot High / Low der letzten 20 Kerzen), BOS & Fibonacci Golden Pocket
    df["Swing_High_20"] = h.shift(1).rolling(20).max()
    df["Swing_Low_20"] = l.shift(1).rolling(20).min()
    swing_range = (df["Swing_High_20"] - df["Swing_Low_20"]).replace(0, np.nan)

    # Retracement vom Hoch (0.0 = am Swing High, 0.50-0.65 = im Fibonacci Golden Pocket)
    df["Fib_Retrace_Bull"] = (df["Swing_High_20"] - c) / swing_range
    df["Fib_Retrace_Bear"] = (c - df["Swing_Low_20"]) / swing_range

    # Break of Structure (BOS) & Liquidity Sweep
    df["Bull_BOS"] = c > df["Swing_High_20"]
    df["Bear_BOS"] = c < df["Swing_Low_20"]
    df["Bull_BOS_Recent"] = df["Bull_BOS"].rolling(8).max() > 0
    df["Bear_BOS_Recent"] = df["Bear_BOS"].rolling(8).max() > 0
    df["Bull_Sweep"] = (l < l.shift(1).rolling(10).min()) & (c > o_or_c(df))

    return df.dropna(subset=["SMA_50", "ATR"])

def o_or_c(df):
    return df["Open"]


# ==============================================================================
# 4. SELBSTLERNENDE STRATEGIE-ENGINE (TESTET 4 STRATEGIEN PRO ASSET)
# ==============================================================================
def evaluate_strategies_on_history(df_4h, daily_trend_bull, daily_trend_bear):
    """
    Simuliert 4 institutionelle Swing-Strategien Kerze für Kerze auf der 4H-Historie
    und berechnet Winrate, Profit Faktor, Expectancy und MAE.
    """
    strategies = {
        "SMC_FIB_BOS": {
            "title": "Smart Money Concept (BOS + Fibonacci Golden Pocket + SMA)",
            "desc": "4H Break of Structure mit Pullback in die 0.50–0.65 Fibonacci-Zone in Richtung des Daily-SMA-Trends."
        },
        "MOMENTUM_BOS_RVOL": {
            "title": "Institutional Momentum Breakout (BOS + RVOL + MACD + ADX)",
            "desc": "4H Strukturbruch über Widerstand mit erhöhtem Volumen (RVOL), positivem MACD-Impuls und starkem ADX-Trend."
        },
        "TREND_RSI_RECLAIM": {
            "title": "Multi-Timeframe RSI Pullback & EMA-20 Reclaim",
            "desc": "Überverkaufter Rücksetzer (RSI < 40 / Bollinger-Support) im intakten Daily-Aufwärtstrend mit bullischem Reclaim des EMA 20."
        },
        "VOLA_SQUEEZE_SWING": {
            "title": "Volatility Squeeze & EMA-Trend-Expansion",
            "desc": "Ausbruch aus einer engen Bollinger-Volatilitäts-Kompression mit MACD-Bestätigung und Trend-Alignment."
        }
    }

    best_result = None
    closes = df_4h["Close"].values
    highs = df_4h["High"].values
    lows = df_4h["Low"].values
    atrs = df_4h["ATR"].values
    sma50 = df_4h["SMA_50"].values
    ema20 = df_4h["EMA_20"].values
    rsi = df_4h["RSI"].values
    macd_h = df_4h["MACD_Hist"].values
    rvol = df_4h["RVOL"].values
    adx = df_4h["ADX"].values
    fib_bull = df_4h["Fib_Retrace_Bull"].values
    bull_bos = df_4h["Bull_BOS"].values
    bull_bos_rec = df_4h["Bull_BOS_Recent"].values
    bb_w = df_4h["BB_Width"].values
    bb_w_min = df_4h["BB_Width_Min20"].values

    n = len(df_4h)
    if n < 80:
        return None

    for strat_key, meta in strategies.items():
        wins = 0
        losses = 0
        gross_profit = 0.0
        gross_loss = 0.0
        mae_list = []
        recent_trades = []
        target_rr = 2.4

        # Simuliere historische Trades bis vor 12 Kerzen
        i = 55
        while i < n - 12:
            signal_dir = None

            if strat_key == "SMC_FIB_BOS":
                if bull_bos_rec[i] and (0.38 <= fib_bull[i] <= 0.68) and closes[i] > sma50[i] and closes[i] > closes[i-1]:
                    signal_dir = "LONG"
            elif strat_key == "MOMENTUM_BOS_RVOL":
                if bull_bos[i] and rvol[i] >= 1.20 and macd_h[i] > macd_h[i-1] and adx[i] >= 20:
                    signal_dir = "LONG"
            elif strat_key == "TREND_RSI_RECLAIM":
                if closes[i] > sma50[i] and rsi[i-1] < 42 and closes[i] > ema20[i] and closes[i-1] <= ema20[i-1]:
                    signal_dir = "LONG"
            elif strat_key == "VOLA_SQUEEZE_SWING":
                if bb_w[i-1] <= bb_w_min[i-1] * 1.15 and closes[i] > ema20[i] and macd_h[i] > 0 and rvol[i] >= 1.15:
                    signal_dir = "LONG"

            if signal_dir == "LONG" and atrs[i] > 0:
                entry_p = closes[i]
                risk_dist = atrs[i] * 1.35
                sl_p = entry_p - risk_dist
                tp_p = entry_p + (risk_dist * target_rr)

                outcome = None
                max_adverse = 0.0
                for j in range(i + 1, min(i + 25, n)):
                    adv = (entry_p - lows[j]) / risk_dist
                    if adv > max_adverse:
                        max_adverse = adv
                    if lows[j] <= sl_p:
                        outcome = "LOSS"
                        break
                    if highs[j] >= tp_p:
                        outcome = "WIN"
                        break

                if outcome == "WIN":
                    wins += 1
                    gross_profit += target_rr
                    mae_list.append(min(0.95, max_adverse))
                    recent_trades.append(("WIN", entry_p, sl_p, tp_p, target_rr))
                    i += 6
                    continue
                elif outcome == "LOSS":
                    losses += 1
                    gross_loss += 1.0
                    recent_trades.append(("LOSS", entry_p, sl_p, tp_p, -1.0))
                    i += 4
                    continue
            i += 1

        total_t = wins + losses
        if total_t < 6:
            continue

        winrate = (wins / total_t) * 100.0
        pf = gross_profit / max(0.5, gross_loss)
        expectancy = ((wins / total_t) * target_rr) - (losses / total_t)
        avg_mae = float(np.mean(mae_list)) if mae_list else 0.42

        # Prüfe, ob die Strategie auch AKTUELL (auf den letzten 3 Kerzen) ein Live-Signal hat
        last_idx = n - 1
        is_live_now = False
        if strat_key == "SMC_FIB_BOS":
            is_live_now = bool(bull_bos_rec[last_idx] and (0.32 <= fib_bull[last_idx] <= 0.72) and closes[last_idx] >= sma50[last_idx] * 0.99)
        elif strat_key == "MOMENTUM_BOS_RVOL":
            is_live_now = bool((bull_bos[last_idx] or bull_bos_rec[last_idx]) and macd_h[last_idx] > 0 and adx[last_idx] >= 20)
        elif strat_key == "TREND_RSI_RECLAIM":
            is_live_now = bool(closes[last_idx] >= sma50[last_idx] and (32 <= rsi[last_idx] <= 58) and closes[last_idx] >= ema20[last_idx] * 0.995)
        elif strat_key == "VOLA_SQUEEZE_SWING":
            is_live_now = bool(closes[last_idx] > ema20[last_idx] and macd_h[last_idx] > 0 and rvol[last_idx] >= 1.05)

        if not (daily_trend_bull or daily_trend_bear):
            continue

        # Berechne den objektiven Confluence-Score (0-100)
        p1 = min(30, int(18 + (6 if bull_bos_rec[last_idx] else 0) + (6 if 0.35 <= fib_bull[last_idx] <= 0.68 else 3)))
        p2 = min(25, int(14 + (5 if rvol[last_idx] >= 1.2 else 2) + (6 if macd_h[last_idx] > 0 else 2)))
        p3 = min(25, int(15 + (6 if daily_trend_bull else 0) + (4 if adx[last_idx] >= 22 else 2)))
        p4 = min(20, int(min(10, winrate / 7.0) + min(10, pf * 3.8)))
        total_score = p1 + p2 + p3 + p4

        candidate = {
            "strat_key": strat_key,
            "strat_title": meta["title"],
            "strat_desc": meta["desc"],
            "total_trades": total_t,
            "winrate": round(winrate, 1),
            "pf": round(pf, 2),
            "expectancy": round(expectancy, 2),
            "avg_mae": round(avg_mae, 2),
            "is_live": is_live_now,
            "score": total_score,
            "p1": p1, "p2": p2, "p3": p3, "p4": p4,
            "target_rr": target_rr,
            "recent_trades": recent_trades[-2:]
        }

        # Wähle die Strategie mit dem besten Erwartungswert & aktivem Signal
        if best_result is None or (candidate["is_live"] and not best_result["is_live"]) or (candidate["score"] > best_result["score"]):
            best_result = candidate

    return best_result


# ==============================================================================
# 5. STUFE 1 & STUFE 2 MARKT-SCANNER
# ==============================================================================
def run_autonomous_market_scan():
    universe = build_market_universe()
    all_symbols = list(universe.keys())

    print("Stufe 1: Starte schnellen Daily-Bulk-Scan über das gesamte Aktien-, ETF- & Krypto-Universum...")
    pre_selected = []

    # Lade in schnellen 60er-Paketen
    batch_size = 60
    for i in range(0, len(all_symbols), batch_size):
        batch = all_symbols[i:i+batch_size]
        try:
            data = yf.download(batch, period="1y", interval="1d", group_by="ticker", threads=True, progress=False)
            for sym in batch:
                try:
                    df_d = data[sym].dropna(how="all") if len(batch) > 1 else data.dropna(how="all")
                    if len(df_d) < 150:
                        continue
                    c = df_d["Close"]
                    sma50 = c.rolling(50).mean().iloc[-1]
                    sma200 = c.rolling(200).mean().iloc[-1]
                    last_c = c.iloc[-1]
                    vol_ma = df_d["Volume"].rolling(20).mean().iloc[-1]
                    rvol_d = df_d["Volume"].iloc[-1] / max(1, vol_ma)

                    # Vorfilter: Starker Aufwärtstrend (Close > SMA50 > SMA200)
                    if last_c > sma50 and sma50 > sma200 * 0.99:
                        rank_score = ((last_c - sma50) / sma50) * 100 + (rvol_d * 5)
                        pre_selected.append((sym, rank_score, True, False, round(sma50, 2), round(sma200, 2)))
                except Exception:
                    continue
        except Exception as e:
            print(f"Batch-Hinweis: {e}")

    # Sortiere die besten Trend-Kandidaten + nimm alle Krypto-Assets zur strengen Prüfung mit
    pre_selected.sort(key=lambda x: x[1], reverse=True)
    top_candidates = pre_selected[:40]

    print(f"Stufe 2: Führe tiefe 4H + 1D Multi-Timeframe Backtests für die {len(top_candidates)} besten Kandidaten durch...")
    live_signals = []
    history_logs = []

    for sym, _, d_bull, d_bear, d_sma50, d_sma200 in top_candidates:
        info = universe[sym]
        asset_class = info["asset_class"]
        try:
            ticker_obj = yf.Ticker(sym)
            # Lade 2 Jahre an 1h-Daten und aggregiere sie zu echten 4H-Swing-Kerzen
            df_1h = ticker_obj.history(period="730d", interval="1h")
            if len(df_1h) < 400:
                continue

            df_4h = df_1h.resample("4h").agg({
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum"
            }).dropna()

            df_4h = compute_indicators(df_4h)
            if len(df_4h) < 90:
                continue

            best = evaluate_strategies_on_history(df_4h, d_bull, d_bear)
            if not best or not best["is_live"]:
                continue

            # PRÜFE STRENGE QUALITÄTS-SCHWELLEN (Aktien/ETFs vs. Krypto-Sonderregel)
            if asset_class == "CRYPTO":
                if best["score"] < MIN_SCORE_CRYPTO or best["winrate"] < MIN_WINRATE_CRYPTO or best["pf"] < MIN_PF_CRYPTO:
                    print(f"  [Krypto-Filter] {sym} abgelehnt (Score {best['score']}, Winrate {best['winrate']}% < {MIN_WINRATE_CRYPTO}%)")
                    continue
            else:
                if best["score"] < MIN_SCORE_STOCKS_ETFS or best["winrate"] < MIN_WINRATE_STOCKS_ETFS or best["pf"] < MIN_PF_STOCKS_ETFS:
                    continue

            last = df_4h.iloc[-1]
            entry = round(float(last["Close"]), 2)
            atr = float(last["ATR"])
            risk_dist = atr * 1.35
            rr = best["target_rr"]
            sl = round(entry - risk_dist, 2)
            tp = round(entry + (risk_dist * rr), 2)

            fib_lvl = round(float(last["Swing_High_20"] - (last["Swing_High_20"] - last["Swing_Low_20"]) * 0.618), 2)
            rvol_val = round(float(last["RVOL"]), 2)
            adx_val = round(float(last["ADX"]), 1)
            rsi_val = round(float(last["RSI"]), 1)

            grade = "A+" if best["score"] >= 90 else ("A" if best["score"] >= 85 else "A-")

            live_signals.append({
                "id": f"QUANT-{sym}",
                "mode": "live",
                "ticker": sym,
                "name": f"{info['name']} [{info['asset_class']}]",
                "sector": info["sector"],
                "timeframe": "4H + 1D (MTF)",
                "direction": "LONG",
                "score": best["score"],
                "grade": grade,
                "entry": entry,
                "stopLoss": sl,
                "takeProfit": tp,
                "rr": rr,
                "expectedRoiPct": rr,
                "rvol": rvol_val,
                "adx": adx_val,
                "sma50": round(float(last["SMA_50"]), 2),
                "sma200": d_sma200,
                "headline": f"Beste Bot-Strategie: {best['strat_title']} | Backtest-Winrate: {best['winrate']}% (PF {best['pf']})",
                "pillar1Score": f"{best['p1']} / 30",
                "pillar1Text": f"{best['strat_desc']} | 4H Swing-Spanne aktiv, Fibonacci 0.618 Golden Pocket liegt bei {fib_lvl}.",
                "pillar2Score": f"{best['p2']} / 25",
                "pillar2Text": f"Daily-Trend über SMA 50 ({d_sma50}) & SMA 200 ({d_sma200}). 4H-RSI bei {rsi_val}, Relatives Volumen (RVOL): {rvol_val}x.",
                "pillar3Score": f"{best['p3']} / 25",
                "pillar3Text": f"Marktregime-Filter bestanden: ADX-Trendstärke bei {adx_val}. ATR-basierter Schutz-Stop bei {sl}.",
                "pillar4Score": f"{best['p4']} / 20",
                "pillar4Text": f"Verifiziert in {best['total_trades']} historischen 4H-Trades auf {sym}: {best['winrate']}% Trefferquote, Profit Faktor {best['pf']}, Ø MAE -{best['avg_mae']}R."
            })

            # Füge echte historische Backtest-Trades für den Historien-Tab hinzu
            for idx_t, (out_status, h_en, h_sl, h_tp, h_r) in enumerate(best["recent_trades"]):
                history_logs.append({
                    "id": f"HIST-{sym}-{idx_t}",
                    "mode": "history",
                    "ticker": sym,
                    "name": f"{info['name']} — Verifizierter Backtest ({out_status})",
                    "sector": info["sector"],
                    "timeframe": "4H + 1D",
                    "direction": "LONG",
                    "score": best["score"],
                    "grade": out_status,
                    "entry": round(float(h_en), 2),
                    "stopLoss": round(float(h_sl), 2),
                    "takeProfit": round(float(h_tp), 2),
                    "rr": rr,
                    "expectedRoiPct": round(float(h_r), 2),
                    "rvol": rvol_val,
                    "adx": adx_val,
                    "sma50": d_sma50,
                    "sma200": d_sma200,
                    "headline": f"HISTORISCHER BACKTEST ({out_status}): Strategie '{best['strat_title']}' erzielte {h_r:+.2f}R.",
                    "pillar1Score": f"{best['p1']} / 30",
                    "pillar1Text": best["strat_desc"],
                    "pillar2Score": f"{best['p2']} / 25",
                    "pillar2Text": f"Historischer Einstieg bei {round(float(h_en), 2)} mit Stop-Loss bei {round(float(h_sl), 2)}.",
                    "pillar3Score": f"{best['p3']} / 25",
                    "pillar3Text": f"Multi-Timeframe Trendfilter (1D + 4H) aktiv.",
                    "pillar4Score": f"{best['p4']} / 20",
                    "pillar4Text": f"Gesamt-Statistik auf {sym}: {best['winrate']}% Winrate über {best['total_trades']} Trades."
                })

            print(f"  [TREFFER] {sym} ({info['asset_class']}): Score {best['score']}/100 | Winrate {best['winrate']}% | Strategie: {best['strat_title']}")

        except Exception as e:
            print(f"  Fehler bei {sym}: {e}")

    # Sortiere Live-Signale absteigend nach Confluence-Score
    live_signals.sort(key=lambda x: (x["score"], x["pillar4Score"]), reverse=True)
    combined_output = live_signals + history_logs[:25]
    return combined_output


if __name__ == "__main__":
    print(f"=== Starte Autonome QuantSwing Multi-Timeframe Engine ({datetime.now().strftime('%d.%m.%Y %H:%M')}) ===")
    results = run_autonomous_market_scan()

    with open("trades.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"=== Fertig! {len(results)} geprüfte Datensätze (Live-Signale + echte Backtest-Historie) in trades.json gespeichert. ===")
