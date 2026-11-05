# Walk-Forward-Bericht

Testfenster à 2 Jahre ab 2010. Vor jedem Fenster wird – nur mit Trades, die bis dahin abgeschlossen waren – die beste Variante gewählt; sie handelt dann im Fenster. Alle Fenster zusammen ergeben ein echtes Out-of-Sample-Ergebnis.

Symbole: 502 geladen · Liquiditätsfilter: mind. 5 Mio. USD Tagesumsatz (Median 60 Tage)

> Ein Backtest zeigt die Vergangenheit, keine Garantie für die Zukunft. Keine Anlageberatung.

## Übersicht

| Strategie | Klasse | Urteil | Trades | Ø R | Depot p.a. | Drawdown | MAR | Vergleich p.a. / MAR |
|---|---|---|---:|---:|---:|---:|---:|---|
| Trend-Pullback | Aktien & ETFs | ❌ | 16611 | 0.059 R | 1.7 % | -34.9 % | 0.05 | SPY: 13.7 % / 0.41<br>ACWI: 9.9 % / 0.29<br>Universum gleichgewichtet: 17.2 % / 0.52 |
| Trend-Pullback | Krypto | ❌ | 80 | 0.113 R | 0.3 % | -16.2 % | 0.02 | BTC-USD: 10.7 % / 0.16<br>Universum gleichgewichtet: 0.8 % / 0.01 |
| Ausbruch mit Volumen (BOS + RVOL) | Aktien & ETFs | ❌ | 11709 | 0.058 R | 4.9 % | -26.2 % | 0.19 | SPY: 13.7 % / 0.41<br>ACWI: 9.9 % / 0.29<br>Universum gleichgewichtet: 17.2 % / 0.52 |
| Ausbruch mit Volumen (BOS + RVOL) | Krypto | ❌ | 54 | 0.729 R | 7.3 % | -4.4 % | 1.65 | BTC-USD: 37.7 % / 0.71<br>Universum gleichgewichtet: 29.2 % / 0.44 |
| Relative Stärke (Momentum-Trendfolge) | Aktien & ETFs | ❌ | 7148 | 0.112 R | 8.8 % | -24.4 % | 0.36 | SPY: 13.7 % / 0.41<br>ACWI: 9.9 % / 0.29<br>Universum gleichgewichtet: 17.2 % / 0.52 |
| Relative Stärke (Momentum-Trendfolge) | Krypto | ❌ | 31 | 0.550 R | 6.4 % | -2.7 % | 2.37 | BTC-USD: 74.9 % / 2.66<br>Universum gleichgewichtet: 84.9 % / 1.98 |

MAR = Rendite p.a. ÷ größter Rückgang: wie viel Rendite pro ertragenem Verlust. Damit lassen sich Strategien mit weniger Risiko fair mit dem Index vergleichen.

## Trend-Pullback

Kauft im intakten Aufwärtstrend (Kurs > SMA200, SMA50 > SMA200, ADX stark), nachdem ein Rücksetzer (RSI tief) wieder nach oben dreht.

Varianten: `Ziel 2 R` · `Ziel 2 R + Regime` · `Trailing 3 ATR` · `Trailing 3 ATR + Regime`

### Aktien & ETFs – ❌ NICHT BESTANDEN

- Profit-Faktor 1.10 < 1.30
- Portfolio-Drawdown im Test zu groß (-34.9 % < -25.0 %)

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | Ziel 2 R + Regime | 2397 | 0.138 R | 1609 | -0.109 R |
| 2012–2013 | Trailing 3 ATR + Regime | 4090 | 0.102 R | 2186 | +0.203 R |
| 2014–2015 | Trailing 3 ATR + Regime | 6142 | 0.112 R | 2063 | -0.041 R |
| 2016–2017 | Trailing 3 ATR | 9653 | 0.104 R | 1920 | +0.224 R |
| 2018–2019 | Trailing 3 ATR | 11525 | 0.101 R | 2096 | -0.027 R |
| 2020–2021 | Trailing 3 ATR | 13652 | 0.084 R | 2042 | +0.126 R |
| 2022–2023 | Trailing 3 ATR | 15673 | 0.093 R | 1873 | -0.079 R |
| 2024–2025 | Trailing 3 ATR + Regime | 14996 | 0.072 R | 1875 | +0.199 R |
| 2026–heute | Trailing 3 ATR | 19694 | 0.095 R | 947 | -0.067 R |

