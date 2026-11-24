"""Group the parsed lines of a regulation into units: articles, recitals and annexes.

detect_articles, detect_recitals and detect_annexes must have run, so every
line knows its article, recital or annex number.

1. Consecutive lines with the same article number form one article,
   consecutive lines with the same recital number form one recital,
   consecutive lines with the same annex number form one annex.
   Footnotes are skipped, so a unit runs on across a page break.
2. The "Article N" and "ANNEX N" lines are not part of the text. The bold
   lines right after them are the article or annex title.
3. The leading "(N)" of a recital is not part of the text.
4. So that every article knows the TITLE, CHAPTER and Section it belongs to,
   a grouping heading and the bold lines after it are remembered and given to
   every following article. A new TITLE clears the chapter and section, a new
   CHAPTER clears the section.
5. Lines are joined with a space. A line ending in "-" before a lowercase word
   is joined without one ("third-" + "party" = "third-party"), except before
   "und", "oder", "and", "or" ("Audit- und Aufsicht").

Example (input lines, simplified):

    CHAPTER I              (heading, no article)
    General provisions     (bold)
    Article 1              (article=1)
    Subject matter         (bold, article=1)
    This Regulation lays   (article=1)
    down third-            (article=1)
    [footnote]             (skipped)
    party rules.           (article=1, next page)

Result: a unit "article 1" with headings ["CHAPTER I General provisions"],
title "Subject matter" and text "This Regulation lays down third-party rules.".
"""
from dataclasses import dataclass, field
from typing import Literal

from compliance_search.processing.parsing.annex_detection import ANNEX_START
from compliance_search.processing.parsing.article_detection import ARTICLE_HEADING, GROUPING_HEADING
from compliance_search.processing.parsing.recital_detection import RECITAL_START
from compliance_search.processing.sections import SectionLine

# Level of a grouping heading, outermost first
HEADING_LEVEL = {
    "TITLE": 0, "TITEL": 0,
    "CHAPTER": 1, "KAPITEL": 1,
    "SECTION": 2, "ABSCHNITT": 2,
}
# A hyphen before these words stays a hyphen with a space ("Audit- und Aufsicht")
WORDS_AFTER_OPEN_HYPHEN = {"und", "oder", "and", "or"}


@dataclass
class Unit:
    unit_type: Literal["article", "recital", "annex"]
    number: str
    headings: list[str]  # one entry per heading level above the article, outermost first, e.g. ["TITLE II …", "CHAPTER I …"]; empty for recitals and annexes
    title_lines: list[str] = field(default_factory=list)  # raw bold lines after "Article N" or "ANNEX N", joined by .title; empty for recitals
    text_lines: list[str] = field(default_factory=list)  # raw content lines (without "Article N", "ANNEX N" and "(N)"), joined by .text
    pages: list[int] = field(default_factory=list)

    @property
    def title(self) -> str | None:
        return join_lines(self.title_lines) or None

    @property
    def text(self) -> str:
        return join_lines(self.text_lines)


def join_lines(texts: list[str]) -> str:
    """Join line texts into one string, following rule 5."""
    joined = ""
    for text in texts:
        text = text.strip()
        if not text:
            continue
        first_word = text.split()[0]
        if not joined:
            joined = text
        elif joined.endswith("-") and first_word[0].islower() and first_word not in WORDS_AFTER_OPEN_HYPHEN:
            joined += text
        else:
            joined += " " + text
    return joined


def group_units(lines: list[SectionLine]) -> list[Unit]:
    """Return the articles, recitals and annexes of one document in reading order."""
    units: list[Unit] = []
    headings: list[list[str]] = [[], [], []]  # lines of the current title, chapter, section heading
    open_heading: int | None = None  # level whose bold title lines are still being collected
    unit: Unit | None = None
    in_title = False  # True while the bold title lines after "Article N" are read

    for line in lines:
        text = line.text.strip()

        if line.section_type == "enacting_terms" and line.article is None:
            grouping_match = GROUPING_HEADING.match(text)
            if grouping_match:
                open_heading = HEADING_LEVEL[text.split()[0].upper()]
                headings[open_heading] = [text]
                for lower in range(open_heading + 1, len(headings)):
                    headings[lower] = []
            elif open_heading is not None and line.bold:
                headings[open_heading].append(text)
            unit = None
            continue

        if line.section_type == "enacting_terms":
            unit_type, number = "article", line.article
        elif line.section_type == "recitals" and line.recital is not None:
            unit_type, number = "recital", line.recital
        elif line.section_type == "annex" and line.annex is not None:
            unit_type, number = "annex", line.annex
        else:  # footnotes, introduction line before recital 1, other sections
            continue

        open_heading = None
        if unit is None or (unit.unit_type, unit.number) != (unit_type, number):
            current_headings = [join_lines(h) for h in headings if h] if unit_type == "article" else []
            unit = Unit(unit_type=unit_type, number=number, headings=current_headings)
            units.append(unit)
            in_title = False

        unit.pages.append(line.page_number)

        if (unit_type == "article" and ARTICLE_HEADING.match(text)
                or unit_type == "annex" and ANNEX_START.match(text)):
            in_title = True
            continue
        if in_title and line.bold:
            unit.title_lines.append(text)
            continue
        in_title = False

        if unit_type == "recital" and not unit.text_lines:
            text = RECITAL_START.sub("", text).strip()
        unit.text_lines.append(text)

    return units
