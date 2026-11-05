# QuantSwing – Signal-Bot für Swing-Trading

QuantSwing sucht weltweit nach Swing-Trading-Setups (Haltedauer Tage bis Wochen),
prüft jede Strategie vorher mit tausenden historischen Trades und erklärt jedes
Signal in Klartext. **Der Bot handelt nicht selbst** – du entscheidest und führst aus.

Ziel ist nicht blindes Nachtraden, sondern den Markt zu verstehen.

> Backtests zeigen die Vergangenheit, keine Garantie für die Zukunft. Keine Anlageberatung.

---

## Projektstruktur

```
trading-bot/
├── quantswing/               ← der eigentliche Bot (Python-Paket)
│   ├── data.py               Kursdaten laden, prüfen, zwischenspeichern, Umsatz in USD
│   ├── markets.py            Börsenplatz + Währung aus dem Kürzel (SAP.DE → Deutschland, EUR)
│   ├── universe.py           Universumsdateien lesen
│   ├── context.py            Marktkontext: Regime-Filter, relative Stärke
│   ├── indicators.py         SMA, EMA, ATR, RSI, ADX, Swings, Strukturbruch
│   ├── structure.py          Confluence-Bausteine: Swings, BOS/CHoCH, Fibonacci, Zonen
│   ├── charts.py             Prüf-Charts: was der Bot auf dem Chart erkennt
│   ├── strategies/           eine Datei pro Strategie
│   │   ├── base.py           Grundgerüst, das jede Strategie erfüllen muss
│   │   ├── trend_pullback.py Strategie 1: Rücksetzer im Aufwärtstrend
│   │   ├── breakout.py       Strategie 2: Ausbruch mit Volumen
│   │   └── momentum.py       Strategie 3: Relative Stärke (Momentum)
│   ├── backtest/             Prüfstand
│   │   ├── engine.py         spielt Trades Kerze für Kerze durch
│   │   ├── metrics.py        Kennzahlen + Hürden „bestanden / nicht bestanden“
│   │   ├── portfolio.py      Depot-Simulation (Positionslimits, Vergleich mit Index)
│   │   ├── runner.py         viele Symbole, Liquidität, Trennung Training / Test
│   │   ├── walkforward.py    Walk-Forward-Test (rollierende Testfenster)
│   │   └── report.py         Bericht als Tabelle
│   └── __main__.py           Kommandozeile (python -m quantswing …)
├── config/universes/         Listen von Börsenkürzeln (welt.txt = ~500 Werte weltweit)
├── tests/                    automatische Prüfungen (laufen bei jedem Push)
├── docs/                     Doku: Fahrplan, Entscheidungen, Erklärungen
│   ├── ERGEBNISSE.md         Logbuch aller Backtest-Läufe mit Fazit
│   ├── recherche/            Recherche-Berichte (z.B. Regeln für Confluence-Trading)
│   └── ergebnisse/           vollständige Berichte der Läufe
├── legacy/                   alte Gemini-Oberfläche, nur als Vorlage für Phase 3
└── .github/workflows/        Automatisierung auf GitHub
```

**Faustregel:** Strategien kommen nur unter `strategies/`, Kennzahlen nur unter
`backtest/`, Indikatoren nur in `indicators.py`. Jede Datei hat eine Aufgabe.

## Backtest starten (ohne eigenen Rechner)

1. Auf GitHub den Reiter **Actions** öffnen
2. Links **Backtest** wählen → rechts **Run workflow**
3. Modus wählen (**walkforward** ist der ehrlichste Test), Strategie und Zeitraum
   wählen (Voreinstellungen passen) → **Run workflow**
4. Nach 10–20 Minuten den Lauf anklicken: Der Bericht steht direkt auf der
   Seite, alle Einzeltrades gibt es unten unter **Artifacts** als Download.

Was die Kennzahlen bedeuten: [docs/BACKTEST_ERKLAERT.md](docs/BACKTEST_ERKLAERT.md)

## Auf dem eigenen Rechner (optional)

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest                                                   # Prüfungen
python -m quantswing backtest --demo                     # Probelauf mit Kunstdaten
python -m quantswing walkforward --universe config/universes/welt.txt   # ehrlichster Test
python -m quantswing backtest --universe config/universes/welt.txt      # fester Stichtag
python -m quantswing backtest --symbols SAP.DE AAPL --strategy trend_pullback
python -m quantswing universe-check config/universes/welt.txt   # Kürzel prüfen
python -m quantswing chart SAP.DE BTC-USD --von 2025-08-01      # Prüf-Charts
```

## Arbeitsweise

- Jede Phase bzw. jedes größere Thema bekommt einen **eigenen Branch** und
  einen **Pull Request**. Dort siehst du alle Änderungen und klickst auf
  *Merge*, wenn du einverstanden bist. `main` bleibt immer lauffähig.
- Wichtige Entscheidungen mit Begründung stehen in
  [docs/ENTSCHEIDUNGEN.md](docs/ENTSCHEIDUNGEN.md).
- Stand und nächste Schritte: [docs/ROADMAP.md](docs/ROADMAP.md).
- Jeder wichtige Backtest landet mit Fazit im Logbuch
  [docs/ERGEBNISSE.md](docs/ERGEBNISSE.md) – so bleibt nachvollziehbar,
  welche Änderung was gebracht hat.
