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

### 2b – Strategien verbessern
- [ ] Walk-Forward-Test (rollierende Training/Test-Fenster) statt eines Stichtags
- [ ] Markt-Regime-Filter (z.B. Leitindex über SMA200, Volatilität)
- [ ] Ausstiege: Trailing-Stop / Gewinne laufen lassen statt festem 2-R-Ziel
- [ ] Relative Stärke als eigene Strategie bzw. Hauptkriterium
- [ ] Weitere Ideen testen und aussortieren

### 2c – Täglicher Scanner
- [ ] Nur Signale aus Strategien, die die Hürden bestanden haben
- [ ] Positionsgröße in € (Wechselkurs)
- [ ] Wirtschaftstermine (Earnings, Zentralbanken) als Warnhinweis am Signal

## Phase 3 – Oberfläche & Zugriff von überall
- [ ] Neues Dashboard (GitHub Pages): Signale, Begründungen, Kennzahlen, Charts
- [ ] Signal-Journal: Ergebnis jedes Signals wird automatisch nachverfolgt
- [ ] Benachrichtigung aufs Handy (Telegram)
- [ ] KI-Assistent im Dashboard für Fragen zu Signal und Markt (Schlüssel sicher, nicht im Browser)
- [ ] Lern-Bereich: warum ein Setup funktioniert, was dagegen spricht

## Phase 4 – optional
- [ ] Paper-Trading-Auswertung über mehrere Monate vor echtem Kapitaleinsatz
