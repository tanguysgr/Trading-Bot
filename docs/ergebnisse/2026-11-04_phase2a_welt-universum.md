# Backtest-Bericht

Stichtag Training/Test: **2018-01-01** – Regeln wurden nur mit Daten davor entwickelt; entscheidend ist die Spalte **Test**.

Symbole: 502 geladen · Liquiditätsfilter: mind. 5 Mio. USD Tagesumsatz (Median 60 Tage)

> Ein Backtest zeigt die Vergangenheit, keine Garantie für die Zukunft. Keine Anlageberatung.

## Trend-Pullback

Kauft im intakten Aufwärtstrend (Kurs > SMA200, SMA50 > SMA200, ADX stark), nachdem ein Rücksetzer (RSI tief) wieder nach oben dreht.

Kursziel 2.0 R · Zeit-Stop 40 Tage · Parameter: `{'adx_min': 20.0, 'rsi_dip': 40.0, 'lookback': 5, 'min_stop_atr': 1.0}`

### Aktien & ETFs – ❌ NICHT BESTANDEN

- Profit-Faktor 1.06 < 1.30
- Portfolio-Drawdown im Test zu groß (-30.6 % < -25.0 %)

**Trade-Statistik** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Gesamt | Training | **Test** |
|---|---:|---:|---:|
| Abgeschlossene Trades | 20572 | 11519 | **9053** |
| Trades pro Jahr | 976.7 | 933.9 | **1 025.0** |
| Trefferquote | 41.5 % | 41.8 % | **41.2 %** |
| … sicher mindestens | 40.9 % | 41.0 % | **40.3 %** |
| Ø Gewinn-Trade | 1.66 R | 1.64 R | **1.68 R** |
| Ø Verlust-Trade | -1.09 R | -1.08 R | **-1.11 R** |
| **Erwartungswert je Trade** | 0.048 R | 0.057 R | **0.037 R** |
| … sicher mindestens | 0.032 R | 0.035 R | **0.011 R** |
| Profit-Faktor | 1.08 | 1.09 | **1.06** |
| Ø Haltedauer (Tage) | 15.7 | 16.2 | **15.2** |

Ausstiege: Stop-Loss 9510×, Kursziel 5370×, Zeit-Stop 2935×, Stop-Loss (Gap, schlechter ausgeführt) 1808×, Kursziel (Gap, besser ausgeführt) 949×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Gesamt (2005–2026) | **Test** (2018–2026) |
|---|---:|---:|
| **Rendite p.a. Strategie** | **2.1 %** | **3.5 %** |
| Max. Drawdown Strategie | -45.9 % | -30.6 % |
| Rendite p.a. SPY (Kaufen & Halten) | 11.2 % | 14.1 % |
| Max. Drawdown SPY | -55.2 % | -33.7 % |
| Rendite p.a. ACWI (Kaufen & Halten) | 8.3 % | 10.9 % |
| Max. Drawdown ACWI | -56.3 % | -33.5 % |
| Trades genommen / übersprungen | 3333 / 17284 | 1484 / 7614 |
| Ø gleichzeitige Positionen | 8.7 | 8.8 |
| Ø tatsächliches Risiko je Trade | 0.46 % | 0.44 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | SPY |
|---|---:|---:|
| 2005 | 13.6 % | 5.5 % |
| 2006 | 11.0 % | 15.8 % |
| 2007 | 12.0 % | 5.2 % |
| 2008 | -41.2 % | -36.8 % |
| 2009 | 30.9 % | 26.4 % |
| 2010 | -0.7 % | 15.1 % |
| 2011 | -9.4 % | 1.9 % |
| 2012 | 3.4 % | 16.0 % |
| 2013 | 6.3 % | 32.3 % |
| 2014 | -7.5 % | 13.5 % |
| 2015 | 1.6 % | 1.2 % |
| 2016 | -3.4 % | 12.0 % |
| 2017 | 14.6 % | 21.7 % |
| 2018 | -15.0 % | -4.6 % |
| 2019 | 16.8 % | 31.2 % |
| 2020 | 3.1 % | 18.3 % |
| 2021 | -3.1 % | 28.7 % |
| 2022 | -16.4 % | -18.2 % |
| 2023 | 13.6 % | 26.2 % |
| 2024 | 23.0 % | 24.9 % |
| 2025 | 15.2 % | 17.7 % |
| 2026 | 3.2 % | 11.5 % |

</details>

### Krypto – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze -0.27 R < 0.15 R)
- Profit-Faktor 0.87 < 1.60
- Trefferquote nicht sicher genug (26.9 % < 50.0 % untere Grenze)
- Portfolio im Test ohne Gewinn

