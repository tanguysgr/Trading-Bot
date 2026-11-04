"""
Portfolio-Simulation: Was wäre mit einem echten Depot passiert?

Die Engine liefert für jedes Symbol alle möglichen Trades. In der Realität
kannst du aber nicht 50 Positionen gleichzeitig halten. Diese Simulation geht
die Trades chronologisch durch und nimmt nur die, für die Platz ist.

Regeln (alle ohne Blick in die Zukunft):
- Höchstens `max_positions` Positionen gleichzeitig, davon höchstens
  `max_per_market` aus demselben Land (gegen Klumpenrisiko).
- Gibt es an einem Tag mehr Signale als freie Plätze, gewinnt das Signal mit
  der höchsten `priority` (Standard: 6-Monats-Kursentwicklung am Signaltag –
  die relativ stärksten Werte zuerst).
- Ein Platz wird erst am Tag NACH dem Ausstieg wieder frei.
- Risiko pro Trade: `risk_per_trade` vom aktuellen Konto. Damit kein Hebel
  entsteht, ist jede Position zusätzlich auf `1 / max_positions` des Kontos
  begrenzt. Bei sehr engen Stops wird dann weniger als 1 % riskiert.
- Gewinne und Verluste werden beim Ausstieg verbucht (der Kontoverlauf zeigt
  also realisierte Werte; Schwankungen offener Positionen sind nicht enthalten).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .metrics import max_drawdown


@dataclass(frozen=True)
class PortfolioRules:
    max_positions: int = 10
    max_per_market: int = 4
    risk_per_trade: float = 0.01
    start_equity: float = 100_000.0


@dataclass
class PortfolioResult:
    rules: PortfolioRules
    taken: pd.DataFrame = field(default_factory=pd.DataFrame)
    skipped: int = 0
    equity: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    stats: dict = field(default_factory=dict)


def _cagr(equity: pd.Series, start: pd.Timestamp, start_value: float) -> float:
    if equity.empty:
        return 0.0
    years = max((equity.index[-1] - start).days / 365.25, 1 / 365.25)
    final = equity.iloc[-1] / start_value
    return float((final ** (1 / years) - 1) * 100.0) if final > 0 else -100.0


def simulate_portfolio(trades: pd.DataFrame, rules: PortfolioRules | None = None) -> PortfolioResult:
    rules = rules or PortfolioRules()
    res = PortfolioResult(rules=rules)
    if trades.empty:
        return res

    t = trades.copy()
    t["entry_date"] = pd.to_datetime(t["entry_date"])
    t["exit_date"] = pd.to_datetime(t["exit_date"])
    if "priority" not in t:
        t["priority"] = 0.0
    if "market" not in t:
        t["market"] = "?"
    t["priority"] = t["priority"].fillna(-np.inf)
    t = t.sort_values(["entry_date", "priority", "symbol"], ascending=[True, False, True])

    equity = rules.start_equity
    max_notional = 1.0 / rules.max_positions
    open_pos: list[dict] = []          # offene Positionen
    curve: list[tuple[pd.Timestamp, float]] = []
    taken_rows = []
    skipped = 0
    position_days = 0.0

    def realize_until(day: pd.Timestamp) -> None:
        """Bucht alle Positionen, deren Ausstieg VOR `day` liegt."""
        nonlocal equity, open_pos
        done = sorted((p for p in open_pos if p["exit_date"] < day), key=lambda p: p["exit_date"])
        for p in done:
            equity += p["pnl"]
            curve.append((p["exit_date"], equity))
        open_pos = [p for p in open_pos if p["exit_date"] >= day]

    for day, group in t.groupby("entry_date", sort=True):
        realize_until(day)
        for _, tr in group.iterrows():
            per_market = sum(1 for p in open_pos if p["market"] == tr["market"])
            if len(open_pos) >= rules.max_positions or per_market >= rules.max_per_market:
                skipped += 1
                continue
            stop_pct = abs(tr["entry_price"] - tr["stop_price"]) / tr["entry_price"]
            risk_frac = min(rules.risk_per_trade, max_notional * stop_pct)
            risk_amount = equity * risk_frac
            pnl = float(tr["r_multiple"]) * risk_amount
            p = {"exit_date": tr["exit_date"], "market": tr["market"], "pnl": pnl}
            open_pos.append(p)
            position_days += max((tr["exit_date"] - day).days, 1)
            row = tr.to_dict()
            row.update(risk_pct=round(100 * risk_frac, 3), risk_amount=round(risk_amount, 2),
                       pnl=round(pnl, 2), equity_at_entry=round(equity, 2))
            taken_rows.append(row)

    realize_until(pd.Timestamp.max)

    res.taken = pd.DataFrame(taken_rows)
    res.skipped = skipped
    start = t["entry_date"].min()
    eq = pd.Series([e for _, e in curve], index=pd.DatetimeIndex([d for d, _ in curve]))
    eq = eq.groupby(level=0).last()
    res.equity = eq

    span_days = max((t["exit_date"].max() - start).days, 1)
    yearly = {}
    if not eq.empty:
        full = pd.concat([pd.Series([rules.start_equity], index=[start - pd.Timedelta(days=1)]), eq])
        year_end = full.groupby(full.index.year).last()
        prev = year_end.shift(1).fillna(rules.start_equity)
        yearly = {int(y): round(float((v / p - 1) * 100), 2) for y, v, p in
                  zip(year_end.index, year_end.values, prev.values)}

    res.stats = {
        "start": start.strftime("%Y-%m-%d"),
        "ende": t["exit_date"].max().strftime("%Y-%m-%d"),
        "startkapital": rules.start_equity,
        "endkapital": round(float(eq.iloc[-1]), 2) if not eq.empty else rules.start_equity,
        "rendite_pa_pct": round(_cagr(eq, start, rules.start_equity), 2),
        "max_drawdown_pct": round(max_drawdown(eq / rules.start_equity), 2),
        "trades_genommen": len(taken_rows),
        "trades_uebersprungen": skipped,
        "avg_positionen": round(position_days / span_days, 2),
        "avg_risiko_pct": round(float(res.taken["risk_pct"].mean()), 3) if taken_rows else 0.0,
        "jahresrenditen_pct": yearly,
    }
    return res


def buy_and_hold(close: pd.Series, start: str, end: str) -> dict:
    """Vergleichswert: einfach kaufen und halten (z.B. S&P-500-ETF)."""
    c = close.loc[start:end].dropna()
    if len(c) < 2:
        return {}
    eq = c / c.iloc[0]
    years = max((c.index[-1] - c.index[0]).days / 365.25, 1 / 365.25)
    yearly = eq.groupby(eq.index.year).last()
    prev = yearly.shift(1).fillna(1.0)
    return {
        "rendite_pa_pct": round(float((eq.iloc[-1] ** (1 / years) - 1) * 100), 2),
        "max_drawdown_pct": round(max_drawdown(eq), 2),
        "jahresrenditen_pct": {int(y): round(float((v / p - 1) * 100), 2)
                               for y, v, p in zip(yearly.index, yearly.values, prev.values)},
    }
