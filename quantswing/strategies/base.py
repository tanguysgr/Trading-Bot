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

    # Ausstiegsregeln (gelten für alle Strategien, pro Strategie anpassbar)
    target_r: float = 2.0      # Kursziel als Vielfaches des Risikos (CRV)
    max_bars: int = 40         # Zeit-Stop: spätestens nach so vielen Tagen raus
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
            "max_bars": self.max_bars,
            "direction": self.direction,
            "params": dict(self.params),
        }
