from pypdf import PdfReader

def parse_pdf(source_path : str) -> dict:
    reader = PdfReader(source_path)

    all_lines = []

    for pagenumber, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
    
        for linenumber, line in enumerate(text.splitlines(), start=1):
            line = line.strip()

            if not line:
                continue

            all_lines.append({
                "page": pagenumber,
                "line_no": linenumber,
                "text": line
            })

    return {
        "document" : source_path,
        "pages": len(reader.pages),
        "lines": all_lines
    }