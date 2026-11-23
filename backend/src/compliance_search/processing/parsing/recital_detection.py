"""Assign a recital number to the lines of a delegated regulation.

Only lines in recitals are looked at, so detect_sections must run first.
All other lines keep the default recital = None.

1. A line that starts with "(N)" starts recital N.
   That line and every following line get recital = "N".
2. The introduction line before recital 1 ("Whereas:" /
   "in Erwägung nachstehender Gründe:") stays None.
3. Footnote lines are skipped, because they are not in recitals.
   They keep None but do not end the recital, so a recital runs on
   across a page break.

The structure is described in docs/analysis/doc-type-structure/delegated_regulation.md.
"""
import re

from compliance_search.processing.sections import SectionLine

# "(12) The ..." or a line that is only "(12)", the same in English and German
RECITAL_START = re.compile(r"^\((\d+)\)(?:\s|$)")


def detect_recitals(lines: list[SectionLine]) -> list[SectionLine]:
    """Set line.recital for every line in recitals and return the same lines."""
    current_recital: str | None = None

    for line in lines:
        if line.section_type != "recitals":
            continue

        recital_match = RECITAL_START.match(line.text)
        if recital_match:
            current_recital = recital_match.group(1)

        line.recital = current_recital

    return lines
