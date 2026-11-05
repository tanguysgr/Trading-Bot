# Ergebnis-Logbuch

Jeder wichtige Backtest-Lauf mit Datum, Stand und Fazit – neuester oben.
Die vollständigen Berichte liegen in [`docs/ergebnisse/`](ergebnisse/).

Lesehilfe: [BACKTEST_ERKLAERT.md](BACKTEST_ERKLAERT.md). Entscheidend sind immer Ergebnisse auf
ungesehenen Daten: beim Walk-Forward alle Testfenster zusammen, beim einfachen Test die Spalte **Test**.

---

**Versuchszähler** (je mehr Ideen getestet werden, desto eher ist ein Treffer Zufall):
4 Strategie-Ideen · 20 Varianten (+ 14 Kontrollläufe, nie auswählbar) · Stand 2026-11-06

---

## 2026-11-06 · Phase 2c · Confluence-Strategie des Nutzers (Long + Short)

Bericht: [2026-11-06_phase2c_confluence.md](ergebnisse/2026-11-06_phase2c_confluence.md)
Regeln: Trend (SMA50/200 + BOS/CHoCH) + Zone (SMA, Fibonacci 0,5–0,618, Swing-Zone) +
Bestätigungskerze, Ziel 1,25 R (E19). Walk-Forward ab 2010, 4 Varianten je Richtung.

| Richtung | Klasse | Trades OOS | Trefferquote | Ø R | sicher ≥ | Depot p.a. | Drawdown | MAR | Urteil |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Long | Aktien | 23 755 | 40,5 % | +0,03 | −0,00 | 5,7 % | −33,2 % | 0,17 | ❌ |
| Long | Krypto | 183 | 39,9 % | +0,70 | +0,28 | 11,2 % | −12,3 % | 0,91 | ❌ Trefferquote < 50 % |
| Short | Aktien | 0 | – | – | – | – | – | – | ❌ nie profitabel, nie gehandelt |
| Short | Krypto | 98 | 25,5 % | −0,16 | −0,37 | −1,8 % | −16,2 % | – | ❌ |

Vergleich Aktien (2010–2026): SPY 13,7 % (MAR 0,41), ACWI 9,9 % (0,30). Krypto (2018–2026): BTC 34,0 % (MAR 0,44).

**Kontrollläufe – welcher Baustein trägt? (feste Regeln, alle Trades ab 2010)**

| Lauf | Aktien Long: Trefferquote / Ø R | Krypto Long: Trefferquote / Ø R |
|---|---|---|
| V1 Basis | 48,6 % / −0,01 R | 52,3 % / +0,15 R |
| K1 ohne Fibonacci | 48,5 % / −0,02 R | 52,6 % / +0,15 R |
| K2 Zufalls-Fibonacci (5 Läufe) | 48,5–48,6 % / −0,02 bis −0,00 R | 51,5–54,3 % / +0,14 bis +0,18 R |
| K3 Ausbruch statt BOS/CHoCH | 48,6 % / −0,02 R | 51,7 % / +0,13 R |

Zufallsniveau bei 1,25 R: 44,4 %.

**Fazit**
- **Fibonacci trägt nichts bei.** Ohne Fibonacci oder mit zufälligen Zonen gleicher Breite
  sind die Ergebnisse praktisch identisch – bei Aktien wie bei Krypto. Deckt sich mit der Recherche.
- **BOS/CHoCH ist nicht besser als ein simpler 20-Tage-Ausbruch** als Trendbestätigung.
- **Aktien Long:** Die Trefferquote liegt 4 Prozentpunkte über dem Zufallsniveau, aber Kosten
  und Kurslücken fressen das auf (Ø −0,01 R bei festem Ziel). Ein Teil der 4 Pp dürfte zudem
  aus dem Survivorship Bias stammen (nur heutige Gewinner im Universum steigen im Schnitt).
  Mit Trailing-Stop (V4) bleibt ein kleiner Vorteil (+0,04 R), der als Depot aber deutlich
  hinter dem Index liegt.
