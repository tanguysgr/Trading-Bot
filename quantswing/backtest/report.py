"""Backtest-Ergebnisse als Markdown-Bericht (lesbar auf GitHub und im Terminal)."""

from __future__ import annotations

from .engine import EXIT_LABELS
from .runner import BacktestResult

CLASS_LABEL = {"stock": "Aktien & ETFs", "crypto": "Krypto"}


def _fmt(v, suffix: str = "", digits: int = 2) -> str:
    if v is None:
        return "–"
    if isinstance(v, float):
        if v == float("inf"):
            return "∞"
        return f"{v:,.{digits}f}{suffix}".replace(",", " ")
    return f"{v}{suffix}"


ROWS = [
    ("Abgeschlossene Trades", "trades", "", 0),
    ("Trades pro Jahr", "trades_per_year", "", 1),
    ("Trefferquote", "winrate", " %", 1),
    ("… sicher mindestens", "winrate_lower", " %", 1),
    ("Ø Gewinn-Trade", "avg_win_r", " R", 2),
    ("Ø Verlust-Trade", "avg_loss_r", " R", 2),
    ("**Erwartungswert je Trade**", "expectancy_r", " R", 3),
    ("… sicher mindestens", "expectancy_lower_r", " R", 3),
    ("Profit-Faktor", "profit_factor", "", 2),
    ("Ø Haltedauer (Tage)", "avg_bars_held", "", 1),
]


def _trade_stats(lines: list[str], res: BacktestResult, cls: str) -> None:
    block = res.summary.get(cls)
    if block:
        verdict = "✅ BESTANDEN" if block["bestanden"] else "❌ NICHT BESTANDEN"
        lines += [f"### {CLASS_LABEL.get(cls, cls)} – {verdict}", ""]
        if block["gruende"]:
            lines += [f"- {g}" for g in block["gruende"]] + [""]
        lines += ["**Trade-Statistik** (alle Signale, ohne Depot-Begrenzung)", ""]
        lines += ["| Kennzahl | Gesamt | Training | **Test** |", "|---|---:|---:|---:|"]
        for label, key, suf, dig in ROWS:
            vals = [_fmt(block[p].get(key), suf, dig) for p in ("gesamt", "training", "test")]
            lines.append(f"| {label} | {vals[0]} | {vals[1]} | **{vals[2]}** |")
        exits = block["gesamt"].get("exit_reasons") or {}
        if exits:
            lines.append("")
            lines.append("Ausstiege: " + ", ".join(
                f"{EXIT_LABELS.get(k, k)} {v}×" for k, v in exits.items()))
        lines.append("")


def _portfolio(lines: list[str], res: BacktestResult, cls: str) -> None:
    pf = res.portfolio.get(cls)
    if not pf:
        return
    rules = res.config.get("portfolio", {})
    lines += [
        "**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)",
        "",
        f"Max. {rules.get('max_positions')} Positionen gleichzeitig, max. "
        f"{rules.get('max_per_market')} pro Land, {100 * rules.get('risk_per_trade', 0):.0f} % "
        "Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.",
        "",
    ]
    cols = [k for k in ("gesamt", "test") if k in pf]
    head = " | ".join(f"{'Gesamt' if c == 'gesamt' else '**Test**'} ({pf[c]['start'][:4]}–{pf[c]['ende'][:4]})"
                      for c in cols)
    lines += [f"| | {head} |", "|---|" + "---:|" * len(cols)]

    def row(label, fn):
        lines.append(f"| {label} | " + " | ".join(fn(pf[c]) for c in cols) + " |")

    row("**Rendite p.a. Strategie**", lambda p: f"**{_fmt(p['rendite_pa_pct'], ' %', 1)}**")
    row("Max. Drawdown Strategie", lambda p: _fmt(p["max_drawdown_pct"], " %", 1))
    bench_names = list(dict.fromkeys(b for c in cols for b in pf[c]["vergleich"]))
    for b in bench_names:
        row(f"Rendite p.a. {b} (Kaufen & Halten)",
            lambda p, b=b: _fmt(p["vergleich"].get(b, {}).get("rendite_pa_pct"), " %", 1))
        row(f"Max. Drawdown {b}",
            lambda p, b=b: _fmt(p["vergleich"].get(b, {}).get("max_drawdown_pct"), " %", 1))
    row("Trades genommen / übersprungen",
        lambda p: f"{p['trades_genommen']} / {p['trades_uebersprungen']}")
    row("Ø gleichzeitige Positionen", lambda p: _fmt(p["avg_positionen"], "", 1))
    row("Ø tatsächliches Risiko je Trade", lambda p: _fmt(p["avg_risiko_pct"], " %", 2))
    lines.append("")

    years = pf.get("gesamt", {}).get("jahresrenditen_pct", {})
    ref = bench_names[0] if bench_names else None
    ref_years = pf.get("gesamt", {}).get("vergleich", {}).get(ref, {}).get("jahresrenditen_pct", {}) if ref else {}
    if years:
        lines += ["<details><summary>Jahresrenditen</summary>", "",
                  f"| Jahr | Strategie | {ref or '–'} |", "|---|---:|---:|"]
        for y in sorted(years):
            lines.append(f"| {y} | {_fmt(years[y], ' %', 1)} | {_fmt(ref_years.get(y), ' %', 1)} |")
        lines += ["", "</details>", ""]


