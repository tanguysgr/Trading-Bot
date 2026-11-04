"""
Kommandozeile.

Beispiele:
  python -m quantswing backtest --universe config/universes/welt.txt
  python -m quantswing backtest --symbols AAPL SAP.DE BTC-USD --strategy trend_pullback
  python -m quantswing backtest --demo            # ohne Internet, mit Kunstdaten
  python -m quantswing universe-check config/universes/welt.txt
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .backtest.portfolio import PortfolioRules
from .backtest.report import to_markdown
from .backtest.runner import RunConfig, run_many
from .data import load_fx_usd, load_ohlcv, prefetch, synthetic_ohlcv
from .strategies import REGISTRY, get_strategy
from .universe import by_market, read_universe



def _symbols(args: argparse.Namespace) -> list[str]:
    symbols = [s.upper() for s in (args.symbols or [])]
    for path in args.universe or []:
        symbols += read_universe(path)
    return list(dict.fromkeys(symbols))


def cmd_backtest(args: argparse.Namespace) -> int:
    cfg = RunConfig(
        split_date=args.split,
        min_turnover_usd=args.min_turnover * 1e6,
        portfolio=PortfolioRules(max_positions=args.max_positions,
                                 max_per_market=args.max_per_market,
                                 risk_per_trade=args.risk / 100.0),
    )
    fx_loader = None
    if args.demo:
        cfg.benchmarks = ()
        symbols = ["DEMO-A", "DEMO-B", "DEMO-C", "DEMO-D", "DEMO-E"]
        seeds = {s: i + 1 for i, s in enumerate(symbols)}

        def loader(s):
            if s not in seeds:
                raise KeyError(f"{s} gibt es im Demo-Modus nicht")
            return synthetic_ohlcv(n=4000, seed=seeds[s], start="2008-01-01")
    else:
        symbols = _symbols(args)
        if not symbols:
            print("Keine Symbole angegeben (--symbols oder --universe).", file=sys.stderr)
            return 2
        print(f"Lade Kursdaten für {len(symbols)} Symbole …", file=sys.stderr)
        prefetch(symbols + list(cfg.benchmarks), start=args.start, cache_dir=args.cache)

        def loader(s):
            return load_ohlcv(s, start=args.start, cache_dir=args.cache)

        def fx_loader(cur):
            return load_fx_usd(cur, start=args.start, cache_dir=args.cache)

    keys = list(REGISTRY) if args.strategy == "all" else [args.strategy]
    results = []
    for key in keys:
        print(f"→ {key}: {len(symbols)} Symbole …", file=sys.stderr)
        results.append(run_many(symbols, get_strategy(key), loader, cfg, fx_loader))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = to_markdown(results)
    (out / "bericht.md").write_text(report, encoding="utf-8")
    summary = {
        r.strategy["key"]: {
            "strategie": r.strategy,
            "stichtag": r.split_date,
            "einstellungen": r.config,
            "symbole_ok": r.symbols_ok,
            "symbole_fehler": r.symbols_failed,
            "hinweise": r.notes,
            "auswertung": r.summary,
            "laender": r.by_market,
            "portfolio": r.portfolio,
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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="quantswing", description="QuantSwing Signal-Bot")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("backtest", help="Strategien auf historischen Daten testen")
    b.add_argument("--symbols", nargs="*", help="Börsenkürzel, z.B. AAPL SAP.DE BTC-USD")
    b.add_argument("--universe", action="append", help="Universumsdatei (mehrfach möglich)")
    b.add_argument("--strategy", default="all", choices=["all", *REGISTRY])
    b.add_argument("--start", default="2005-01-01", help="Beginn der Kursdaten")
    b.add_argument("--split", default="2018-01-01", help="Stichtag Training/Test")
    b.add_argument("--min-turnover", type=float, default=5.0,
                   help="Mindest-Tagesumsatz in Mio. USD (0 = aus)")
    b.add_argument("--max-positions", type=int, default=10)
    b.add_argument("--max-per-market", type=int, default=4)
    b.add_argument("--risk", type=float, default=1.0, help="Risiko je Trade in %% des Kontos")
    b.add_argument("--out", default="results", help="Ausgabeordner")
    b.add_argument("--cache", default=".cache/prices", help="Ordner für Kursdaten-Cache")
    b.add_argument("--demo", action="store_true", help="Kunstdaten statt Yahoo (offline)")
    b.add_argument("-v", "--verbose", action="store_true")
    b.set_defaults(func=cmd_backtest)

    u = sub.add_parser("universe-check", help="Kürzel einer Universumsdatei prüfen")
    u.add_argument("file")
    u.add_argument("--start", default="2005-01-01")
    u.add_argument("--cache", default=".cache/prices")
    u.add_argument("-v", "--verbose", action="store_true")
    u.set_defaults(func=cmd_universe_check)

    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO if getattr(args, "verbose", False) else logging.WARNING,
                        format="%(levelname)s %(message)s")
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
