"""
Chart-Bausteine für Confluence-Trading: Swings, Marktstruktur (BOS/CHoCH),
Fibonacci-Schenkel und Unterstützungs-/Widerstandszonen.

Grundregel (wie überall im Projekt): Ein Wert gilt erst ab der Kerze, an der
man ihn wirklich kennen konnte ("bekannt ab"). Ein Swing-Hoch an Kerze p ist
erst sicher, wenn danach `right` Kerzen tiefer geblieben sind – also ab
Kerze p + right. Alle Funktionen hier liefern Werte erst ab diesem Zeitpunkt.

Definitionen (vorab festgelegt, siehe docs/recherche/confluence_regeln.md):

Swing-Hoch (Pivot) an Kerze p:
    High[p] > alle Hochs der `left` Kerzen davor  UND
    High[p] >= alle Hochs der `right` Kerzen danach
    (bei gleich hohen Hochs zählt das erste). Swing-Tief gespiegelt.

Marktstruktur (Zustandsautomat, nachgebaut nach der Logik von LuxAlgo):
    - Merke das zuletzt bestätigte Swing-Hoch und -Tief ("Level").
    - Schlusskurs über dem ungebrochenen Swing-Hoch = Bruch nach oben.
      War der Zustand vorher abwärts (-1): CHoCH (Charakterwechsel),
      sonst: BOS (Strukturbruch in Trendrichtung). Zustand wird +1.
    - Schlusskurs unter dem Swing-Tief gespiegelt, Zustand -1.
    - Jedes Level kann nur einmal gebrochen werden.

Fibonacci-Schenkel (Long):
    Sobald ein Swing-Hoch bestätigt ist, wird vom "letzten wichtigen Tief"
    gezogen: dem tiefsten Tief zwischen dem vorherigen Swing-Hoch und diesem.
    Der Schenkel zählt nur, wenn er mindestens `min_leg_atr` ATR groß ist,
    und erlischt, wenn ein Schlusskurs unter sein Tief fällt oder ein neues
    Swing-Hoch bestätigt wird. Short gespiegelt (vom letzten wichtigen Hoch).

Zonen:
    Bestätigte Swing-Hochs UND -Tiefs der letzten `lookback` Kerzen werden
    gesammelt. Liegen mindestens `min_touches` davon innerhalb von
    `merge_atr` ATR beieinander, bilden sie eine Zone. Weil Hochs und Tiefs
    gemeinsam zählen, wird ein alter Widerstand automatisch zur Unterstützung,
    sobald der Kurs darüber steht (Rollentausch).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

LONG, SHORT = 1, -1

EVENT_LABELS = {1: "BOS ↑", 2: "CHoCH ↑", -1: "BOS ↓", -2: "CHoCH ↓"}


# ---------------------------------------------------------------------------
# Swings
# ---------------------------------------------------------------------------

def pivots(df: pd.DataFrame, left: int = 5, right: int = 5) -> pd.DataFrame:
    """
    Bestätigte Swing-Hochs und -Tiefs.

    Rückgabe (ein Wert nur an der Bestätigungskerze t = p + right, sonst NaN):
      PH, PH_BAR  – Preis und Kerzen-Position (0, 1, 2, …) des Swing-Hochs
      PL, PL_BAR  – dasselbe für Swing-Tiefs
    """
    h = df["High"].astype(float).reset_index(drop=True)
    lo = df["Low"].astype(float).reset_index(drop=True)
    n = len(df)

    left_max = h.shift(1).rolling(left, min_periods=left).max()
    right_max = h[::-1].shift(1).rolling(right, min_periods=right).max()[::-1]
    left_min = lo.shift(1).rolling(left, min_periods=left).min()
    right_min = lo[::-1].shift(1).rolling(right, min_periods=right).min()[::-1]

    is_ph = ((h > left_max) & (h >= right_max)).to_numpy()
    is_pl = ((lo < left_min) & (lo <= right_min)).to_numpy()

    ph = np.full(n, np.nan)
    ph_bar = np.full(n, np.nan)
    pl = np.full(n, np.nan)
    pl_bar = np.full(n, np.nan)
    for p in np.flatnonzero(is_ph):
        t = p + right
        if t < n:
            ph[t], ph_bar[t] = h.iat[p], p
    for p in np.flatnonzero(is_pl):
        t = p + right
        if t < n:
            pl[t], pl_bar[t] = lo.iat[p], p
    return pd.DataFrame({"PH": ph, "PH_BAR": ph_bar, "PL": pl, "PL_BAR": pl_bar}, index=df.index)


# ---------------------------------------------------------------------------
# Marktstruktur
# ---------------------------------------------------------------------------

def market_structure(df: pd.DataFrame, left: int = 5, right: int = 5,
                     piv: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Zustandsautomat für BOS/CHoCH.

    Rückgabe je Kerze (Stand nach dem Schlusskurs dieser Kerze):
      BIAS        +1 = Aufwärtsstruktur, -1 = Abwärtsstruktur, 0 = noch unbekannt
      EVENT       +1 BOS ↑, +2 CHoCH ↑, -1 BOS ↓, -2 CHoCH ↓, 0 = nichts
      LEVEL_HIGH  aktuelles (letztes bestätigtes) Swing-Hoch, LEVEL_HIGH_BAR seine Kerze
      LEVEL_LOW   aktuelles Swing-Tief, LEVEL_LOW_BAR seine Kerze
    """
    piv = pivots(df, left, right) if piv is None else piv
    close = df["Close"].to_numpy(float)
    ph, ph_bar = piv["PH"].to_numpy(float), piv["PH_BAR"].to_numpy(float)
    pl, pl_bar = piv["PL"].to_numpy(float), piv["PL_BAR"].to_numpy(float)
    n = len(df)

    bias_out = np.zeros(n, dtype=int)
    event_out = np.zeros(n, dtype=int)
    top_out = np.full(n, np.nan)
    bot_out = np.full(n, np.nan)
    top_bar_out = np.full(n, np.nan)
    bot_bar_out = np.full(n, np.nan)

    bias = 0
    top = bot = top_bar = bot_bar = np.nan
    top_broken = bot_broken = True
    for t in range(n):
        if not np.isnan(ph[t]):
            top, top_bar, top_broken = ph[t], ph_bar[t], False
        if not np.isnan(pl[t]):
            bot, bot_bar, bot_broken = pl[t], pl_bar[t], False
        c = close[t]
        if not top_broken and c > top:
            event_out[t] = 2 if bias == SHORT else 1
            bias, top_broken = LONG, True
        elif not bot_broken and c < bot:
            event_out[t] = -2 if bias == LONG else -1
            bias, bot_broken = SHORT, True
        bias_out[t] = bias
        top_out[t], bot_out[t] = top, bot
        top_bar_out[t], bot_bar_out[t] = top_bar, bot_bar
    return pd.DataFrame({"BIAS": bias_out, "EVENT": event_out,
                         "LEVEL_HIGH": top_out, "LEVEL_HIGH_BAR": top_bar_out,
                         "LEVEL_LOW": bot_out, "LEVEL_LOW_BAR": bot_bar_out}, index=df.index)


