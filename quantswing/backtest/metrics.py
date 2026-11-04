"""
Kennzahlen und Qualitäts-Hürden.

Alle Kennzahlen werden in "R" gerechnet: 1 R = der Betrag, den du riskierst,
wenn der Stop-Loss greift. Ein Trade mit +2 R hat also das Doppelte des
Risikos gewonnen. So sind Trades in Aktien zu 5 € und zu 500 € vergleichbar.

Erklärung aller Kennzahlen für Einsteiger: docs/BACKTEST_ERKLAERT.md
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


def wilson_lower_bound(wins: int, n: int, z: float = 1.645) -> float:
    """
    Untere Grenze der Trefferquote (90 %-Konfidenz, einseitig 95 %).
    Bei wenigen Trades ist die gemessene Trefferquote Glückssache –
    diese Grenze sagt: "Mit hoher Sicherheit ist sie mindestens so hoch."
    """
    if n == 0:
        return 0.0
    p = wins / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (centre - margin) / denom)


def bootstrap_expectancy_lower(r: np.ndarray, n_boot: int = 5000, q: float = 0.05,
                               seed: int = 42) -> float:
    """
    Untere 5 %-Grenze des Erwartungswerts per Bootstrap: Die Trades werden
    tausendfach zufällig neu gezogen. Ist die Grenze > 0, ist der Vorteil
    sehr wahrscheinlich kein Zufall.
    """
    if len(r) < 2:
        return float("nan")
    rng = np.random.default_rng(seed)
    samples = rng.choice(r, size=(n_boot, len(r)), replace=True).mean(axis=1)
    return float(np.quantile(samples, q))


def equity_curve(r: pd.Series, risk_per_trade: float = 0.01) -> pd.Series:
    """
    Kontoverlauf, wenn man pro Trade `risk_per_trade` (z.B. 1 %) des aktuellen
    Kontos riskiert. Trades werden nach Ausstiegsdatum nacheinander verbucht.
    Vereinfachung: Gleichzeitig offene Trades werden nicht gegeneinander
    verrechnet (das Portfolio-Modell kommt in Phase 2).
    """
    growth = 1.0 + risk_per_trade * r.to_numpy(float)
    growth = np.clip(growth, 0.0, None)
    return pd.Series(np.cumprod(growth), index=r.index)


def max_drawdown(equity: pd.Series) -> float:
    if equity.empty:
        return 0.0
    peak = np.maximum.accumulate(np.r_[1.0, equity.to_numpy(float)])[1:]
    return float(((equity.to_numpy(float) - peak) / peak).min() * 100.0)


def max_losing_streak(r: np.ndarray) -> int:
    best = cur = 0
    for x in r:
        cur = cur + 1 if x <= 0 else 0
        best = max(best, cur)
    return best


@dataclass
class Metrics:
    trades: int = 0
    open_trades: int = 0
    winrate: float = 0.0
    winrate_lower: float = 0.0
    avg_win_r: float = 0.0
    avg_loss_r: float = 0.0
    expectancy_r: float = 0.0
    expectancy_lower_r: float = float("nan")
    profit_factor: float = 0.0
    total_r: float = 0.0
    max_drawdown_pct: float = 0.0
    total_return_pct: float = 0.0
    cagr_pct: float = 0.0
    max_losing_streak: int = 0
    avg_bars_held: float = 0.0
    avg_mae_r: float = 0.0
    trades_per_year: float = 0.0
    exit_reasons: dict | None = None

    def to_dict(self) -> dict:
        out = {}
        for k, v in asdict(self).items():
            if isinstance(v, float):
                out[k] = None if not math.isfinite(v) else round(v, 4)
            else:
                out[k] = v
        return out


def compute_metrics(trades: pd.DataFrame, risk_per_trade: float = 0.01) -> Metrics:
    """Kennzahlen für eine Menge von Trades (Ausgabe von trades_to_frame)."""
    if trades.empty:
        return Metrics(exit_reasons={})

    open_mask = trades["exit_reason"] == "end_of_data"
    closed = trades[~open_mask].copy()
    m = Metrics(open_trades=int(open_mask.sum()))
    if closed.empty:
        m.exit_reasons = {}
        return m

    closed["exit_date"] = pd.to_datetime(closed["exit_date"])
    closed = closed.sort_values("exit_date")
    r = closed["r_multiple"].to_numpy(float)
    wins, losses = r[r > 0], r[r <= 0]

    m.trades = len(r)
    m.winrate = 100.0 * len(wins) / len(r)
    m.winrate_lower = 100.0 * wilson_lower_bound(len(wins), len(r))
    m.avg_win_r = float(wins.mean()) if len(wins) else 0.0
    m.avg_loss_r = float(losses.mean()) if len(losses) else 0.0
    m.expectancy_r = float(r.mean())
    m.expectancy_lower_r = bootstrap_expectancy_lower(r)
    gross_loss = -losses.sum()
    m.profit_factor = float(wins.sum() / gross_loss) if gross_loss > 0 else float("inf")
    m.total_r = float(r.sum())

    eq = equity_curve(pd.Series(r, index=closed["exit_date"]), risk_per_trade)
    m.max_drawdown_pct = max_drawdown(eq)
    m.total_return_pct = float((eq.iloc[-1] - 1.0) * 100.0)

    first = pd.to_datetime(closed["entry_date"]).min()
    last = closed["exit_date"].max()
    years = max((last - first).days / 365.25, 1 / 365.25)
    m.cagr_pct = float((eq.iloc[-1] ** (1 / years) - 1.0) * 100.0) if eq.iloc[-1] > 0 else -100.0
    m.trades_per_year = len(r) / years

    m.max_losing_streak = max_losing_streak(r)
    m.avg_bars_held = float(closed["bars_held"].mean())
    m.avg_mae_r = float(closed["mae_r"].mean())
    m.exit_reasons = closed["exit_reason"].value_counts().to_dict()
    return m


# ---------------------------------------------------------------------------
# Qualitäts-Hürden: Wann gilt eine Strategie als "bestanden"?
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QualityGate:
    min_trades: int
    min_expectancy_lower_r: float     # untere Bootstrap-Grenze des Erwartungswerts
    min_profit_factor: float
    min_winrate_lower: float          # untere Wilson-Grenze in %
    max_drawdown_pct: float           # Portfolio-Drawdown im Test, z.B. -25 = höchstens 25 % Rückgang

    def check(self, m: Metrics, portfolio: dict | None = None) -> tuple[bool, list[str]]:
        """
        Prüft Trade-Statistik (`m`) und – falls vorhanden – die Portfolio-
        Simulation des Testzeitraums (`portfolio`). Der Drawdown wird nur im
        Portfolio geprüft: Bei hunderten Werten überlappen sich Trades, eine
        einfache Hintereinander-Rechnung wäre dort sinnlos.
        """
        problems = []
        if m.trades < self.min_trades:
            problems.append(f"zu wenige Trades ({m.trades} < {self.min_trades})")
        if not (m.expectancy_lower_r >= self.min_expectancy_lower_r):
            problems.append(
                f"Vorteil statistisch nicht gesichert (untere Grenze "
                f"{m.expectancy_lower_r:.2f} R < {self.min_expectancy_lower_r:.2f} R)")
        if m.profit_factor < self.min_profit_factor:
            problems.append(f"Profit-Faktor {m.profit_factor:.2f} < {self.min_profit_factor:.2f}")
        if m.winrate_lower < self.min_winrate_lower:
            problems.append(
                f"Trefferquote nicht sicher genug ({m.winrate_lower:.1f} % < "
                f"{self.min_winrate_lower:.1f} % untere Grenze)")
        if portfolio:
            dd = portfolio.get("max_drawdown_pct", 0.0)
            if dd < self.max_drawdown_pct:
                problems.append(
                    f"Portfolio-Drawdown im Test zu groß ({dd:.1f} % < {self.max_drawdown_pct:.1f} %)")
            if portfolio.get("rendite_pa_pct", 0.0) <= 0:
                problems.append("Portfolio im Test ohne Gewinn")
        return (not problems, problems)


GATES = {
    # Aktien & ETFs: solider, statistisch gesicherter Vorteil nach Kosten
    "stock": QualityGate(min_trades=50, min_expectancy_lower_r=0.0,
                         min_profit_factor=1.3, min_winrate_lower=0.0,
                         max_drawdown_pct=-25.0),
    # Krypto: deutlich strenger (Nutzer-Vorgabe: nur sehr hohe Erfolgswahrscheinlichkeit)
    "crypto": QualityGate(min_trades=40, min_expectancy_lower_r=0.15,
                          min_profit_factor=1.6, min_winrate_lower=50.0,
                          max_drawdown_pct=-20.0),
}
