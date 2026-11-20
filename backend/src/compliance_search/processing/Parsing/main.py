from pathlib import Path

from compliance_search.processing.Parsing.build_lines import build_lines
from compliance_search.processing.Parsing.parse_pdf import parse_pdf
from compliance_search.processing.Parsing.save_json import save_jsonl
from compliance_search.processing.Parsing.section_detection import detect_sections

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

def main() -> None:

    pdf_files = sorted(
        SOURCE_FOLDER.rglob("*.pdf")
    )

    for pdf_path in pdf_files:
        document_id = pdf_path.stem #take name from the front of file name
        print(f"\nProcessing {document_id}")
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

            print(f"Finished {document_id}")

        except Exception as exc:
            print(f"Failed {document_id}: {exc}")

if __name__ == "__main__":
    main()
    