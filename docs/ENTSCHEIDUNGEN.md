# Entscheidungen

Kurz festgehalten, was entschieden wurde und warum. Neue Einträge unten anfügen.

### E1 – Signal-Bot, kein Auto-Trading (2026-11-03)
Der Bot meldet Setups mit Begründung; Ausführung erfolgt manuell.
Grund: Wunsch des Nutzers, Lernziel, kein Broker-Risiko.

### E2 – Swing-Trading auf Tageskerzen (2026-11-03)
Signale entstehen am Tagesschluss, Einstieg zur Eröffnung des nächsten Tages.
Grund: Kein Daytrading gewünscht. Yahoo liefert Stunden-/4H-Daten nur für rund
zwei Jahre – zu wenig für tausende Backtest-Trades. Tagesdaten reichen 20+ Jahre zurück.
Ein 4H-Feinschliff für den Einstieg kann später ergänzt werden.

### E3 – Keine KI, die Code umschreibt (2026-11-03)
Der Gemini-„Trainer“ wurde entfernt. Regeln so lange zu ändern, bis die
Vergangenheit gut aussieht, ist Overfitting. Optimiert werden künftig nur
Parameter, und nur, wenn das Ergebnis auf ungesehenen Daten (Test) hält.

### E4 – Krypto nur mit strengeren Hürden (2026-11-03)
Nutzer-Vorgabe: Krypto nur bei sehr hoher Erfolgswahrscheinlichkeit.
Umsetzung in `quantswing/backtest/metrics.py` (`GATES["crypto"]`): u.a.
gesicherte Trefferquote ≥ 50 %, Profit-Faktor ≥ 1,6, Drawdown ≤ 20 %.

### E5 – Konservative Ausführung im Backtest (2026-11-03)
Bei Stop und Ziel in derselben Kerze zählt der Stop; Gaps werden zum
Eröffnungskurs ausgeführt; Gebühren und Slippage auf beiden Seiten.
Lieber zu pessimistisch als eine Strategie, die nur auf dem Papier funktioniert.

### E6 – Bewertung nach Training/Test-Trennung (2026-11-03)
Bestanden ist eine Strategie nur, wenn sie im Testzeitraum (nach dem Stichtag)
die Hürden erfüllt UND im Trainingszeitraum profitabel war.
