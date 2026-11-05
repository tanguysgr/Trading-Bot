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

## Walk-Forward – der ehrlichste Test
Ein fester Stichtag hat einen Haken: Sobald man das Testergebnis gesehen hat
und daraufhin etwas ändert, ist der Test „verbraucht“. Der Walk-Forward spielt
stattdessen nach, was man damals wirklich hätte tun können:

1. Die Zeit wird in 2-Jahres-Fenster geteilt (2010–11, 2012–13, …).
2. Vor jedem Fenster wird aus wenigen Varianten einer Strategie die gewählt,
   die **bis dahin** am verlässlichsten Gewinn brachte.
3. Diese Variante handelt im Fenster. Danach wird neu gewählt.
4. Alle Fenster zusammen ergeben das Ergebnis – jeder Trade darin war bei der
   Auswahl unbekannt.

Springt die Wahl ständig zwischen Varianten, ist das ein Warnsignal: Dann gibt
es vermutlich kein stabiles Muster.

## Trailing-Stop – Gewinne laufen lassen
Statt eines festen Kursziels wird der Stop nach jedem Tag nachgezogen:
höchstes Hoch seit Einstieg minus z.B. 3 ATR. Er steigt mit, sinkt aber nie.
Folge: weniger Gewinn-Trades, dafür einzelne sehr große Gewinner. Die
Trefferquote sinkt, der durchschnittliche Gewinn steigt.

## Regime-Filter und relative Stärke
- **Regime-Filter:** Nur kaufen, wenn der Gesamtmarkt (S&P 500 bzw. Bitcoin)
  über seiner 200-Tage-Linie liegt. Viele Strategien verlieren in Bärenmärkten.
- **Relative Stärke:** Rang der 6-Monats-Performance im ganzen Universum
  (1,0 = bester Wert). Starke Aktien bleiben im Schnitt eine Weile stark
  („Momentum“, einer der am besten belegten Effekte am Aktienmarkt).

## Zufallsniveau – warum eine hohe Trefferquote allein nichts beweist
Wo Stop und Ziel liegen, bestimmt, welche Trefferquote man **ohne jedes Können**
erreicht: Zufallsniveau = 1 ÷ (1 + CRV). Bei Ziel = Stop (CRV 1) sind das 50 %,
bei 1,25 R schon 44,4 %, bei 2 R nur 33 %. Ein weites Ziel senkt die Quote, ein
nahes hebt sie – ohne dass sich am Vorteil etwas ändert. Echte Qualität ist nur
der **Vorsprung** über dem Zufallsniveau. Deshalb steht er im Bericht neben jeder
Trefferquote.

## Kontrollläufe – trägt ein Baustein wirklich etwas bei?
Ein Kontrolllauf ist die Strategie mit einem absichtlich veränderten Baustein:
- **ohne Fibonacci:** Ist das Ergebnis genauso gut, bringt Fibonacci nichts.
- **mit Zufalls-„Fibonacci“-Zonen:** gleich breite Zonen an zufälligen Stellen.
  Sind die genauso gut, ist 0,5–0,618 nichts Besonderes.
- **Ausbruch statt BOS/CHoCH:** Ist ein simpler 20-Tage-Ausbruch genauso gut,
  steckt im BOS/CHoCH-Konzept keine zusätzliche Information.
Kontrollläufe werden nie als Gewinner ausgewählt – sie dienen nur dem Verständnis.

## Trade-Statistik vs. Portfolio
- Die **Trade-Statistik** wertet jedes Signal aus, als könntest du unbegrenzt
  viele Positionen halten. Sie misst, ob die Idee an sich einen Vorteil hat.
- Die **Portfolio-Simulation** zeigt, was mit einem echten Depot passiert wäre:
  höchstens 10 Positionen, höchstens 4 aus einem Land, kein Hebel. Dazu der
  Vergleich mit **Kaufen & Halten** eines Index-ETFs. Eine Strategie, die
  dauerhaft schlechter als der ETF ist, lohnt den Aufwand nicht.
- Faustregel: Rendite p.a. ≈ Erwartungswert (R) × Risiko je Trade × Trades pro Jahr.
- **MAR-Quote** = Rendite p.a. ÷ größter Rückgang. Damit vergleicht man fair:
  Eine Strategie mit 8 % Rendite und 20 % Rückgang (MAR 0,4) ist risikobereinigt
  so gut wie ein Index mit 12 % und 30 % Rückgang.
- **Universum gleichgewichtet:** alle Werte der Liste zu gleichen Teilen halten.
  Weil die Liste nur heutige Gewinner enthält (Survivorship Bias), ist dieser
  Wert geschönt – er zeigt, wie viel „Rückenwind“ allein in der Auswahl steckt.

## Wie der Prüfstand rechnet
- Signal am Tagesschluss → Einstieg zur Eröffnung am nächsten Tag
- Stop und Ziel am selben Tag berührt → zählt als Verlust
- Kurslücken (Gaps) über den Stop → Ausführung zum schlechteren Eröffnungskurs
- Gebühren 0,1 % und Slippage 0,05 % (Krypto 0,1 %) je Kauf und Verkauf
- Signale nur bei Werten mit mind. 5 Mio. USD Tagesumsatz (damals, nicht heute)

Diese Regeln sind absichtlich streng. Ein Backtest, der zu gut aussieht, ist
fast immer ein fehlerhafter Backtest.
