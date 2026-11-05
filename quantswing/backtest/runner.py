"""
Führt Backtests über viele Symbole aus und bewertet das Ergebnis getrennt nach
Trainings- (In-Sample) und Testzeitraum (Out-of-Sample).

Warum die Trennung? Wer Regeln so lange anpasst, bis die Vergangenheit gut
aussieht, misst am Ende nur die eigene Anpassung. Darum gilt:
Regeln dürfen nur mit Daten VOR dem Stichtag entwickelt werden. Bestanden ist
eine Strategie erst, wenn sie auch NACH dem Stichtag funktioniert.

Ablauf je Strategie:
1. Pro Symbol: Kursdaten laden, Liquidität prüfen, alle Trades simulieren
2. Trade-Statistik je Anlageklasse (Aktien / Krypto) inkl. Hürden-Prüfung
3. Aufschlüsselung nach Ländern
4. Portfolio-Simulation (Aktien) für Gesamt- und Testzeitraum + Vergleich mit Index
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from ..context import asof_before, regime_flag, rs_rank
from ..data import DataError, turnover_usd
from ..markets import asset_class, currency_of, market_of
from ..strategies.base import Strategy
from .engine import Costs, run_backtest, trades_to_frame
from .metrics import GATES, compute_metrics
from .portfolio import PortfolioRules, buy_and_hold, simulate_portfolio

log = logging.getLogger(__name__)

Loader = Callable[[str], pd.DataFrame]
FxLoader = Callable[[str], "pd.Series | None"]

PRIORITY_LOOKBACK = 126   # ~6 Monate Handelstage


@dataclass
class RunConfig:
    split_date: str = "2018-01-01"
    min_turnover_usd: float = 5_000_000.0   # Median-Tagesumsatz, damit Orders problemlos ausgeführt werden
    portfolio: PortfolioRules = field(default_factory=PortfolioRules)
    benchmarks: tuple[str, ...] = ("SPY", "ACWI")      # Vergleich für Aktien
    crypto_benchmarks: tuple[str, ...] = ("BTC-USD",)  # Vergleich für Krypto
    regime_symbols: dict = field(default_factory=lambda: {"stock": "SPY", "crypto": "BTC-USD"})


@dataclass
class BacktestResult:
    strategy: dict
    split_date: str
    config: dict = field(default_factory=dict)
    symbols_ok: list[str] = field(default_factory=list)
    symbols_failed: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    trades: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: dict = field(default_factory=dict)
    by_market: list[dict] = field(default_factory=list)
    portfolio: dict = field(default_factory=dict)


def _split(trades: pd.DataFrame, split_date: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    entry = pd.to_datetime(trades["entry_date"])
    cut = pd.Timestamp(split_date)
    return trades[entry < cut], trades[entry >= cut]


def evaluate(trades: pd.DataFrame, split_date: str, portfolios: dict | None = None) -> dict:
    """
    Kennzahlen + Hürden-Prüfung je Anlageklasse (Aktien / Krypto).
    `portfolios`: Ergebnis der Portfolio-Simulation je Klasse (für die Drawdown-Hürde).
    """
    out: dict = {}
    if trades.empty:
        return out
    portfolios = portfolios or {}
    trades = trades.assign(asset_class=trades["symbol"].map(asset_class))
    for cls, grp in trades.groupby("asset_class"):
        ins, oos = _split(grp, split_date)
        m_all, m_in, m_oos = (compute_metrics(x) for x in (grp, ins, oos))
        passed, problems = GATES[cls].check(m_oos, portfolios.get(cls, {}).get("test"))
        if m_in.expectancy_r <= 0:
            passed = False
            problems.append("im Trainingszeitraum nicht profitabel – Testergebnis vermutlich Zufall")
        out[cls] = {
            "gesamt": m_all.to_dict(),
            "training": m_in.to_dict(),
            "test": m_oos.to_dict(),
            "bestanden": passed,
            "gruende": problems,
            "huerden": GATES[cls].__dict__,
        }
    return out


def market_breakdown(trades: pd.DataFrame) -> list[dict]:
    """Trade-Statistik je Land/Markt, sortiert nach Anzahl Trades."""
    rows = []
    if trades.empty:
        return rows
    for code, grp in trades.groupby("market"):
        m = compute_metrics(grp)
        if m.trades == 0:
            continue
        rows.append({"markt": code, "symbole": grp["symbol"].nunique(), "trades": m.trades,
                     "trefferquote": round(m.winrate, 1), "erwartungswert_r": round(m.expectancy_r, 3),
                     "profit_faktor": round(m.profit_factor, 2) if m.profit_factor != float("inf") else None})
    return sorted(rows, key=lambda r: -r["trades"])


def _tradable(df: pd.DataFrame, sym: str, cfg: RunConfig, fx_loader: FxLoader | None,
              fx_cache: dict, notes: list[str]) -> pd.Series | None:
    if cfg.min_turnover_usd <= 0:
        return None
    cur = currency_of(sym)
    fx = None
    if cur != "USD":
        if fx_loader is None:
            return None
        if cur not in fx_cache:
            fx_cache[cur] = fx_loader(cur)
        fx = fx_cache[cur]
        if fx is None:
            note = f"Kein Wechselkurs für {cur} – Liquiditätsfilter für diese Werte ausgesetzt"
            if note not in notes:
                notes.append(note)
            return None
    return turnover_usd(df, sym, fx) >= cfg.min_turnover_usd


@dataclass
class Universe:
    """Einmal geladene und vorbereitete Daten – für mehrere Strategien wiederverwendbar."""
    data: dict[str, pd.DataFrame] = field(default_factory=dict)       # OHLCV + Kontextspalten
    tradable: dict[str, "pd.Series | None"] = field(default_factory=dict)
    failed: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def prepare_universe(
    symbols: list[str],
    loader: Loader,
    cfg: RunConfig | None = None,
    fx_loader: FxLoader | None = None,
) -> Universe:
    """Lädt alle Symbole, berechnet Liquidität und Marktkontext (Regime, relative Stärke)."""
    cfg = cfg or RunConfig()
    uni = Universe()
    fx_cache: dict = {}
    for sym in symbols:
        try:
            df = loader(sym)
            if len(df) < 260:
                raise DataError(f"nur {len(df)} Kerzen (mind. 260 nötig)")
            uni.data[sym] = df.copy()
            uni.tradable[sym] = _tradable(df, sym, cfg, fx_loader, fx_cache, uni.notes)
        except Exception as e:  # Fehler sichtbar sammeln statt verschlucken
            log.warning("%s übersprungen: %s", sym, e)
            uni.failed[sym] = str(e)

    for cls in ("stock", "crypto"):
        syms = [s for s in uni.data if asset_class(s) == cls]
        if not syms:
            continue
        ranks = rs_rank({s: uni.data[s]["Close"] for s in syms})
        flag = None
        bench = cfg.regime_symbols.get(cls)
        try:
            flag = regime_flag(loader(bench)["Close"]) if bench else None
        except Exception as e:  # noqa: BLE001
            log.warning("Regime-Leitwert %s nicht verfügbar: %s", bench, e)
        if flag is None:
            uni.notes.append(f"Regime-Filter für {cls} ausgesetzt (Leitwert {bench} fehlt)")
        for s in syms:
            df = uni.data[s]
            df["RS_RANK"] = ranks[s]
            df["REGIME_OK"] = asof_before(flag, df.index) if flag is not None else 1.0
    return uni


def collect_trades(uni: Universe, strategy: Strategy) -> pd.DataFrame:
    """Alle Trades einer Strategie über das ganze Universum (ohne Depot-Begrenzung)."""
    frames = []
    for sym, df in uni.data.items():
        trades = run_backtest(df, strategy, sym, Costs.for_asset(asset_class(sym)),
                              uni.tradable.get(sym))
        tf = trades_to_frame(trades)
        if tf.empty:
            continue
        prio = df["Close"] / df["Close"].shift(PRIORITY_LOOKBACK) - 1.0
        prio.index = prio.index.strftime("%Y-%m-%d")
        tf["priority"] = tf["signal_date"].map(prio)
        tf["market"] = market_of(sym).code
        frames.append(tf)
    return pd.concat(frames, ignore_index=True) if frames else trades_to_frame([])


def run_many(
    symbols: list[str],
    strategy: Strategy,
    loader: Loader,
    cfg: RunConfig | None = None,
    fx_loader: FxLoader | None = None,
    universe: Universe | None = None,
) -> BacktestResult:
    """Einfacher Backtest mit festem Stichtag (Training davor, Test danach)."""
    cfg = cfg or RunConfig()
    uni = universe or prepare_universe(symbols, loader, cfg, fx_loader)
    res = BacktestResult(strategy=strategy.describe(), split_date=cfg.split_date,
                         config={"min_umsatz_usd": cfg.min_turnover_usd,
                                 "portfolio": cfg.portfolio.__dict__})
    res.symbols_ok = list(uni.data)
    res.symbols_failed = dict(uni.failed)
    res.notes = list(uni.notes)
    res.trades = collect_trades(uni, strategy)
    res.portfolio = _portfolio_section(res.trades, cfg, loader)
    res.summary = evaluate(res.trades, cfg.split_date, res.portfolio)
    res.by_market = market_breakdown(res.trades)
    return res


def benchmarks_for(cls: str, start: str, end: str, cfg: RunConfig, loader: Loader) -> dict:
    """Kaufen-&-Halten-Vergleich im selben Zeitraum (Aktien: SPY/ACWI, Krypto: BTC)."""
    out = {}
    for b in (cfg.benchmarks if cls == "stock" else cfg.crypto_benchmarks):
        try:
            out[b] = buy_and_hold(loader(b)["Close"], start, end)
        except Exception as e:  # noqa: BLE001
            log.warning("Vergleichswert %s nicht verfügbar: %s", b, e)
    return out


UNIVERSE_BENCH = "Universum gleichgewichtet"


def universe_benchmark(uni: Universe, cls: str, start: str, end: str) -> dict:
    """
    Kaufen & Halten aller Werte des Universums zu gleichen Teilen (täglich
    neu gewichtet, Renditen in Landeswährung). Weil das Universum aus heutigen
    Index-Mitgliedern besteht, zeigt dieser Vergleich, wie viel
    "Überlebenden-Vorteil" schon in den Daten steckt.
    """
    rets = {s: df["Close"].pct_change() for s, df in uni.data.items() if asset_class(s) == cls}
    if not rets:
        return {}
    daily = pd.DataFrame(rets).sort_index().loc[start:end].mean(axis=1, skipna=True).fillna(0.0)
    if daily.empty:
        return {}
    return buy_and_hold((1.0 + daily).cumprod(), start, end)


def _portfolio_section(trades: pd.DataFrame, cfg: RunConfig, loader: Loader) -> dict:
    """Portfolio-Simulation je Anlageklasse, jeweils für Gesamt- und Testzeitraum."""
    out: dict = {}
    if trades.empty:
        return out
    classes = trades["symbol"].map(asset_class)
    for cls in ("stock", "crypto"):
        subset_cls = trades[classes == cls]
        if subset_cls.empty:
            continue
        _, test = _split(subset_cls, cfg.split_date)
        out[cls] = {}
        for label, subset in (("gesamt", subset_cls), ("test", test)):
            if subset.empty:
                continue
            sim = simulate_portfolio(subset, cfg.portfolio)
            out[cls][label] = {**sim.stats, "vergleich": benchmarks_for(
                cls, sim.stats["start"], sim.stats["ende"], cfg, loader)}
    return out
