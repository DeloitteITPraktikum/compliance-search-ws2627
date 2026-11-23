"""Assign an article number to the lines of a delegated regulation (level 3).

Only lines in enacting_terms are looked at, so detect_sections must run first.
All other lines keep the default article = None.

1. A line that is exactly "Article N" / "Artikel N" starts article N.
   That line and every following line get article = "N".
2. A grouping heading (CHAPTER, TITLE, Section and their German forms) ends
   the current article. The heading and its title stay None until the next
   article starts.
3. Footnote lines are skipped, because they are not in enacting_terms.
   They keep None but do not end the article, so an article runs on
   across a page break.

The structure is described in docs/analysis/doc-type-structure/delegated_regulation.md.
"""
import re

from compliance_search.processing.sections import SectionLine

# Headings stand alone on their line, English and German
ARTICLE_HEADING = re.compile(r"^(?:Article|Artikel) (\d+[a-z]?)$")
GROUPING_HEADING = re.compile(
    r"^(?:CHAPTER|KAPITEL|TITLE|TITEL|SECTION|Section|ABSCHNITT|Abschnitt) (?:[IVXLC]+|\d+)$"
)


def detect_articles(lines: list[SectionLine]) -> list[SectionLine]:
    """Set line.article for every line in enacting_terms and return the same lines."""
    current_article: str | None = None

    for line in lines:
        if line.section_type != "enacting_terms":  # also skips footnotes inside an article
            continue

        article_match = ARTICLE_HEADING.match(line.text)
        if article_match:
            current_article = article_match.group(1)
        elif GROUPING_HEADING.match(line.text):
            current_article = None

        line.article = current_article

    return lines
