import time
from collections import Counter
from pathlib import Path

from compliance_search.processing.Parsing.build_lines import build_lines
from compliance_search.processing.Parsing.parse_pdf import parse_pdf
from compliance_search.processing.Parsing.save_json import save_jsonl
from compliance_search.processing.Parsing.section_detection import detect_sections
from compliance_search.processing.sections import SectionLine

REPOSITORY_ROOT = Path(__file__).resolve().parents[5]

# TODO: Switch this path to data/pdfs/... once DEL-91 is done.
# Until then the parser reads the static PDF folder in docs/analysis.
# Focus for now: only documents of doc_type "delegated_regulation"
# (see docs/analysis/doc-type-structure/delegated_regulation.md).
# The folder holds only those PDFs. Other doc types come later.
SOURCE_FOLDER = (
    REPOSITORY_ROOT
    /"docs"
    / "analysis"
    / "unlabled-pdfs"
)

OUTPUT_FOLDER = (
    REPOSITORY_ROOT
    / "data"
    / "pdfs"
    / "parsed"
)

INDENT = " " * 8  # lines below a document line start under its id
SECTIONS_PER_ROW = 5


def print_section_counts(lines: list[SectionLine]) -> None:
    """Print how many lines each section got, largest first, and warn about unassigned lines."""
    counts = Counter(line.section_id for line in lines)
    unassigned = counts.pop("", 0)

    entries = [f"{section} {count}" for section, count in counts.most_common()]
    for start in range(0, len(entries), SECTIONS_PER_ROW):
        print(INDENT + " · ".join(entries[start:start + SECTIONS_PER_ROW]))

    if unassigned:
        print(f"{INDENT}⚠ {unassigned} lines without a section")


def main() -> None:

    pdf_files = sorted(
        SOURCE_FOLDER.rglob("*.pdf")
    )

    print(f"Parsing {len(pdf_files)} PDFs")
    print(f"  from: {SOURCE_FOLDER.relative_to(REPOSITORY_ROOT)}")
    print(f"  to:   {OUTPUT_FOLDER.relative_to(REPOSITORY_ROOT)}\n")

    total_start = time.perf_counter()
    failed = []
    width = len(str(len(pdf_files)))  # so [ 7/13] and [13/13] line up

    for number, pdf_path in enumerate(pdf_files, start=1):
        document_id = pdf_path.stem #take name from the front of file name
        progress = f"[{number:>{width}}/{len(pdf_files)}]"
        start = time.perf_counter()
        try:
            fragments = parse_pdf(pdf_path) # extract all text fragments
            unlabeled_lines = build_lines(fragments)
            labeled_lines = detect_sections(unlabeled_lines)

            save_jsonl(
                document_id=document_id,
                sections=[],
                lines=labeled_lines,
                output_folder=OUTPUT_FOLDER,
            )

            # parse_pdf does not return the page count, so take the highest page with text
            pages = max((fragment.page_number for fragment in fragments), default=0)
            seconds = time.perf_counter() - start
            print(
                f"{progress} {document_id}  {pages} pages · {len(fragments):,} fragments"
                f" · {len(labeled_lines):,} lines  ({seconds:.1f} s)"
            )
            print_section_counts(labeled_lines)

        except Exception as exc:
            failed.append(document_id)
            print(f"{progress} {document_id}  FAILED: {type(exc).__name__}: {exc}")

    total_seconds = time.perf_counter() - total_start
    succeeded = len(pdf_files) - len(failed)
    print(f"\nDone in {total_seconds:.1f} s: {succeeded} ok, {len(failed)} failed")
    if failed:
        print(f"  failed: {', '.join(failed)}")

if __name__ == "__main__":
    main()
    