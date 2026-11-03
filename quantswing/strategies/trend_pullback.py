"""
Strategie 1: Trend-Pullback ("Im Aufwärtstrend den Rücksetzer kaufen")

Idee: Steigt eine Aktie langfristig, kaufen viele Profis nicht beim Hoch,
sondern wenn der Kurs kurz zurückfällt und dann wieder dreht.

Bedingungen (alle am Tagesschluss):
  1. Langfristiger Aufwärtstrend: Kurs > SMA 200 und SMA 50 > SMA 200
  2. Trend hat Kraft: ADX > adx_min
  3. Rücksetzer: RSI(14) war in den letzten `lookback` Tagen unter `rsi_dip`
  4. Wende: Schlusskurs über dem Hoch des Vortags (Käufer übernehmen wieder)
Stop: unter dem tiefsten Tief der letzten `lookback` Tage, mindestens 1 ATR.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .. import indicators as ind
from .base import Strategy


@dataclass
class TrendPullback(Strategy):
    key = "trend_pullback"
    title = "Trend-Pullback"
    description = (
        "Kauft im intakten Aufwärtstrend (Kurs > SMA200, SMA50 > SMA200, ADX stark), "
        "nachdem ein Rücksetzer (RSI tief) wieder nach oben dreht."
    )
    target_r: float = 2.0
    max_bars: int = 40
    params: dict = field(default_factory=lambda: {
        "adx_min": 20.0,
        "rsi_dip": 40.0,
        "lookback": 5,
        "min_stop_atr": 1.0,
    })

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["SMA50"] = ind.sma(out["Close"], 50)
        out["SMA200"] = ind.sma(out["Close"], 200)
        out["ATR"] = ind.atr(out, 14)
        out["RSI"] = ind.rsi(out["Close"], 14)
        out["ADX"] = ind.adx(out, 14)["ADX"]
        return out

    def signals(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        lb = int(p["lookback"])
        out = df.copy()
        out["RSI_MIN_LB"] = out["RSI"].rolling(lb, min_periods=lb).min()
        out["LOW_LB"] = out["Low"].rolling(lb, min_periods=lb).min()

        trend = (out["Close"] > out["SMA200"]) & (out["SMA50"] > out["SMA200"])
        strong = out["ADX"] > p["adx_min"]
        dipped = out["RSI_MIN_LB"] < p["rsi_dip"]
        turn = out["Close"] > out["High"].shift(1)

        out["signal"] = (trend & strong & dipped & turn).fillna(False)
        structural_stop = out["LOW_LB"]
        atr_stop = out["Close"] - p["min_stop_atr"] * out["ATR"]
        out["stop"] = np.minimum(structural_stop, atr_stop)
        return out

    def explain(self, row: pd.Series) -> list[str]:
        p = self.params
        return [
            f"Aufwärtstrend: Kurs {row['Close']:.2f} > SMA200 {row['SMA200']:.2f}, "
            f"SMA50 {row['SMA50']:.2f} > SMA200",
            f"Trendstärke: ADX {row['ADX']:.1f} > {p['adx_min']:.0f}",
            f"Rücksetzer: RSI fiel in den letzten {int(p['lookback'])} Tagen auf "
            f"{row['RSI_MIN_LB']:.1f} (< {p['rsi_dip']:.0f}), aktuell {row['RSI']:.1f}",
            "Wende: Schlusskurs über dem Vortageshoch",
            f"Stop unter dem {int(p['lookback'])}-Tage-Tief bzw. mind. "
            f"{p['min_stop_atr']:.1f} ATR ({row['ATR']:.2f}) Abstand",
        ]
