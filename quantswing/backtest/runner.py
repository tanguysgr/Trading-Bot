"""
Führt Backtests über viele Symbole aus und bewertet das Ergebnis getrennt nach
Trainings- (In-Sample) und Testzeitraum (Out-of-Sample).

Warum die Trennung? Wer Regeln so lange anpasst, bis die Vergangenheit gut
aussieht, misst am Ende nur die eigene Anpassung. Darum gilt:
Regeln dürfen nur mit Daten VOR dem Stichtag entwickelt werden. Bestanden ist
eine Strategie erst, wenn sie auch NACH dem Stichtag funktioniert.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from ..data import DataError, asset_class
from ..strategies.base import Strategy
from .engine import Costs, run_backtest, trades_to_frame
from .metrics import GATES, compute_metrics

log = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    strategy: dict
    split_date: str
    symbols_ok: list[str] = field(default_factory=list)
    symbols_failed: dict[str, str] = field(default_factory=dict)
    trades: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: dict = field(default_factory=dict)


def _split(trades: pd.DataFrame, split_date: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    entry = pd.to_datetime(trades["entry_date"])
    cut = pd.Timestamp(split_date)
    return trades[entry < cut], trades[entry >= cut]


def evaluate(trades: pd.DataFrame, split_date: str) -> dict:
    """Kennzahlen + Hürden-Prüfung je Anlageklasse (Aktien / Krypto)."""
    out: dict = {}
    if trades.empty:
        return out
    trades = trades.assign(asset_class=trades["symbol"].map(asset_class))
    for cls, grp in trades.groupby("asset_class"):
        ins, oos = _split(grp, split_date)
        m_all, m_in, m_oos = (compute_metrics(x) for x in (grp, ins, oos))
        passed, problems = GATES[cls].check(m_oos)
        if passed and m_in.expectancy_r <= 0:
            passed, problems = False, ["im Trainingszeitraum nicht profitabel – Testergebnis vermutlich Zufall"]
        out[cls] = {
            "gesamt": m_all.to_dict(),
            "training": m_in.to_dict(),
            "test": m_oos.to_dict(),
            "bestanden": passed,
            "gruende": problems,
            "huerden": GATES[cls].__dict__,
        }
    return out


def run_many(
    symbols: list[str],
    strategy: Strategy,
    loader: Callable[[str], pd.DataFrame],
    split_date: str = "2018-01-01",
) -> BacktestResult:
    res = BacktestResult(strategy=strategy.describe(), split_date=split_date)
    frames = []
    for sym in symbols:
        try:
            df = loader(sym)
            if len(df) < 260:
                raise DataError(f"nur {len(df)} Kerzen (mind. 260 nötig)")
            trades = run_backtest(df, strategy, sym, Costs.for_asset(asset_class(sym)))
            frames.append(trades_to_frame(trades))
            res.symbols_ok.append(sym)
        except Exception as e:  # Fehler sichtbar sammeln statt verschlucken
            log.warning("%s übersprungen: %s", sym, e)
            res.symbols_failed[sym] = str(e)

    frames = [f for f in frames if not f.empty]
    res.trades = pd.concat(frames, ignore_index=True) if frames else trades_to_frame([])
    res.summary = evaluate(res.trades, split_date)
    return res
