# Walk-Forward-Bericht

Testfenster à 2 Jahre ab 2010. Vor jedem Fenster wird – nur mit Trades, die bis dahin abgeschlossen waren – die beste Variante gewählt; sie handelt dann im Fenster. Alle Fenster zusammen ergeben ein echtes Out-of-Sample-Ergebnis.

Symbole: 502 geladen · Liquiditätsfilter: mind. 5 Mio. USD Tagesumsatz (Median 60 Tage)

> Ein Backtest zeigt die Vergangenheit, keine Garantie für die Zukunft. Keine Anlageberatung.

## Übersicht

| Strategie | Klasse | Urteil | Trades | Ø R | Depot p.a. | Drawdown | MAR | Vergleich p.a. / MAR |
|---|---|---|---:|---:|---:|---:|---:|---|
| Confluence Long (Trend + Zone + Bestätigung) | Aktien & ETFs | ❌ | 23755 | 0.026 R | 5.7 % | -33.2 % | 0.17 | SPY: 13.7 % / 0.41<br>ACWI: 9.9 % / 0.30<br>Universum gleichgewichtet: 17.2 % / 0.52 |
| Confluence Long (Trend + Zone + Bestätigung) | Krypto | ❌ | 183 | 0.699 R | 11.2 % | -12.3 % | 0.91 | BTC-USD: 34.0 % / 0.44<br>Universum gleichgewichtet: 45.5 % / 0.56 |
| Confluence Short (gespiegelt) | Aktien & ETFs | ❌ | 0 | 0.000 R | – | – | – | – |
| Confluence Short (gespiegelt) | Krypto | ❌ | 98 | -0.158 R | -1.8 % | -16.2 % | -0.11 | BTC-USD: 40.3 % / 0.53<br>Universum gleichgewichtet: 75.7 % / 0.94 |

MAR = Rendite p.a. ÷ größter Rückgang: wie viel Rendite pro ertragenem Verlust. Damit lassen sich Strategien mit weniger Risiko fair mit dem Index vergleichen.

## Confluence Long (Trend + Zone + Bestätigung)

Kauft im Aufwärtstrend (SMA50 > SMA200, Struktur aufwärts), wenn ein Rücksetzer eine Unterstützung berührt (SMA, Fibonacci 0,5–0,618 oder Swing-Zone) und eine grüne Kerze darüber schließt. Stop hinter der Zone, Ziel 1,25 R.

Varianten: `V1 Basis` · `V2 Cluster (≥ 2 Zonentypen)` · `V3 + interner Bruch` · `V4 Trailing 3 ATR`

### Aktien & ETFs – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze -0.00 R < 0.00 R)
- Profit-Faktor 1.05 < 1.30
- Portfolio-Drawdown im Test zu groß (-33.2 % < -25.0 %)

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | V1 Basis | 5048 | 0.085 R | 2700 | -0.100 R |
| 2012–2013 | V1 Basis | 7866 | 0.019 R | 3823 | -0.009 R |
| 2014–2015 | V3 + interner Bruch | 5231 | 0.045 R | 1553 | -0.098 R |
| 2016–2017 | V4 Trailing 3 ATR | 13087 | 0.028 R | 3046 | +0.212 R |
| 2018–2019 | V4 Trailing 3 ATR | 16025 | 0.040 R | 2723 | -0.058 R |
| 2020–2021 | V4 Trailing 3 ATR | 18717 | 0.034 R | 3207 | +0.090 R |
| 2022–2023 | V4 Trailing 3 ATR | 21995 | 0.048 R | 2230 | -0.104 R |
| 2024–2025 | V4 Trailing 3 ATR | 24229 | 0.029 R | 3220 | +0.193 R |
| 2026–heute | V4 Trailing 3 ATR | 27436 | 0.046 R | 1253 | -0.080 R |

**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Out-of-Sample |
|---|---:|
| Abgeschlossene Trades | 23755 |
| Trades pro Jahr | 1 411.0 |
| Trefferquote | 40.5 % |
| … sicher mindestens | 39.9 % |
| Ø Gewinn-Trade | 1.40 R |
| Ø Verlust-Trade | -0.91 R |
| **Erwartungswert je Trade** | 0.026 R |
| … sicher mindestens | -0.004 R |
| Profit-Faktor | 1.05 |
| Ø Haltedauer (Tage) | 16.4 |

