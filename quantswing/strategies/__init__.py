"""Verzeichnis aller Strategien. Neue Strategien hier eintragen."""

from .base import Strategy
from .breakout import BreakoutVolume
from .confluence import ConfluenceLong, ConfluenceShort
from .momentum import RelativeStrength
from .trend_pullback import TrendPullback

REGISTRY: dict[str, type[Strategy]] = {
    TrendPullback.key: TrendPullback,
    BreakoutVolume.key: BreakoutVolume,
    RelativeStrength.key: RelativeStrength,
    ConfluenceLong.key: ConfluenceLong,
    ConfluenceShort.key: ConfluenceShort,
}


def get_strategy(key: str, **overrides) -> Strategy:
    """
    Erzeugt eine Strategie. `overrides` ändern Ausstiegsregeln
    (z.B. target_r=None, trail_atr=3.0) oder einzelne Parameter
    (params={"use_regime": True}) – nicht genannte Parameter behalten ihren Standardwert.
    """
    if key not in REGISTRY:
        raise KeyError(f"Unbekannte Strategie '{key}'. Verfügbar: {', '.join(REGISTRY)}")
    strat = REGISTRY[key]()
    for name, value in overrides.items():
        if name == "params":
            unknown = set(value) - set(strat.params)
            if unknown:
                raise KeyError(f"{key}: unbekannte Parameter {sorted(unknown)}")
            strat.params = {**strat.params, **value}
        elif name in ("target_r", "trail_atr", "max_bars"):
            setattr(strat, name, value)
        else:
            raise KeyError(f"{key}: '{name}' kann nicht überschrieben werden")
    return strat


def variants(key: str) -> list[tuple[str, Strategy]]:
    """Alle Varianten einer Strategie für den Walk-Forward-Test."""
    grid = REGISTRY[key].grid or [{"label": "Standard", "overrides": {}}]
    return [(g["label"], get_strategy(key, **g["overrides"])) for g in grid]


__all__ = ["Strategy", "REGISTRY", "get_strategy", "variants",
           "TrendPullback", "BreakoutVolume", "RelativeStrength", "ConfluenceLong", "ConfluenceShort"]