# ---------------------------------------------------------------------------
# Fibonacci
# ---------------------------------------------------------------------------

def fib_price(leg_high: float, leg_low: float, ratio: float, direction: int = LONG) -> float:
    """
    Preis eines Fibonacci-Niveaus.
    Long  (Schenkel Tief → Hoch): Hoch − ratio × Spanne   (0,618 = 61,8 % Rücksetzer)
    Short (Schenkel Hoch → Tief): Tief + ratio × Spanne
    Werte > 1 bzw. < 0 ergeben Extensionen (z.B. −0,272 = Ziel über dem Hoch).
    """
    span = leg_high - leg_low
    return leg_high - ratio * span if direction == LONG else leg_low + ratio * span


def fib_legs(df: pd.DataFrame, piv: pd.DataFrame, atr: pd.Series,
             min_leg_atr: float = 3.0, max_lookback: int = 120) -> pd.DataFrame:
    """
    Aktiver Fibonacci-Schenkel je Kerze (NaN = kein gültiger Schenkel).

      UP_HI, UP_LO   Long-Schenkel: letztes wichtiges Tief → bestätigtes Swing-Hoch
      DN_HI, DN_LO   Short-Schenkel: letztes wichtiges Hoch → bestätigtes Swing-Tief
    """
    high = df["High"].to_numpy(float)
    low = df["Low"].to_numpy(float)
    close = df["Close"].to_numpy(float)
    a = atr.to_numpy(float)
    ph, ph_bar = piv["PH"].to_numpy(float), piv["PH_BAR"].to_numpy(float)
    pl, pl_bar = piv["PL"].to_numpy(float), piv["PL_BAR"].to_numpy(float)
    n = len(df)
    out = {k: np.full(n, np.nan) for k in ("UP_HI", "UP_LO", "DN_HI", "DN_LO")}

    up = dn = None                 # aktive Schenkel (hi, lo)
    prev_ph_bar = prev_pl_bar = None
    for t in range(n):
        if not np.isnan(ph[t]):
            p = int(ph_bar[t])
            start = max(prev_ph_bar if prev_ph_bar is not None else 0, p - max_lookback)
            leg_lo = low[start:p + 1].min()
            up = (ph[t], leg_lo) if np.isfinite(a[t]) and ph[t] - leg_lo >= min_leg_atr * a[t] else None
            prev_ph_bar = p
        if not np.isnan(pl[t]):
            p = int(pl_bar[t])
            start = max(prev_pl_bar if prev_pl_bar is not None else 0, p - max_lookback)
            leg_hi = high[start:p + 1].max()
            dn = (leg_hi, pl[t]) if np.isfinite(a[t]) and leg_hi - pl[t] >= min_leg_atr * a[t] else None
            prev_pl_bar = p
        if up is not None and close[t] < up[1]:
            up = None               # Tief unterschritten: Schenkel ungültig
        if dn is not None and close[t] > dn[0]:
            dn = None
        if up is not None:
            out["UP_HI"][t], out["UP_LO"][t] = up
        if dn is not None:
            out["DN_HI"][t], out["DN_LO"][t] = dn
    return pd.DataFrame(out, index=df.index)


