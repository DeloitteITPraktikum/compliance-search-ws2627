"""Assign an annex number to lines in annex sections."""

import re

from compliance_search.processing.sections import SectionLine

# "ANNEX I", "ANNEX 1", "ANHANG I" or "ANHANG 1", optionally followed by a title.
ANNEX_START = re.compile(r"^(?:ANNEX|ANHANG)\s+([IVXLCDM]+|\d+)\b", re.IGNORECASE)


def detect_annexes(lines: list[SectionLine]) -> list[SectionLine]:
    """Set ``line.annex`` for every line belonging to an annex."""
    current_annex: str | None = None

    for line in lines:
        if line.section_type != "annex":
            continue

        annex_match = ANNEX_START.match(line.text)
        if annex_match:
            current_annex = annex_match.group(1).upper()

        line.annex = current_annex

    return lines
