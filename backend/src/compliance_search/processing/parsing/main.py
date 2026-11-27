import time
from pathlib import Path

from compliance_search.processing.document_types import get_document_type
from compliance_search.processing.parsing.annex_detection import detect_annexes
from compliance_search.processing.parsing.article_detection import detect_articles
from compliance_search.processing.parsing.build_lines import build_lines
from compliance_search.processing.parsing.parse_pdf import parse_pdf
from compliance_search.processing.parsing.recital_detection import detect_recitals
from compliance_search.processing.parsing.save_json import save_jsonl
from compliance_search.processing.parsing.run_report import (
    RunStats,
    print_document,
    print_failure,
    print_start,
    print_summary,
)
from compliance_search.processing.parsing.section_detection import detect_sections
from compliance_search.processing.parsing.trim_lines import trim_lines
from compliance_search.processing.sections import SectionLine

REPOSITORY_ROOT = Path(__file__).resolve().parents[5]

# The sync sorts the PDFs into data/pdfs/<status>/<doc_type>/ (DEL-91).
# Parse only the doc types that section_detection has rules for.
# Other doc types come later.
SOURCE_ROOT = REPOSITORY_ROOT / "data" / "pdfs" / "active"
SOURCE_DOC_TYPES = ["delegated_regulation", "regulation"]

OUTPUT_FOLDER = (
    REPOSITORY_ROOT
    / "data"
    / "pdfs"
    / "parsed"
)
METADATA_FOLDER = REPOSITORY_ROOT / "data" / "metadata"  # one <document_id>.json per document

# Every regulation and delegated regulation has these sections. If a start
# phrase is not found, its section is missing and the document must fail.
REQUIRED_SECTIONS = ["citations", "recitals", "enacting_formula", "enacting_terms", "final_formula"]


def check_lines(lines: list[SectionLine]) -> None:
    """Raise a ValueError if a required section or every article is missing."""
    found = {line.section_type for line in lines}
    missing = [section for section in REQUIRED_SECTIONS if section not in found]
    if missing:
        raise ValueError(f"sections not found: {', '.join(missing)}")
    if not any(line.article for line in lines):
        raise ValueError("no articles found")


def main() -> None:

    pdf_files = sorted(
        pdf_path
        for doc_type in SOURCE_DOC_TYPES
        for pdf_path in (SOURCE_ROOT / doc_type).rglob("*.pdf")
    )
    print_start(pdf_files, SOURCE_ROOT, OUTPUT_FOLDER, REPOSITORY_ROOT)

    run = RunStats(total=len(pdf_files))
    for number, pdf_path in enumerate(pdf_files, start=1):
        document_id = pdf_path.stem #take name from the front of file name
        start = time.perf_counter()
        try:
            document_type = get_document_type(document_id, METADATA_FOLDER)
            fragments = parse_pdf(pdf_path) # extract all text fragments
            unlabeled_lines = build_lines(fragments)
            trimmed_lines = trim_lines(unlabeled_lines) # drop running headers and footers
            labeled_lines = detect_sections(trimmed_lines, document_type=document_type)
            labeled_lines = detect_annexes(labeled_lines)
            labeled_lines = detect_articles(labeled_lines)
            labeled_lines = detect_recitals(labeled_lines)
            check_lines(labeled_lines)

            save_jsonl(
                document_id=document_id,
                lines=labeled_lines,
                output_folder=OUTPUT_FOLDER,
            )

            print_document(run, number, document_id, fragments, labeled_lines, start)

        except Exception as exc:
            print_failure(run, number, document_id, exc)
            # Delete the output of an earlier run, so chunking does not use stale lines
            (OUTPUT_FOLDER / f"{document_id}LinesParsed.jsonl").unlink(missing_ok=True)

    print_summary(run)

if __name__ == "__main__":
    main()
