"""Tests for the text normalization of every block."""
import re

from compliance_search.processing.normalize import normalize_text


def grader_view(text: str) -> str:
    """How the grader compares text (metrics.must_contain_score)."""
    return re.sub(r"\s+", " ", text).lower()


def test_soft_hyphens_are_removed():
    assert normalize_text("Finanz\u00adunternehmen") == "Finanzunternehmen"


def test_word_broken_at_line_end_is_joined():
    assert normalize_text("die Finanz-\nunternehmen melden") == "die Finanzunternehmen melden"


def test_real_hyphen_at_line_end_is_kept():
    assert normalize_text("IKT-\nDienstleister") == "IKT-Dienstleister"


def test_change_markers_are_removed():
    text = "►M1 Institutions shall report ◄ the data ▼B daily."
    assert normalize_text(text) == "Institutions shall report the data daily."


def test_no_break_spaces_become_normal_spaces():
    assert normalize_text("mehr als 100\u00a0000 Kunden") == "mehr als 100 000 Kunden"


def test_whitespace_is_collapsed():
    assert normalize_text("  1.  Financial\n entities\tshall  ") == "1. Financial entities shall"


def test_numbering_is_kept():
    text = "(15) term means x; (16) other term means y;"
    assert normalize_text(text) == text


def test_required_fact_survives_for_the_grader():
    raw = "mehr als 10\u00a0% aller Kun\u00adden oder mehr als 100\u202f000"
    clean = grader_view(normalize_text(raw))
    assert "10 %" in clean
    assert "100 000" in clean
    assert "kunden" in clean