**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Out-of-Sample |
|---|---:|
| Abgeschlossene Trades | 16611 |
| Trades pro Jahr | 986.9 |
| Trefferquote | 35.0 % |
| … sicher mindestens | 34.4 % |
| Ø Gewinn-Trade | 1.92 R |
| Ø Verlust-Trade | -0.95 R |
| **Erwartungswert je Trade** | 0.059 R |
| … sicher mindestens | 0.033 R |
| Profit-Faktor | 1.10 |
| Ø Haltedauer (Tage) | 17.1 |

Ausstiege: Trailing-Stop (Gewinne gesichert) 7896×, Stop-Loss 5473×, Trailing-Stop (Gap, schlechter ausgeführt) 1624×, Stop-Loss (Gap, schlechter ausgeführt) 970×, Kursziel 366×, Zeit-Stop 228×, Kursziel (Gap, besser ausgeführt) 54×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Out-of-Sample (2010–2026) |
|---|---:|
| **Rendite p.a. Strategie** | **1.7 %** |
| Max. Drawdown Strategie | -34.9 % |
| MAR (Rendite ÷ Drawdown) Strategie | 0.05 |
| Rendite p.a. SPY (Kaufen & Halten) | 13.7 % |
| Max. Drawdown SPY | -33.7 % |
| MAR SPY | 0.41 |
| Rendite p.a. ACWI (Kaufen & Halten) | 9.9 % |
| Max. Drawdown ACWI | -33.5 % |
| MAR ACWI | 0.29 |
| Rendite p.a. Universum gleichgewichtet (Kaufen & Halten) | 17.2 % |
| Max. Drawdown Universum gleichgewichtet | -33.0 % |
| MAR Universum gleichgewichtet | 0.52 |
| Trades genommen / übersprungen | 2354 / 14324 |
| Ø gleichzeitige Positionen | 8.4 |
| Ø tatsächliches Risiko je Trade | 0.42 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | SPY |
|---|---:|---:|
| 2010 | -10.6 % | 12.8 % |
| 2011 | -19.6 % | 1.9 % |
| 2012 | -5.6 % | 16.0 % |
| 2013 | 18.7 % | 32.3 % |
| 2014 | 2.7 % | 13.5 % |
| 2015 | 3.6 % | 1.2 % |
| 2016 | -9.3 % | 12.0 % |
| 2017 | 34.3 % | 21.7 % |
| 2018 | -2.5 % | -4.6 % |
| 2019 | 16.8 % | 31.2 % |
| 2020 | 8.7 % | 18.3 % |
| 2021 | -0.0 % | 28.7 % |
| 2022 | -1.7 % | -18.2 % |
| 2023 | -5.5 % | 26.2 % |
| 2024 | 24.6 % | 24.9 % |
| 2025 | -12.6 % | 17.7 % |
| 2026 | 1.2 % | 8.3 % |

</details>

### Krypto – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze -0.26 R < 0.15 R)
- Profit-Faktor 1.19 < 1.60
- Trefferquote nicht sicher genug (20.1 % < 50.0 % untere Grenze)

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2012–2013 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2014–2015 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2016–2017 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2018–2019 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2020–2021 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2022–2023 | Trailing 3 ATR | 62 | 1.187 R | 15 | +0.419 R |
| 2024–2025 | Trailing 3 ATR | 80 | 0.973 R | 54 | +0.265 R |
| 2026–heute | Trailing 3 ATR | 134 | 0.687 R | 11 | -1.054 R |

**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Out-of-Sample |
|---|---:|
| Abgeschlossene Trades | 80 |
| Trades pro Jahr | 16.5 |
| Trefferquote | 27.5 % |
| … sicher mindestens | 20.1 % |
| Ø Gewinn-Trade | 2.56 R |
| Ø Verlust-Trade | -0.81 R |
| **Erwartungswert je Trade** | 0.113 R |
| … sicher mindestens | -0.255 R |
| Profit-Faktor | 1.19 |
| Ø Haltedauer (Tage) | 15.1 |

