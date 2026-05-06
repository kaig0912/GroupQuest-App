# GroupQuest-App
GroupQuest ist eine Social-Challenge-App: User erstellen Challenges mit Regeln und Dauer, andere nehmen teil und dokumentieren Fortschritt (Check-ins, Fotos, Texte). Fortschritt wird bestätigt (automatisch oder durch Gruppe). Gamification (Punkte, Level, Badges) + Leaderboards + Social Feed sorgen für Motivation, Wettbewerb und Austausch.

## MVP: M1-M3

Diese Version setzt den abgabefaehigen Kern als Streamlit/Python-App um:

- M1 User Management: Registrierung, Login, Logout, Profil bearbeiten
- M2 Challenge System: Challenges erstellen, suchen/filtern, beitreten, Teilnehmende sehen, eigene Challenges bearbeiten/loeschen
- M3 Check-in System: Text-Check-ins, Foto-Uploads, Check-in-Historie, Check-ins anderer bestaetigen

M4 Punkte/Badges, M5 Leaderboards und M6 Social Feed bleiben als naechste Ausbaustufen geplant.

## Ganz einfacher Start auf Mac

1. Den Projektordner `GroupQuest-App` oeffnen.
2. Die Datei `start_groupquest.command` doppelklicken.
3. Falls macOS fragt, ob die Datei ausgefuehrt werden darf: erlauben.
4. Wenn kein Browser automatisch aufgeht, diese Adresse oeffnen: `http://localhost:8501`

Beim ersten Start dauert es etwas, weil Streamlit installiert wird.

Die App erstellt beim Start automatisch eine lokale SQLite-Datenbank in `data/groupquest.db`.
Uploads werden lokal im Ordner `uploads/` gespeichert.

## Start, falls Doppelklick nicht geht

Terminal im Projektordner oeffnen und nacheinander ausfuehren:

```bash
chmod +x start_groupquest.command
./start_groupquest.command
```

## Manueller Start fuer Entwickler

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Tests

```bash
pytest
```

## GitHub-Issue-Abdeckung

Umgesetzt durch den MVP:

- #15 Registrierung
- #24 Login
- #28 Logout
- #27 Profil bearbeiten
- #21 Challenge erstellen
- #22 Challenge beitreten
- #23 Challenges suchen/filtern
- #25 Challenge bearbeiten/loeschen
- #26 Teilnehmer einer Challenge sehen
- #6 Text-Check-in
- #7 Foto-Check-in
- #8 vergangene Check-ins anzeigen
- #19 Check-ins anderer validieren/bestaetigen

Aufraeumen nach Review:

- #18 als Duplikat von #24 markieren/schliessen
- #1 und #2 mit den neueren Challenge-Issues zusammenfuehren oder als Duplikate markieren
- #3 ist bereits geschlossen und dupliziert #6