Ausstiege: Trailing-Stop (Gewinne gesichert) 9914×, Stop-Loss 6407×, Kursziel 2846×, Trailing-Stop (Gap, schlechter ausgeführt) 2036×, Stop-Loss (Gap, schlechter ausgeführt) 1102×, Zeit-Stop 1044×, Kursziel (Gap, besser ausgeführt) 406×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Out-of-Sample (2010–2026) |
|---|---:|
| **Rendite p.a. Strategie** | **5.7 %** |
| Max. Drawdown Strategie | -33.2 % |
| MAR (Rendite ÷ Drawdown) Strategie | 0.17 |
| Rendite p.a. SPY (Kaufen & Halten) | 13.7 % |
| Max. Drawdown SPY | -33.7 % |
| MAR SPY | 0.41 |
| Rendite p.a. ACWI (Kaufen & Halten) | 9.9 % |
| Max. Drawdown ACWI | -33.5 % |
| MAR ACWI | 0.30 |
| Rendite p.a. Universum gleichgewichtet (Kaufen & Halten) | 17.2 % |
| Max. Drawdown Universum gleichgewichtet | -33.0 % |
| MAR Universum gleichgewichtet | 0.52 |
| Trades genommen / übersprungen | 2664 / 21158 |
| Ø gleichzeitige Positionen | 9.1 |
| Ø tatsächliches Risiko je Trade | 0.52 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | SPY |
|---|---:|---:|
| 2010 | 10.6 % | 13.1 % |
| 2011 | -7.0 % | 1.9 % |
| 2012 | 11.3 % | 16.0 % |
| 2013 | 19.8 % | 32.3 % |
| 2014 | 0.9 % | 13.5 % |
| 2015 | 11.1 % | 1.2 % |
| 2016 | 1.7 % | 12.0 % |
| 2017 | 14.3 % | 21.7 % |
| 2018 | -6.5 % | -4.6 % |
| 2019 | 10.9 % | 31.2 % |
| 2020 | 6.7 % | 18.3 % |
| 2021 | 0.6 % | 28.7 % |
| 2022 | -15.7 % | -18.2 % |
| 2023 | -7.6 % | 26.2 % |
| 2024 | 22.1 % | 24.9 % |
| 2025 | 21.9 % | 17.7 % |
| 2026 | 10.0 % | 8.3 % |

</details>

**Varianten und Kontrollläufe im Vergleich** (feste Regeln, alle Trades ab 2010; nur zum Verstehen, welcher Baustein etwas beiträgt – Kontrollläufe werden nie ausgewählt)

| Lauf | Trades | Trefferquote | sicher ≥ | Zufallsniveau | Vorsprung | Ø R | sicher ≥ | PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 Basis | 27802 | 48.6 % | 48.1 % | 44.4 % | +4.1 Pp | -0.014 R | -0.038 R | 0.98 |
| V2 Cluster (≥ 2 Zonentypen) | 12157 | 48.2 % | 47.4 % | 44.4 % | +3.7 Pp | -0.003 R | -0.020 R | 0.99 |
| V3 + interner Bruch | 12663 | 48.6 % | 47.9 % | 44.4 % | +4.2 Pp | +0.001 R | -0.015 R | 1.00 |
| V4 Trailing 3 ATR | 24346 | 35.9 % | 35.4 % | – | – | +0.043 R | 0.026 R | 1.08 |
| _K1 ohne Fibonacci_ | 27915 | 48.5 % | 48.0 % | 44.4 % | +4.0 Pp | -0.018 R | -0.042 R | 0.97 |
| _K2 Zufalls-Fibonacci 0.336–0.454_ | 28828 | 48.6 % | 48.1 % | 44.4 % | +4.2 Pp | -0.001 R | -0.012 R | 1.00 |
| _K2 Zufalls-Fibonacci 0.421–0.539_ | 28159 | 48.6 % | 48.1 % | 44.4 % | +4.1 Pp | -0.014 R | -0.037 R | 0.97 |
| _K2 Zufalls-Fibonacci 0.429–0.547_ | 28096 | 48.6 % | 48.1 % | 44.4 % | +4.1 Pp | -0.013 R | -0.037 R | 0.98 |
| _K2 Zufalls-Fibonacci 0.475–0.593_ | 27842 | 48.5 % | 48.0 % | 44.4 % | +4.1 Pp | -0.016 R | -0.039 R | 0.97 |
| _K2 Zufalls-Fibonacci 0.558–0.676_ | 27737 | 48.5 % | 48.0 % | 44.4 % | +4.1 Pp | -0.017 R | -0.040 R | 0.97 |
| _K3 20-Tage-Ausbruch statt BOS/CHoCH_ | 28467 | 48.6 % | 48.1 % | 44.4 % | +4.1 Pp | -0.017 R | -0.041 R | 0.97 |