def _markets(lines: list[str], res: BacktestResult) -> None:
    if not res.by_market:
        return
    lines += ["<details><summary>Aufschlüsselung nach Ländern (alle Trades)</summary>", "",
              "| Markt | Symbole | Trades | Trefferquote | Erwartungswert | Profit-Faktor |",
              "|---|---:|---:|---:|---:|---:|"]
    for r in res.by_market:
        lines.append(f"| {r['markt']} | {r['symbole']} | {r['trades']} | {r['trefferquote']} % | "
                     f"{r['erwartungswert_r']:+.3f} R | {_fmt(r['profit_faktor'])} |")
    lines += ["", "Einzelne Länder haben oft zu wenige Trades für sichere Aussagen – "
              "nur grobe Hinweise.", "", "</details>", ""]


def to_markdown(results: list[BacktestResult]) -> str:
    lines = ["# Backtest-Bericht", ""]
    if results:
        r0 = results[0]
        lines += [
            f"Stichtag Training/Test: **{r0.split_date}** – Regeln wurden nur "
            "mit Daten davor entwickelt; entscheidend ist die Spalte **Test**.",
            "",
            f"Symbole: {len(r0.symbols_ok)} geladen"
            + (f", {len(r0.symbols_failed)} fehlgeschlagen" if r0.symbols_failed else "")
            + f" · Liquiditätsfilter: mind. {r0.config.get('min_umsatz_usd', 0) / 1e6:.0f} Mio. USD "
              "Tagesumsatz (Median 60 Tage)",
            "",
            "> Ein Backtest zeigt die Vergangenheit, keine Garantie für die Zukunft. "
            "Keine Anlageberatung.",
            "",
        ]
        for n in r0.notes:
            lines.append(f"> ⚠️ {n}")
        if r0.notes:
            lines.append("")
    for res in results:
        s = res.strategy
        lines += [f"## {s['title']}", "", s["description"], "",
                  f"Kursziel {s['target_r']} R · Zeit-Stop {s['max_bars']} Tage · "
                  f"Parameter: `{s['params']}`", ""]
        if not res.summary:
            lines += ["_Keine Trades erzeugt._", ""]
        for cls in ("stock", "crypto"):
            _trade_stats(lines, res, cls)
            _portfolio(lines, res, cls)
        _markets(lines, res)
    if results and results[0].symbols_failed:
        lines += ["<details><summary>Fehlgeschlagene Symbole</summary>", ""]
        lines += [f"- `{k}`: {v}" for k, v in results[0].symbols_failed.items()]
        lines += ["", "</details>", ""]
    return "\n".join(lines)