Ausstiege: Trailing-Stop (Gewinne gesichert) 51×, Stop-Loss 28×, Trailing-Stop (Gap, schlechter ausgeführt) 1×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Out-of-Sample (2022–2026) |
|---|---:|
| **Rendite p.a. Strategie** | **0.3 %** |
| Max. Drawdown Strategie | -16.2 % |
| MAR (Rendite ÷ Drawdown) Strategie | 0.02 |
| Rendite p.a. BTC-USD (Kaufen & Halten) | 10.7 % |
| Max. Drawdown BTC-USD | -66.7 % |
| MAR BTC-USD | 0.16 |
| Rendite p.a. Universum gleichgewichtet (Kaufen & Halten) | 0.8 % |
| Max. Drawdown Universum gleichgewichtet | -73.0 % |
| MAR Universum gleichgewichtet | 0.01 |
| Trades genommen / übersprungen | 82 / 1 |
| Ø gleichzeitige Positionen | 0.6 |
| Ø tatsächliches Risiko je Trade | 0.77 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | BTC-USD |
|---|---:|---:|
| 2022 | -3.2 % | -64.4 % |
| 2023 | 4.5 % | 155.4 % |
| 2024 | 19.3 % | 121.0 % |
| 2025 | -11.1 % | -6.3 % |
| 2026 | -5.7 % | -13.3 % |

</details>

<details><summary>Aufschlüsselung nach Ländern (alle Trades)</summary>

| Markt | Symbole | Trades | Trefferquote | Erwartungswert | Profit-Faktor |
|---|---:|---:|---:|---:|---:|
| US | 134 | 5185 | 35.7 % | +0.088 R | 1.15 |
| DE | 40 | 1261 | 33.6 % | -0.008 R | 0.99 |
| FR | 38 | 1243 | 34.5 % | +0.021 R | 1.04 |
| JP | 39 | 1159 | 34.7 % | +0.113 R | 1.18 |
| UK | 35 | 1129 | 32.6 % | -0.054 R | 0.91 |
| IN | 20 | 700 | 34.4 % | +0.068 R | 1.11 |
| CA | 20 | 681 | 37.3 % | +0.153 R | 1.26 |
| CH | 18 | 633 | 37.4 % | +0.126 R | 1.21 |
| AU | 19 | 595 | 35.1 % | +0.071 R | 1.10 |
| NL | 18 | 556 | 34.5 % | +0.077 R | 1.13 |
| HK | 19 | 484 | 35.3 % | -0.010 R | 0.99 |
| IT | 14 | 453 | 43.5 % | +0.210 R | 1.40 |
| SE | 11 | 380 | 36.3 % | +0.072 R | 1.12 |
| ES | 10 | 333 | 38.7 % | +0.076 R | 1.14 |
| BR | 10 | 311 | 23.2 % | -0.086 R | 0.89 |
| TW | 10 | 293 | 36.9 % | +0.125 R | 1.20 |
| DK | 8 | 255 | 30.2 % | -0.091 R | 0.86 |
| KR | 10 | 251 | 31.1 % | +0.080 R | 1.13 |
| NO | 6 | 206 | 32.0 % | +0.003 R | 1.01 |
| FI | 5 | 167 | 31.7 % | -0.262 R | 0.58 |
| SG | 4 | 140 | 46.4 % | +0.399 R | 1.77 |
| BE | 4 | 112 | 34.8 % | -0.146 R | 0.77 |
| MX | 3 | 84 | 22.6 % | -0.335 R | 0.49 |
| CRYPTO | 6 | 80 | 27.5 % | +0.112 R | 1.19 |

Einzelne Länder haben oft zu wenige Trades für sichere Aussagen – nur grobe Hinweise.

</details>

## Ausbruch mit Volumen (BOS + RVOL)

Kauft, wenn der Kurs im Aufwärtstrend ein bestätigtes Swing-Hoch mit deutlich erhöhtem Volumen überwindet.

Varianten: `Ziel 2 R` · `Ziel 2 R + Regime` · `Trailing 3 ATR` · `Trailing 3 ATR + Regime`

### Aktien & ETFs – ❌ NICHT BESTANDEN

