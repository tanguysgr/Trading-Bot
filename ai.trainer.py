import os
import json
import requests
import re

# 1. Lese die letzten Backtest-Ergebnisse
try:
    with open('trades.json', 'r') as f:
        trades = json.load(f)
except FileNotFoundError:
    print("Keine trades.json gefunden. Trainer bricht ab.")
    exit()

# 2. Lese den aktuellen Quellcode der Strategie
with open('backtester.py', 'r') as f:
    current_code = f.read()

# 3. Bewerte die Leistung
total_trades = len(trades)
if total_trades == 0:
    print("Keine Trades simuliert. Keine Optimierung möglich.")
    exit()

losses = sum(1 for t in trades if t.get('grade') == 'LOSS')
winrate = ((total_trades - losses) / total_trades) * 100

print(f"Aktuelle Winrate: {winrate:.1f}%")

# Wenn die Strategie gut läuft (z.B. > 60%), müssen wir nichts ändern
if winrate >= 60.0:
    print("Strategie performt gut. Kein KI-Eingriff nötig.")
    exit()

print("Winrate unter 60%. Starte autonome KI-Optimierung (Self-Healing)...")

# 4. Baue den Prompt für Gemini
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("FEHLER: GEMINI_API_KEY nicht in den GitHub Secrets gefunden!")
    exit()

prompt = f"""Du bist ein quantitativer KI-Entwickler. 
Unser Python Trading Bot (backtester.py) hat aktuell nur eine Winrate von {winrate}%.
Wir müssen die Einstiegsbedingungen in der Funktion 'evaluate_strategies_on_history' verbessern.

Hier ist der aktuelle Code:
```python
{current_code}
