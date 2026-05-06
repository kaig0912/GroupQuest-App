#!/bin/zsh
cd "$(dirname "$0")"

echo ""
echo "GroupQuest startet..."
echo "Ordner: $(pwd)"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 wurde nicht gefunden."
  echo "Bitte installiere Python von https://www.python.org/downloads/"
  read -k 1 "?Druecke eine Taste zum Schliessen..."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Erstelle lokale Python-Umgebung..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installiere/aktualisiere benoetigte Pakete..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo ""
echo "Wenn gleich ein Browserfenster aufgeht, ist alles richtig."
echo "Falls nicht, oeffne: http://localhost:8501"
echo ""

python -m streamlit run app.py
