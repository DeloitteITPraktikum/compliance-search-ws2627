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

REPOSITORY_ROOT = Path(__file__).resolve().parents[5]

# TODO: Switch this path to data/pdfs/... once DEL-91 is done.
# Until then the parser reads the static PDF folder in docs/analysis.
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
METADATA_FOLDER = REPOSITORY_ROOT / "data" / "metadata"  # one <document_id>.json per document

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
            document_type = get_document_type(document_id, METADATA_FOLDER)
            fragments = parse_pdf(pdf_path) # extract all text fragments
            unlabeled_lines = build_lines(fragments)
            trimmed_lines = trim_lines(unlabeled_lines) # drop running headers and footers
            labeled_lines = detect_sections(trimmed_lines, document_type=document_type)
            labeled_lines = detect_annexes(labeled_lines)
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
