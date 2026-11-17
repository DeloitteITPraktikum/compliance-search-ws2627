import parse_pdf
import save_json
import build_lines
from pathlib import Path
repository_root = Path(__file__).resolve().parents[5]
document_parsed = parse_pdf.parse_pdf(repository_root / "setup" / "downloads" / "32025R0532_DE.pdf")
lines = build_lines.build_lines(document_parsed["fragments"])
save_json.save_json(lines, repository_root / "backend" / "src" / "compliance_search" / "processing" / "Parsing" / "ParsedDocuments")