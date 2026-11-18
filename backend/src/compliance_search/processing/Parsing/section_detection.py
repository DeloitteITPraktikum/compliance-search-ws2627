# -*- coding: cp1252 -*-
"""Erkennung und Klassifizierung von Dokumentabschnitten.

Das Modul weist jeder Textzeile anhand ihres Inhalts, ihrer Position und
ihrer Schriftgröße eine ``section_id`` zu. Die Funktionen verändern die
übergebenen Zeilenobjekte direkt und geben anschließend dieselbe Liste zurück.

Die Reihenfolge der Erkennung ist wichtig: Die Einleitungs- und Schlussformel
müssen vor den erlassenden Bestimmungen erkannt werden. Die Fußnoten werden
zuletzt erkannt, weil ihre Erkennung auf der kleinsten Schriftgröße des
Dokuments basiert.

Eine ausführliche Beschreibung der Erkennungsregeln befindet sich in
``section-detection.md``.
"""

import re


def detect_enacting_formula_lines(lines: list) -> list:
    """Markiert die Einleitungsformel einer Verordnung.

    Unterstützt werden die deutsche Formulierung
    ``HAT FOLGENDE VERORDNUNG ERLASSEN:`` und die englische Formulierung
    ``HAS ADOPTED THIS REGULATION:``.

    Args:
        lines: Geordnete Textzeilen mit den Attributen ``text`` und
            ``section_id``.

    Returns:
        Dieselbe Liste von Zeilen mit gesetzter ``section_id``.

    Siehe auch:
        ``section-detection.md``
    """
    for line in lines:
        if re.match(r"^HAT FOLGENDE VERORDNUNG ERLASSEN:", line.text):
            line.section_id = "enacting_formula"
        if re.match(r"^HAS ADOPTED THIS REGULATION:", line.text):
            line.section_id = "enacting_formula"

    return lines

def detect_final_formula_lines(lines: list) -> list:
    """Markiert die Schlussformel und die nachfolgenden Zeilen.

    Die Erkennung beginnt bei ``Brüssel, den`` beziehungsweise
    ``Done at Brussels,``. Die erkannte Startzeile und alle danach folgenden
    Zeilen werden als ``final_formula`` markiert.

    Args:
        lines: Geordnete Textzeilen des Dokuments.

    Returns:
        Dieselbe Liste von Zeilen mit gesetzter ``section_id``.

    Siehe auch:
        ``section-detection.md``
    """
    line_before = False
    for line in lines:
        if line_before:
            line.section_id = "final_formula"
        if re.match(r"^Br.*ssel, den", line.text):
            line.section_id = "final_formula"
            line_before = True
        if re.match(r"^Done at Brussels,", line.text):
            line.section_id = "final_formula"
            line_before = True

    return lines

def detect_enacting_terms_lines(lines: list) -> list:
    """Markiert den verfügenden Teil zwischen den Formeln.

    Die Markierung beginnt nach der erkannten ``enacting_formula`` und endet,
    sobald eine Zeile mit ``final_formula`` erreicht wird. Deshalb muss diese
    Funktion nach ``detect_enacting_formula_lines`` und
    ``detect_final_formula_lines`` aufgerufen werden.

    Args:
        lines: Geordnete Textzeilen des Dokuments.

    Returns:
        Dieselbe Liste von Zeilen mit gesetzter ``section_id``.

    Siehe auch:
        ``section-detection.md``
    """
    beginns = False
    for line in lines :
        if line.section_id == "enacting_formula":
            beginns = True
            continue
        if (beginns and not line.section_id == "final_formula"):
            line.section_id = "enacting_terms"

    return lines


def detect_recitals_lines(lines: list) -> list:
    """Markiert die Erwägungsgründe einer Verordnung.

    Die Erkennung beginnt auf Seite 1 bei ``Whereas`` oder bei der deutschen
    Formulierung ``in Erwägung nachstehender Gründe:`` und läuft bis zur
    ``enacting_formula``.

    Args:
        lines: Geordnete Textzeilen des Dokuments.

    Returns:
        Dieselbe Liste von Zeilen mit gesetzter ``section_id``.

    Siehe auch:
        ``section-detection.md``
    """
    begin_fill = False
    
    for line in lines:
        if (line.section_id == "enacting_formula"):
            break
        
        if (begin_fill):
            line.section_id = "recitals"
        
        if (re.match(r"^Whereas", line.text) and line.page_number == 1):
                line.section_id = "recitals"
                begin_fill = True
        if (re.match(r"^in Erw.*gung nachstehender Gr.*nde:", line.text) and line.page_number == 1):
                line.section_id = "recitals"
                begin_fill = True

    return lines