Zufallsniveau = Trefferquote, die bei diesem Kursziel/Stop-Verhältnis ohne jeden Vorteil zu erwarten wäre (vor Kosten). Erst der Vorsprung darüber ist Können. K1–K3: Ist ein Baustein wertvoll, sollte der Kontrolllauf ohne ihn bzw. mit Zufallswerten deutlich schlechter sein als V1.

### Krypto – ❌ NICHT BESTANDEN

- Trefferquote nicht sicher genug (34.1 % < 50.0 % untere Grenze)

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2012–2013 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2014–2015 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2016–2017 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2018–2019 | V1 Basis | 42 | 0.356 R | 20 | -0.067 R |
| 2020–2021 | V4 Trailing 3 ATR | 48 | 1.215 R | 76 | +1.699 R |
| 2022–2023 | V4 Trailing 3 ATR | 123 | 1.529 R | 23 | +0.038 R |
| 2024–2025 | V4 Trailing 3 ATR | 143 | 1.332 R | 58 | +0.008 R |
| 2026–heute | V4 Trailing 3 ATR | 205 | 0.921 R | 6 | -0.221 R |

**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Out-of-Sample |
|---|---:|
| Abgeschlossene Trades | 183 |
| Trades pro Jahr | 21.9 |
| Trefferquote | 39.9 % |
| … sicher mindestens | 34.1 % |
| Ø Gewinn-Trade | 2.90 R |
| Ø Verlust-Trade | -0.77 R |
| **Erwartungswert je Trade** | 0.699 R |
| … sicher mindestens | 0.278 R |
| Profit-Faktor | 2.52 |
| Ø Haltedauer (Tage) | 15.2 |

Ausstiege: Trailing-Stop (Gewinne gesichert) 129×, Stop-Loss 44×, Kursziel 8×, Zeit-Stop 1×, Trailing-Stop (Gap, schlechter ausgeführt) 1×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Out-of-Sample (2018–2026) |
|---|---:|
| **Rendite p.a. Strategie** | **11.2 %** |
| Max. Drawdown Strategie | -12.3 % |
| MAR (Rendite ÷ Drawdown) Strategie | 0.91 |
| Rendite p.a. BTC-USD (Kaufen & Halten) | 34.0 % |
| Max. Drawdown BTC-USD | -76.6 % |
| MAR BTC-USD | 0.44 |
| Rendite p.a. Universum gleichgewichtet (Kaufen & Halten) | 45.5 % |
| Max. Drawdown Universum gleichgewichtet | -80.9 % |
| MAR Universum gleichgewichtet | 0.56 |
| Trades genommen / übersprungen | 172 / 11 |
| Ø gleichzeitige Positionen | 0.8 |
| Ø tatsächliches Risiko je Trade | 0.91 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | BTC-USD |
|---|---:|---:|
| 2018 | -1.0 % | -44.4 % |
| 2019 | -1.1 % | 92.2 % |
| 2020 | 21.7 % | 303.2 % |
| 2021 | 116.2 % | 59.7 % |
| 2022 | -0.6 % | -64.3 % |
| 2023 | 3.2 % | 155.4 % |
| 2024 | -2.0 % | 121.0 % |
| 2025 | -5.0 % | -6.3 % |
| 2026 | -1.3 % | -11.1 % |

