# Abschnittserkennung

Die Abschnittserkennung klassifiziert die extrahierten Textzeilen eines Dokuments. Dazu werden Textmuster, Seitennummern und Layoutinformationen wie Schriftgröße und vertikale Position ausgewertet.

Die Implementierung befindet sich in [`section_detection.py`](section_detection.py).

## Erkannte Abschnittstypen

Die Erkennung verwendet folgende Werte für `line.section_type`:

| Wert | Bedeutung |
|---|---|
| `header` | Kopfbereich bzw. Titel der Verordnung |
| `citations` | Einleitung mit der zuständigen Institution |
| `recitals` | Erwägungsgründe |
| `enacting_formula` | Einleitungsformel vor den verfügenden Bestimmungen |
| `enacting_terms` | Verfügender bzw. erlassender Teil der Verordnung |
| `final_formula` | Schlussformel einschließlich der folgenden Zeilen |
| `footnotes` | Fußnoten und deren Folgezeilen auf derselben Seite |

## Voraussetzungen für die Eingabe

Die Funktion erwartet eine geordnete Liste von Zeilenobjekten. Jede Zeile muss mindestens über folgende Attribute verfügen:

- `text`: Textinhalt der Zeile
- `page_number`: Seitennummer, beginnend bei 1
- `font_size`: erkannte Schriftgröße
- `y`: vertikale Position der Zeile
- `section_type`: beschreibbares Feld für das Erkennungsergebnis

Die Zeilen müssen in Dokumentreihenfolge vorliegen. Die Funktionen setzen `section_type` direkt am bestehenden Zeilenobjekt. Die Objekte werden also verändert; es wird keine unabhängige Kopie erzeugt.

## Verarbeitungsreihenfolge

`detect_sections(lines)` führt die Erkennung in dieser Reihenfolge aus:

1. `detect_enacting_formula_lines`
2. `detect_final_formula_lines`
3. `detect_enacting_terms_lines`
4. `detect_recitals_lines`
5. `detect_citations_lines`
6. `detect_header_lines`
7. `detect_footnote_lines`

Die Reihenfolge ist fachlich relevant. Die Erkennung der Einleitungs- und Schlussformel muss vor den verfügenden Bestimmungen erfolgen, weil die Grenzen von `enacting_terms` anhand dieser Markierungen bestimmt werden. Fußnoten werden zuletzt erkannt, da ihre Erkennung die kleinste Schriftgröße des gesamten Dokuments verwendet und bereits gesetzte Abschnittsmarkierungen überschreiben kann.

## Erkennungsregeln

### Einleitungsformel

Die deutsche Formel beginnt mit:

- `HAT FOLGENDE VERORDNUNG ERLASSEN:`

Die englische Formel beginnt mit:

- `HAS ADOPTED THIS REGULATION:`

Nach der Erkennung wird die jeweilige Zeile als `enacting_formula` markiert.

### Schlussformel

Die Erkennung beginnt bei einer Zeile, die mit einer der folgenden Formulierungen beginnt:

- `Brüssel, den` beziehungsweise die entsprechende erkannte Zeichenfolge
- `Done at Brussels,`

Die Startzeile und alle danach folgenden Zeilen werden als `final_formula` markiert.

### Verfügende Bestimmungen

Sobald eine `enacting_formula` erkannt wurde, werden die nachfolgenden Zeilen als `enacting_terms` markiert. Die Erkennung endet, sobald eine Zeile bereits als `final_formula` markiert ist.

### Erwägungsgründe

Die Erkennung startet auf Seite 1 bei einer Zeile, die mit einer der folgenden Formulierungen beginnt:

- `Whereas`
- `in Erwägung nachstehender Gründe:`

Ab dieser Zeile werden die Zeilen bis zur `enacting_formula` als `recitals` markiert.

### Zitierungen

Die Erkennung startet auf Seite 1 bei einer Zeile, die mit einer der folgenden Formulierungen beginnt:

- `THE EUROPEAN COMMISSION,`
- `DIE EUROPÄISCHE KOMMISSION`

Die Zeilen werden bis zum Beginn der `recitals` als `citations` markiert.

### Kopfbereich

Die Erkennung startet auf Seite 1 bei einer Zeile, die mit einer der folgenden Formulierungen beginnt:

- `COMMISSION DELEGATED REGULATION (EU)`
- `DELEGIERTE VERORDNUNG (EU)`

Die Zeilen werden bis zum Beginn der `citations` als `header` markiert.

### Fußnoten

Für jedes Dokument wird zunächst die kleinste vorkommende Schriftgröße ermittelt. Eine Zeile wird als Fußnote erkannt, wenn alle drei folgenden Kriterien erfüllt sind:

1. `font_size` ist höchstens fünf Prozent größer als die kleinste Schriftgröße.
2. Der Text beginnt mit einer numerischen Markierung wie `1` oder `(1)`.
3. `y` ist kleiner als `500`.

Nach einer erkannten Fußnotenzeile werden weitere Zeilen derselben Seite ebenfalls als `footnotes` markiert. Beim Wechsel auf eine neue Seite wird die normale Erkennung erneut angewendet.

## Rückgabewert und Seiteneffekte

Alle Erkennungsfunktionen geben dieselbe übergebene Liste zurück. Zusätzlich verändern sie die `section_type`-Eigenschaft der enthaltenen Zeilen direkt. Bereits gesetzte Werte können durch nachfolgende Erkennungsschritte überschrieben werden.

Bei einer leeren Liste kann keine minimale Schriftgröße ermittelt werden. Die Fußnotenerkennung löst in diesem Fall einen `ValueError` aus.

## Beispielablauf

```python
lines = detect_sections(lines)

for line in lines:
	print(line.section_type, line.text)
```

Die Abschnittskennung ist anschließend an jeder Zeile verfügbar und kann für die weitere Verarbeitung, beispielsweise die Bildung von Sektionen oder Chunks, verwendet werden.