# ---------------------------------------------------------------------------
# Unterstützungs- und Widerstandszonen
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Zone:
    bottom: float
    top: float
    touches: int

    def contains(self, price: float) -> bool:
        return self.bottom <= price <= self.top

    @property
    def mid(self) -> float:
        return (self.bottom + self.top) / 2


class PivotBook:
    """Alle bestätigten Swings eines Symbols – abfragbar "Stand Kerze t"."""

    def __init__(self, piv: pd.DataFrame):
        rows = []
        for col, bar_col in (("PH", "PH_BAR"), ("PL", "PL_BAR")):
            known = np.flatnonzero(piv[col].notna().to_numpy())
            for t in known:
                rows.append((piv[col].iat[t], piv[bar_col].iat[t], t))
        rows.sort(key=lambda r: r[2])
        arr = np.array(rows, dtype=float).reshape(-1, 3)
        self.price, self.bar, self.known = arr[:, 0], arr[:, 1], arr[:, 2]

    def active(self, t: int, lookback: int = 250) -> np.ndarray:
        """Preise aller Swings, die an Kerze t bekannt sind und höchstens `lookback` alt."""
        k = np.searchsorted(self.known, t, side="right")
        price, bar = self.price[:k], self.bar[:k]
        return price[bar >= t - lookback]


def cluster_zones(prices: np.ndarray, merge_dist: float, pad: float = 0.0,
                  min_touches: int = 2) -> list[Zone]:
    """
    Fasst nahe beieinanderliegende Swing-Preise zu Zonen zusammen.
    Zwei Preise gehören zusammen, wenn ihr Abstand <= merge_dist ist
    (Ketten-Regel). Jede Zone wird um `pad` nach oben und unten verbreitert.
    """
    if len(prices) == 0 or not np.isfinite(merge_dist) or merge_dist <= 0:
        return []
    p = np.sort(prices)
    zones, start = [], 0
    for i in range(1, len(p) + 1):
        if i == len(p) or p[i] - p[i - 1] > merge_dist:
            group = p[start:i]
            if len(group) >= min_touches:
                zones.append(Zone(group[0] - pad, group[-1] + pad, len(group)))
            start = i
    return zones


def zones_at(book: PivotBook, t: int, atr_t: float, lookback: int = 250,
             merge_atr: float = 0.5, pad_atr: float = 0.25, min_touches: int = 2) -> list[Zone]:
    """Alle Zonen, die an Kerze t bekannt sind (Breiten in ATR von Kerze t)."""
    if not np.isfinite(atr_t):
        return []
    return cluster_zones(book.active(t, lookback), merge_atr * atr_t, pad_atr * atr_t, min_touches)