</details>

**Varianten und Kontrollläufe im Vergleich** (feste Regeln, alle Trades ab 2010; nur zum Verstehen, welcher Baustein etwas beiträgt – Kontrollläufe werden nie ausgewählt)

| Lauf | Trades | Trefferquote | sicher ≥ | Zufallsniveau | Vorsprung | Ø R | sicher ≥ | PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 Basis | 266 | 52.3 % | 47.2 % | 44.4 % | +7.8 Pp | +0.152 R | 0.044 R | 1.33 |
| V2 Cluster (≥ 2 Zonentypen) | 111 | 51.4 % | 43.6 % | 44.4 % | +6.9 Pp | +0.127 R | -0.041 R | 1.27 |
| V3 + interner Bruch | 132 | 55.3 % | 48.1 % | 44.4 % | +10.9 Pp | +0.207 R | 0.056 R | 1.48 |
| V4 Trailing 3 ATR | 211 | 42.7 % | 37.2 % | – | – | +0.889 R | 0.482 R | 3.10 |
| _K1 ohne Fibonacci_ | 268 | 52.6 % | 47.6 % | 44.4 % | +8.2 Pp | +0.154 R | 0.043 R | 1.34 |
| _K2 Zufalls-Fibonacci 0.336–0.454_ | 269 | 54.3 % | 49.3 % | 44.4 % | +9.8 Pp | +0.176 R | 0.067 R | 1.40 |
| _K2 Zufalls-Fibonacci 0.421–0.539_ | 270 | 53.0 % | 48.0 % | 44.4 % | +8.5 Pp | +0.160 R | 0.054 R | 1.35 |
| _K2 Zufalls-Fibonacci 0.429–0.547_ | 271 | 52.8 % | 47.8 % | 44.4 % | +8.3 Pp | +0.152 R | 0.045 R | 1.33 |
| _K2 Zufalls-Fibonacci 0.475–0.593_ | 272 | 52.9 % | 48.0 % | 44.4 % | +8.5 Pp | +0.162 R | 0.055 R | 1.36 |
| _K2 Zufalls-Fibonacci 0.558–0.676_ | 266 | 51.5 % | 46.5 % | 44.4 % | +7.1 Pp | +0.137 R | 0.029 R | 1.30 |
| _K3 20-Tage-Ausbruch statt BOS/CHoCH_ | 263 | 51.7 % | 46.7 % | 44.4 % | +7.3 Pp | +0.126 R | 0.018 R | 1.27 |

Zufallsniveau = Trefferquote, die bei diesem Kursziel/Stop-Verhältnis ohne jeden Vorteil zu erwarten wäre (vor Kosten). Erst der Vorsprung darüber ist Können. K1–K3: Ist ein Baustein wertvoll, sollte der Kontrolllauf ohne ihn bzw. mit Zufallswerten deutlich schlechter sein als V1.

<details><summary>Aufschlüsselung nach Ländern (alle Trades)</summary>

| Markt | Symbole | Trades | Trefferquote | Erwartungswert | Profit-Faktor |
|---|---:|---:|---:|---:|---:|
| US | 134 | 7522 | 42.3 % | +0.013 R | 1.02 |
| JP | 39 | 1856 | 39.8 % | +0.077 R | 1.14 |
| FR | 38 | 1848 | 39.3 % | -0.009 R | 0.98 |
| DE | 39 | 1751 | 38.3 % | -0.043 R | 0.92 |
| UK | 35 | 1410 | 35.3 % | -0.130 R | 0.78 |
| CA | 20 | 999 | 43.9 % | +0.170 R | 1.35 |
| AU | 19 | 942 | 39.0 % | +0.005 R | 1.01 |
| IN | 20 | 890 | 40.2 % | +0.047 R | 1.09 |
| CH | 18 | 862 | 41.2 % | +0.062 R | 1.12 |
| NL | 18 | 685 | 38.5 % | -0.010 R | 0.98 |
| HK | 19 | 678 | 41.2 % | +0.094 R | 1.18 |
| IT | 14 | 675 | 40.0 % | +0.033 R | 1.06 |
| SE | 11 | 533 | 42.2 % | +0.022 R | 1.04 |
| ES | 10 | 482 | 44.2 % | +0.158 R | 1.33 |
| TW | 10 | 477 | 38.6 % | +0.035 R | 1.07 |
| KR | 10 | 377 | 38.5 % | +0.223 R | 1.43 |
| DK | 8 | 361 | 44.6 % | +0.203 R | 1.43 |
| BR | 10 | 360 | 35.0 % | +0.141 R | 1.25 |
| NO | 6 | 319 | 37.9 % | -0.058 R | 0.89 |
| FI | 5 | 232 | 38.4 % | -0.095 R | 0.83 |
| SG | 4 | 204 | 44.6 % | +0.195 R | 1.37 |
| CRYPTO | 6 | 183 | 39.9 % | +0.699 R | 2.52 |
| BE | 4 | 164 | 37.2 % | -0.006 R | 0.99 |
| MX | 3 | 128 | 37.5 % | -0.073 R | 0.86 |

