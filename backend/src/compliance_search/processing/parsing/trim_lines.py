"""Remove the running headers and footers of each page before section detection.

The Official Journal repeats a running header at the top of every page and,
in the layout used since 2023, an ELI footer at the bottom. On page 1 the
running header has a longer form ("Official Journal EN" / "of the European
Union L series"), on later pages a short one ("EN OJ L, 20.2.2025"). None of
these lines are part of the act, so every line in the top or bottom zone is
removed.

The removed lines are marked in docs/analysis/labeled-pdfs/delegated_regulation.
"""
from compliance_search.processing.sections import SectionLine

TOP_ZONE_MIN_Y = 770  # running headers sit at y ≈ 783 (page 1: up to ≈ 795), body text ends at ≈ 760
BOTTOM_ZONE_MAX_Y = 35  # the running footer sits at y ≈ 22, footnotes end at ≈ 49


def is_running_header(line: SectionLine) -> bool:
    return line.y > TOP_ZONE_MIN_Y


def is_running_footer(line: SectionLine) -> bool:
    return line.y < BOTTOM_ZONE_MAX_Y


def trim_lines(lines: list[SectionLine]) -> list[SectionLine]:
    """Return the lines without running headers and footers."""
    return [line for line in lines if not (is_running_header(line) or is_running_footer(line))]
