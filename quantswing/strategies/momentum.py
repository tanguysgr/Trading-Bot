"""
Strategie 3: Relative Stärke (Momentum-Trendfolge)

Idee: Aktien, die in den letzten Monaten besser liefen als fast alle anderen,
laufen im Schnitt noch eine Weile weiter ("Momentum", wissenschaftlich gut
belegt, z.B. Jegadeesh & Titman 1993). Man kauft die Stärksten, solange der
Gesamtmarkt mitspielt, und lässt Gewinne mit einem nachgezogenen Stop laufen.

Bedingungen (alle am Tagesschluss):
  1. Relative Stärke: 6-Monats-Performance unter den besten (1 − rs_min) des
     Universums (RS_RANK >= rs_min, Wert vom Vortag)
  2. Sauberer Aufwärtstrend: Kurs > SMA50 > SMA200, und SMA200 steigt
     (höher als vor 20 Tagen)
  3. Nahe am Hoch: Kurs mindestens `near_high` × 52-Wochen-Hoch
  4. Auslöser: Schlusskurs über dem 20-Tage-Hoch (neuer Schub)
  5. Gesamtmarkt im Aufwärtstrend (Regime-Filter), da Momentum in
     Bärenmärkten besonders hart einbricht (Daniel & Moskowitz 2016)
Stop: `stop_atr` ATR unter dem Schlusskurs, danach Trailing-Stop.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .. import indicators as ind
from .base import Strategy


@dataclass
class RelativeStrength(Strategy):
    key = "rs_momentum"
    title = "Relative Stärke (Momentum-Trendfolge)"
    description = (
        "Kauft die stärksten Werte des Universums (6-Monats-Performance) im sauberen "
        "Aufwärtstrend nahe am 52-Wochen-Hoch, sobald sie ein neues 20-Tage-Hoch "
        "markieren – nur bei positivem Gesamtmarkt. Gewinne laufen mit Trailing-Stop."
    )
    grid = [
        {"label": "Top 20 %, Trailing 3 ATR",
         "overrides": {"trail_atr": 3.0, "params": {"rs_min": 0.8}}},
        {"label": "Top 20 %, Trailing 4 ATR",
         "overrides": {"trail_atr": 4.0, "params": {"rs_min": 0.8}}},
        {"label": "Top 10 %, Trailing 3 ATR",
         "overrides": {"trail_atr": 3.0, "params": {"rs_min": 0.9}}},
        {"label": "Top 10 %, Trailing 4 ATR",
         "overrides": {"trail_atr": 4.0, "params": {"rs_min": 0.9}}},
    ]
    target_r: float | None = None
    trail_atr: float | None = 3.0
    max_bars: int = 250
    params: dict = field(default_factory=lambda: {
        "rs_min": 0.8,
        "near_high": 0.85,
        "breakout_days": 20,
        "stop_atr": 2.5,
        "use_regime": True,
    })

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        out = df.copy()
        out["SMA50"] = ind.sma(out["Close"], 50)
        out["SMA200"] = ind.sma(out["Close"], 200)
        out["SMA200_RISING"] = out["SMA200"] > out["SMA200"].shift(20)
        out["ATR"] = ind.atr(out, 14)
        out["HIGH_252"] = out["High"].rolling(252, min_periods=252).max()
        out["DONCH_HIGH"] = ind.donchian_high(out["High"], int(p["breakout_days"]))
        if "RS_RANK" not in out:
            out["RS_RANK"] = np.nan     # ohne Marktkontext keine Signale
        return out

    def signals(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        out = df.copy()
        strong = out["RS_RANK"] >= p["rs_min"]
        trend = (out["Close"] > out["SMA50"]) & (out["SMA50"] > out["SMA200"]) & out["SMA200_RISING"]
        near = out["Close"] >= p["near_high"] * out["HIGH_252"]
        trigger = out["Close"] > out["DONCH_HIGH"]
        cond = strong & trend & near & trigger
        if p.get("use_regime"):
            cond &= self.regime_ok(out)
        out["signal"] = cond.fillna(False)
        out["stop"] = out["Close"] - p["stop_atr"] * out["ATR"]
        return out

    def explain(self, row: pd.Series) -> list[str]:
        p = self.params
        top = round(100 * (1 - row["RS_RANK"]))
        return [
            f"Relative Stärke: 6-Monats-Performance gehört zu den besten {max(top, 1)} % "
            f"des Universums (Rang {row['RS_RANK']:.2f}, Schwelle {p['rs_min']:.2f})",
            f"Aufwärtstrend: Kurs {row['Close']:.2f} > SMA50 {row['SMA50']:.2f} > "
            f"SMA200 {row['SMA200']:.2f}, SMA200 steigt",
            f"Nahe am Hoch: {100 * row['Close'] / row['HIGH_252']:.0f} % des 52-Wochen-Hochs "
            f"{row['HIGH_252']:.2f}",
            f"Auslöser: neues {int(p['breakout_days'])}-Tage-Hoch (über {row['DONCH_HIGH']:.2f})",
            f"Anfangs-Stop {p['stop_atr']:.1f} ATR ({row['ATR']:.2f}) unter dem Schlusskurs, "
            f"danach nachgezogen ({self.trail_atr:g} ATR unter dem höchsten Hoch)",
        ] + (["Gesamtmarkt im Aufwärtstrend (Leitindex über SMA200)"] if p.get("use_regime") else [])