- Profit-Faktor 1.10 < 1.30
- Portfolio-Drawdown im Test zu groß (-26.2 % < -25.0 %)

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | Ziel 2 R + Regime | 2366 | 0.180 R | 1136 | -0.082 R |
| 2012–2013 | Ziel 2 R + Regime | 3562 | 0.103 R | 1721 | +0.180 R |
| 2014–2015 | Ziel 2 R + Regime | 5212 | 0.128 R | 1475 | -0.054 R |
| 2016–2017 | Ziel 2 R + Regime | 6750 | 0.090 R | 1702 | +0.230 R |
| 2018–2019 | Ziel 2 R + Regime | 8391 | 0.109 R | 1346 | -0.133 R |
| 2020–2021 | Ziel 2 R + Regime | 9685 | 0.082 R | 1492 | +0.111 R |
| 2022–2023 | Trailing 3 ATR + Regime | 10809 | 0.092 R | 874 | -0.011 R |
| 2024–2025 | Ziel 2 R + Regime | 12140 | 0.075 R | 1418 | +0.149 R |
| 2026–heute | Trailing 3 ATR + Regime | 13036 | 0.089 R | 545 | -0.071 R |

**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Out-of-Sample |
|---|---:|
| Abgeschlossene Trades | 11709 |
| Trades pro Jahr | 695.6 |
| Trefferquote | 41.7 % |
| … sicher mindestens | 41.0 % |
| Ø Gewinn-Trade | 1.56 R |
| Ø Verlust-Trade | -1.02 R |
| **Erwartungswert je Trade** | 0.058 R |
| … sicher mindestens | 0.036 R |
| Profit-Faktor | 1.10 |
| Ø Haltedauer (Tage) | 15.7 |

Ausstiege: Stop-Loss 4918×, Kursziel 2434×, Zeit-Stop 2148×, Trailing-Stop (Gewinne gesichert) 824×, Stop-Loss (Gap, schlechter ausgeführt) 803×, Kursziel (Gap, besser ausgeführt) 410×, Trailing-Stop (Gap, schlechter ausgeführt) 172×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Out-of-Sample (2010–2026) |
|---|---:|
| **Rendite p.a. Strategie** | **4.9 %** |
| Max. Drawdown Strategie | -26.2 % |
| MAR (Rendite ÷ Drawdown) Strategie | 0.19 |
| Rendite p.a. SPY (Kaufen & Halten) | 13.7 % |
| Max. Drawdown SPY | -33.7 % |
| MAR SPY | 0.41 |
| Rendite p.a. ACWI (Kaufen & Halten) | 9.9 % |
| Max. Drawdown ACWI | -33.5 % |
| MAR ACWI | 0.29 |
| Rendite p.a. Universum gleichgewichtet (Kaufen & Halten) | 17.2 % |
| Max. Drawdown Universum gleichgewichtet | -33.0 % |
| MAR Universum gleichgewichtet | 0.52 |
| Trades genommen / übersprungen | 2270 / 9507 |
| Ø gleichzeitige Positionen | 7.8 |
| Ø tatsächliches Risiko je Trade | 0.47 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | SPY |
|---|---:|---:|
| 2010 | -1.8 % | 12.8 % |
| 2011 | -6.1 % | 1.9 % |
| 2012 | 6.5 % | 16.0 % |
| 2013 | 13.3 % | 32.3 % |
| 2014 | 5.7 % | 13.5 % |
| 2015 | 4.2 % | 1.2 % |
| 2016 | -1.1 % | 12.0 % |
| 2017 | 4.7 % | 21.7 % |
| 2018 | -17.0 % | -4.6 % |
| 2019 | 0.6 % | 31.2 % |
| 2020 | 20.1 % | 18.3 % |
| 2021 | 10.3 % | 28.7 % |
| 2022 | -6.9 % | -18.2 % |
| 2023 | 5.2 % | 26.2 % |
| 2024 | 13.7 % | 24.9 % |
| 2025 | 23.5 % | 17.7 % |
| 2026 | 15.9 % | 8.3 % |

</details>

### Krypto – ❌ NICHT BESTANDEN

- Trefferquote nicht sicher genug (32.1 % < 50.0 % untere Grenze)

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2012–2013 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2014–2015 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2016–2017 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2018–2019 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2020–2021 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2022–2023 | Trailing 3 ATR + Regime | 37 | 1.384 R | 19 | +1.040 R |
| 2024–2025 | Trailing 3 ATR + Regime | 56 | 1.267 R | 29 | +0.789 R |
| 2026–heute | Trailing 3 ATR + Regime | 85 | 1.104 R | 6 | -0.548 R |

**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Out-of-Sample |
|---|---:|
| Abgeschlossene Trades | 54 |
| Trades pro Jahr | 14.3 |
| Trefferquote | 42.6 % |
| … sicher mindestens | 32.1 % |
| Ø Gewinn-Trade | 2.68 R |
| Ø Verlust-Trade | -0.72 R |
| **Erwartungswert je Trade** | 0.729 R |
| … sicher mindestens | 0.213 R |
| Profit-Faktor | 2.76 |
| Ø Haltedauer (Tage) | 13.7 |

