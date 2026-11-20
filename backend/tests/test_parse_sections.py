"""Tests für den Section-Parser (DEL-11).

Der Parser liest ein PDF und liefert Section- und SectionLine-Objekte
(siehe compliance_search/processing/sections.py).

Die PDFs kommen aus setup/downloads/ (nicht im Git). Fehlen sie, werden die
Tests übersprungen. Herunterladen mit: setup/download_all_pdfs.py
"""
import functools
from pathlib import Path

import pytest

from compliance_search.processing.Parsing.parse_sections import parse_sections
from compliance_search.processing.Parsing.save_json import save_jsonl
from compliance_search.processing.sections import Section, SectionLine

DOWNLOADS = Path(__file__).resolve().parents[2] / "setup" / "downloads"

# Erwartete Reihenfolge der Sections (ohne footnotes), laut
# docs/analysis/doc-type-structure/doc_type_analysis.md
BASE = ["header", "citations", "recitals", "enacting_formula", "enacting_terms", "final_formula"]
EXPECTED_TYPES = {
    "32025R0532_DE": BASE,                  # delegated_regulation, deutsch
    "32025R0532_EN": BASE,                  # dasselbe auf Englisch
    "32025R0302_EN": BASE + ["annex"] * 4,  # implementing_regulation mit Anhängen I–IV
    "32022R2554_DE": BASE,                  # regulation (DORA)
}

SAMPLE = "32025R0532_DE"  # Beispieldokument


@functools.cache
def parsed(document_id):
    """Parst ein PDF (jedes nur einmal) und gibt (sections, lines) zurück."""
    pdf = DOWNLOADS / f"{document_id}.pdf"
    if not pdf.exists():
        pytest.skip(f"{pdf.name} fehlt, erst setup/download_all_pdfs.py ausführen")
    return parse_sections(str(pdf), document_id)


def section(document_id, section_type):
    """Die erste Section eines Typs."""
    sections, _ = parsed(document_id)
    return next(s for s in sections if s.section_type == section_type)


def line(document_id, text):
    """Die Zeile mit genau diesem Text."""
    _, lines = parsed(document_id)
    return next(l for l in lines if l.text == text)


# 1. Werden die richtigen Sections in der richtigen Reihenfolge erkannt?
@pytest.mark.parametrize("document_id", EXPECTED_TYPES)
def test_section_order(document_id):
    sections, _ = parsed(document_id)
    types = [s.section_type for s in sections if s.section_type != "footnotes"]

    assert types == EXPECTED_TYPES[document_id]


# 2. Beginnt jede Section mit der Phrase aus der Analyse?
def test_headings():
    assert section(SAMPLE, "citations").heading.startswith("DIE EUROPÄISCHE KOMMISSION")
    assert section(SAMPLE, "recitals").heading == "in Erwägung nachstehender Gründe:"
    assert section(SAMPLE, "enacting_formula").heading == "HAT FOLGENDE VERORDNUNG ERLASSEN:"
    assert section(SAMPLE, "enacting_terms").heading == "Artikel 1"
    assert section(SAMPLE, "final_formula").heading.startswith("Brüssel, den")


# 3. Gehört jede Zeile zu einer Section, und hat jede Section Zeilen?
def test_lines_belong_to_sections():
    sections, lines = parsed(SAMPLE)
    section_ids = {s.section_id for s in sections}
    used_ids = {l.section_id for l in lines}

    assert used_ids == section_ids


# 4. Sind Kopf- und Fußzeile der Seiten (Amtsblatt, ELI-Link) entfernt?
def test_no_page_header_or_footer():
    _, lines = parsed(SAMPLE)
    texts = [l.text for l in lines]

    assert not any(t.startswith("ABl. L vom") for t in texts)
    assert not any(t.startswith("ELI: http") for t in texts)


# 5. Landen die Fußnoten in eigenen footnotes-Sections (Seite 1 und 3)?
def test_footnotes():
    sections, _ = parsed(SAMPLE)
    footnote_pages = [s.page_start for s in sections if s.section_type == "footnotes"]

    assert 1 in footnote_pages
    assert 3 in footnote_pages


# 6. Stimmen Schriftgröße und Fettdruck einer Zeile?
def test_font_and_bold():
    title = line(SAMPLE, "Gesamtrisikoprofil und Komplexität")  # Titel von Artikel 1

    assert title.page_number == 3
    assert title.bold
    assert title.font_size == pytest.approx(9.6, abs=0.2)


# 7. Kommt beim Speichern und Wiedereinlesen dasselbe heraus?
def test_save_and_load(tmp_path):
    sections, lines = parsed(SAMPLE)

    save_jsonl(sections, lines, tmp_path, SAMPLE)

    sections_file = tmp_path / f"{SAMPLE}.sections.jsonl"
    lines_file = tmp_path / f"{SAMPLE}.lines.jsonl"
    loaded_sections = [Section.model_validate_json(row) for row in sections_file.read_text().splitlines()]
    loaded_lines = [SectionLine.model_validate_json(row) for row in lines_file.read_text().splitlines()]
    assert loaded_sections == sections
    assert loaded_lines == lines
