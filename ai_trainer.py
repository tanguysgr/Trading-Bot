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

prompt = (
    "Du bist ein quantitativer KI-Entwickler. \n"
    f"Unser Python Trading Bot (backtester.py) hat aktuell nur eine Winrate von {winrate:.1f}%.\n"
    "Wir müssen die Einstiegsbedingungen in der Funktion 'evaluate_strategies_on_history' verbessern.\n\n"
    "Hier ist der aktuelle Code:\n"
    "```python\n"
    f"{current_code}\n"
    "```\n\n"
    "Aufgabe: \n"
    "Analysiere, warum die Strategien zu oft fehlschlagen. \n"
    "Optimiere die Filter (z.B. SMA-Abstände, RSI-Grenzen, Volumen-Schwellenwerte) oder füge neue Price-Action-Regeln hinzu.\n"
    "Gib mir NUR den kompletten, verbesserten Python-Code zurück, eingeschlossen in ```python ... ```. \n"
    "Schreibe keinen zusätzlichen Text, nur den reinen Code!"
)

# 5. Sende die Aufgabe an die Gemini API
url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=){API_KEY}"
headers = {'Content-Type': 'application/json'}
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0.2} # Niedrige Temperatur für logischen Code
}

try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    
    ai_response_text = result['candidates'][0]['content']['parts'][0]['text']
    
    # 6. Extrahiere den reinen Python-Code aus der Antwort
    match = re.search(r'```python\n(.*?)\n```', ai_response_text, re.DOTALL)
    if match:
        new_code = match.group(1)
        
        # 7. Überschreibe die alte Datei mit dem verbesserten Code
        with open('backtester.py', 'w') as f:
            f.write(new_code)
        print("Erfolg! KI hat den Code analysiert und backtester.py mit neuen Regeln überschrieben.")
    else:
        print("KI hat keinen gültigen Python-Code zurückgegeben.")

except Exception as e:
    print(f"Fehler bei der KI-Anfrage: {e}")
