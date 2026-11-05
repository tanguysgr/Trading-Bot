# Fahrplan

## Phase 1 – Ehrlicher Prüfstand ✅
- [x] Gemini-Altlasten entfernt (gefälschte Backtests, KI-Selbstüberschreibung)
- [x] Echte Indikatoren (Wilder-ATR/RSI/ADX, Swings ohne Blick in die Zukunft)
- [x] Backtest-Engine mit konservativen Ausführungsregeln, Gebühren, Slippage
- [x] Kennzahlen in R, statistische Sicherheit, Training/Test-Trennung
- [x] Strengere Hürden für Krypto
- [x] Zwei Strategie-Vorlagen: Trend-Pullback, Ausbruch mit Volumen
- [x] Automatische Tests + manueller Backtest auf GitHub
- [x] Erster echter Backtest-Lauf auf GitHub und gemeinsame Auswertung

## Phase 2 – Strategien & Scanner
### 2a – Mehr Daten, realistischere Simulation ✅
- [x] Weltweites Universum (502 Werte, 24 Märkte) + Prüfwerkzeug für Kürzel
- [x] Börsenplatz und Währung je Kürzel, historische Wechselkurse
- [x] Liquiditätsfilter (Tagesumsatz in USD, ohne Blick in die Zukunft)
- [x] Portfolio-Simulation: begrenzte Positionen, Klumpenrisiko je Land, kein Hebel
- [x] Vergleich mit Kaufen & Halten (SPY, ACWI, BTC)
- [x] Ergebnis-Logbuch (`docs/ERGEBNISSE.md`)

### 2b – Strategien verbessern ✅
- [x] Walk-Forward-Test (2-Jahres-Testfenster ab 2010, Variantenwahl nur mit Vergangenheit)
- [x] Markt-Regime-Filter (SPY bzw. Bitcoin über SMA200, um einen Tag verzögert)
- [x] Ausstiege: Trailing-Stop / Gewinne laufen lassen statt festem 2-R-Ziel
- [x] Relative Stärke als eigene Strategie (bisher beste Idee, Hürde knapp verfehlt)
- [x] Vergleichsmaßstäbe: MAR-Quote, Universum gleichgewichtet

### 2b+ – offene Forschungsfragen (nach Bedarf)
- [ ] Wie gehen wir damit um, dass noch keine Strategie die Hürden besteht? (siehe ERGEBNISSE.md)
- [ ] Survivorship Bias verringern (historische Index-Zusammensetzungen, ggf. kostenpflichtig)
- [ ] Positionsgröße: Hebelgrenze 10 %/Position drückt das echte Risiko auf ~0,6 % je Trade
- [ ] Wirtschaftsdaten/Ereignisse als Filter (Earnings-Termine, Zinsentscheide)

### 2c – Deine Confluence-Strategie (SMA, Fibonacci, Zonen, BOS/CHoCH)
Recherche: `docs/recherche/confluence_regeln.md`
- [x] Teil 1: Bausteine als geprüfte Indikatoren (Swings, BOS/CHoCH, Fibonacci, Zonen) + Prüf-Charts
- [x] Teil 2: Strategie Long + Short, 4 Varianten, 3 Kontrollläufe, Walk-Forward (Ergebnis: Fibonacci und BOS ohne Mehrwert, Krypto Long vielversprechend)
- [ ] Teil 3: Daten-Import 1H/4H (Binance für Krypto, Alpaca für US-Aktien)

### 2d – Täglicher Scanner
- [ ] Signale mit Begründung; Kennzeichnung „bestanden“ bzw. „nur Beobachtung“
- [ ] Signal-Journal: Ergebnis jedes Signals wird automatisch nachverfolgt
- [ ] Positionsgröße in € (Wechselkurs)
- [ ] Wirtschaftstermine (Earnings, Zentralbanken) als Warnhinweis am Signal

## Phase 3 – Oberfläche & Zugriff von überall
- [ ] Neues Dashboard (GitHub Pages): Signale, Begründungen, Kennzahlen, Charts
- [ ] Benachrichtigung aufs Handy (Telegram)
- [ ] KI-Assistent im Dashboard für Fragen zu Signal und Markt (Schlüssel sicher, nicht im Browser)
- [ ] Lern-Bereich: warum ein Setup funktioniert, was dagegen spricht

## Phase 4 – optional
- [ ] Paper-Trading-Auswertung über mehrere Monate vor echtem Kapitaleinsatz