def detect_citations_lines(lines: list) -> list:
    """Markiert den einleitenden Abschnitt mit den Zitierungen.

    Die Erkennung beginnt auf Seite 1 bei ``THE EUROPEAN COMMISSION,`` oder
    ``DIE EUROPÄISCHE KOMMISSION`` und läuft bis zum Beginn der ``recitals``.

    Args:
        lines: Geordnete Textzeilen des Dokuments.

    Returns:
        Dieselbe Liste von Zeilen mit gesetzter ``section_id``.

    Siehe auch:
        ``section-detection.md``
    """

    begin_fill = False

    for line in lines:
        if (line.section_id == "recitals"):
            break
        
        if (begin_fill):
            line.section_id = "citations"
        
        if (re.match(r"^THE EUROPEAN COMMISSION,", line.text) and line.page_number == 1):
                line.section_id = "citations"
                begin_fill = True
        if (re.match(r"^DIE EUROP.*ISCHE KOMMISSION", line.text) and line.page_number == 1):
                line.section_id = "citations"
                begin_fill = True

    return lines

def detect_header_lines(lines: list) -> list:
    """Markiert den Kopfbereich einer Verordnung.

    Die Erkennung beginnt auf Seite 1 bei ``COMMISSION DELEGATED REGULATION
    (EU)`` oder ``DELEGIERTE VERORDNUNG (EU)`` und läuft bis zum Beginn der
    ``citations``.

    Args:
        lines: Geordnete Textzeilen des Dokuments.

    Returns:
        Dieselbe Liste von Zeilen mit gesetzter ``section_id``.

    Siehe auch:
        ``section-detection.md``
    """

    begin_fill = False

    for line in lines:
        if (line.section_id == "citations"):
            break
        
        if (begin_fill):
            line.section_id = "header"
        
        if (re.match(r"^COMMISSION DELEGATED REGULATION \(EU\)", line.text) and line.page_number == 1):
                line.section_id = "header"
                begin_fill = True
        if (re.match(r"^DELEGIERTE VERORDNUNG \(EU\)", line.text) and line.page_number == 1):
                line.section_id = "header"
                begin_fill = True

    return lines

def detect_footnote_lines(lines: list) -> list:
    """Erkennt Fußnoten anhand von Schriftgröße, Präfix und Position.

    Eine Zeile wird als Fußnote klassifiziert, wenn alle drei Kriterien
    erfüllt sind: Die Schriftgröße liegt höchstens fünf Prozent über der
    kleinsten Dokument-Schriftgröße, der Text beginnt mit einer numerischen
    Markierung wie ``1`` oder ``(1)``, und die vertikale Position ``y`` ist
    kleiner als ``500``. Nach einer erkannten Fußnotenzeile werden weitere
    Zeilen derselben Seite ebenfalls als Fußnoten übernommen.

    Args:
        lines: Textzeilen mit den Attributen ``font_size``, ``text``, ``y``
            und ``page_number``.

    Returns:
        Dieselbe Liste von Zeilen mit gesetzter ``section_id``.

    Raises:
        ValueError: Wenn ``lines`` leer ist und keine minimale Schriftgröße
            ermittelt werden kann.

    Siehe auch:
        ``section-detection.md``
    """

    min_font_size = min(
        line.font_size
        for line in lines
    )
    line_before = False
    line_before_page = 1
    
    for line in lines:
        score = 0

        if (line.page_number == line_before_page and line_before) :
            line.section_id = "footnotes"
            continue

                

        if (
            line.font_size <= min_font_size * 1.05
            ): score  += 1

        if (
            re.match(r"^(?:\(\d+\)|\d+)\s*", line.text)
        ):
            score += 1

        if (
            line.y < 500
        ):
            score += 1

        if score >= 3: 
            line.section_id = "footnotes"
            line_before = True
            line_before_page = line.page_number

            
            
    
    
    
    return lines
def section_detection(lines: list) -> list:
    """Führt die vollständige Abschnittserkennung in definierter Reihenfolge aus.

    Die einzelnen Erkennungsschritte werden für Einleitungsformel,
    Schlussformel, verfügenden Teil, Erwägungsgründe, Zitierungen, Kopfbereich
    und Fußnoten ausgeführt. Die Reihenfolge darf nicht verändert werden.

    Args:
        lines: In Dokumentreihenfolge sortierte Textzeilen. Jede Zeile muss
            mindestens ``text``, ``page_number``, ``font_size``, ``y`` und
            ``section_id`` bereitstellen.

    Returns:
        Dieselbe Liste von Zeilen mit den erkannten ``section_id``-Werten.

    Siehe auch:
        ``section-detection.md``
    """
    step1 = detect_enacting_formula_lines(lines)
    step2 = detect_final_formula_lines(step1)
    step3 = detect_enacting_terms_lines(step2)
    step4 = detect_recitals_lines(step3)
    step5 = detect_citations_lines(step4)
    step6 = detect_header_lines(step5)
    step7 = detect_footnote_lines(step6)
    return step7