Einzelne Länder haben oft zu wenige Trades für sichere Aussagen – nur grobe Hinweise.

</details>

## Confluence Short (gespiegelt)

Verkauft (short) im Abwärtstrend (SMA50 < SMA200, Struktur abwärts), wenn eine Erholung einen Widerstand berührt (SMA, Fibonacci 0,5–0,618 oder Swing-Zone) und eine rote Kerze darunter schließt. Stop hinter der Zone, Ziel 1,25 R.

Varianten: `V1 Basis` · `V2 Cluster (≥ 2 Zonentypen)` · `V3 + interner Bruch` · `V4 Trailing 3 ATR`

### Aktien & ETFs – ❌ NICHT BESTANDEN

- in keinem Testfenster gehandelt

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | – kein Handel (bis dahin keine Variante profitabel) | 2942 | -0.011 R | – | – |
| 2012–2013 | – kein Handel (bis dahin keine Variante profitabel) | 3856 | -0.053 R | – | – |
| 2014–2015 | – kein Handel (bis dahin keine Variante profitabel) | 4342 | -0.089 R | – | – |
| 2016–2017 | – kein Handel (bis dahin keine Variante profitabel) | 5173 | -0.110 R | – | – |
| 2018–2019 | – kein Handel (bis dahin keine Variante profitabel) | 6118 | -0.123 R | – | – |
| 2020–2021 | – kein Handel (bis dahin keine Variante profitabel) | 7352 | -0.135 R | – | – |
| 2022–2023 | – kein Handel (bis dahin keine Variante profitabel) | 8280 | -0.160 R | – | – |
| 2024–2025 | – kein Handel (bis dahin keine Variante profitabel) | 9774 | -0.181 R | – | – |
| 2026–heute | – kein Handel (bis dahin keine Variante profitabel) | 10830 | -0.191 R | – | – |

**Varianten und Kontrollläufe im Vergleich** (feste Regeln, alle Trades ab 2010; nur zum Verstehen, welcher Baustein etwas beiträgt – Kontrollläufe werden nie ausgewählt)

| Lauf | Trades | Trefferquote | sicher ≥ | Zufallsniveau | Vorsprung | Ø R | sicher ≥ | PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 Basis | 8446 | 35.7 % | 34.8 % | 44.4 % | -8.8 Pp | -0.258 R | -0.277 R | 0.61 |
| V2 Cluster (≥ 2 Zonentypen) | 3460 | 35.3 % | 34.0 % | 44.4 % | -9.2 Pp | -0.266 R | -0.295 R | 0.59 |
| V3 + interner Bruch | 3492 | 34.5 % | 33.2 % | 44.4 % | -9.9 Pp | -0.279 R | -0.308 R | 0.58 |
| V4 Trailing 3 ATR | 8046 | 24.6 % | 23.8 % | – | – | -0.322 R | -0.344 R | 0.48 |
| _K1 ohne Fibonacci_ | 8470 | 35.8 % | 35.0 % | 44.4 % | -8.6 Pp | -0.257 R | -0.276 R | 0.61 |
| _K2 Zufalls-Fibonacci 0.336–0.454_ | 8661 | 35.8 % | 34.9 % | 44.4 % | -8.7 Pp | -0.256 R | -0.275 R | 0.61 |
| _K2 Zufalls-Fibonacci 0.421–0.539_ | 8491 | 35.6 % | 34.8 % | 44.4 % | -8.8 Pp | -0.261 R | -0.280 R | 0.60 |
| _K2 Zufalls-Fibonacci 0.429–0.547_ | 8485 | 35.6 % | 34.8 % | 44.4 % | -8.8 Pp | -0.261 R | -0.281 R | 0.60 |
| _K2 Zufalls-Fibonacci 0.475–0.593_ | 8442 | 35.6 % | 34.7 % | 44.4 % | -8.9 Pp | -0.262 R | -0.281 R | 0.60 |
| _K2 Zufalls-Fibonacci 0.558–0.676_ | 8445 | 36.0 % | 35.1 % | 44.4 % | -8.5 Pp | -0.253 R | -0.273 R | 0.62 |
| _K3 20-Tage-Ausbruch statt BOS/CHoCH_ | 8378 | 36.0 % | 35.2 % | 44.4 % | -8.4 Pp | -0.249 R | -0.268 R | 0.62 |