Ausstiege: Trailing-Stop (Gewinne gesichert) 41×, Stop-Loss 13×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Out-of-Sample (2023–2026) |
|---|---:|
| **Rendite p.a. Strategie** | **7.3 %** |
| Max. Drawdown Strategie | -4.4 % |
| MAR (Rendite ÷ Drawdown) Strategie | 1.65 |
| Rendite p.a. BTC-USD (Kaufen & Halten) | 37.7 % |
| Max. Drawdown BTC-USD | -53.1 % |
| MAR BTC-USD | 0.71 |
| Rendite p.a. Universum gleichgewichtet (Kaufen & Halten) | 29.2 % |
| Max. Drawdown Universum gleichgewichtet | -66.5 % |
| MAR Universum gleichgewichtet | 0.44 |
| Trades genommen / übersprungen | 52 / 2 |
| Ø gleichzeitige Positionen | 0.5 |
| Ø tatsächliches Risiko je Trade | 0.83 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | BTC-USD |
|---|---:|---:|
| 2023 | 15.7 % | 86.7 % |
| 2024 | 15.7 % | 121.0 % |
| 2025 | -0.6 % | -6.3 % |
| 2026 | -1.8 % | -13.3 % |

</details>

<details><summary>Aufschlüsselung nach Ländern (alle Trades)</summary>

| Markt | Symbole | Trades | Trefferquote | Erwartungswert | Profit-Faktor |
|---|---:|---:|---:|---:|---:|
| US | 134 | 2916 | 44.0 % | +0.110 R | 1.19 |
| JP | 39 | 1080 | 45.4 % | +0.165 R | 1.28 |
| FR | 38 | 854 | 39.2 % | -0.039 R | 0.94 |
| DE | 40 | 847 | 37.3 % | -0.060 R | 0.91 |
| UK | 35 | 691 | 38.5 % | -0.030 R | 0.95 |
| IN | 20 | 670 | 40.1 % | +0.024 R | 1.04 |
| HK | 19 | 552 | 41.8 % | +0.081 R | 1.14 |
| AU | 19 | 427 | 39.8 % | -0.009 R | 0.99 |
| TW | 10 | 401 | 42.9 % | +0.112 R | 1.19 |
| IT | 14 | 397 | 42.6 % | +0.085 R | 1.15 |
| CA | 20 | 396 | 43.7 % | +0.123 R | 1.21 |
| CH | 18 | 377 | 40.8 % | +0.000 R | 1.00 |
| NL | 18 | 342 | 36.3 % | -0.078 R | 0.88 |
| KR | 10 | 337 | 38.0 % | +0.069 R | 1.12 |
| SE | 11 | 247 | 41.3 % | +0.015 R | 1.02 |
| ES | 10 | 236 | 37.7 % | -0.078 R | 0.88 |
| BR | 10 | 213 | 48.4 % | +0.203 R | 1.36 |
| DK | 8 | 179 | 42.5 % | +0.084 R | 1.15 |
| NO | 6 | 156 | 41.0 % | +0.061 R | 1.11 |
| SG | 4 | 144 | 49.3 % | +0.254 R | 1.50 |
| FI | 5 | 109 | 44.0 % | +0.105 R | 1.18 |
| BE | 4 | 80 | 40.0 % | +0.085 R | 1.14 |
| MX | 3 | 58 | 37.9 % | -0.095 R | 0.85 |
| CRYPTO | 6 | 54 | 42.6 % | +0.729 R | 2.76 |

Einzelne Länder haben oft zu wenige Trades für sichere Aussagen – nur grobe Hinweise.

</details>

## Relative Stärke (Momentum-Trendfolge)

Kauft die stärksten Werte des Universums (6-Monats-Performance) im sauberen Aufwärtstrend nahe am 52-Wochen-Hoch, sobald sie ein neues 20-Tage-Hoch markieren – nur bei positivem Gesamtmarkt. Gewinne laufen mit Trailing-Stop.

Varianten: `Top 20 %, Trailing 3 ATR` · `Top 20 %, Trailing 4 ATR` · `Top 10 %, Trailing 3 ATR` · `Top 10 %, Trailing 4 ATR`

### Aktien & ETFs – ❌ NICHT BESTANDEN

