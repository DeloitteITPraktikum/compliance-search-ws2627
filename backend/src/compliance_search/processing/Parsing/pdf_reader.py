from pathlib import Path

import parse_pdf
import save_json

# pdf_reader.py lives in backend/src/compliance_search/processing/Parsing/,
# so the repo root is five folders up.
REPO_ROOT = Path(__file__).resolve().parents[5]

SOURCE_PDF = REPO_ROOT / "setup" / "downloads" / "32025R0532_DE.pdf"
OUTPUT_FOLDER = Path(__file__).resolve().parent / "Parsed_Test"


if __name__ == "__main__":
    document_parsed = parse_pdf.parse_pdf(str(SOURCE_PDF))
    save_json.save_json(document_parsed, str(OUTPUT_FOLDER))
