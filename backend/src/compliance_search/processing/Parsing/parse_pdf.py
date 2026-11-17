from pathlib import Path

from pypdf import PdfReader

def parse_pdf(source_path: Path) -> dict:

    reader = PdfReader(source_path)

    all_fragments = []

    for pagenumber, page in enumerate(reader.pages, start=1):

        def visitor_function(text, cm, tm, font_dict, font_size):

            text = text.strip()

            if not text:
                return

            x = cm[4] + tm[4]
            y = cm[5] + tm[5]

            font = ""

            if font_dict:
                font = str(font_dict.get("/BaseFont"))

            bold = "Bold" in font

            all_fragments.append({
                "page_number": pagenumber,
                "x": x,
                "y": y,
                "font": font,
                "font_size": font_size,
                "effective_font_size": font_size * cm[0],
                "bold": bold,
                "text": text
            })

        page.extract_text(visitor_text=visitor_function)

    return {
        "document": str(source_path),
        "pages": len(reader.pages),
        "fragments": all_fragments
    }