"""Assign a section_type to every line of a delegated regulation (level 1).

The detectors change the lines in place. Their order matters, so call
detect_sections instead of the single detectors:

1. enacting_formula and final_formula are found by their phrase.
2. enacting_terms lie between them.
3. recitals, citations and header are filled backwards from there, each one
   stops where the section after it begins.
4. footnotes come last, because they overwrite lines inside other sections.

The rules are described in section-detection.md.
"""
import re

from compliance_search.processing.sections import SectionLine

# Start phrases, English and German
ENACTING_FORMULA = re.compile(r"^(HAS ADOPTED THIS REGULATION:|HAT FOLGENDE VERORDNUNG ERLASSEN:)")
# The final formula starts with the binding clause after the last article.
# "Done at Brussels," is the fallback if a document has no binding clause.
FINAL_FORMULA = re.compile(
    r"^(This Regulation shall be binding in its entirety"
    r"|Diese Verordnung ist in allen ihren Teilen verbindlich"
    r"|Done at Brussels,|Brüssel, den)"
)
RECITALS_START = re.compile(r"^(Whereas|in Erwägung nachstehender Gründe:)")
CITATIONS_START = re.compile(r"^(THE EUROPEAN COMMISSION,|DIE EUROPÄISCHE KOMMISSION)")

# Footnotes: small font, a number at the start, in the lower part of the page
FOOTNOTE_MARKER = re.compile(r"^(?:\(\d+\)|\d+)\s*")  # "1" or "(1)"
FOOTNOTE_MAX_FONT_FACTOR = 1.05  # at most 5 % above the smallest font size of the document
FOOTNOTE_MAX_Y = 500


def detect_enacting_formula_lines(lines: list[SectionLine]) -> None:
    """Label the line "HAS ADOPTED THIS REGULATION:" as enacting_formula."""
    for line in lines:
        if ENACTING_FORMULA.match(line.text):
            line.section_type = "enacting_formula"


def detect_final_formula_lines(lines: list[SectionLine]) -> None:
    """Label the binding clause ("This Regulation shall be binding …") and every line after it as final_formula."""
    started = False
    for line in lines:
        if FINAL_FORMULA.match(line.text):
            started = True
        if started:
            line.section_type = "final_formula"


def detect_enacting_terms_lines(lines: list[SectionLine]) -> None:
    """Label every line between enacting_formula and final_formula as enacting_terms."""
    started = False
    for line in lines:
        if line.section_type == "enacting_formula":
            started = True
            continue
        if started and line.section_type != "final_formula":
            line.section_type = "enacting_terms"


def _label_until(lines: list[SectionLine], start: re.Pattern, stop_type: str, label: str) -> None:
    """Label lines from a start phrase on page 1 until the first line of stop_type."""
    started = False
    for line in lines:
        if line.section_type == stop_type:
            break
        if line.page_number == 1 and start.match(line.text):
            started = True
        if started:
            line.section_type = label


def detect_recitals_lines(lines: list[SectionLine]) -> None:
    """Label the recitals: from "Whereas" on page 1 up to the enacting_formula."""
    _label_until(lines, RECITALS_START, stop_type="enacting_formula", label="recitals")


def detect_citations_lines(lines: list[SectionLine]) -> None:
    """Label the citations: from "THE EUROPEAN COMMISSION," on page 1 up to the recitals."""
    _label_until(lines, CITATIONS_START, stop_type="recitals", label="citations")


def detect_header_lines(lines: list[SectionLine]) -> None:
    """Label every line on page 1 before the citations as header.

    No start phrase is needed, because trim_lines has already removed the
    running header. In the old layout "REGULATIONS" thereby belongs to the header.
    """
    for line in lines:
        if line.section_type == "citations" or line.page_number > 1:
            break
        line.section_type = "header"


def detect_footnote_lines(lines: list[SectionLine]) -> None:
    """Label footnotes: the first footnote line and every line after it on the same page.

    A line starts the footnotes of its page if its font is at most 5 % above
    the smallest font size of the document, it begins with a number such as
    "1" or "(1)" and it lies below y = 500.
    """
    smallest_font_size = min(line.font_size for line in lines)
    footnote_page = None  # page on which the footnotes have started

    for line in lines:
        if line.page_number == footnote_page:
            line.section_type = "footnotes"
            continue
        if (
            line.font_size <= smallest_font_size * FOOTNOTE_MAX_FONT_FACTOR
            and FOOTNOTE_MARKER.match(line.text)
            and line.y < FOOTNOTE_MAX_Y
        ):
            line.section_type = "footnotes"
            footnote_page = line.page_number


def detect_sections(lines: list[SectionLine]) -> list[SectionLine]:
    """Run all detectors in the required order and return the same, now labeled lines.

    The lines must be in document order and already trimmed by trim_lines.
    """
    detect_enacting_formula_lines(lines)
    detect_final_formula_lines(lines)
    detect_enacting_terms_lines(lines)
    detect_recitals_lines(lines)
    detect_citations_lines(lines)
    detect_header_lines(lines)
    detect_footnote_lines(lines)
    return lines
