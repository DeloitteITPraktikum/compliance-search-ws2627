from pathlib import Path

import build_lines
import parse_pdf
import save_json

# main.py lives in backend/src/compliance_search/processing/Parsing/,
# so the repository root is five folders up.
REPOSITORY_ROOT = Path(__file__).resolve().parents[5]

SOURCE_PDF = REPOSITORY_ROOT / "setup" / "downloads" / "32025R0532_DE.pdf"
OUTPUT_FOLDER = Path(__file__).resolve().parent / "ParsedDocuments"


def main() -> None:
    document_parsed = parse_pdf.parse_pdf(SOURCE_PDF)
    lines = build_lines.build_lines(document_parsed["fragments"])
    save_json.save_json(lines, OUTPUT_FOLDER)


if __name__ == "__main__":
    main()
