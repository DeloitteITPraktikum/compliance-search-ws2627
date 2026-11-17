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

            # Position: transform the text matrix with cm into page coordinates (pt)
            x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]

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
                # Font size on the page: font_size × vertical scale of tm × vertical scale of cm
                "effective_font_size": font_size * tm[3] * cm[3],
                "bold": bold,
                "text": text
            })

        page.extract_text(visitor_text=visitor_function)

    return {
        "document": str(source_path),
        "pages": len(reader.pages),
        "fragments": all_fragments
    }