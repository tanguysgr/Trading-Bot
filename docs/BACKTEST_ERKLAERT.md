# Den Backtest-Bericht lesen

## Die Einheit „R“
**1 R = der Betrag, den du bei einem Trade riskierst**, also was du verlierst,
wenn der Stop-Loss greift. Riskierst du 100 € und gewinnst 250 €, war das +2,5 R.
So lassen sich Trades in ganz unterschiedlichen Aktien vergleichen.

## Die wichtigsten Kennzahlen

| Kennzahl | Bedeutung | Faustregel |
|---|---|---|
| **Erwartungswert je Trade** | Durchschnittlicher Gewinn pro Trade in R, nach Kosten | > 0 ist Pflicht; ab ~0,2 R interessant |
| … sicher mindestens | Untere Grenze des Erwartungswerts (Bootstrap, 95 %) | > 0 heißt: Vorteil sehr wahrscheinlich kein Zufall |
| Trefferquote | Anteil der Gewinn-Trades | Allein wertlos – mit 35 % kann man reich, mit 70 % pleite werden |
| … sicher mindestens | Untere Grenze der Trefferquote (Wilson, 95 %) | Wichtig bei wenigen Trades |
| Profit-Faktor | Summe Gewinne ÷ Summe Verluste | > 1,3 solide, > 2 sehr gut (oft verdächtig) |
| Max. Drawdown | Größter Rückgang vom Kontohoch bei 1 % Risiko je Trade | Was du psychisch aushalten musst |
| Längste Verlustserie | So viele Verluste nacheinander kamen vor | Rechne damit, dass es live mehr werden |

## Training vs. Test – die wichtigste Spalte
Die Daten werden an einem **Stichtag** getrennt:
- **Training** (davor): Hier dürfen Regeln entwickelt und Parameter gewählt werden.
- **Test** (danach): Wird nur zur Prüfung benutzt.

Wenn eine Strategie im Training glänzt, im Test aber nicht, hat sie die
Vergangenheit auswendig gelernt (Overfitting). **Entscheidend ist immer die Test-Spalte.**

## Trade-Statistik vs. Portfolio
- Die **Trade-Statistik** wertet jedes Signal aus, als könntest du unbegrenzt
  viele Positionen halten. Sie misst, ob die Idee an sich einen Vorteil hat.
- Die **Portfolio-Simulation** zeigt, was mit einem echten Depot passiert wäre:
  höchstens 10 Positionen, höchstens 4 aus einem Land, kein Hebel. Dazu der
  Vergleich mit **Kaufen & Halten** eines Index-ETFs. Eine Strategie, die
  dauerhaft schlechter als der ETF ist, lohnt den Aufwand nicht.
- Faustregel: Rendite p.a. ≈ Erwartungswert (R) × Risiko je Trade × Trades pro Jahr.

## Wie der Prüfstand rechnet
- Signal am Tagesschluss → Einstieg zur Eröffnung am nächsten Tag
- Stop und Ziel am selben Tag berührt → zählt als Verlust
- Kurslücken (Gaps) über den Stop → Ausführung zum schlechteren Eröffnungskurs
- Gebühren 0,1 % und Slippage 0,05 % (Krypto 0,1 %) je Kauf und Verkauf
- Signale nur bei Werten mit mind. 5 Mio. USD Tagesumsatz (damals, nicht heute)

Diese Regeln sind absichtlich streng. Ein Backtest, der zu gut aussieht, ist
fast immer ein fehlerhafter Backtest.