- Profit-Faktor 1.21 < 1.30

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | Top 10 %, Trailing 4 ATR | 596 | 0.228 R | 435 | -0.126 R |
| 2012–2013 | Top 10 %, Trailing 4 ATR | 1044 | 0.072 R | 556 | +0.160 R |
| 2014–2015 | Top 20 %, Trailing 4 ATR | 2911 | 0.068 R | 1007 | +0.005 R |
| 2016–2017 | Top 20 %, Trailing 4 ATR | 3946 | 0.074 R | 1041 | +0.365 R |
| 2018–2019 | Top 10 %, Trailing 4 ATR | 2746 | 0.119 R | 625 | -0.006 R |
| 2020–2021 | Top 20 %, Trailing 4 ATR | 5998 | 0.088 R | 1053 | +0.199 R |
| 2022–2023 | Top 20 %, Trailing 4 ATR | 7074 | 0.127 R | 815 | -0.109 R |
| 2024–2025 | Top 20 %, Trailing 4 ATR | 7874 | 0.084 R | 1183 | +0.261 R |
| 2026–heute | Top 20 %, Trailing 4 ATR | 9065 | 0.104 R | 433 | -0.104 R |

**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Out-of-Sample |
|---|---:|
| Abgeschlossene Trades | 7148 |
| Trades pro Jahr | 424.7 |
| Trefferquote | 36.3 % |
| … sicher mindestens | 35.4 % |
| Ø Gewinn-Trade | 1.77 R |
| Ø Verlust-Trade | -0.83 R |
| **Erwartungswert je Trade** | 0.112 R |
| … sicher mindestens | 0.076 R |
| Profit-Faktor | 1.21 |
| Ø Haltedauer (Tage) | 27.8 |

Ausstiege: Trailing-Stop (Gewinne gesichert) 4137×, Stop-Loss 1820×, Trailing-Stop (Gap, schlechter ausgeführt) 863×, Stop-Loss (Gap, schlechter ausgeführt) 328×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Out-of-Sample (2010–2026) |
|---|---:|
| **Rendite p.a. Strategie** | **8.8 %** |
| Max. Drawdown Strategie | -24.4 % |
| MAR (Rendite ÷ Drawdown) Strategie | 0.36 |
| Rendite p.a. SPY (Kaufen & Halten) | 13.7 % |
| Max. Drawdown SPY | -33.7 % |
| MAR SPY | 0.41 |
| Rendite p.a. ACWI (Kaufen & Halten) | 9.9 % |
| Max. Drawdown ACWI | -33.5 % |
| MAR ACWI | 0.29 |
| Rendite p.a. Universum gleichgewichtet (Kaufen & Halten) | 17.2 % |
| Max. Drawdown Universum gleichgewichtet | -33.0 % |
| MAR Universum gleichgewichtet | 0.52 |
| Trades genommen / übersprungen | 1240 / 5966 |
| Ø gleichzeitige Positionen | 8.1 |
| Ø tatsächliches Risiko je Trade | 0.61 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | SPY |
|---|---:|---:|
| 2010 | -19.5 % | 12.8 % |
| 2011 | 9.1 % | 1.9 % |
| 2012 | 1.0 % | 16.0 % |
| 2013 | 26.9 % | 32.3 % |
| 2014 | 1.9 % | 13.5 % |
| 2015 | 4.0 % | 1.2 % |
| 2016 | 11.7 % | 12.0 % |
| 2017 | 22.8 % | 21.7 % |
| 2018 | 4.6 % | -4.6 % |
| 2019 | -4.1 % | 31.2 % |
| 2020 | 21.6 % | 18.3 % |
| 2021 | 32.6 % | 28.7 % |
| 2022 | -11.2 % | -18.2 % |
| 2023 | 3.6 % | 26.2 % |
| 2024 | 19.9 % | 24.9 % |
| 2025 | 5.3 % | 17.7 % |
| 2026 | 34.7 % | 8.3 % |

</details>

### Krypto – ❌ NICHT BESTANDEN

- zu wenige Trades (31 < 40)
- Vorteil statistisch nicht gesichert (untere Grenze -0.04 R < 0.15 R)
- Trefferquote nicht sicher genug (43.4 % < 50.0 % untere Grenze)

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2012–2013 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2014–2015 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2016–2017 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2018–2019 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2020–2021 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2022–2023 | Top 20 %, Trailing 3 ATR | 32 | 1.020 R | 11 | +0.314 R |
| 2024–2025 | Top 20 %, Trailing 4 ATR | 31 | 1.028 R | 20 | +0.680 R |
| 2026–heute | Top 10 %, Trailing 4 ATR | 31 | 1.631 R | 0 | – |

