from pathlib import Path

from compliance_search.processing.Parsing import (
    build_lines,
    parse_pdf,
    save_json,
    section_detection,
)
from compliance_search.processing import sections


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
print(REPOSITORY_ROOT)

SOURCE_FOLDER = (
    REPOSITORY_ROOT
    /"docs"
    / "analysis"
    / "unlabled-pdfs"
)
print(SOURCE_FOLDER)
print(f"Exists: {SOURCE_FOLDER.exists()}")

OUTPUT_FOLDER = (
    Path(__file__).resolve().parent
    / "ParsedDocuments"
)



def main() -> None:

    pdf_files = sorted(
        SOURCE_FOLDER.glob("*")
    )
    print(len(pdf_files))

    

    for pdf_file in pdf_files:

        document_id = pdf_file.stem

        print(f"\nProcessing {document_id}")

        try:
            document_parsed = parse_pdf.parse_pdf(pdf_file)

            lines = build_lines.build_lines(
                document_parsed["fragments"],
                document_id,
            )

            
            step7 = section_detection.section_detection(lines)

            save_json.save_jsonl(
                sections=[],
                lines=step7,
                output_folder=OUTPUT_FOLDER,
                document_id=document_id,
            )

            print(
                f"Finished {document_id}"
            )

        except Exception as exc:

            print(
                f"Failed {document_id}: {exc}"
            )


if __name__ == "__main__":
    main()