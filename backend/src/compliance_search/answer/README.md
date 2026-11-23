# Backend: Konsolenanfragen

Dieses Dokument beschreibt, wie eine Frage über die Konsole eingegeben und anschließend im Backend weiterverarbeitet wird.

## Voraussetzungen

- Python `>= 3.12`
- `uv`
- ein gültiger `GATEWAY_KEY` für die Embedding-API
- die Abhängigkeiten des Backends

Die Abhängigkeiten können aus dem Verzeichnis `backend` synchronisiert werden:

```powershell
uv sync
```

Der API-Schlüssel wird über eine `.env`-Datei geladen. Im Repository liegt die Datei in der Regel unter:

```text
setup/.env
```

Sie sollte mindestens folgende Variable enthalten:

```text
GATEWAY_KEY=dein_api_schlüssel
```

Die `.env`-Datei enthält vertrauliche Zugangsdaten und darf nicht committed werden.

## Anfrage aus der Konsole starten

Aus dem Verzeichnis `backend` kann der Konsolenablauf mit folgendem Befehl gestartet werden:

```powershell
uv run --env-file "../setup/.env" python -m compliance_search.answer.firstanswer
```

Falls die relative Pfadangabe in der lokalen Umgebung nicht funktioniert, kann ein absoluter Pfad verwendet werden:

```powershell
uv run --env-file "C:/Users/<Benutzername>/source/repos/<Repository>/setup/.env" python -m compliance_search.answer.firstanswer
```

Danach fragt das Programm zunächst nach der Sprache:

```text
Select language [DE/EN]:
```

Anschließend wird abhängig von der Auswahl die Frage abgefragt:

```text
Bitte stellen Sie Ihre Frage:
```

oder:

```text
Please enter your question:
```

Ein Beispiel:

```text
Select language [DE/EN]: DE
Bitte stellen Sie Ihre Frage: Welche Anforderungen gelten für TLPT?
```

## Ablauf der Verarbeitung

Die Verarbeitung besteht aktuell aus folgenden Schritten:

1. `retrieve_question()` in `question/question_retrieval.py` liest Sprache und Frage aus der Konsole.
2. Die Eingabe wird bereinigt. Ein abschließendes Fragezeichen wird entfernt.
3. Die Frage wird als `AskRequest` aus `models.py` zurückgegeben. Dadurch wird die Frage als nichtleerer String validiert.
4. `answer_from_terminal()` in `answer/firstanswer.py` übernimmt die Frage aus dem `AskRequest`.
5. `answer_question(question)` erstellt einen Embedding-Client.
6. `createEmbedding(...)` sendet die Frage an die Embedding-API.
7. Die API liefert einen Vektor mit 1024 Gleitkommawerten zurück.
8. Der Vektor wird aktuell in einem `AskResponse` ausgegeben.

Vereinfacht sieht der Ablauf so aus:

```text
Konsole
  -> retrieve_question()
  -> (Sprache, AskRequest)
  -> answer_from_terminal()
  -> answer_question(request.question)
  -> createEmbedding(...)
  -> AskResponse
```

## Rückgabewerte

`retrieve_question()` liefert ein Tupel zurück:

```python
language, request = retrieve_question()
```

Dabei gilt:

```python
language        # "DE" oder "EN"
request.question  # eigentliche Frage als String
```

Das Ergebnis von `answer_from_terminal()` ist ebenfalls ein Tupel:

```python
language, response = answer_from_terminal()
```

`response` ist ein `AskResponse` mit diesen Feldern:

```python
response.answer       # Text mit dem erzeugten Embedding
response.citations    # aktuell noch Beispielzitat
response.retrieved    # aktuell noch Beispielpassage
```

Die aktuelle Ausgabe enthält den Embedding-Vektor und dessen Dimension:

```text
Answer: Embedding für die Frage wurde erstellt und lautet [0.0123, -0.0841, ...] (1024 Dimensionen).
```

## Weiterverarbeitung in Python

Die Terminal-Abfrage kann auch aus einem anderen Python-Modul verwendet werden:

```python
from compliance_search.answer.firstanswer import answer_from_terminal

language, response = answer_from_terminal()

print(language)
print(response.answer)
```

Wenn die Frage bereits vorliegt, kann die Terminal-Abfrage übersprungen werden:

```python
from compliance_search.answer.firstanswer import answer_question

response = answer_question("Welche Anforderungen gelten für TLPT?")
print(response.answer)
```

Das ist insbesondere für die spätere API-Anbindung wichtig. Die Funktion `answer_question()` verwendet kein `input()`, sondern erhält die Frage als Parameter. Dadurch kann sie sowohl von einer Konsolenoberfläche als auch von einem HTTP-Endpunkt verwendet werden.

## Aktueller Entwicklungsstand

Der aktuelle Ablauf erzeugt und zeigt nur das Embedding der Frage. Eine echte Antwortgenerierung aus Dokumentpassagen ist noch nicht angeschlossen.

Die Werte `citations` und `retrieved` in `firstanswer.py` enthalten derzeit Beispielwerte. Für die vollständige Verarbeitung müssen später noch folgende Schritte ergänzt werden:

1. relevante Dokumentpassagen anhand des Frage-Embeddings suchen,
2. die gefundenen Passagen an die Antwortgenerierung übergeben,
3. die generierte Antwort mit den tatsächlichen Quellen in `AskResponse` eintragen.

Die FastAPI-Anwendung verwendet derzeit noch den Platzhalter in `answer/placeholder.py`. Soll die API ebenfalls den Embedding-Ablauf verwenden, muss der Import in `api/app.py` auf `firstanswer` geändert werden:

```python
from compliance_search.answer.firstanswer import answer_question
```