- **Short bei Aktien verliert klar** (Trefferquote 36 %, 9 Pp UNTER dem Zufall, −0,26 R). Der
  Walk-Forward hat deshalb zu Recht nie gehandelt. Achtung: Survivorship Bias benachteiligt
  Shorts besonders – die Liste enthält nur Firmen, die sich am Ende erholt haben. Der wahre Wert
  ist vermutlich weniger schlecht, aber kaum positiv.
- **Krypto Long ist der interessanteste Teil:** Mit Trailing-Stop +0,70 R je Trade (sicher
  ≥ +0,28 R), als Depot 11 % p.a. bei nur −12 % Rückgang – risikobereinigt doppelt so gut wie
  Bitcoin halten (MAR 0,91 vs. 0,44). Aber: Trefferquote 40 %, die Krypto-Hürde (sicher > 50 %,
  E16) ist damit klar verfehlt. Die Variante mit festem Ziel und internem Bruch (V3) erreicht
  55 % Trefferquote, ist mit 132 Trades aber noch nicht sicher über 50 % (untere Grenze 48 %).
  Nur 6 Coins und wenige Jahre – mehr Trades kann es nur über 4H-Daten geben (Teil 3).

---

## 2026-11-05 · Phase 2b · Walk-Forward mit 3 Strategien × 4 Varianten

Bericht: [2026-11-05_phase2b_walkforward.md](ergebnisse/2026-11-05_phase2b_walkforward.md)
Neu: Walk-Forward (2-Jahres-Testfenster ab 2010), Trailing-Stop, Markt-Regime-Filter,
Strategie „Relative Stärke“, Vergleichsmaßstab „Universum gleichgewichtet“, MAR-Quote.

| Strategie | Klasse | Trades OOS | Ø R | sicher ≥ | Depot p.a. | Drawdown | MAR | Urteil |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Trend-Pullback | Aktien | 16 611 | +0,06 | +0,03 | 1,7 % | −34,9 % | 0,05 | ❌ |
| Ausbruch (BOS + RVOL) | Aktien | 11 709 | +0,06 | +0,04 | 4,9 % | −26,2 % | 0,19 | ❌ |
| **Relative Stärke** | **Aktien** | 7 148 | **+0,11** | **+0,08** | **8,8 %** | **−24,4 %** | **0,36** | ❌ knapp (PF 1,21 < 1,30) |
| Ausbruch (BOS + RVOL) | Krypto | 54 | +0,73 | +0,21 | 7,3 % | −4,4 % | 1,65 | ❌ Trefferquote zu niedrig |
| Relative Stärke | Krypto | 31 | +0,55 | −0,05 | 6,4 % | −2,7 % | 2,37 | ❌ zu wenige Trades |
| Trend-Pullback | Krypto | 80 | +0,11 | −0,26 | 0,3 % | −16,2 % | 0,02 | ❌ |

Vergleich im selben Zeitraum (2010–2026): SPY 13,7 % p.a. (MAR 0,41) · ACWI 9,9 % (0,29) ·
Universum gleichgewichtet 17,2 % (0,52).

**Fazit**
- **Relative Stärke ist die erste Idee mit einem statistisch gesicherten Vorteil**
  über 16 Jahre echter Out-of-Sample-Zeit (untere Grenze +0,08 R > 0). Risikobereinigt
  liegt sie zwischen Welt-Index (ACWI) und S&P 500, mit kleinerem Drawdown als beide.
  Die Hürde verfehlt sie knapp am Profit-Faktor. **Die Hürde wird bewusst nicht im
  Nachhinein gesenkt** – sonst wäre sie wertlos.
- Die Variantenwahl war bei Relative Stärke stabil (fast immer „Top 20 %, Trailing
  4 ATR“), bei Trend-Pullback sprang sie hin und her – ein Hinweis, dass dort kein
  echtes Muster dahintersteckt.
- Trailing-Stops (Gewinne laufen lassen) wurden bei Aktien meist gegenüber dem festen
  2-R-Ziel bevorzugt. Der Regime-Filter half dem Ausbruch durchgehend, dem Pullback kaum.
