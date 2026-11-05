"""
Grundgerüst für alle Strategien.

Eine Strategie beantwortet nur zwei Fragen, jeweils am Schlusskurs eines Tages:
  1. Gibt es heute ein Einstiegssignal?             -> Spalte `signal`
  2. Wo liegt der Stop-Loss, falls ja?              -> Spalte `stop`
Dazu liefert sie Begründungen in Klartext (`explain`), damit du jeden Trade
nachvollziehen kannst.

Alles Weitere – Einstieg, Ausstieg, Gebühren, Auswertung – erledigt die
Backtest-Engine. So kann keine Strategie versehentlich in die Zukunft schauen
oder sich günstigere Ausführungen ausdenken.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

import pandas as pd


@dataclass
class Strategy:
    """Basisklasse. Neue Strategien erben davon und überschreiben die Methoden."""

    # Wird von Unterklassen überschrieben:
    key: ClassVar[str] = "base"
    title: ClassVar[str] = "Basis"
    description: ClassVar[str] = ""

    # Varianten für den Walk-Forward-Test: Liste von
    # {"label": "Kurzname", "overrides": {...}} – siehe get_strategy()
    grid: ClassVar[list[dict]] = []

    # Ausstiegsregeln (gelten für alle Strategien, pro Strategie anpassbar)
    target_r: float | None = 2.0      # Kursziel als Vielfaches des Risikos (CRV); None = kein Ziel
    trail_atr: float | None = None    # Trailing-Stop-Abstand in ATR; None = aus
    max_bars: int = 40                # Zeit-Stop: spätestens nach so vielen Tagen raus
    direction: str = "LONG"

    params: dict = field(default_factory=dict)

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """Indikatoren berechnen. Gibt eine Kopie mit Zusatzspalten zurück."""
        raise NotImplementedError

    def signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Erwartet die Ausgabe von `prepare`. Muss die Spalten
        `signal` (bool) und `stop` (float, Stop-Kurs) ergänzen.
        """
        raise NotImplementedError

    def explain(self, row: pd.Series) -> list[str]:
        """Begründungen in Klartext für ein Signal an dieser Kerze."""
        return []

    @staticmethod
    def regime_ok(df: pd.DataFrame) -> pd.Series:
        """
        True an Tagen mit positivem Gesamtmarkt (Spalte REGIME_OK, kommt aus
        quantswing/context.py). Fehlt die Spalte, gilt der Filter als aus.
        """
        if "REGIME_OK" not in df:
            return pd.Series(True, index=df.index)
        return df["REGIME_OK"] == 1.0

    def exit_text(self) -> str:
        parts = []
        if self.target_r is not None:
            parts.append(f"Kursziel {self.target_r:g} R")
        if self.trail_atr:
            parts.append(f"Trailing-Stop {self.trail_atr:g} ATR")
        parts.append(f"Zeit-Stop {self.max_bars} Tage")
        return " · ".join(parts)

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        out = self.signals(self.prepare(df))
        out["signal"] = out["signal"].fillna(False).astype(bool)
        return out

    def describe(self) -> dict:
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "target_r": self.target_r,
            "trail_atr": self.trail_atr,
            "max_bars": self.max_bars,
            "exits": self.exit_text(),
            "direction": self.direction,
            "params": dict(self.params),
        }
