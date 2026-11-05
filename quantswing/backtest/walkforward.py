"""
Walk-Forward-Test: der ehrlichste Test, den wir machen können.

Problem eines festen Stichtags: Sobald man das Testergebnis einmal gesehen hat
und daraufhin etwas ändert, ist der Test "verbraucht".

Lösung: Man simuliert, was man in der Vergangenheit WIRKLICH hätte tun können.

  Zeitfenster:   2006 ─────────── 2010 │ 2010–11 │ 2012–13 │ … │ 2024–25 │ 2026
                 Training (wächst mit) │  Test   │  Test   │   │  Test   │ Test

Für jedes 2-Jahres-Testfenster gilt:
1. Es zählen nur Trades, die VOR Fensterbeginn abgeschlossen waren.
2. Daraus wird die Variante mit dem am sichersten positiven Erwartungswert
   gewählt (untere Sicherheitsgrenze, nicht der höchste Mittelwert – das
   bestraft Glückstreffer mit wenigen Trades).
3. War bis dahin keine Variante profitabel, bleibt das Fenster ohne Trades
   (Geld bleibt liegen – auch das ist eine echte Entscheidung).
4. Die gewählte Variante handelt im Fenster. Diese Trades sind echte
   "Out-of-Sample"-Ergebnisse: Bei der Auswahl waren sie unbekannt.
Alle Testfenster zusammen ergeben das Gesamtergebnis, das gegen die Hürden
geprüft wird.

Was der Walk-Forward NICHT verhindert: Wenn Menschen (oder Claude) eine
Strategie-Idee entwerfen, nachdem sie Ergebnisse gesehen haben. Deshalb wird
in docs/ENTSCHEIDUNGEN.md festgehalten, wie viele Ideen insgesamt getestet
wurden. Je mehr Versuche, desto skeptischer muss man bei einem Treffer sein.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..markets import asset_class
from ..strategies import REGISTRY, get_strategy, variants
from .metrics import GATES, compute_metrics
from .portfolio import simulate_portfolio
from .runner import (UNIVERSE_BENCH, Loader, RunConfig, Universe, benchmarks_for,
                     collect_trades, market_breakdown, universe_benchmark)

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class WFConfig:
    first_test_year: int = 2010
    window_years: int = 2
    min_train_trades: int = 30


@dataclass
class WFResult:
    strategy: dict
    variants: list[str]
    config: dict
    symbols_ok: list[str] = field(default_factory=list)
    symbols_failed: dict[str, str] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    windows: dict = field(default_factory=dict)       # Klasse -> Liste der Fenster
    trades: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: dict = field(default_factory=dict)       # Klasse -> Kennzahlen + Urteil
    portfolio: dict = field(default_factory=dict)     # Klasse -> Portfolio-Kennzahlen
    by_market: list[dict] = field(default_factory=list)
    comparison: dict = field(default_factory=dict)    # Klasse -> Varianten + Kontrollläufe (fest)


def make_windows(first_year: int, window_years: int,
                 last_date: pd.Timestamp) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """Testfenster [Beginn, Ende) bis einschließlich `last_date`."""
    out = []
    year = first_year
    while pd.Timestamp(year=year, month=1, day=1) <= last_date:
        start = pd.Timestamp(year=year, month=1, day=1)
        end = pd.Timestamp(year=year + window_years, month=1, day=1)
        out.append((start, end))
        year += window_years
    return out


def select_variant(trades_by_variant: dict[str, pd.DataFrame], window_start: pd.Timestamp,
                   min_train_trades: int) -> tuple[str | None, dict]:
    """
    Wählt die Variante NUR anhand von Trades, die vor `window_start`
    abgeschlossen waren. Rückgabe: (Name oder None für "kein Handel", Infos).
    """
    best_label, best = None, None
    for label, tf in trades_by_variant.items():
        if tf.empty:
            continue
        train = tf[pd.to_datetime(tf["exit_date"]) < window_start]
        m = compute_metrics(train)
        if m.trades < min_train_trades or not np.isfinite(m.expectancy_lower_r):
            continue
        if best is None or m.expectancy_lower_r > best.expectancy_lower_r:
            best_label, best = label, m
    if best is None:
        return None, {"grund": f"keine Variante mit mind. {min_train_trades} Trainings-Trades"}
    info = {"training_trades": best.trades, "training_erwartung_r": round(best.expectancy_r, 3),
            "training_sicher_r": round(best.expectancy_lower_r, 3)}
    if best.expectancy_r <= 0:
        return None, {**info, "grund": "bis dahin keine Variante profitabel"}
    return best_label, info


def walk_forward(uni: Universe, key: str, cfg: RunConfig, wf: WFConfig,
                 loader: Loader) -> WFResult:
    vs = variants(key)
    base = REGISTRY[key]().describe()
    res = WFResult(
        strategy=base, variants=[label for label, _ in vs],
        config={"min_umsatz_usd": cfg.min_turnover_usd, "portfolio": cfg.portfolio.__dict__,
                "walk_forward": wf.__dict__},
        symbols_ok=list(uni.data), symbols_failed=dict(uni.failed), notes=list(uni.notes),
    )
    by_variant = {}
    for label, strat in vs:
        log.info("%s – Variante %s", key, label)
        tf = collect_trades(uni, strat)
        if not tf.empty:
            tf["asset_class"] = tf["symbol"].map(asset_class)
        by_variant[label] = tf

    if not uni.data:
        return res
    last_date = max(df.index[-1] for df in uni.data.values())
    windows = make_windows(wf.first_test_year, wf.window_years, last_date)

    oos_frames = []
    for cls in ("stock", "crypto"):
        tb = {lbl: (tf[tf["asset_class"] == cls] if not tf.empty else tf)
              for lbl, tf in by_variant.items()}
        if all(t.empty for t in tb.values()):
            continue
        rows, frames = [], []
        for ws, we in windows:
            choice, info = select_variant(tb, ws, wf.min_train_trades)
            last_year = (we - pd.Timedelta(days=1)).year
            label = (f"{ws.year}–heute" if we > last_date
                     else f"{ws.year}–{last_year}" if last_year != ws.year else str(ws.year))
            row = {"fenster": label, "variante": choice, **info}
            if choice is not None:
                t = tb[choice]
                entry = pd.to_datetime(t["entry_date"])
                test = t[(entry >= ws) & (entry < we)].assign(variante=choice)
                m = compute_metrics(test)
                row.update(trades=m.trades, offen=m.open_trades,
                           erwartung_r=round(m.expectancy_r, 3) if m.trades else None)
                frames.append(test)
            rows.append(row)
        res.windows[cls] = rows
        oos = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if oos.empty:
            res.summary[cls] = {"oos": compute_metrics(oos).to_dict(), "bestanden": False,
                                "gruende": ["in keinem Testfenster gehandelt"],
                                "huerden": GATES[cls].__dict__}
            continue
        oos_frames.append(oos)
        m = compute_metrics(oos)
        sim = simulate_portfolio(oos, cfg.portfolio)
        bench = benchmarks_for(cls, sim.stats["start"], sim.stats["ende"], cfg, loader)
        ew = universe_benchmark(uni, cls, sim.stats["start"], sim.stats["ende"])
        if ew:
            bench[UNIVERSE_BENCH] = ew
        pf = {**sim.stats, "vergleich": bench}
        res.portfolio[cls] = {"oos": pf}
        passed, problems = GATES[cls].check(m, pf)
        res.summary[cls] = {"oos": m.to_dict(), "bestanden": passed, "gruende": problems,
                            "huerden": GATES[cls].__dict__}

    res.trades = pd.concat(oos_frames, ignore_index=True) if oos_frames else pd.DataFrame()
    res.by_market = market_breakdown(res.trades)

    controls = REGISTRY[key].controls
    if controls:
        runs = [(label, "Variante", dict(vs)[label], by_variant[label]) for label, _ in vs]
        for c in controls:
            strat = get_strategy(key, **c["overrides"])
            log.info("%s – Kontrolle %s", key, c["label"])
            tf = collect_trades(uni, strat)
            if not tf.empty:
                tf["asset_class"] = tf["symbol"].map(asset_class)
            runs.append((c["label"], "Kontrolle", strat, tf))
        res.comparison = compare_runs(runs, pd.Timestamp(year=wf.first_test_year, month=1, day=1))
    return res


def compare_runs(runs: list, since: pd.Timestamp) -> dict:
    """
    Feste Regeln nebeneinander (alle Trades ab `since`): Varianten und Kontrollläufe.
    Dient nur dem Verständnis, welcher Baustein etwas beiträgt – nicht der Auswahl.
    """
    out: dict = {}
    for label, kind, strat, tf in runs:
        if tf.empty:
            continue
        tf = tf[pd.to_datetime(tf["entry_date"]) >= since]
        for cls, grp in tf.groupby("asset_class"):
            m = compute_metrics(grp)
            if m.trades == 0:
                continue
            chance = 100.0 / (1.0 + strat.target_r) if strat.target_r else None
            out.setdefault(cls, []).append({
                "lauf": label, "art": kind, "trades": m.trades,
                "trefferquote": round(m.winrate, 1), "trefferquote_sicher": round(m.winrate_lower, 1),
                "zufall": round(chance, 1) if chance else None,
                "vorsprung_pp": round(m.winrate - chance, 1) if chance else None,
                "erwartung_r": round(m.expectancy_r, 3),
                "erwartung_sicher_r": None if not np.isfinite(m.expectancy_lower_r)
                else round(m.expectancy_lower_r, 3),
                "profit_faktor": round(m.profit_factor, 2) if np.isfinite(m.profit_factor) else None,
            })
    return out