- **Ernüchternder Maßstab:** Alle 500 Werte einfach gleichgewichtet zu halten brachte
  17,2 % p.a. Ein großer Teil davon ist Survivorship Bias (die Liste enthält nur
  heutige Gewinner) und Landeswährungs-Effekte. Keine Strategie schlägt diesen Maßstab:
  Die Auswahl der Strategien war schlechter als „einfach alles halten“.
- Krypto: Ausbruch mit Trailing-Stop sieht stark aus (+0,73 R, Profit-Faktor 2,8),
  hat aber nur 54 Trades in 4 Jahren und eine Trefferquote von 43 %. Die strenge
  Krypto-Hürde (sichere Trefferquote ≥ 50 %) blockiert das – wie gewünscht.

---

## 2026-11-04 · Phase 2a · Weltweites Universum (502 Werte, 24 Märkte)

Bericht: [2026-11-04_phase2a_welt-universum.md](ergebnisse/2026-11-04_phase2a_welt-universum.md)
Neu: Liquiditätsfilter (≥ 5 Mio. USD Tagesumsatz), Portfolio-Simulation (10 Positionen, max. 4 je Land), Vergleich mit Kaufen & Halten.

| Strategie | Klasse | Trades | Erwartungswert Test | Portfolio p.a. Test | SPY / BTC p.a. Test | Urteil |
|---|---|---:|---:|---:|---:|---|
| Trend-Pullback | Aktien | 20 572 | +0,037 R | 3,5 % | 14,1 % | ❌ |
| Trend-Pullback | Krypto | 135 | −0,082 R | −1,6 % | 24,2 % | ❌ |
| Ausbruch (BOS + RVOL) | Aktien | 15 722 | +0,025 R | 5,5 % | 14,0 % | ❌ |
| Ausbruch (BOS + RVOL) | Krypto | 111 | +0,318 R | 3,2 % | 19,4 % | ❌ knapp |

**Fazit**
- Mit 30-mal mehr Daten schrumpft der Vorteil beider Strategien fast auf null.
  Das +0,16 R des Ausbruchs aus Phase 1 kam vor allem daher, dass das kleine
  Beispiel-Universum aus bekannten Gewinner-Aktien bestand.
- Als echtes Depot verlieren beide Strategien deutlich gegen einfaches Halten
  eines Index-ETFs. Der Drawdown ist kaum kleiner.
- Faustregel bestätigt: Erwartungswert × Risiko × Trades pro Jahr ≈ Rendite.
  0,03 R × 0,5 % × ~180 Trades ≈ 3 % p.a.
- Ausbruch bei Krypto bleibt der interessanteste Kandidat, fällt aber an den
  strengen Krypto-Hürden durch (Profit-Faktor 1,59 statt 1,6; Trefferquote zu unsicher).
- Länder-Unterschiede (z.B. Ausbruch besser in Asien/USA als in Europa) sind
  bei Einzelländern statistisch zu dünn, um darauf zu bauen.

**Konsequenz für Phase 2b:** Beide Ideen in ihrer Grundform haben keinen
nutzbaren Vorteil. Ansatzpunkte: Markt-Regime-Filter, Gewinne laufen lassen
(Trailing-Stop statt festes 2-R-Ziel), Ranking nach relativer Stärke als
Hauptkriterium. Alles nur auf Trainingsdaten entwickeln.

---

## 2026-11-03 · Phase 1 · Beispiel-Universum (29 Werte)

Bericht: [2026-11-03_phase1_beispiel-universum.md](ergebnisse/2026-11-03_phase1_beispiel-universum.md)

| Strategie | Klasse | Trades | Erwartungswert Test | Urteil |
|---|---|---:|---:|---|
| Trend-Pullback | Aktien | 1 301 | +0,08 R | ❌ |
| Trend-Pullback | Krypto | 73 | −0,04 R | ❌ |
| Ausbruch (BOS + RVOL) | Aktien | 805 | +0,10 R | ❌ knapp |
| Ausbruch (BOS + RVOL) | Krypto | 51 | +0,40 R | ❌ zu wenige Trades |

**Fazit:** Prüfstand funktioniert, Ergebnisse realistisch. Ausbruch bei Aktien
wirkte vielversprechend – in Phase 2a mit größerem Universum widerlegt.
