"""
Technische Indikatoren.

Regel für dieses ganze Modul: Jeder Wert in Zeile t darf nur Daten bis
einschließlich Zeile t verwenden. Kein Indikator schaut in die Zukunft.
Das ist die wichtigste Voraussetzung für einen ehrlichen Backtest.

Glättungen (ATR, RSI, ADX) folgen der Original-Definition von J. Welles Wilder,
damit die Werte mit TradingView & Co. vergleichbar sind.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _wilder(series: pd.Series, period: int) -> pd.Series:
    """Wilder-Glättung (entspricht einem EMA mit alpha = 1/period)."""
    return series.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def sma(close: pd.Series, period: int) -> pd.Series:
    return close.rolling(period, min_periods=period).mean()


def ema(close: pd.Series, period: int) -> pd.Series:
    return close.ewm(span=period, adjust=False, min_periods=period).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["Close"].shift(1)
    return pd.concat(
        [
            df["High"] - df["Low"],
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range: durchschnittliche Tagesschwankung in Preis-Einheiten."""
    return _wilder(true_range(df), period)


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index (0–100). <30 gilt als überverkauft, >70 als überkauft."""
    delta = close.diff()
    gain = _wilder(delta.clip(lower=0.0), period)
    loss = _wilder(-delta.clip(upper=0.0), period)
    rs = gain / loss.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    # Keine Verluste im Fenster -> RSI 100 (statt NaN)
    out = out.where(~(loss == 0.0) | gain.isna(), 100.0)
    return out


def adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Average Directional Index nach Wilder.

    Rückgabe: DataFrame mit den Spalten ADX, PLUS_DI, MINUS_DI.
    ADX misst die *Stärke* eines Trends (egal welche Richtung):
    < 20 eher Seitwärtsmarkt, > 25 deutlicher Trend.
    """
    up = df["High"].diff()
    down = -df["Low"].diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index)

    atr_ = atr(df, period)
    plus_di = 100.0 * _wilder(plus_dm, period) / atr_
    minus_di = 100.0 * _wilder(minus_dm, period) / atr_
    di_sum = (plus_di + minus_di).replace(0.0, np.nan)
    dx = 100.0 * (plus_di - minus_di).abs() / di_sum
    adx_ = _wilder(dx, period)
    return pd.DataFrame({"ADX": adx_, "PLUS_DI": plus_di, "MINUS_DI": minus_di})


def relative_volume(volume: pd.Series, period: int = 20) -> pd.Series:
    """
    Relatives Volumen: heutiges Volumen geteilt durch den Durchschnitt der
    *vorherigen* `period` Tage (der heutige Tag zählt nicht zum Durchschnitt).
    """
    avg = volume.shift(1).rolling(period, min_periods=period).mean()
    return volume / avg.replace(0.0, np.nan)


def donchian_high(high: pd.Series, period: int = 20) -> pd.Series:
    """Höchstes Hoch der *vorherigen* `period` Kerzen (ohne die aktuelle)."""
    return high.shift(1).rolling(period, min_periods=period).max()


def donchian_low(low: pd.Series, period: int = 20) -> pd.Series:
    """Tiefstes Tief der *vorherigen* `period` Kerzen (ohne die aktuelle)."""
    return low.shift(1).rolling(period, min_periods=period).min()


def confirmed_swings(df: pd.DataFrame, strength: int = 3) -> pd.DataFrame:
    """
    Swing-Hochs und -Tiefs (Pivots) ohne Blick in die Zukunft.

    Ein Swing-Hoch ist ein Hoch, das höher ist als die `strength` Kerzen links
    UND rechts davon. Man weiß also erst `strength` Kerzen später, dass es ein
    Swing-Hoch war. Genau deshalb wird der Wert erst ab der Bestätigungs-Kerze
    sichtbar gemacht – sonst würde der Backtest "schummeln".

    Rückgabe-Spalten:
      SWING_HIGH  – zuletzt bestätigtes Swing-Hoch (vorwärts aufgefüllt)
      SWING_LOW   – zuletzt bestätigtes Swing-Tief (vorwärts aufgefüllt)
    """
    window = 2 * strength + 1
    h, l = df["High"], df["Low"]
    is_ph = h == h.rolling(window, center=True, min_periods=window).max()
    is_pl = l == l.rolling(window, center=True, min_periods=window).min()

    # Wert erst `strength` Kerzen später bekannt machen.
    swing_high = h.where(is_ph).shift(strength).ffill()
    swing_low = l.where(is_pl).shift(strength).ffill()
    return pd.DataFrame({"SWING_HIGH": swing_high, "SWING_LOW": swing_low})


def break_of_structure_up(df: pd.DataFrame, strength: int = 3) -> pd.Series:
    """
    Bullischer Strukturbruch (BOS): Schlusskurs schließt erstmals über dem
    zuletzt bestätigten Swing-Hoch.
    """
    sw = confirmed_swings(df, strength)
    above = df["Close"] > sw["SWING_HIGH"]
    prev_above = (df["Close"].shift(1) > sw["SWING_HIGH"].shift(1)).fillna(False)
    return (above & ~prev_above).fillna(False)
