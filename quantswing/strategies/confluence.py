"""
Strategie 4: Confluence (die Strategie des Nutzers, in feste Regeln übersetzt)

Grundlage: docs/recherche/confluence_regeln.md, Definitionen in E17.
Gezählt werden KATEGORIEN, nicht Indikatoren – alle drei sind Pflicht:

  A Trend      SMA50 > SMA200, SMA200 steigt (höher als vor 10 Tagen),
               Kurs > SMA200 und Marktstruktur aufwärts (letzter Bruch = BOS/CHoCH ↑)
  B Zone       Ein Tief der letzten 3 Kerzen berührt eine Unterstützung:
                 - SMA-Zone: SMA50/SMA200 (Tageschart) oder die 4H-Gegenstücke
                   (als Tageslinien angenähert, siehe SMA_4H_EQUIV) ± 0,25 ATR
                 - Fibonacci-Zone: 0,5–0,618 des aktiven Schenkels ± 0,25 ATR
                 - Unterstützungszone: ≥ 2 Swings auf ähnlichem Preis
               und kein Tief lag mehr als 1 ATR unter der Zone (sonst "durchgefallen")
  C Bestätigung  Grüne Kerze, die ÜBER der berührten Zone schließt
                 ("Kerze schließt über der Linie" – Regel des Nutzers)

Risiko & Ausstieg:
  Stop       unter dem Rücksetzer-Tief bzw. der Zone, minus 0,5 ATR Puffer;
             mindestens 1 ATR Abstand, bei mehr als 3 ATR kein Trade
  Ziel       1,25 R (fast das geringste Zufallsniveau für die Krypto-Hürde)
  Platz      Liegt zwischen Einstieg und Ziel eine Widerstandszone, kein Trade
  Zeit       nach 30 Tagen raus

Short ist die exakte Spiegelung: Intern wird der Chart "auf den Kopf gestellt"
(Preise negiert) und dieselbe Long-Logik angewendet. So sind Long und Short
garantiert symmetrisch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

import numpy as np
import pandas as pd

from .. import indicators as ind
from ..structure import PivotBook, fib_legs, fib_price, market_structure, pivots, zones_at
from .base import Strategy

# Kontrolle K2: zufällige "Fibonacci"-Zonen gleicher Breite (fest gesetzter Zufall)
_FIB_WIDTH = 0.118
_RANDOM_CENTERS = sorted(round(float(c), 3) for c in
                         np.random.default_rng(2026).uniform(0.25 + _FIB_WIDTH / 2, 0.85 - _FIB_WIDTH / 2, 5))

# 4H-SMAs als Tageslinien angenähert (4H-Kerzen pro Handelstag: US-Aktien 2, Krypto 6)
SMA_4H_EQUIV = {"stock": (25, 100), "crypto": (8, 33)}
ZONE_NAMES = {"sma": "SMA-Zone", "fib": "Fibonacci-Zone", "sr": "Unterstützungszone"}


def _mirror(df: pd.DataFrame) -> pd.DataFrame:
    """Chart auf den Kopf stellen: aus Short wird Long."""
    out = df.copy()
    out["Open"], out["Close"] = -df["Open"], -df["Close"]
    out["High"], out["Low"] = -df["Low"], -df["High"]
    return out


def _asset_class(df: pd.DataFrame) -> str:
    cls = df.attrs.get("asset_class")
    if cls:
        return cls
    # Ohne Angabe: Handel am Wochenende => Krypto
    return "crypto" if len(df) and (df.index.dayofweek >= 5).mean() > 0.2 else "stock"


@dataclass
class ConfluenceLong(Strategy):
    key = "confluence_long"
    title = "Confluence Long (Trend + Zone + Bestätigung)"
    description = (
        "Kauft im Aufwärtstrend (SMA50 > SMA200, Struktur aufwärts), wenn ein Rücksetzer "
        "eine Unterstützung berührt (SMA, Fibonacci 0,5–0,618 oder Swing-Zone) und eine "
        "grüne Kerze darüber schließt. Stop hinter der Zone, Ziel 1,25 R."
    )
    grid = [
        {"label": "V1 Basis", "overrides": {}},
        {"label": "V2 Cluster (≥ 2 Zonentypen)", "overrides": {"params": {"min_types": 2}}},
        {"label": "V3 + interner Bruch", "overrides": {"params": {"need_internal": True}}},
        {"label": "V4 Trailing 3 ATR",
         "overrides": {"target_r": None, "trail_atr": 3.0, "max_bars": 120}},
    ]
    controls = (
        [{"label": "K1 ohne Fibonacci", "overrides": {"params": {"zone_types": ("sma", "sr")}}}]
        + [{"label": f"K2 Zufalls-Fibonacci {c - _FIB_WIDTH / 2:.3f}–{c + _FIB_WIDTH / 2:.3f}",
            "overrides": {"params": {"fib_lo": round(c - _FIB_WIDTH / 2, 3),
                                     "fib_hi": round(c + _FIB_WIDTH / 2, 3)}}}
           for c in _RANDOM_CENTERS]
        + [{"label": "K3 20-Tage-Ausbruch statt BOS/CHoCH", "overrides": {"params": {"use_bias": False}}}]
    )
    target_r: float | None = 1.25
    max_bars: int = 30
    direction: str = "LONG"
    params: dict = field(default_factory=lambda: {
        "zone_types": ("sma", "fib", "sr"),
        "min_types": 1,
        "need_internal": False,
        "use_bias": True,          # False = Kontrolle: 20-Tage-Ausbruch statt Marktstruktur
        "fib_lo": 0.5,
        "fib_hi": 0.618,
        "touch_atr": 0.25,
        "max_pierce_atr": 1.0,
        "stop_buffer_atr": 0.5,
        "min_stop_atr": 1.0,
        "max_stop_atr": 3.0,
        "room_r": 1.25,
        "lookback": 3,
    })

    _cache: ClassVar[dict] = {}

    # --- Vorbereitung (teuer, wird je Datensatz und Richtung zwischengespeichert) ----
    def _prepared(self, df: pd.DataFrame) -> pd.DataFrame:
        long = self.direction.upper() == "LONG"
        key = (id(df), len(df), long, float(df["Close"].iat[0]), float(df["Close"].iat[-1]),
               float(df["High"].sum()), float(df["Low"].sum()))
        hit = self._cache.get(key)
        if hit is not None:
            return hit
        w = df if long else _mirror(df)
        cls = _asset_class(df)
        out = pd.DataFrame(index=df.index)
        out["W_OPEN"], out["W_HIGH"], out["W_LOW"], out["W_CLOSE"] = (
            w["Open"], w["High"], w["Low"], w["Close"])
        out["ATR"] = ind.atr(w, 14)
        out["W_SMA50"] = ind.sma(w["Close"], 50)
        out["W_SMA200"] = ind.sma(w["Close"], 200)
        f50, f200 = SMA_4H_EQUIV[cls]
        out["W_SMA4H50"] = ind.sma(w["Close"], f50)
        out["W_SMA4H200"] = ind.sma(w["Close"], f200)
        piv = pivots(w, 5, 5)
        out = out.join(piv)
        ms = market_structure(w, piv=piv)
        out["BIAS"] = ms["BIAS"]
        out["INT_EVENT"] = market_structure(w, 2, 2)["EVENT"]
        legs = fib_legs(w, piv, out["ATR"])
        out["LEG_HI"], out["LEG_LO"] = legs["UP_HI"], legs["UP_LO"]
        out["BRK20"] = (w["Close"] > ind.donchian_high(w["High"], 20)).rolling(20, min_periods=1).max() > 0
        if len(self._cache) > 3000:
            self._cache.clear()
        self._cache[key] = out
        return out

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        prep = self._prepared(df)
        for col in prep.columns:
            out[col] = prep[col].to_numpy()
        return out

    # --- Signale ---------------------------------------------------------------
    def signals(self, df: pd.DataFrame) -> pd.DataFrame:
        p = self.params
        s = 1.0 if self.direction.upper() == "LONG" else -1.0
        out = df.copy()
        n = len(out)
        o, h, lo, c = (out[k].to_numpy(float) for k in ("W_OPEN", "W_HIGH", "W_LOW", "W_CLOSE"))
        atr = out["ATR"].to_numpy(float)
        sma50, sma200 = out["W_SMA50"].to_numpy(float), out["W_SMA200"].to_numpy(float)
        smas = {"SMA50": sma50, "SMA200": sma200,
                "4H-SMA50": out["W_SMA4H50"].to_numpy(float),
                "4H-SMA200": out["W_SMA4H200"].to_numpy(float)}
        leg_hi, leg_lo = out["LEG_HI"].to_numpy(float), out["LEG_LO"].to_numpy(float)
        int_ev = out["INT_EVENT"].to_numpy(int)

        rising = sma200 > np.r_[np.full(10, np.nan), sma200[:-10]] if n > 10 else np.zeros(n, bool)
        structure = out["BIAS"].to_numpy() == 1 if p["use_bias"] else out["BRK20"].to_numpy(bool)
        trend = (sma50 > sma200) & rising & (c > sma200) & structure
        candidates = np.flatnonzero(trend & (c > o) & np.isfinite(atr))

        book = PivotBook(out[["PH", "PH_BAR", "PL", "PL_BAR"]])
        lb = int(p["lookback"])
        ta = p["touch_atr"]
        signal = np.zeros(n, bool)
        stop_w = np.full(n, np.nan)
        why = np.full(n, "", dtype=object)
        px = lambda v: s * v  # noqa: E731  (Arbeits-Preis -> echter Preis)

        for t in candidates:
            if t < lb:
                continue
            a = atr[t]
            low_min = lo[t - lb + 1:t + 1].min()

            zones = []                                   # (Typ, Unterkante, Oberkante, Beschreibung)
            if "sma" in p["zone_types"]:
                for name, arr in smas.items():
                    v = arr[t]
                    if np.isfinite(v):
                        zones.append(("sma", v - ta * a, v + ta * a, f"{name} bei {abs(px(v)):.2f}"))
            if "fib" in p["zone_types"] and np.isfinite(leg_hi[t]):
                f1 = fib_price(leg_hi[t], leg_lo[t], p["fib_hi"])
                f2 = fib_price(leg_hi[t], leg_lo[t], p["fib_lo"])
                zones.append(("fib", f1 - ta * a, f2 + ta * a,
                              f"Fibonacci {p['fib_lo']:.3g}–{p['fib_hi']:.3g} "
                              f"({abs(px(f2)):.2f}–{abs(px(f1)):.2f}) des Schenkels "
                              f"{abs(px(leg_lo[t])):.2f} → {abs(px(leg_hi[t])):.2f}"))
            sr = zones_at(book, t, a)
            if "sr" in p["zone_types"]:
                for z in sr:
                    zones.append(("sr", z.bottom, z.top,
                                  f"Swing-Zone {min(abs(px(z.bottom)), abs(px(z.top))):.2f}–"
                                  f"{max(abs(px(z.bottom)), abs(px(z.top))):.2f} ({z.touches} Swings)"))

            hits = [z for z in zones
                    if low_min <= z[2] and low_min >= z[1] - p["max_pierce_atr"] * a and c[t] > z[2]]
            if len({z[0] for z in hits}) < p["min_types"] or not hits:
                continue
            if p["need_internal"] and not (int_ev[t - lb + 1:t + 1] > 0).any():
                continue

            stop = min(low_min, min(z[1] for z in hits)) - p["stop_buffer_atr"] * a
            stop = min(stop, c[t] - p["min_stop_atr"] * a)
            risk = c[t] - stop
            if risk > p["max_stop_atr"] * a:
                continue
            target = c[t] + p["room_r"] * risk
            if any(z.top > c[t] and z.bottom < target for z in sr):
                continue                                  # Widerstand im Weg

            signal[t] = True
            stop_w[t] = stop
            word = "Unterstützung" if s > 0 else "Widerstand"
            why[t] = " | ".join(
                [("Trend: SMA50 > SMA200, SMA200 steigt, Kurs darüber" if s > 0 else
                  "Trend: SMA50 < SMA200, SMA200 fällt, Kurs darunter")
                 + (", Struktur " + ("aufwärts (BOS/CHoCH ↑)" if s > 0 else "abwärts (BOS/CHoCH ↓)")
                    if p["use_bias"] else ", 20-Tage-Ausbruch")]
                + [f"Zone berührt ({ZONE_NAMES[z[0]].replace('Unterstützung', word)}): {z[3]}" for z in hits]
                + [f"Bestätigung: {'grüne' if s > 0 else 'rote'} Kerze schließt "
                   f"{'über' if s > 0 else 'unter'} der Zone ({abs(px(c[t])):.2f})"]
                + (["Interner Strukturbruch in Handelsrichtung"] if p["need_internal"] else [])
                + [f"Stop {abs(px(stop)):.2f} hinter Zone/Rücksetzer (+{p['stop_buffer_atr']:g} ATR Puffer), "
                   f"kein {('Widerstand' if s > 0 else 'Unterstützung')} vor dem Ziel"])

        out["signal"] = signal
        out["stop"] = s * stop_w
        out["WHY"] = why
        return out

    def explain(self, row: pd.Series) -> list[str]:
        return [x for x in str(row.get("WHY", "")).split(" | ") if x]


@dataclass
class ConfluenceShort(ConfluenceLong):
    key = "confluence_short"
    title = "Confluence Short (gespiegelt)"
    description = (
        "Verkauft (short) im Abwärtstrend (SMA50 < SMA200, Struktur abwärts), wenn eine "
        "Erholung einen Widerstand berührt (SMA, Fibonacci 0,5–0,618 oder Swing-Zone) und "
        "eine rote Kerze darunter schließt. Stop hinter der Zone, Ziel 1,25 R."
    )
    direction: str = "SHORT"
