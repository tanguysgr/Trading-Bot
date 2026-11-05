"""
Marktkontext: Informationen, die über ein einzelnes Symbol hinausgehen.

1. Markt-Regime (REGIME_OK)
   Ist der Gesamtmarkt in einem Aufwärtstrend? Gemessen am Leitwert
   (Aktien: S&P-500-ETF SPY, Krypto: Bitcoin) über seiner 200-Tage-Linie.
   Viele Strategien funktionieren in Bärenmärkten deutlich schlechter –
   der Filter soll genau dann pausieren.

2. Relative Stärke (RS_RANK)
   Wie gut lief ein Wert in den letzten ~6 Monaten im Vergleich zu allen
   anderen Werten des Universums? 1,0 = bester, 0,0 = schlechtester.
   "Momentum" gehört zu den am besten belegten Effekten am Aktienmarkt:
   Starke Aktien bleiben im Schnitt eine Weile stark.

Gegen Blick in die Zukunft: Beide Werte werden für einen Tag t immer nur aus
Daten STRIKT VOR t gebildet (also vom Vortag). Das ist wichtig, weil Börsen
in verschiedenen Zeitzonen schließen: Wenn Tokio am Tag t schließt, kennt man
den US-Schlusskurs vom Tag t noch nicht.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

RS_LOOKBACK = 126       # ~6 Monate Handelstage
REGIME_SMA = 200


def asof_before(series: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
    """Für jedes Datum in `index`: letzter Wert von `series` STRIKT davor."""
    if series is None or series.empty:
        return pd.Series(np.nan, index=index)
    left = pd.DataFrame({"t": pd.DatetimeIndex(index).astype("datetime64[ns]")})
    right = pd.DataFrame({"t": pd.DatetimeIndex(series.index).astype("datetime64[ns]"),
                          "v": series.to_numpy(float)}).sort_values("t")
    merged = pd.merge_asof(left, right, on="t", allow_exact_matches=False)
    return pd.Series(merged["v"].to_numpy(), index=index)


def regime_flag(close: pd.Series, period: int = REGIME_SMA) -> pd.Series:
    """1.0 = Kurs über SMA(period), 0.0 = darunter, NaN = noch nicht genug Daten."""
    sma = close.rolling(period, min_periods=period).mean()
    flag = (close > sma).astype(float)
    flag[sma.isna()] = np.nan
    return flag


def rs_rank(closes: dict[str, pd.Series], lookback: int = RS_LOOKBACK,
            min_count: int | None = None) -> dict[str, pd.Series]:
    """
    Rang der `lookback`-Tage-Rendite je Symbol (0..1) über alle Symbole,
    bereits um einen Tag verzögert (siehe asof_before).
    """
    if not closes:
        return {}
    if min_count is None:
        min_count = max(3, min(20, len(closes) // 2))
    rets = pd.DataFrame({s: c / c.shift(lookback) - 1.0 for s, c in closes.items()})
    rets = rets.sort_index().ffill(limit=5)        # andere Feiertage überbrücken
    rank = rets.rank(axis=1, pct=True)
    rank[rets.notna().sum(axis=1) < min_count] = np.nan
    return {s: asof_before(rank[s], closes[s].index) for s in closes}