**Trade-Statistik** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Gesamt | Training | **Test** |
|---|---:|---:|---:|
| Abgeschlossene Trades | 135 | 6 | **129** |
| Trades pro Jahr | 12.0 | 2.7 | **14.7** |
| Trefferquote | 34.8 % | 66.7 % | **33.3 %** |
| … sicher mindestens | 28.4 % | 34.7 % | **26.9 %** |
| Ø Gewinn-Trade | 1.63 R | 1.07 R | **1.68 R** |
| Ø Verlust-Trade | -0.97 R | -1.05 R | **-0.96 R** |
| **Erwartungswert je Trade** | -0.062 R | 0.366 R | **-0.082 R** |
| … sicher mindestens | -0.244 R | -0.393 R | **-0.271 R** |
| Profit-Faktor | 0.90 | 2.05 | **0.87** |
| Ø Haltedauer (Tage) | 16.8 | 26.7 | **16.4** |

Ausstiege: Stop-Loss 79×, Kursziel 36×, Zeit-Stop 20×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Gesamt (2015–2026) | **Test** (2018–2026) |
|---|---:|---:|
| **Rendite p.a. Strategie** | **-1.0 %** | **-1.6 %** |
| Max. Drawdown Strategie | -18.1 % | -18.1 % |
| Rendite p.a. BTC-USD (Kaufen & Halten) | 65.8 % | 24.2 % |
| Max. Drawdown BTC-USD | -83.4 % | -76.6 % |
| Trades genommen / übersprungen | 136 / 2 | 130 / 2 |
| Ø gleichzeitige Positionen | 0.5 | 0.6 |
| Ø tatsächliches Risiko je Trade | 0.83 % | 0.82 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | BTC-USD |
|---|---:|---:|
| 2015 | -0.4 % | 61.6 % |
| 2016 | 0.8 % | 123.8 % |
| 2017 | 2.4 % | 1 368.9 % |
| 2018 | -1.9 % | -73.6 % |
| 2019 | -1.0 % | 92.2 % |
| 2020 | -1.8 % | 303.2 % |
| 2021 | 6.0 % | 59.7 % |
| 2022 | -7.4 % | -64.3 % |
| 2023 | 2.6 % | 155.4 % |
| 2024 | 4.1 % | 121.0 % |
| 2025 | -10.4 % | -6.3 % |
| 2026 | -3.5 % | -11.2 % |

</details>

<details><summary>Aufschlüsselung nach Ländern (alle Trades)</summary>

| Markt | Symbole | Trades | Trefferquote | Erwartungswert | Profit-Faktor |
|---|---:|---:|---:|---:|---:|
| US | 134 | 6437 | 41.9 % | +0.060 R | 1.09 |
| FR | 38 | 1619 | 42.3 % | +0.089 R | 1.14 |
| DE | 40 | 1550 | 40.3 % | -0.004 R | 0.99 |
| JP | 39 | 1451 | 40.7 % | -0.007 R | 0.99 |
| UK | 35 | 1418 | 40.4 % | +0.016 R | 1.02 |
| IN | 20 | 835 | 40.4 % | +0.036 R | 1.06 |
| CA | 20 | 827 | 42.0 % | +0.067 R | 1.11 |
| CH | 18 | 759 | 43.3 % | +0.079 R | 1.13 |
| AU | 19 | 728 | 39.8 % | -0.003 R | 0.99 |
| NL | 18 | 650 | 40.9 % | +0.071 R | 1.11 |
| HK | 19 | 616 | 40.9 % | +0.041 R | 1.06 |
| IT | 14 | 560 | 48.6 % | +0.262 R | 1.48 |
| SE | 11 | 479 | 42.0 % | +0.074 R | 1.12 |
| ES | 10 | 403 | 45.2 % | +0.197 R | 1.34 |
| BR | 10 | 355 | 33.5 % | -0.209 R | 0.71 |
| KR | 10 | 345 | 39.4 % | +0.041 R | 1.07 |
| TW | 10 | 337 | 45.4 % | +0.105 R | 1.17 |
| DK | 8 | 306 | 39.5 % | -0.021 R | 0.97 |
| NO | 6 | 273 | 34.1 % | -0.125 R | 0.83 |
| FI | 5 | 216 | 39.4 % | -0.013 R | 0.98 |
| SG | 4 | 156 | 52.6 % | +0.352 R | 1.70 |
| BE | 4 | 136 | 43.4 % | +0.089 R | 1.15 |
| CRYPTO | 6 | 135 | 34.8 % | -0.062 R | 0.90 |
| MX | 3 | 116 | 35.3 % | -0.116 R | 0.82 |

