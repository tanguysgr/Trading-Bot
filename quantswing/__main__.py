"""
Kommandozeile.

Beispiele:
  python -m quantswing backtest --universe config/universes/beispiel.txt
  python -m quantswing backtest --symbols AAPL SAP.DE BTC-USD --strategy trend_pullback
  python -m quantswing backtest --demo            # ohne Internet, mit Kunstdaten
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from .backtest.report import to_markdown
from .backtest.runner import run_many
from .data import load_ohlcv, synthetic_ohlcv
from .strategies import REGISTRY, get_strategy


def read_universe(path: str) -> list[str]:
    syms = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            syms.append(line)
    return syms


def cmd_backtest(args: argparse.Namespace) -> int:
    if args.demo:
        symbols = ["DEMO-A", "DEMO-B", "DEMO-C", "DEMO-D", "DEMO-E"]
        seeds = {s: i + 1 for i, s in enumerate(symbols)}
        loader = lambda s: synthetic_ohlcv(n=4000, seed=seeds[s], start="2008-01-01")  # noqa: E731
    else:
        symbols = list(args.symbols or [])
        if args.universe:
            symbols += read_universe(args.universe)
        if not symbols:
            print("Keine Symbole angegeben (--symbols oder --universe).", file=sys.stderr)
            return 2
        loader = lambda s: load_ohlcv(s, start=args.start, cache_dir=args.cache)  # noqa: E731

    keys = list(REGISTRY) if args.strategy == "all" else [args.strategy]
    results = []
    for key in keys:
        print(f"→ {key}: {len(symbols)} Symbole …", file=sys.stderr)
        results.append(run_many(symbols, get_strategy(key), loader, args.split))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = to_markdown(results)
    (out / "bericht.md").write_text(report, encoding="utf-8")
    summary = {
        r.strategy["key"]: {
            "strategie": r.strategy,
            "stichtag": r.split_date,
            "symbole_ok": r.symbols_ok,
            "symbole_fehler": r.symbols_failed,
            "auswertung": r.summary,
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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="quantswing", description="QuantSwing Signal-Bot")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("backtest", help="Strategien auf historischen Daten testen")
    b.add_argument("--symbols", nargs="*", help="Börsenkürzel, z.B. AAPL SAP.DE BTC-USD")
    b.add_argument("--universe", help="Textdatei mit einem Kürzel pro Zeile")
    b.add_argument("--strategy", default="all", choices=["all", *REGISTRY])
    b.add_argument("--start", default="2005-01-01", help="Beginn der Kursdaten")
    b.add_argument("--split", default="2018-01-01", help="Stichtag Training/Test")
    b.add_argument("--out", default="results", help="Ausgabeordner")
    b.add_argument("--cache", default=".cache/prices", help="Ordner für Kursdaten-Cache")
    b.add_argument("--demo", action="store_true", help="Kunstdaten statt Yahoo (offline)")
    b.add_argument("-v", "--verbose", action="store_true")
    b.set_defaults(func=cmd_backtest)

    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO if getattr(args, "verbose", False) else logging.WARNING,
                        format="%(levelname)s %(message)s")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
