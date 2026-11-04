# Backtest-Bericht

Stichtag Training/Test: **2018-01-01** – Regeln wurden nur mit Daten davor entwickelt; entscheidend ist die Spalte **Test**.

> Ein Backtest zeigt die Vergangenheit, keine Garantie für die Zukunft. Keine Anlageberatung.

## Trend-Pullback

Kauft im intakten Aufwärtstrend (Kurs > SMA200, SMA50 > SMA200, ADX stark), nachdem ein Rücksetzer (RSI tief) wieder nach oben dreht.

Kursziel 2.0 R · Zeit-Stop 40 Tage · Parameter: `{'adx_min': 20.0, 'rsi_dip': 40.0, 'lookback': 5, 'min_stop_atr': 1.0}`

Symbole getestet: 29

### Krypto – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze -0.31 R < 0.15 R)
- Profit-Faktor 0.94 < 1.60
- Trefferquote nicht sicher genug (25.6 % < 50.0 % untere Grenze)

| Kennzahl | Gesamt | Training | **Test** |
|---|---:|---:|---:|
| Abgeschlossene Trades | 73 | 6 | **67** |
| Trades pro Jahr | 6.5 | 2.7 | **7.6** |
| Trefferquote | 37.0 % | 66.7 % | **34.3 %** |
| … sicher mindestens | 28.3 % | 34.7 % | **25.6 %** |
| Ø Gewinn-Trade | 1.67 R | 1.07 R | **1.77 R** |
| Ø Verlust-Trade | -0.99 R | -1.05 R | **-0.99 R** |
| **Erwartungswert je Trade** | -0.007 R | 0.366 R | **-0.041 R** |
| … sicher mindestens | -0.269 R | -0.393 R | **-0.310 R** |
| Profit-Faktor | 0.99 | 2.05 | **0.94** |
| Max. Drawdown (1 % Risiko/Trade) | -12.9 % | -1.2 % | **-12.9 %** |
| Rendite p.a. (1 % Risiko/Trade) | -0.1 % | 1.0 % | **-0.4 %** |
| Längste Verlustserie | 12 | 1 | **12** |
| Ø Haltedauer (Tage) | 15.7 | 26.7 | **14.7** |

Ausstiege: Stop-Loss 43×, Kursziel 21×, Zeit-Stop 9×

### Aktien & ETFs – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze -0.02 R < 0.00 R)
- Profit-Faktor 1.13 < 1.30
- Drawdown zu groß (-28.9 % < -25.0 %)

| Kennzahl | Gesamt | Training | **Test** |
|---|---:|---:|---:|
| Abgeschlossene Trades | 1304 | 752 | **552** |
| Trades pro Jahr | 62.0 | 61.1 | **62.6** |
| Trefferquote | 41.6 % | 39.8 % | **44.0 %** |
| … sicher mindestens | 39.3 % | 36.9 % | **40.6 %** |
| Ø Gewinn-Trade | 1.67 R | 1.72 R | **1.61 R** |
| Ø Verlust-Trade | -1.11 R | -1.11 R | **-1.12 R** |
| **Erwartungswert je Trade** | 0.043 R | 0.015 R | **0.081 R** |
| … sicher mindestens | -0.023 R | -0.073 R | **-0.020 R** |
| Profit-Faktor | 1.07 | 1.02 | **1.13** |
| Max. Drawdown (1 % Risiko/Trade) | -39.6 % | -39.4 % | **-28.9 %** |
| Rendite p.a. (1 % Risiko/Trade) | 2.0 % | 0.3 % | **4.5 %** |
| Längste Verlustserie | 19 | 19 | **19** |
| Ø Haltedauer (Tage) | 15.3 | 14.9 | **15.9** |

Ausstiege: Stop-Loss 585×, Kursziel 323×, Zeit-Stop 172×, Stop-Loss (Gap, schlechter ausgeführt) 141×, Kursziel (Gap, besser ausgeführt) 83×

## Ausbruch mit Volumen (BOS + RVOL)

Kauft, wenn der Kurs im Aufwärtstrend ein bestätigtes Swing-Hoch mit deutlich erhöhtem Volumen überwindet.

Kursziel 2.0 R · Zeit-Stop 30 Tage · Parameter: `{'swing_strength': 3, 'rvol_min': 1.5, 'max_ext_atr': 1.5, 'stop_atr': 2.0}`

Symbole getestet: 29

### Krypto – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze 0.05 R < 0.15 R)
- Trefferquote nicht sicher genug (35.8 % < 50.0 % untere Grenze)

| Kennzahl | Gesamt | Training | **Test** |
|---|---:|---:|---:|
| Abgeschlossene Trades | 51 | 7 | **44** |
| Trades pro Jahr | 4.5 | 4.6 | **5.0** |
| Trefferquote | 52.9 % | 85.7 % | **47.7 %** |
| … sicher mindestens | 41.6 % | 54.8 % | **35.8 %** |
| Ø Gewinn-Trade | 1.80 R | 1.57 R | **1.87 R** |
| Ø Verlust-Trade | -0.94 R | -1.05 R | **-0.94 R** |
| **Erwartungswert je Trade** | 0.511 R | 1.192 R | **0.403 R** |
| … sicher mindestens | 0.174 R | 0.493 R | **0.051 R** |
| Profit-Faktor | 2.15 | 8.95 | **1.82** |
| Max. Drawdown (1 % Risiko/Trade) | -5.2 % | -1.0 % | **-5.2 %** |
| Rendite p.a. (1 % Risiko/Trade) | 2.3 % | 5.6 % | **2.0 %** |
| Längste Verlustserie | 5 | 1 | **5** |
| Ø Haltedauer (Tage) | 12.1 | 18.1 | **11.1** |

Ausstiege: Kursziel 23×, Stop-Loss 21×, Zeit-Stop 7×

### Aktien & ETFs – ❌ NICHT BESTANDEN

- Vorteil statistisch nicht gesichert (untere Grenze -0.03 R < 0.00 R)
- Profit-Faktor 1.17 < 1.30

| Kennzahl | Gesamt | Training | **Test** |
|---|---:|---:|---:|
| Abgeschlossene Trades | 805 | 498 | **307** |
| Trades pro Jahr | 38.3 | 40.6 | **34.8** |
| Trefferquote | 45.2 % | 46.8 % | **42.7 %** |
| … sicher mindestens | 42.4 % | 43.1 % | **38.1 %** |
| Ø Gewinn-Trade | 1.65 R | 1.62 R | **1.70 R** |
| Ø Verlust-Trade | -1.05 R | -1.04 R | **-1.08 R** |
| **Erwartungswert je Trade** | 0.169 R | 0.206 R | **0.108 R** |
| … sicher mindestens | 0.086 R | 0.102 R | **-0.026 R** |
| Profit-Faktor | 1.29 | 1.37 | **1.17** |
| Max. Drawdown (1 % Risiko/Trade) | -21.0 % | -17.0 % | **-21.0 %** |
| Rendite p.a. (1 % Risiko/Trade) | 6.2 % | 8.3 % | **3.4 %** |
| Längste Verlustserie | 13 | 13 | **10** |
| Ø Haltedauer (Tage) | 15.6 | 16.3 | **14.5** |

Ausstiege: Stop-Loss 330×, Kursziel 208×, Zeit-Stop 147×, Stop-Loss (Gap, schlechter ausgeführt) 75×, Kursziel (Gap, besser ausgeführt) 45×
