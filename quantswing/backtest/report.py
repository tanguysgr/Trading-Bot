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


def _portfolio_table(lines: list[str], cols: dict[str, dict], rules: dict) -> None:
    """Tabelle der Portfolio-Simulation; `cols`: Spaltenüberschrift -> Kennzahlen."""
    if not cols:
        return
    lines += [
        "**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)",
        "",
        f"Max. {rules.get('max_positions')} Positionen gleichzeitig, max. "
        f"{rules.get('max_per_market')} pro Land, {100 * rules.get('risk_per_trade', 0):.0f} % "
        "Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.",
        "",
    ]
    head = " | ".join(f"{h} ({p['start'][:4]}–{p['ende'][:4]})" for h, p in cols.items())
    lines += [f"| | {head} |", "|---|" + "---:|" * len(cols)]

    def row(label, fn):
        lines.append(f"| {label} | " + " | ".join(fn(p) for p in cols.values()) + " |")

    row("**Rendite p.a. Strategie**", lambda p: f"**{_fmt(p['rendite_pa_pct'], ' %', 1)}**")
    row("Max. Drawdown Strategie", lambda p: _fmt(p["max_drawdown_pct"], " %", 1))
    row("MAR (Rendite ÷ Drawdown) Strategie", lambda p: _fmt(p.get("mar"), "", 2))
    bench_names = list(dict.fromkeys(b for p in cols.values() for b in p["vergleich"]))
    for b in bench_names:
        row(f"Rendite p.a. {b} (Kaufen & Halten)",
            lambda p, b=b: _fmt(p["vergleich"].get(b, {}).get("rendite_pa_pct"), " %", 1))
        row(f"Max. Drawdown {b}",
            lambda p, b=b: _fmt(p["vergleich"].get(b, {}).get("max_drawdown_pct"), " %", 1))
        row(f"MAR {b}", lambda p, b=b: _fmt(p["vergleich"].get(b, {}).get("mar"), "", 2))
    row("Trades genommen / übersprungen",
        lambda p: f"{p['trades_genommen']} / {p['trades_uebersprungen']}")
    row("Ø gleichzeitige Positionen", lambda p: _fmt(p["avg_positionen"], "", 1))
    row("Ø tatsächliches Risiko je Trade", lambda p: _fmt(p["avg_risiko_pct"], " %", 2))
    lines.append("")

    first = next(iter(cols.values()))
    years = first.get("jahresrenditen_pct", {})
    ref = bench_names[0] if bench_names else None
    ref_years = first.get("vergleich", {}).get(ref, {}).get("jahresrenditen_pct", {}) if ref else {}
    if years:
        lines += ["<details><summary>Jahresrenditen</summary>", "",
                  f"| Jahr | Strategie | {ref or '–'} |", "|---|---:|---:|"]
        for y in sorted(years):
            lines.append(f"| {y} | {_fmt(years[y], ' %', 1)} | {_fmt(ref_years.get(y), ' %', 1)} |")
        lines += ["", "</details>", ""]


def _portfolio(lines: list[str], res: BacktestResult, cls: str) -> None:
    pf = res.portfolio.get(cls) or {}
    cols = {("Gesamt" if k == "gesamt" else "**Test**"): pf[k] for k in ("gesamt", "test") if k in pf}
    _portfolio_table(lines, cols, res.config.get("portfolio", {}))


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
                  f"{s['exits']} · Parameter: `{s['params']}`", ""]
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


# ---------------------------------------------------------------------------
# Walk-Forward-Bericht
# ---------------------------------------------------------------------------