Zufallsniveau = Trefferquote, die bei diesem Kursziel/Stop-Verhältnis ohne jeden Vorteil zu erwarten wäre (vor Kosten). Erst der Vorsprung darüber ist Können. K1–K3: Ist ein Baustein wertvoll, sollte der Kontrolllauf ohne ihn bzw. mit Zufallswerten deutlich schlechter sein als V1.

### Krypto – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze -0.37 R < 0.15 R)
- Profit-Faktor 0.71 < 1.60
- Trefferquote nicht sicher genug (19.0 % < 50.0 % untere Grenze)
- Portfolio im Test ohne Gewinn

**Gewählte Variante je Testfenster** (Auswahl nur mit Daten vor dem Fenster)

| Fenster | Variante | Trainings-Trades | Ø R Training | Trades im Fenster | Ø R im Fenster |
|---|---|---:|---:|---:|---:|
| 2010–2011 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2012–2013 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2014–2015 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2016–2017 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2018–2019 | – kein Handel (keine Variante mit mind. 30 Trainings-Trades) | – | – | – | – |
| 2020–2021 | V4 Trailing 3 ATR | 37 | 0.915 R | 5 | -0.885 R |
| 2022–2023 | V4 Trailing 3 ATR | 45 | 0.708 R | 43 | +0.154 R |
| 2024–2025 | V4 Trailing 3 ATR | 88 | 0.438 R | 15 | -0.443 R |
| 2026–heute | V4 Trailing 3 ATR | 99 | 0.328 R | 35 | -0.315 R |

**Trade-Statistik aller Testfenster** (alle Signale, ohne Depot-Begrenzung)

| Kennzahl | Out-of-Sample |
|---|---:|
| Abgeschlossene Trades | 98 |
| Trades pro Jahr | 14.8 |
| Trefferquote | 25.5 % |
| … sicher mindestens | 19.0 % |
| Ø Gewinn-Trade | 1.49 R |
| Ø Verlust-Trade | -0.72 R |
| **Erwartungswert je Trade** | -0.158 R |
| … sicher mindestens | -0.372 R |
| Profit-Faktor | 0.71 |
| Ø Haltedauer (Tage) | 16.0 |

Ausstiege: Trailing-Stop (Gewinne gesichert) 72×, Stop-Loss 26×

**Portfolio-Simulation** (so wäre ein echtes Depot gelaufen)

Max. 10 Positionen gleichzeitig, max. 4 pro Land, 1 % Risiko je Trade, kein Hebel. Bei zu vielen Signalen gewinnen die relativ stärksten Werte.

| | Out-of-Sample (2020–2026) |
|---|---:|
| **Rendite p.a. Strategie** | **-1.8 %** |
| Max. Drawdown Strategie | -16.2 % |
| MAR (Rendite ÷ Drawdown) Strategie | -0.11 |
| Rendite p.a. BTC-USD (Kaufen & Halten) | 40.3 % |
| Max. Drawdown BTC-USD | -76.6 % |
| MAR BTC-USD | 0.53 |
| Rendite p.a. Universum gleichgewichtet (Kaufen & Halten) | 75.7 % |
| Max. Drawdown Universum gleichgewichtet | -80.9 % |
| MAR Universum gleichgewichtet | 0.94 |
| Trades genommen / übersprungen | 90 / 8 |
| Ø gleichzeitige Positionen | 0.5 |
| Ø tatsächliches Risiko je Trade | 0.84 % |

