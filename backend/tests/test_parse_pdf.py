from pathlib import Path

from compliance_search.processing.parsing.parse_pdf import parse_pdf

# A short delegated regulation (5 pages)
PDF_PATH = (Path(__file__).resolve().parents[2]
            / "docs" / "analysis" / "unlabled-pdfs" / "32025R0301_EN.pdf")


def test_every_fragment_has_a_positive_font_size():
    fragments = parse_pdf(PDF_PATH)

    assert all(fragment.font_size > 0 for fragment in fragments)


def test_bold_text_is_detected():
    fragments = parse_pdf(PDF_PATH)

    assert any(fragment.bold for fragment in fragments)