**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Out-of-Sample |
|---|---:|
| Abgeschlossene Trades | 31 |
| Trades pro Jahr | 12.1 |
| Trefferquote | 58.1 % |
| … sicher mindestens | 43.4 % |
| Ø Gewinn-Trade | 1.60 R |
| Ø Verlust-Trade | -0.91 R |
| **Erwartungswert je Trade** | 0.550 R |
| … sicher mindestens | -0.045 R |
| Profit-Faktor | 2.44 |
| Ø Haltedauer (Tage) | 18.3 |

Ausstiege: Trailing-Stop (Gewinne gesichert) 22×, Stop-Loss 9×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Out-of-Sample (2023–2025) |
|---|---:|
| **Rendite p.a. Strategie** | **6.4 %** |
| Max. Drawdown Strategie | -2.7 % |
| MAR (Rendite ÷ Drawdown) Strategie | 2.37 |
| Rendite p.a. BTC-USD (Kaufen & Halten) | 74.9 % |
| Max. Drawdown BTC-USD | -28.1 % |
| MAR BTC-USD | 2.66 |
| Rendite p.a. Universum gleichgewichtet (Kaufen & Halten) | 84.9 % |
| Max. Drawdown Universum gleichgewichtet | -42.9 % |
| MAR Universum gleichgewichtet | 1.98 |
| Trades genommen / übersprungen | 31 / 0 |
| Ø gleichzeitige Positionen | 0.6 |
| Ø tatsächliches Risiko je Trade | 0.92 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | BTC-USD |
|---|---:|---:|
| 2023 | 3.5 % | 56.7 % |
| 2024 | 15.0 % | 121.0 % |
| 2025 | -1.5 % | 21.2 % |

</details>

<details><summary>Aufschlüsselung nach Ländern (alle Trades)</summary>

| Markt | Symbole | Trades | Trefferquote | Erwartungswert | Profit-Faktor |
|---|---:|---:|---:|---:|---:|
| US | 133 | 2028 | 38.4 % | +0.161 R | 1.31 |
| JP | 39 | 755 | 35.4 % | +0.095 R | 1.18 |
| DE | 40 | 511 | 31.5 % | -0.044 R | 0.92 |
| FR | 38 | 489 | 29.7 % | -0.082 R | 0.86 |
| UK | 34 | 350 | 31.1 % | +0.045 R | 1.08 |
| IN | 20 | 334 | 36.2 % | +0.087 R | 1.16 |
| NL | 18 | 268 | 38.1 % | +0.036 R | 1.07 |
| IT | 14 | 254 | 38.6 % | +0.098 R | 1.20 |
| HK | 19 | 249 | 36.9 % | +0.242 R | 1.45 |
| CA | 20 | 236 | 34.7 % | +0.205 R | 1.37 |
| AU | 19 | 206 | 39.3 % | +0.302 R | 1.57 |
| CH | 18 | 203 | 34.0 % | -0.068 R | 0.87 |
| KR | 10 | 178 | 43.3 % | +0.486 R | 2.00 |
| ES | 10 | 175 | 35.4 % | -0.051 R | 0.91 |
| TW | 10 | 161 | 42.9 % | +0.346 R | 1.72 |
| SE | 11 | 150 | 35.3 % | -0.118 R | 0.79 |
| DK | 8 | 145 | 39.3 % | +0.214 R | 1.40 |
| BR | 10 | 135 | 43.0 % | +0.482 R | 1.94 |
| NO | 6 | 93 | 34.4 % | -0.087 R | 0.84 |
| FI | 5 | 77 | 36.4 % | +0.092 R | 1.18 |
| BE | 4 | 72 | 40.3 % | +0.282 R | 1.61 |
| MX | 3 | 45 | 31.1 % | -0.156 R | 0.72 |
| SG | 4 | 34 | 38.2 % | +0.088 R | 1.17 |
| CRYPTO | 6 | 31 | 58.1 % | +0.550 R | 2.44 |

Einzelne Länder haben oft zu wenige Trades für sichere Aussagen – nur grobe Hinweise.

</details>
