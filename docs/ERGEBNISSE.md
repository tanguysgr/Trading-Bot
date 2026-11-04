# Ergebnis-Logbuch

Jeder wichtige Backtest-Lauf mit Datum, Stand und Fazit – neuester oben.
Die vollständigen Berichte liegen in [`docs/ergebnisse/`](ergebnisse/).

Lesehilfe: [BACKTEST_ERKLAERT.md](BACKTEST_ERKLAERT.md). Entscheidend ist immer der **Test**-Zeitraum (ab 2018).

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
