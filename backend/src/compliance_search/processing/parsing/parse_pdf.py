from pathlib import Path
from pypdf import PdfReader

from compliance_search.processing.sections import TextFragment


def parse_pdf(pdf_path: Path) -> list[TextFragment]:
    """Read a PDF and return its text fragments in pypdf order.

    Coordinates are in points, with the origin at the bottom-left
    of the page. Line building happens later in build_lines.
    """
    reader = PdfReader(pdf_path)
    all_fragments = []
    for pagenumber, page in enumerate(reader.pages, start=1):

        def visitor_function(text, cm, tm, font_dict, font_size):

            # Skip fragments without visible text. In the delegated
            # regulations these are only line breaks ("\n"). The spaces
            # between words come inside the word fragments, and
            # build_lines uses them to separate words.
            if not text.strip():
                return

            # Position: transform the text matrix with cm into page coordinates (pt)
            x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]

            font = ""

            if font_dict:
                font = str(font_dict.get("/BaseFont", ""))

            bold = "Bold" in font

            all_fragments.append(TextFragment(
                page_number=pagenumber,
                x=x,
                y=y,
                font=font,
                # Font size on the page: pypdf's font_size (often 1.0)
                # × vertical scale of tm × vertical scale of cm
                font_size=font_size * tm[3] * cm[3],
                bold=bold,
                text=text,
            ))

        page.extract_text(visitor_text=visitor_function)

    return all_fragments
