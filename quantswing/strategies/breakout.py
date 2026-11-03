"""
Strategie 2: Ausbruch mit Volumen (Break of Structure + RVOL)

Idee: Schließt der Kurs über dem letzten bestätigten Swing-Hoch (Strukturbruch)
und passiert das mit deutlich erhöhtem Volumen, steigen oft größere Käufer ein.

Bedingungen (alle am Tagesschluss):
  1. Langfristiger Aufwärtstrend: Kurs > SMA 200
  2. Strukturbruch: Schlusskurs erstmals über dem letzten bestätigten Swing-Hoch
  3. Volumen: relatives Volumen (RVOL) >= rvol_min
  4. Kein überdehnter Ausbruch: Schlusskurs höchstens max_ext_atr ATR über
     dem gebrochenen Swing-Hoch
Stop: `stop_atr` ATR unter dem Schlusskurs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .. import indicators as ind
from .base import Strategy


@dataclass
class BreakoutVolume(Strategy):
    key = "breakout_volume"
    title = "Ausbruch mit Volumen (BOS + RVOL)"
    description = (
        "Kauft, wenn der Kurs im Aufwärtstrend ein bestätigtes Swing-Hoch mit "
        "deutlich erhöhtem Volumen überwindet."
    )
    target_r: float = 2.0
    max_bars: int = 30
    params: dict = field(default_factory=lambda: {
        "swing_strength": 3,
        "rvol_min": 1.5,
        "max_ext_atr": 1.5,
        "stop_atr": 2.0,
    })

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        out = df.copy()
        out["SMA200"] = ind.sma(out["Close"], 200)
        out["ATR"] = ind.atr(out, 14)
        out["RVOL"] = ind.relative_volume(out["Volume"], 20)
        sw = ind.confirmed_swings(out, int(p["swing_strength"]))
        out["SWING_HIGH"] = sw["SWING_HIGH"]
        out["BOS_UP"] = ind.break_of_structure_up(out, int(p["swing_strength"]))
        return out

    def signals(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        out = df.copy()
        trend = out["Close"] > out["SMA200"]
        volume_ok = out["RVOL"] >= p["rvol_min"]
        not_extended = (out["Close"] - out["SWING_HIGH"]) <= p["max_ext_atr"] * out["ATR"]
        out["signal"] = (trend & out["BOS_UP"] & volume_ok & not_extended).fillna(False)
        out["stop"] = out["Close"] - p["stop_atr"] * out["ATR"]
        return out

    def explain(self, row: pd.Series) -> list[str]:
        p = self.params
        return [
            f"Aufwärtstrend: Kurs {row['Close']:.2f} > SMA200 {row['SMA200']:.2f}",
            f"Strukturbruch: Schluss über bestätigtem Swing-Hoch {row['SWING_HIGH']:.2f}",
            f"Volumen: RVOL {row['RVOL']:.2f} (≥ {p['rvol_min']:.1f}× Durchschnitt)",
            f"Stop {p['stop_atr']:.1f} ATR ({row['ATR']:.2f}) unter Einstiegssignal",
        ]