def _wf_header(lines: list[str], r0) -> None:
    wf = r0.config.get("walk_forward", {})
    lines += [
        "# Walk-Forward-Bericht",
        "",
        f"Testfenster à {wf.get('window_years')} Jahre ab {wf.get('first_test_year')}. "
        "Vor jedem Fenster wird – nur mit Trades, die bis dahin abgeschlossen waren – "
        "die beste Variante gewählt; sie handelt dann im Fenster. Alle Fenster zusammen "
        "ergeben ein echtes Out-of-Sample-Ergebnis.",
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


def _wf_windows(lines: list[str], rows: list[dict]) -> None:
    lines += ["**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)", "",
              "| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |",
              "|---|---|---:|---:|---:|---:|"]
    for r in rows:
        var = r["variante"] or f"– kein Handel ({r.get('grund', '')})"
        er = r.get("erwartung_r")
        lines.append(
            f"| {r['fenster']} | {var} | {_fmt(r.get('training_trades'))} | "
            f"{_fmt(r.get('training_erwartung_r'), ' R', 3)} | {_fmt(r.get('trades'))} | "
            f"{'–' if er is None else f'{er:+.3f} R'} |")
    lines.append("")


def _wf_stats(lines: list[str], block: dict) -> None:
    lines += ["**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)", "",
              "| Kennzahl | Out-of-Sample |", "|---|---:|"]
    for label, key, suf, dig in ROWS:
        lines.append(f"| {label} | {_fmt(block['oos'].get(key), suf, dig)} |")
    exits = block["oos"].get("exit_reasons") or {}
    if exits:
        lines.append("")
        lines.append("Ausstiege: " + ", ".join(f"{EXIT_LABELS.get(k, k)} {v}×" for k, v in exits.items()))
    lines.append("")


def walkforward_markdown(results: list) -> str:
    lines: list[str] = []
    if not results:
        return "# Walk-Forward-Bericht\n\n_Keine Ergebnisse._"
    _wf_header(lines, results[0])
    lines += ["## Übersicht", "",
              "| Strategie | Klasse | Urteil | Trades | Ø R | Depot p.a. | Drawdown | MAR "
              "| Vergleich p.a. / MAR |",
              "|---|---|---|---:|---:|---:|---:|---:|---|"]
    for res in results:
        for cls, block in res.summary.items():
            pf = res.portfolio.get(cls, {}).get("oos", {})
            comp = "<br>".join(
                f"{name}: {_fmt(b.get('rendite_pa_pct'), ' %', 1)} / {_fmt(b.get('mar'), '', 2)}"
                for name, b in pf.get("vergleich", {}).items())
            lines.append(
                f"| {res.strategy['title']} | {CLASS_LABEL.get(cls, cls)} | "
                f"{'✅' if block['bestanden'] else '❌'} | {block['oos'].get('trades')} | "
                f"{_fmt(block['oos'].get('expectancy_r'), ' R', 3)} | "
                f"{_fmt(pf.get('rendite_pa_pct'), ' %', 1)} | {_fmt(pf.get('max_drawdown_pct'), ' %', 1)} | "
                f"{_fmt(pf.get('mar'), '', 2)} | {comp or '–'} |")
    lines += ["", "MAR = Rendite p.a. ÷ größter Rückgang: wie viel Rendite pro ertragenem "
              "Verlust. Damit lassen sich Strategien mit weniger Risiko fair mit dem Index vergleichen.", ""]
    for res in results:
        s = res.strategy
        lines += [f"## {s['title']}", "", s["description"], "",
                  "Varianten: " + " · ".join(f"`{v}`" for v in res.variants), ""]
        for cls in ("stock", "crypto"):
            block = res.summary.get(cls)
            if not block:
                continue
            verdict = "✅ BESTANDEN" if block["bestanden"] else "❌ NICHT BESTANDEN"
            lines += [f"### {CLASS_LABEL.get(cls, cls)} – {verdict}", ""]
            if block["gruende"]:
                lines += [f"- {g}" for g in block["gruende"]] + [""]
            _wf_windows(lines, res.windows.get(cls, []))
            if block["oos"].get("trades"):
                _wf_stats(lines, block)
            pf = res.portfolio.get(cls, {}).get("oos")
            if pf:
                _portfolio_table(lines, {"Out-of-Sample": pf}, res.config.get("portfolio", {}))
        if res.by_market:
            _markets(lines, res)
    return "\n".join(lines)
