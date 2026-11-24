import time
from pathlib import Path

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

REPOSITORY_ROOT = Path(__file__).resolve().parents[5]

# Focus for now: only documents of doc_type "delegated_regulation"
# (see docs/analysis/doc-type-structure/delegated_regulation.md).
# The sync sorts the PDFs into data/pdfs/<status>/<doc_type>/ (DEL-91).
# Other doc types come later.
SOURCE_FOLDER = (
    REPOSITORY_ROOT
    / "data"
    / "pdfs"
    / "active"
    / "delegated_regulation"
)

OUTPUT_FOLDER = (
    REPOSITORY_ROOT
    / "data"
    / "pdfs"
    / "parsed"
)

def main() -> None:

    pdf_files = sorted(
        SOURCE_FOLDER.rglob("*.pdf")
    )
    print_start(pdf_files, SOURCE_FOLDER, OUTPUT_FOLDER, REPOSITORY_ROOT)

    run = RunStats(total=len(pdf_files))
    for number, pdf_path in enumerate(pdf_files, start=1):
        document_id = pdf_path.stem #take name from the front of file name
        start = time.perf_counter()
        try:
            fragments = parse_pdf(pdf_path) # extract all text fragments
            unlabeled_lines = build_lines(fragments)
            trimmed_lines = trim_lines(unlabeled_lines) # drop running headers and footers
            labeled_lines = detect_sections(trimmed_lines)
            labeled_lines = detect_articles(labeled_lines)
            labeled_lines = detect_recitals(labeled_lines)

            save_jsonl(
                document_id=document_id,
                lines=labeled_lines,
                output_folder=OUTPUT_FOLDER,
            )

            print_document(run, number, document_id, fragments, labeled_lines, start)

        except Exception as exc:
            print_failure(run, number, document_id, exc)

    print_summary(run)

if __name__ == "__main__":
    main()
