"""Verzeichnis aller Strategien. Neue Strategien hier eintragen."""

from .base import Strategy
from .breakout import BreakoutVolume
from .trend_pullback import TrendPullback

REGISTRY: dict[str, type[Strategy]] = {
    TrendPullback.key: TrendPullback,
    BreakoutVolume.key: BreakoutVolume,
}


def get_strategy(key: str, **overrides) -> Strategy:
    if key not in REGISTRY:
        raise KeyError(f"Unbekannte Strategie '{key}'. Verfügbar: {', '.join(REGISTRY)}")
    return REGISTRY[key](**overrides)


__all__ = ["Strategy", "REGISTRY", "get_strategy", "TrendPullback", "BreakoutVolume"]
