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
        return f"{v:.{digits}f}{suffix}"
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
    ("Max. Drawdown (1 % Risiko/Trade)", "max_drawdown_pct", " %", 1),
    ("Rendite p.a. (1 % Risiko/Trade)", "cagr_pct", " %", 1),
    ("Längste Verlustserie", "max_losing_streak", "", 0),
    ("Ø Haltedauer (Tage)", "avg_bars_held", "", 1),
]


def to_markdown(results: list[BacktestResult]) -> str:
    lines = ["# Backtest-Bericht", ""]
    if results:
        lines += [
            f"Stichtag Training/Test: **{results[0].split_date}** – Regeln wurden nur "
            "mit Daten davor entwickelt; entscheidend ist die Spalte **Test**.",
            "",
            "> Ein Backtest zeigt die Vergangenheit, keine Garantie für die Zukunft. "
            "Keine Anlageberatung.",
            "",
        ]
    for res in results:
        s = res.strategy
        lines += [f"## {s['title']}", "", s["description"], ""]
        lines.append(
            f"Kursziel {s['target_r']} R · Zeit-Stop {s['max_bars']} Tage · "
            f"Parameter: `{s['params']}`"
        )
        lines.append("")
        lines.append(f"Symbole getestet: {len(res.symbols_ok)}"
                     + (f" · fehlgeschlagen: {len(res.symbols_failed)}" if res.symbols_failed else ""))
        lines.append("")
        if not res.summary:
            lines += ["_Keine Trades erzeugt._", ""]
        for cls, block in res.summary.items():
            verdict = "✅ BESTANDEN" if block["bestanden"] else "❌ NICHT BESTANDEN"
            lines += [f"### {CLASS_LABEL.get(cls, cls)} – {verdict}", ""]
            if block["gruende"]:
                lines += [f"- {g}" for g in block["gruende"]] + [""]
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
        if res.symbols_failed:
            lines += ["<details><summary>Fehlgeschlagene Symbole</summary>", ""]
            lines += [f"- `{k}`: {v}" for k, v in res.symbols_failed.items()]
            lines += ["", "</details>", ""]
    return "\n".join(lines)
