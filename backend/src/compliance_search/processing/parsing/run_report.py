"""Console output for a run of main.py.

Only for reading the run: nothing here changes what the parser produces.
"""
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from compliance_search.processing.sections import SectionLine, TextFragment

INDENT = " " * 8  # lines below a document line start under its id
SECTIONS_PER_ROW = 5


@dataclass
class RunStats:
    """What the summary at the end of the run needs."""

    total: int  # number of PDFs in the run
    start: float = field(default_factory=time.perf_counter)
    failed: list[str] = field(default_factory=list)  # document ids


def print_start(pdf_files: list[Path], source_folder: Path, output_folder: Path, root: Path) -> None:
    """Print how many PDFs are parsed and from where to where (paths relative to root)."""
    print(f"Parsing {len(pdf_files)} PDFs")
    print(f"  from: {source_folder.relative_to(root)}")
    print(f"  to:   {output_folder.relative_to(root)}\n")


def print_document(
    run: RunStats,
    number: int,
    document_id: str,
    fragments: list[TextFragment],
    lines: list[SectionLine],
    start: float,
) -> None:
    """Print one line with the counts and time for a document, then its section counts."""
    # parse_pdf does not return the page count, so take the highest page with text
    pages = max((fragment.page_number for fragment in fragments), default=0)
    seconds = time.perf_counter() - start
    print(
        f"{_progress(run, number)} {document_id}  {pages} pages · {len(fragments):,} fragments"
        f" · {len(lines):,} lines  ({seconds:.1f} s)"
    )
    _print_section_counts(lines)


def print_failure(run: RunStats, number: int, document_id: str, exc: Exception) -> None:
    """Print why a document failed and remember it for the summary."""
    run.failed.append(document_id)
    print(f"{_progress(run, number)} {document_id}  FAILED: {type(exc).__name__}: {exc}")


def print_summary(run: RunStats) -> None:
    """Print the total time and how many documents worked or failed."""
    seconds = time.perf_counter() - run.start
    succeeded = run.total - len(run.failed)
    print(f"\nDone in {seconds:.1f} s: {succeeded} ok, {len(run.failed)} failed")
    if run.failed:
        print(f"  failed: {', '.join(run.failed)}")


def _progress(run: RunStats, number: int) -> str:
    """Return e.g. "[ 7/13]", padded so all progress markers line up."""
    width = len(str(run.total))
    return f"[{number:>{width}}/{run.total}]"


def _print_section_counts(lines: list[SectionLine]) -> None:
    """Print how many lines each section got, largest first, and warn about unassigned lines."""
    counts = Counter(line.section_type for line in lines)
    unassigned = counts.pop("", 0)

    entries = [f"{section} {count}" for section, count in counts.most_common()]
    for row_start in range(0, len(entries), SECTIONS_PER_ROW):
        print(INDENT + " · ".join(entries[row_start:row_start + SECTIONS_PER_ROW]))

    if unassigned:
        print(f"{INDENT}⚠ {unassigned} lines without a section")
