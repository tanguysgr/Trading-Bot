"""Universen: Listen von Börsenkürzeln, die getestet bzw. gescannt werden."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from .markets import market_of


def read_universe(path: str | Path) -> list[str]:
    """
    Liest eine Universumsdatei. Erlaubt mehrere Kürzel pro Zeile und
    Kommentare nach '#'. Doppelte Einträge werden entfernt (Reihenfolge bleibt).
    """
    seen: dict[str, None] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        for sym in line.split("#", 1)[0].split():
            seen.setdefault(sym.strip().upper(), None)
    return list(seen)


def by_market(symbols: list[str]) -> Counter:
    return Counter(market_of(s).code for s in symbols)