Einzelne Länder haben oft zu wenige Trades für sichere Aussagen – nur grobe Hinweise.

</details>

## Ausbruch mit Volumen (BOS + RVOL)

Kauft, wenn der Kurs im Aufwärtstrend ein bestätigtes Swing-Hoch mit deutlich erhöhtem Volumen überwindet.

Kursziel 2.0 R · Zeit-Stop 30 Tage · Parameter: `{'swing_strength': 3, 'rvol_min': 1.5, 'max_ext_atr': 1.5, 'stop_atr': 2.0}`

### Aktien & ETFs – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze -0.00 R < 0.00 R)
- Profit-Faktor 1.04 < 1.30
- Portfolio-Drawdown im Test zu groß (-25.8 % < -25.0 %)

**Trade-Statistik** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Gesamt | Training | **Test** |
|---|---:|---:|---:|
| Abgeschlossene Trades | 15722 | 9319 | **6403** |
| Trades pro Jahr | 746.4 | 756.9 | **725.0** |
| Trefferquote | 43.0 % | 44.2 % | **41.2 %** |
| … sicher mindestens | 42.4 % | 43.4 % | **40.2 %** |
| Ø Gewinn-Trade | 1.53 R | 1.52 R | **1.55 R** |
| Ø Verlust-Trade | -1.04 R | -1.04 R | **-1.05 R** |
| **Erwartungswert je Trade** | 0.064 R | 0.091 R | **0.025 R** |
| … sicher mindestens | 0.046 R | 0.066 R | **-0.004 R** |
| Profit-Faktor | 1.11 | 1.16 | **1.04** |
| Ø Haltedauer (Tage) | 15.8 | 16.3 | **15.1** |

Ausstiege: Stop-Loss 6947×, Kursziel 3668×, Zeit-Stop 3337×, Stop-Loss (Gap, schlechter ausgeführt) 1165×, Kursziel (Gap, besser ausgeführt) 605×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Gesamt (2005–2026) | **Test** (2018–2026) |
|---|---:|---:|
| **Rendite p.a. Strategie** | **3.9 %** | **5.5 %** |
| Max. Drawdown Strategie | -47.3 % | -25.8 % |
| Rendite p.a. SPY (Kaufen & Halten) | 11.2 % | 14.0 % |
| Max. Drawdown SPY | -55.2 % | -33.7 % |
| Rendite p.a. ACWI (Kaufen & Halten) | 8.3 % | 10.9 % |
| Max. Drawdown ACWI | -56.3 % | -33.5 % |
| Trades genommen / übersprungen | 3182 / 12579 | 1388 / 5054 |
| Ø gleichzeitige Positionen | 8.8 | 8.8 |
| Ø tatsächliches Risiko je Trade | 0.51 % | 0.50 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | SPY |
|---|---:|---:|
| 2005 | 4.6 % | 5.5 % |
| 2006 | 3.7 % | 15.8 % |
| 2007 | 15.7 % | 5.2 % |
| 2008 | -37.5 % | -36.8 % |
| 2009 | 21.2 % | 26.4 % |
| 2010 | 20.8 % | 15.1 % |
| 2011 | -12.3 % | 1.9 % |
| 2012 | 8.9 % | 16.0 % |
| 2013 | 18.9 % | 32.3 % |
| 2014 | 7.2 % | 13.5 % |
| 2015 | 0.9 % | 1.2 % |
| 2016 | -7.5 % | 12.0 % |
| 2017 | 4.7 % | 21.7 % |
| 2018 | -21.1 % | -4.6 % |
| 2019 | 5.4 % | 31.2 % |
| 2020 | 20.8 % | 18.3 % |
| 2021 | 11.5 % | 28.7 % |
| 2022 | -14.4 % | -18.2 % |
| 2023 | 13.1 % | 26.2 % |
| 2024 | 6.0 % | 24.9 % |
| 2025 | 18.2 % | 17.7 % |
| 2026 | 21.3 % | 11.5 % |

</details>

### Krypto – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze 0.09 R < 0.15 R)
- Profit-Faktor 1.59 < 1.60
- Trefferquote nicht sicher genug (37.4 % < 50.0 % untere Grenze)

