# Bewirti

Dieses Tool hilft dir dabei, schnell und unkompliziert einen professionellen Bewirtungsbeleg zu erstellen.
Du kannst folgende Angaben machen:

- Anlass und Datum der Bewirtung
- Die bewirteten Personen
- Betrag, Trinkgeld und Gesamtbetrag
- Ein Foto machen oder ein bereits vorhandenes Belegdokument hochladen
- Der generierte PDF-Beleg enthält außerdem ein Feld für die Unterschrift

Klicke unten auf "Generiere Beleg", um die PDF-Datei zu erstellen und herunterzuladen.

## Gehostete Version

Die gehostete Version findet sich hier: https://bewirti.swokiz.com/

## Setup local

python3 -m venv venv  
source venv/bin/activate  
python3 -m pip install -r requirements.txt

## Development checks

Install dev dependencies first:

python3 -m pip install -r requirements-dev.txt

Run lint:

ruff check .

Run type checks:

mypy app.py receipt_service.py

Run unit tests:

pytest -m "not e2e"

Run e2e tests:

pytest -m e2e

Run coverage report (XML for CI/SonarQube):

pytest -m "not e2e" --cov=. --cov-report=xml --cov-report=term

Detailed testing notes: `docs/testing.md`
