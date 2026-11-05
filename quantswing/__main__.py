"""
Kommandozeile.

Beispiele:
  python -m quantswing walkforward --universe config/universes/welt.txt     # ehrlichster Test
  python -m quantswing backtest --universe config/universes/welt.txt        # fester Stichtag
  python -m quantswing backtest --symbols AAPL SAP.DE BTC-USD --strategy trend_pullback
  python -m quantswing backtest --demo            # ohne Internet, mit Kunstdaten
  python -m quantswing universe-check config/universes/welt.txt
  python -m quantswing chart SAP.DE NVDA BTC-USD --von 2025-08-01      # Prüf-Charts
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from .backtest.portfolio import PortfolioRules
from .backtest.report import to_markdown, walkforward_markdown
from .backtest.runner import RunConfig, prepare_universe, run_many
from .backtest.walkforward import WFConfig, walk_forward
from .data import load_fx_usd, load_ohlcv, prefetch, synthetic_ohlcv
from .strategies import REGISTRY, get_strategy
from .universe import by_market, read_universe

DEMO_SYMBOLS = ["DEMO-A", "DEMO-B", "DEMO-C", "DEMO-D", "DEMO-E", "DEMO-F", "DEMO-G", "DEMO-H"]


def _symbols(args: argparse.Namespace) -> list[str]:
    symbols = [s.upper() for s in (args.symbols or [])]
    for path in args.universe or []:
        symbols += read_universe(path)
    return list(dict.fromkeys(symbols))


def _setup(args: argparse.Namespace):
    """Gemeinsamer Teil von backtest und walkforward: Einstellungen, Daten, Universum."""
    cfg = RunConfig(
        split_date=getattr(args, "split", "2018-01-01"),
        min_turnover_usd=args.min_turnover * 1e6,
        portfolio=PortfolioRules(max_positions=args.max_positions,
                                 max_per_market=args.max_per_market,
                                 risk_per_trade=args.risk / 100.0),
    )
    fx_loader = None
    if args.demo:
        cfg.benchmarks, cfg.crypto_benchmarks = (), ()
        cfg.regime_symbols = {"stock": "DEMO-INDEX"}
        seeds = {s: i + 1 for i, s in enumerate(DEMO_SYMBOLS + ["DEMO-INDEX"])}
        symbols = list(DEMO_SYMBOLS)

        def loader(s):
            if s not in seeds:
                raise KeyError(f"{s} gibt es im Demo-Modus nicht")
            return synthetic_ohlcv(n=4500, seed=seeds[s], start="2006-01-01")
    else:
        symbols = _symbols(args)
        if not symbols:
            return None
        extra = list(cfg.benchmarks) + list(cfg.crypto_benchmarks) + list(cfg.regime_symbols.values())
        print(f"Lade Kursdaten für {len(symbols)} Symbole …", file=sys.stderr)
        prefetch(list(dict.fromkeys(symbols + extra)), start=args.start, cache_dir=args.cache)

        def loader(s):
            return load_ohlcv(s, start=args.start, cache_dir=args.cache)

        def fx_loader(cur):
            return load_fx_usd(cur, start=args.start, cache_dir=args.cache)

    print("Bereite Universum vor (Liquidität, Regime, relative Stärke) …", file=sys.stderr)
    uni = prepare_universe(symbols, loader, cfg, fx_loader)
    return cfg, loader, uni


def _keys(args) -> list[str]:
    keys = args.strategy if isinstance(args.strategy, list) else [args.strategy]
    return list(REGISTRY) if "all" in keys else keys


def cmd_backtest(args: argparse.Namespace) -> int:
    setup = _setup(args)
    if setup is None:
        print("Keine Symbole angegeben (--symbols oder --universe).", file=sys.stderr)
        return 2
    cfg, loader, uni = setup
    results = []
    for key in _keys(args):
        print(f"→ {key} …", file=sys.stderr)
        results.append(run_many(list(uni.data), get_strategy(key), loader, cfg, universe=uni))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = to_markdown(results)
    (out / "bericht.md").write_text(report, encoding="utf-8")
    summary = {
        r.strategy["key"]: {
            "strategie": r.strategy, "stichtag": r.split_date, "einstellungen": r.config,
            "symbole_ok": r.symbols_ok, "symbole_fehler": r.symbols_failed, "hinweise": r.notes,
            "auswertung": r.summary, "laender": r.by_market, "portfolio": r.portfolio,
        }
        for r in results
    }
    (out / "zusammenfassung.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    for r in results:
        r.trades.to_csv(out / f"trades_{r.strategy['key']}.csv", index=False)
    print(report)
    print(f"\nErgebnisse gespeichert in: {out}/", file=sys.stderr)
    return 0


def cmd_walkforward(args: argparse.Namespace) -> int:
    setup = _setup(args)
    if setup is None:
        print("Keine Symbole angegeben (--symbols oder --universe).", file=sys.stderr)
        return 2
    cfg, loader, uni = setup
    wf = WFConfig(first_test_year=args.first_test_year, window_years=args.window_years,
                  min_train_trades=args.min_train_trades)
    results = []
    for key in _keys(args):
        t0 = time.time()
        print(f"→ {key}: {len(REGISTRY[key].grid) or 1} Varianten …", file=sys.stderr)
        results.append(walk_forward(uni, key, cfg, wf, loader))
        print(f"  fertig in {time.time() - t0:.0f} s", file=sys.stderr)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = walkforward_markdown(results)
    (out / "bericht_walkforward.md").write_text(report, encoding="utf-8")
    summary = {
        r.strategy["key"]: {
            "strategie": r.strategy, "varianten": r.variants, "einstellungen": r.config,
            "symbole_ok": r.symbols_ok, "symbole_fehler": r.symbols_failed, "hinweise": r.notes,
            "fenster": r.windows, "auswertung": r.summary, "portfolio": r.portfolio,
            "laender": r.by_market, "vergleich": r.comparison,
        }
        for r in results
    }
    (out / "zusammenfassung_walkforward.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    for r in results:
        r.trades.to_csv(out / f"trades_oos_{r.strategy['key']}.csv", index=False)
    print(report)
    print(f"\nErgebnisse gespeichert in: {out}/", file=sys.stderr)
    return 0


def cmd_universe_check(args: argparse.Namespace) -> int:
    """Prüft, ob Yahoo für jedes Kürzel einer Universumsdatei Daten liefert."""
    symbols = read_universe(args.file)
    print(f"{len(symbols)} Symbole: {dict(by_market(symbols))}", file=sys.stderr)
    missing = prefetch(symbols, start=args.start, cache_dir=args.cache)
    bad = {}
    for s in missing:
        try:
            load_ohlcv(s, start=args.start, cache_dir=args.cache)
        except Exception as e:  # noqa: BLE001
            bad[s] = str(e)
    if bad:
        print("Ohne Daten (Kürzel prüfen, evtl. umbenannt oder von der Börse genommen):")
        for s, e in bad.items():
            print(f"  {s}: {e}")
        return 1
    print("Alle Kürzel liefern Daten.")
    return 0


def cmd_chart(args: argparse.Namespace) -> int:
    """Prüf-Charts: Swings, BOS/CHoCH, Fibonacci, Zonen und SMAs je Symbol als PNG."""
    from .charts import plot_structure

    out = Path(args.out)
    for sym in args.symbols:
        df = load_ohlcv(sym.upper(), start=args.start, cache_dir=args.cache)
        path = plot_structure(df, sym.upper(), args.von, out / f"{sym.upper().replace('.', '_')}.png")
        print(path)
    return 0


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--symbols", nargs="*", help="Börsenkürzel, z.B. AAPL SAP.DE BTC-USD")
    parser.add_argument("--universe", action="append", help="Universumsdatei (mehrfach möglich)")
    parser.add_argument("--strategy", nargs="+", default=["all"], choices=["all", *REGISTRY],
                        help="eine oder mehrere Strategien (Standard: alle)")
    parser.add_argument("--start", default="2005-01-01", help="Beginn der Kursdaten")
    parser.add_argument("--min-turnover", type=float, default=5.0,
                        help="Mindest-Tagesumsatz in Mio. USD (0 = aus)")
    parser.add_argument("--max-positions", type=int, default=10)
    parser.add_argument("--max-per-market", type=int, default=4)
    parser.add_argument("--risk", type=float, default=1.0, help="Risiko je Trade in %% des Kontos")
    parser.add_argument("--out", default="results", help="Ausgabeordner")
    parser.add_argument("--cache", default=".cache/prices", help="Ordner für Kursdaten-Cache")
    parser.add_argument("--demo", action="store_true", help="Kunstdaten statt Yahoo (offline)")
    parser.add_argument("-v", "--verbose", action="store_true")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="quantswing", description="QuantSwing Signal-Bot")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("backtest", help="Strategien mit festem Stichtag testen")
    _common(b)
    b.add_argument("--split", default="2018-01-01", help="Stichtag Training/Test")
    b.set_defaults(func=cmd_backtest)

    w = sub.add_parser("walkforward", help="Walk-Forward-Test mit rollierenden Testfenstern")
    _common(w)
    w.add_argument("--first-test-year", type=int, default=2010)
    w.add_argument("--window-years", type=int, default=2)
    w.add_argument("--min-train-trades", type=int, default=30)
    w.set_defaults(func=cmd_walkforward)

    u = sub.add_parser("universe-check", help="Kürzel einer Universumsdatei prüfen")
    u.add_argument("file")
    u.add_argument("--start", default="2005-01-01")
    u.add_argument("--cache", default=".cache/prices")
    u.add_argument("-v", "--verbose", action="store_true")
    u.set_defaults(func=cmd_universe_check)

    c = sub.add_parser("chart", help="Prüf-Chart: was erkennt der Bot auf dem Chart?")
    c.add_argument("symbols", nargs="+")
    c.add_argument("--von", default="2025-01-01", help="Chart-Ausschnitt ab (JJJJ-MM-TT)")
    c.add_argument("--start", default="2018-01-01", help="Kursdaten ab (für SMA 200 & Co.)")
    c.add_argument("--out", default="charts")
    c.add_argument("--cache", default=".cache/prices")
    c.add_argument("-v", "--verbose", action="store_true")
    c.set_defaults(func=cmd_chart)

    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO if getattr(args, "verbose", False) else logging.WARNING,
                        format="%(levelname)s %(message)s")
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