**Trade-Statistik** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Gesamt | Training | **Test** |
|---|---:|---:|---:|
| Abgeschlossene Trades | 111 | 7 | **104** |
| Trades pro Jahr | 9.8 | 4.6 | **11.9** |
| Trefferquote | 47.7 % | 85.7 % | **45.2 %** |
| … sicher mindestens | 40.1 % | 54.8 % | **37.4 %** |
| Ø Gewinn-Trade | 1.85 R | 1.57 R | **1.89 R** |
| Ø Verlust-Trade | -0.98 R | -1.05 R | **-0.98 R** |
| **Erwartungswert je Trade** | 0.373 R | 1.192 R | **0.318 R** |
| … sicher mindestens | 0.144 R | 0.493 R | **0.086 R** |
| Profit-Faktor | 1.73 | 8.95 | **1.59** |
| Ø Haltedauer (Tage) | 10.8 | 18.1 | **10.3** |

Ausstiege: Stop-Loss 54×, Kursziel 48×, Zeit-Stop 9×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Gesamt (2015–2026) | **Test** (2018–2026) |
|---|---:|---:|
| **Rendite p.a. Strategie** | **2.9 %** | **3.2 %** |
| Max. Drawdown Strategie | -7.6 % | -7.6 % |
| Rendite p.a. BTC-USD (Kaufen & Halten) | 66.5 % | 19.4 % |
| Max. Drawdown BTC-USD | -83.4 % | -81.5 % |
| Trades genommen / übersprungen | 109 / 2 | 102 / 2 |
| Ø gleichzeitige Positionen | 0.3 | 0.3 |
| Ø tatsächliches Risiko je Trade | 0.86 % | 0.88 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | BTC-USD |
|---|---:|---:|
| 2015 | 3.0 % | 63.7 % |
| 2016 | 0.7 % | 123.8 % |
| 2017 | 0.9 % | 1 368.9 % |
| 2018 | -2.0 % | -73.6 % |
| 2019 | 6.0 % | 92.2 % |
| 2020 | -6.3 % | 303.2 % |
| 2021 | 11.7 % | 59.7 % |
| 2022 | -1.9 % | -64.3 % |
| 2023 | 14.0 % | 155.4 % |
| 2024 | 14.7 % | 121.0 % |
| 2025 | -4.1 % | -6.3 % |
| 2026 | -1.2 % | -5.0 % |

</details>

<details><summary>Aufschlüsselung nach Ländern (alle Trades)</summary>

| Markt | Symbole | Trades | Trefferquote | Erwartungswert | Profit-Faktor |
|---|---:|---:|---:|---:|---:|
| US | 134 | 3994 | 44.4 % | +0.092 R | 1.16 |
| JP | 39 | 1406 | 44.7 % | +0.110 R | 1.18 |
| DE | 40 | 1162 | 39.7 % | -0.032 R | 0.95 |
| FR | 38 | 1150 | 41.0 % | -0.015 R | 0.98 |
| UK | 35 | 1010 | 39.1 % | -0.049 R | 0.92 |
| IN | 20 | 877 | 41.5 % | +0.028 R | 1.05 |
| HK | 19 | 695 | 45.5 % | +0.154 R | 1.27 |
| AU | 19 | 543 | 40.5 % | -0.032 R | 0.95 |
| CA | 20 | 526 | 41.8 % | +0.047 R | 1.08 |
| IT | 14 | 518 | 45.2 % | +0.134 R | 1.24 |
| CH | 18 | 510 | 45.5 % | +0.115 R | 1.20 |
| TW | 10 | 501 | 46.5 % | +0.174 R | 1.31 |
| KR | 10 | 463 | 41.9 % | +0.115 R | 1.20 |
| NL | 18 | 441 | 39.5 % | -0.019 R | 0.97 |
| SE | 11 | 344 | 44.8 % | +0.090 R | 1.16 |
| ES | 10 | 320 | 41.2 % | +0.035 R | 1.06 |
| BR | 10 | 267 | 44.9 % | +0.143 R | 1.24 |
| DK | 8 | 249 | 43.0 % | +0.099 R | 1.17 |
| NO | 6 | 206 | 42.7 % | +0.104 R | 1.18 |
| SG | 4 | 172 | 47.1 % | +0.161 R | 1.30 |
| FI | 5 | 165 | 50.9 % | +0.272 R | 1.54 |
| CRYPTO | 6 | 111 | 47.7 % | +0.373 R | 1.73 |
| BE | 4 | 104 | 38.5 % | +0.010 R | 1.02 |
| MX | 3 | 99 | 38.4 % | -0.121 R | 0.82 |

Einzelne Länder haben oft zu wenige Trades für sichere Aussagen – nur grobe Hinweise.

</details>
