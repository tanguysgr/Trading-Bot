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

### E7 – Weltweites Universum aus heutigen Index-Werten (2026-11-04)
`config/universes/welt.txt`: rund 500 große Aktien aus 24 Märkten plus Krypto.
Bekannte Schwäche (Survivorship Bias): Es sind die HEUTIGEN Mitglieder großer
Indizes. Firmen, die pleitegingen oder abstiegen, fehlen – Backtests wirken
dadurch etwas zu gut. Kostenlose historische Index-Zusammensetzungen gibt es
nicht zuverlässig; der Fehler wird hingenommen und bei der Bewertung bedacht.

### E8 – Liquiditätsfilter (2026-11-04)
Ein Signal zählt nur, wenn der Wert damals im Median der letzten 60 Tage für
mindestens 5 Mio. USD pro Tag gehandelt wurde (umgerechnet mit historischen
Wechselkursen). So landen keine Trades im Test, die man praktisch nicht
sauber hätte ausführen können.

### E9 – Portfolio-Regeln (2026-11-04)
Max. 10 Positionen, max. 4 je Land, 1 % Risiko je Trade, jede Position
höchstens 10 % des Kontos (kein Hebel). Bei zu vielen Signalen entscheidet die
6-Monats-Kursentwicklung am Signaltag (relative Stärke). Krypto wird getrennt
von Aktien simuliert.

### E10 – Drawdown-Hürde über das Portfolio (2026-11-04)
Bei hunderten Werten laufen Trades gleichzeitig. Ein Kontoverlauf, der alle
Trades hintereinander verbucht, ist dann sinnlos (zeigte −98 %). Die
Drawdown-Hürde gilt deshalb jetzt für die Portfolio-Simulation im Testzeitraum,
zusätzlich muss das Portfolio dort Gewinn machen.

### E11 – Walk-Forward als Hauptbewertung (2026-11-05)
Statt eines festen Stichtags: 2-Jahres-Testfenster ab 2010. Vor jedem Fenster
wird aus den Varianten einer Strategie diejenige mit der höchsten *unteren
Sicherheitsgrenze* des Erwartungswerts gewählt – nur mit Trades, die vor dem
Fenster abgeschlossen waren. War keine Variante profitabel, wird im Fenster
nicht gehandelt. Die Hürden (E4/E6/E10) gelten für alle Testfenster zusammen.
Der einfache Stichtag-Test bleibt als schneller Überblick erhalten.

### E12 – Varianten bewusst klein halten und mitzählen (2026-11-05)
Jede Strategie bekommt höchstens wenige, vorab festgelegte Varianten (aktuell 4).
Im Ergebnis-Logbuch steht ein Versuchszähler. Grund: Der Walk-Forward schützt
vor Überanpassung der Parameter, aber nicht davor, dass Menschen nach dem
Anschauen von Ergebnissen neue Ideen entwerfen. Je mehr Versuche, desto
skeptischer muss man bei einem Treffer sein.

### E13 – Hürden werden nicht nachträglich gesenkt (2026-11-05)
Relative Stärke verfehlt die Aktien-Hürde nur am Profit-Faktor (1,21 statt 1,30).
Die Hürde bleibt trotzdem. Würde man sie nach dem Anschauen der Ergebnisse
anpassen, bis etwas besteht, wäre sie wertlos. Änderungen an Hürden nur mit
Begründung, die unabhängig vom aktuellen Ergebnis ist.

### E14 – Marktkontext immer mit einem Tag Verzögerung (2026-11-05)
Regime-Filter (SPY bzw. Bitcoin über SMA200) und relative Stärke werden für
Tag t nur aus Daten bis Tag t−1 gebildet. Grund: Börsen schließen in
unterschiedlichen Zeitzonen – beim Schluss in Tokio ist der US-Schluss desselben
Tages noch unbekannt. Kostet etwas Aktualität, verhindert aber stillen
Blick in die Zukunft.

### E15 – Zusätzlicher Maßstab „Universum gleichgewichtet“ (2026-11-05)
Neben SPY/ACWI wird mit dem gleichgewichteten Halten aller Universumswerte
verglichen. Er zeigt, wie stark Survivorship Bias (E7) die Zahlen schönt
(2010–2026: 17,2 % p.a. gegenüber ACWI 9,9 %). Renditen in Landeswährung,
täglich neu gewichtet – eine grobe, aber ehrliche Messlatte.

### E16 – Krypto: „hohe Erfolgswahrscheinlichkeit“ = Trefferquote nachweislich > 50 % (2026-11-05)
Vom Nutzer bestätigt: Bei Krypto sollen die meisten Trades gewinnen. Umgesetzt
als strenge Prüfung: Nicht nur die gemessene Trefferquote, sondern ihre untere
Sicherheitsgrenze (Wilson, 95 %) muss über 50 % liegen – zusätzlich zu einem
positiven Erwartungswert. Entspricht der bestehenden Hürde `GATES["crypto"]`.
