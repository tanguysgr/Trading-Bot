# Hinweise für Claude

- Sprache: Deutsch (Code-Kommentare, Doku, Ausgaben). Bezeichner im Code englisch.
- Nutzer ist Einsteiger mit Lernziel: Begründungen und Erklärungen in Klartext mitliefern.
- Bot ist ein Signal-Bot (keine Order-Ausführung). Swing-Trading auf Tageskerzen.
- Krypto nur mit strengeren Hürden (`GATES["crypto"]`).
- Nie: Kennzahlen hart codieren, Zufallswerte als Indikatoren, Code von einer KI
  selbst umschreiben lassen, Blick in die Zukunft in Indikatoren/Strategien.
- Jede neue Strategie: eigene Datei in `quantswing/strategies/`, im REGISTRY
  eintragen, wird automatisch vom Look-ahead-Test in `tests/test_indicators.py` geprüft.
- Arbeitsweise: ein Branch + Pull Request pro Phase/Thema; Entscheidungen in
  `docs/ENTSCHEIDUNGEN.md`, Stand in `docs/ROADMAP.md` pflegen.
- Wichtige Backtest-Läufe: Bericht nach `docs/ergebnisse/<datum>_<thema>.md`,
  Kurzfazit oben in `docs/ERGEBNISSE.md`.
- Vor jedem Push: `pytest -q`.