<details><summary>Jahresrenditen</summary>

| Jahr | Strategie | BTC-USD |
|---|---:|---:|
| 2020 | -3.9 % | 294.9 % |
| 2022 | 5.8 % | -64.3 % |
| 2023 | 0.1 % | 155.4 % |
| 2024 | -3.6 % | 121.0 % |
| 2025 | -2.5 % | -6.3 % |
| 2026 | -7.5 % | -20.9 % |

</details>

**Varianten und Kontrollläufe im Vergleich** (feste Regeln, alle Trades ab 2010; nur zum Verstehen, welcher Baustein etwas beiträgt – Kontrollläufe werden nie ausgewählt)

| Lauf | Trades | Trefferquote | sicher ≥ | Zufallsniveau | Vorsprung | Ø R | sicher ≥ | PF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 Basis | 166 | 38.0 % | 32.0 % | 44.4 % | -6.5 Pp | -0.162 R | -0.294 R | 0.72 |
| V2 Cluster (≥ 2 Zonentypen) | 59 | 42.4 % | 32.4 % | 44.4 % | -2.1 Pp | -0.070 R | -0.289 R | 0.86 |
| V3 + interner Bruch | 90 | 30.0 % | 22.7 % | 44.4 % | -14.4 Pp | -0.347 R | -0.518 R | 0.48 |
| V4 Trailing 3 ATR | 138 | 29.0 % | 23.1 % | – | – | +0.151 R | -0.157 R | 1.29 |
| _K1 ohne Fibonacci_ | 170 | 37.6 % | 31.8 % | 44.4 % | -6.8 Pp | -0.159 R | -0.289 R | 0.72 |
| _K2 Zufalls-Fibonacci 0.336–0.454_ | 164 | 35.4 % | 29.5 % | 44.4 % | -9.1 Pp | -0.190 R | -0.316 R | 0.67 |
| _K2 Zufalls-Fibonacci 0.421–0.539_ | 164 | 36.0 % | 30.1 % | 44.4 % | -8.5 Pp | -0.190 R | -0.318 R | 0.67 |
| _K2 Zufalls-Fibonacci 0.429–0.547_ | 167 | 36.5 % | 30.7 % | 44.4 % | -7.9 Pp | -0.171 R | -0.297 R | 0.70 |
| _K2 Zufalls-Fibonacci 0.475–0.593_ | 165 | 37.0 % | 31.0 % | 44.4 % | -7.5 Pp | -0.179 R | -0.303 R | 0.69 |
| _K2 Zufalls-Fibonacci 0.558–0.676_ | 168 | 37.5 % | 31.6 % | 44.4 % | -6.9 Pp | -0.159 R | -0.290 R | 0.72 |
| _K3 20-Tage-Ausbruch statt BOS/CHoCH_ | 158 | 38.6 % | 32.5 % | 44.4 % | -5.8 Pp | -0.165 R | -0.295 R | 0.71 |

Zufallsniveau = Trefferquote, die bei diesem Kursziel/Stop-Verhältnis ohne jeden Vorteil zu erwarten wäre (vor Kosten). Erst der Vorsprung darüber ist Können. K1–K3: Ist ein Baustein wertvoll, sollte der Kontrolllauf ohne ihn bzw. mit Zufallswerten deutlich schlechter sein als V1.

<details><summary>Aufschlüsselung nach Ländern (alle Trades)</summary>

| Markt | Symbole | Trades | Trefferquote | Erwartungswert | Profit-Faktor |
|---|---:|---:|---:|---:|---:|
| CRYPTO | 6 | 98 | 25.5 % | -0.158 R | 0.71 |

Einzelne Länder haben oft zu wenige Trades für sichere Aussagen – nur grobe Hinweise.

</details>
