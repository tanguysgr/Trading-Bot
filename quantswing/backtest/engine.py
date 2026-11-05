"""
Backtest-Engine: spielt eine Strategie Kerze für Kerze durch.

Ausführungsregeln (bewusst konservativ, damit Ergebnisse eher zu schlecht als
zu gut sind):

1. Signal am Schlusskurs von Tag t  ->  Einstieg zum ERÖFFNUNGSKURS von Tag t+1.
   (Den Schlusskurs von Tag t kennt man erst, wenn der Markt zu ist.)
2. Liegt die Eröffnung schon jenseits des Stops (Gap), wird der Trade
   übersprungen – das Setup ist kaputt, bevor es begonnen hat.
3. Kursziel = Einstieg + target_r × Risiko (Risiko = Einstieg − Stop).
4. Werden Stop UND Ziel in derselben Kerze berührt, zählt der STOP
   (mit Tageskerzen weiß man nicht, was zuerst passiert ist).
5. Eröffnet ein Tag jenseits von Stop oder Ziel (Gap), wird zum
   Eröffnungskurs ausgeführt – beim Stop also schlechter als geplant.
6. Zeit-Stop: nach `max_bars` Tagen Ausstieg zum Schlusskurs.
6b. Trailing-Stop (falls die Strategie `trail_atr` setzt): Nach jedem Schluss
   wird der Stop auf "höchstes Hoch seit Einstieg − trail_atr × ATR" angehoben,
   aber nie gesenkt. Der neue Stop gilt ab der NÄCHSTEN Kerze. Ohne festes
   Kursziel (`target_r = None`) laufen Gewinne, bis der Trend dreht.
7. Gebühren und Slippage werden bei Ein- UND Ausstieg abgezogen.
8. Pro Symbol höchstens eine offene Position gleichzeitig.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from ..strategies.base import Strategy


@dataclass(frozen=True)
class Costs:
    """Handelskosten als Anteil vom Kurs, je Seite (Kauf bzw. Verkauf)."""

    commission: float = 0.001   # 0,10 % Ordergebühr
    slippage: float = 0.0005    # 0,05 % schlechtere Ausführung als der Kurs

    @staticmethod
    def for_asset(asset_class: str) -> "Costs":
        if asset_class == "crypto":
            return Costs(commission=0.001, slippage=0.001)
        return Costs()


@dataclass
class Trade:
    symbol: str
    strategy: str
    direction: str
    signal_date: pd.Timestamp
    entry_date: pd.Timestamp
    entry_price: float
    stop_price: float
    target_price: float
    exit_date: pd.Timestamp | None = None
    exit_price: float | None = None
    exit_reason: str = ""
    bars_held: int = 0
    r_multiple: float = 0.0
    return_pct: float = 0.0
    mae_r: float = 0.0          # größter Zwischenverlust in R (Maximum Adverse Excursion)
    mfe_r: float = 0.0          # größter Zwischengewinn in R (Maximum Favorable Excursion)
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in ("signal_date", "entry_date", "exit_date"):
            if d[k] is not None:
                d[k] = pd.Timestamp(d[k]).strftime("%Y-%m-%d")
        for k in ("entry_price", "stop_price", "target_price", "exit_price"):
            if d[k] is not None:
                d[k] = round(float(d[k]), 6)
        for k in ("r_multiple", "return_pct", "mae_r", "mfe_r"):
            d[k] = round(float(d[k]), 4)
        return d


EXIT_LABELS = {
    "stop": "Stop-Loss",
    "stop_gap": "Stop-Loss (Gap, schlechter ausgeführt)",
    "target": "Kursziel",
    "target_gap": "Kursziel (Gap, besser ausgeführt)",
    "trail": "Trailing-Stop (Gewinne gesichert)",
    "trail_gap": "Trailing-Stop (Gap, schlechter ausgeführt)",
    "time": "Zeit-Stop",
    "end_of_data": "Datenende (noch offen)",
}


def run_backtest(
    df: pd.DataFrame,
    strategy: Strategy,
    symbol: str = "?",
    costs: Costs | None = None,
    tradable: pd.Series | None = None,
) -> list[Trade]:
    """
    Simuliert alle Trades einer Strategie auf einem Symbol.

    `tradable` (optional): True/False je Tag. Signale an Tagen mit False werden
    ignoriert – z.B. weil die Aktie damals zu wenig gehandelt wurde.
    """
    costs = costs or Costs()
    sig = strategy.run(df)
    if tradable is not None:
        ok = tradable.reindex(sig.index).fillna(False).astype(bool)
        sig["signal"] = sig["signal"] & ok

    o = sig["Open"].to_numpy(float)
    h = sig["High"].to_numpy(float)
    l = sig["Low"].to_numpy(float)
    c = sig["Close"].to_numpy(float)
    signal = sig["signal"].to_numpy(bool)
    stop_arr = sig["stop"].to_numpy(float)
    dates = sig.index
    n = len(sig)

    trail = strategy.trail_atr
    atr_arr = None
    if trail:
        if "ATR" not in sig:
            raise ValueError(f"{strategy.key}: Trailing-Stop braucht eine Spalte 'ATR'")
        atr_arr = sig["ATR"].to_numpy(float)
    use_target = strategy.target_r is not None

    long = strategy.direction.upper() == "LONG"
    s = 1.0 if long else -1.0   # Vorzeichen: Gewinnrichtung

    trades: list[Trade] = []
    pos: Trade | None = None
    pos_i = -1                     # Index der Einstiegskerze
    risk = 0.0                     # Risiko je Stück in Preis-Einheiten (nach Kosten-Einstieg)
    worst = best = 0.0
    cur_stop = np.nan              # aktueller (ggf. nachgezogener) Stop
    extreme = np.nan               # höchstes Hoch (Long) bzw. tiefstes Tief (Short) seit Einstieg

    def close_position(i: int, raw_price: float, reason: str) -> None:
        nonlocal pos
        assert pos is not None
        # Slippage wirkt immer gegen uns
        fill = raw_price * (1.0 - s * costs.slippage)
        fees = (pos.entry_price + fill) * costs.commission
        pnl = s * (fill - pos.entry_price) - fees
        pos.exit_date = dates[i]
        pos.exit_price = fill
        pos.exit_reason = reason
        pos.bars_held = i - pos_i + 1
        pos.r_multiple = pnl / risk
        pos.return_pct = 100.0 * pnl / pos.entry_price
        pos.mae_r = min(0.0, worst / risk)
        pos.mfe_r = max(0.0, best / risk)
        trades.append(pos)
        pos = None

    for i in range(n):
        # --- 1) Einstieg aus Signal des Vortags ---------------------------
        if pos is None and i > 0 and signal[i - 1]:
            stop = stop_arr[i - 1]
            entry = o[i] * (1.0 + s * costs.slippage)
            planned_risk = s * (entry - stop)
            if np.isfinite(stop) and planned_risk > 0:
                target = entry + s * strategy.target_r * planned_risk if use_target else np.nan
                pos = Trade(
                    symbol=symbol,
                    strategy=strategy.key,
                    direction="LONG" if long else "SHORT",
                    signal_date=dates[i - 1],
                    entry_date=dates[i],
                    entry_price=entry,
                    stop_price=stop,
                    target_price=target,
                    reasons=strategy.explain(sig.iloc[i - 1]),
                )
                pos_i, risk = i, planned_risk
                worst = best = 0.0
                cur_stop = stop
                extreme = o[i]

        if pos is None:
            continue

        # --- 2) Ausstieg prüfen ----------------------------------------
        target = pos.target_price
        trailed = s * (cur_stop - pos.stop_price) > 0   # Stop wurde schon nachgezogen
        adverse = l[i] if long else h[i]
        favorable = h[i] if long else l[i]
        worst = min(worst, s * (adverse - pos.entry_price))
        best = max(best, s * (favorable - pos.entry_price))

        if i > pos_i:  # Gaps gibt es erst ab dem Folgetag
            if s * (o[i] - cur_stop) <= 0:
                close_position(i, o[i], "trail_gap" if trailed else "stop_gap")
                continue
            if use_target and s * (o[i] - target) >= 0:
                close_position(i, o[i], "target_gap")
                continue

        hit_stop = s * (adverse - cur_stop) <= 0
        hit_target = use_target and s * (favorable - target) >= 0
        if hit_stop:                       # Regel 4: Stop hat Vorrang
            close_position(i, cur_stop, "trail" if trailed else "stop")
        elif hit_target:
            close_position(i, target, "target")
        elif i - pos_i + 1 >= strategy.max_bars:
            close_position(i, c[i], "time")

        # --- 3) Stop nachziehen (gilt erst ab der nächsten Kerze) ---------
        if pos is not None and trail:
            extreme = max(extreme, h[i]) if long else min(extreme, l[i])
            if np.isfinite(atr_arr[i]):
                candidate = extreme - s * trail * atr_arr[i]
                if s * (candidate - cur_stop) > 0:
                    cur_stop = candidate

    if pos is not None:
        close_position(n - 1, c[n - 1], "end_of_data")

    return trades


def trades_to_frame(trades: list[Trade]) -> pd.DataFrame:
    if not trades:
        return pd.DataFrame(columns=list(Trade.__dataclass_fields__))
    df = pd.DataFrame([t.to_dict() for t in trades])
    df["reasons"] = df["reasons"].apply(lambda r: " | ".join(r))
    return df
