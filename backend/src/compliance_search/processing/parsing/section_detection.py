"""Assign a section_type to every line of a document (level 1).

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
from dataclasses import dataclass

from compliance_search.processing.document_types import DocumentType
from compliance_search.processing.sections import SectionLine


@dataclass(frozen=True)
class SectionRules:
    """Text patterns used to detect level-one sections of a document type."""

    enacting_formula: re.Pattern[str]
    final_formula: re.Pattern[str]
    recitals_start: re.Pattern[str]
    citations_start: re.Pattern[str]


SECTION_RULES: dict[DocumentType, SectionRules] = {
    "delegated_regulation": SectionRules(
        enacting_formula=re.compile(
            r"^(HAS ADOPTED THIS REGULATION:|HAT FOLGENDE VERORDNUNG ERLASSEN:)"
        ),
        final_formula=re.compile(
            r"^(This Regulation shall be binding in its entirety"
            r"|Diese Verordnung ist in allen ihren Teilen verbindlich)"
        ),
        recitals_start=re.compile(r"^(Whereas|in Erwägung nachstehender Gründe:)"),
        citations_start=re.compile(
            r"^(THE EUROPEAN COMMISSION,|DIE EUROPÄISCHE KOMMISSION)"
        ),
    ),
    "regulation": SectionRules(
        enacting_formula=re.compile(
            r"^(HAVE ADOPTED THIS REGULATION:|HABEN FOLGENDE VERORDNUNG ERLASSEN:)"
        ),
        # The final formula starts with the binding clause. "Done at …" only
        # follows it, so it is no start phrase. DORA (DE) writes "in allen
        # Teilen", without "ihren".
        final_formula=re.compile(
            r"^(This Regulation shall be binding in its entirety"
            r"|Diese Verordnung ist in allen (?:ihren )?Teilen verbindlich)"
        ),
        recitals_start=re.compile(r"^(Whereas|in Erwägung nachstehender Gründe:)"),
        citations_start=re.compile(
            r"^(THE EUROPEAN PARLIAMENT AND THE COUNCIL OF THE EUROPEAN UNION,|"
            r"DAS EUROPÄISCHE PARLAMENT UND DER RAT DER EUROPÄISCHEN UNION)"
        ),
    ),
}

# Annexes start after the final formula in some regulations.
ANNEX_START = re.compile(r"^(?:ANNEX|ANHANG) (?:[IVXLC]+|\d+)\b")

# Footnotes: small font, a number at the start, in the lower part of the page
FOOTNOTE_MARKER = re.compile(r"^(?:\(\d+\)|\d+)\s*")  # "1" or "(1)"
FOOTNOTE_MAX_FONT_FACTOR = 1.05  # at most 5 % above the smallest font size of the document
FOOTNOTE_MAX_Y = 500


def detect_enacting_formula_lines(
    lines: list[SectionLine],
    pattern: re.Pattern[str],
) -> None:
    """Label the document's enacting formula."""
    for line in lines:
        if pattern.match(line.text):
            line.section_type = "enacting_formula"


def detect_final_formula_lines(
    lines: list[SectionLine],
    pattern: re.Pattern[str],
) -> None:
    """Label the final formula and every following line as final_formula."""
    started = False
    for line in lines:
        if pattern.match(line.text):
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


def detect_recitals_lines(
    lines: list[SectionLine],
    pattern: re.Pattern[str],
) -> None:
    """Label the recitals from their start up to the enacting formula."""
    _label_until(lines, pattern, stop_type="enacting_formula", label="recitals")


def detect_citations_lines(
    lines: list[SectionLine],
    pattern: re.Pattern[str],
) -> None:
    """Label the citations from their start up to the recitals."""
    _label_until(lines, pattern, stop_type="recitals", label="citations")


def detect_header_lines(lines: list[SectionLine]) -> None:
    """Label every line on page 1 before the citations as header.

    No start phrase is needed, because trim_lines has already removed the
    running header. In the old layout "REGULATIONS" thereby belongs to the header.
    """
    for line in lines:
        if line.section_type == "citations" or line.page_number > 1:
            break
        line.section_type = "header"


def detect_annex_lines(lines: list[SectionLine]) -> None:
    """Label annexes from their first heading until the end of the document."""
    started = False
    for line in lines:
        if ANNEX_START.match(line.text):
            started = True
        if started:
            line.section_type = "annex"


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


def detect_sections(
    lines: list[SectionLine],
    document_type: DocumentType = "delegated_regulation",
) -> list[SectionLine]:
    """Run all detectors in the required order and return the same, now labeled lines.

    The lines must be in document order and already trimmed by trim_lines.
    """
    rules = SECTION_RULES[document_type]

    detect_enacting_formula_lines(lines, rules.enacting_formula)
    detect_final_formula_lines(lines, rules.final_formula)
    detect_enacting_terms_lines(lines)
    detect_recitals_lines(lines, rules.recitals_start)
    detect_citations_lines(lines, rules.citations_start)
    detect_header_lines(lines)
    detect_annex_lines(lines)
    detect_footnote_lines(lines)
    return lines
