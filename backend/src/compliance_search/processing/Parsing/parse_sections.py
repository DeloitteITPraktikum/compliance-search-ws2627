"""Parse a PDF of an EU legal act into Section and SectionLine objects (DEL-11).

Scope: regulation, delegated_regulation and implementing_regulation, DE and EN.

Steps:
1. read_lines: read every text line with font, size, bold and position
2. remove_page_header_and_footer: drop "ABl. L vom …", "ELI: http… 1/7" and the masthead
3. find_footnotes: find the footnotes at the bottom of each page
4. parse_sections: walk through the lines and start a new section at each start phrase
5. build_models: turn the result into Section and SectionLine objects
"""
import re
from dataclasses import dataclass

from pypdf import PageObject, PdfReader

from compliance_search.processing.sections import Section, SectionLine

PARSER_VERSION = "0.1"

# Text pieces whose y differs by less than this (in points) are on the same line.
LINE_TOLERANCE = 2.0

# On page 1 everything above this y (in points) is the masthead of the
# Official Journal ("Amtsblatt der Europäischen Union Reihe L", date, number).
MASTHEAD_BOTTOM = 90.0

# Body text is 9.6 pt, footnotes 8.5 pt and footnote numbers about 5 pt.
BODY_SIZE = 9.0
SUPERSCRIPT_SIZE = 7.0

FOOTNOTE_WITH_NUMBER = re.compile(r"^\(\d+\) ")

# Running header and footer of each page, old and new layout of the Official Journal:
#   "DE Amtsblatt der Europäischen Union 27.12.2022 L 333/23"
#   "ABl. L vom 2.7.2025 DE", "EN OJ L, 20.2.2025"
#   "ELI: http://data.europa.eu/eli/reg_del/2025/532/oj 1/7" (page number first or last)
# Sometimes the space before "EN" or the page number is missing ("OJ L, 31.12.2024EN").
PAGE_HEADER_OR_FOOTER = re.compile(
    r"^(DE|EN) (Amtsblatt der Europäischen Union|Official Journal of the European Union) "
    r"|^((DE|EN) )?(ABl\. L vom|OJ L,) [\d.]+?( ?(DE|EN))?$"
    r"|^(\d+/\d+ ?)?ELI: http\S+?/oj( ?\d+/\d+)?$"
)

# Sections of regulation, delegated_regulation and implementing_regulation, in
# the order they appear. Start phrases from docs/analysis/doc-type-structure/doc_type_analysis.md.
SECTION_ORDER = [
    "header", "citations", "recitals", "enacting_formula",
    "enacting_terms", "final_formula", "annex",
]

ENACTING_FORMULA = re.compile(
    r"^(HAS|HAVE) ADOPTED THIS REGULATION:$|^(HAT|HABEN) FOLGENDE VERORDNUNG ERLASSEN:$"
)

START_PHRASES = {
    # "THE EUROPEAN COMMISSION,", "DIE EUROPÄISCHE KOMMISSION —",
    # "DAS EUROPÄISCHE PARLAMENT UND DER RAT DER EUROPÄISCHEN UNION —"
    "citations": re.compile(r"^(THE|DIE|DAS) EUROP[A-ZÄÖÜ ]+[,—]$"),
    "recitals": re.compile(r"^(Whereas:|in Erwägung nachstehender Gründe:)$"),
    "enacting_formula": ENACTING_FORMULA,
    # "Done at Brussels, …", "Brüssel, den …", "Geschehen zu Straßburg am …"
    "final_formula": re.compile(r"^(Done at \S+|(Brüssel|Straßburg|Luxemburg), den|Geschehen zu \S+ am) "),
    "annex": re.compile(r"^(ANNEX|ANHANG)( [IVXLC]+)?$"),
}


@dataclass
class RawLine:
    """One text line of a page, before it is assigned to a section."""

    page_number: int  # starting at 1
    seq: int  # line number on the page, starting at 1
    text: str
    font: str  # e.g. "EUAlbertina-Bold"
    font_size: float  # in points
    bold: bool
    x: float  # distance to the left edge in points
    y: float  # distance to the upper edge in points


def read_lines(reader: PdfReader) -> list[RawLine]:
    """All text lines of the PDF, page by page from top to bottom."""
    lines = []
    for page_number, page in enumerate(reader.pages, start=1):
        lines.extend(read_page(page, page_number))
    return lines


def read_page(page: PageObject, page_number: int) -> list[RawLine]:
    """All text lines of one page, from top to bottom."""
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    pieces = []

    # pypdf calls this function for every piece of text on the page.
    # cm and tm are the matrices that place the text on the page.
    def collect(text, cm, tm, font_dict, font_size):
        if not text.strip():
            return
        x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
        y_from_bottom = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
        # Direction in which the text runs (a, b) and the height of a letter (c, d)
        a = tm[0] * cm[0] + tm[1] * cm[2]
        b = tm[0] * cm[1] + tm[1] * cm[3]
        c = tm[2] * cm[0] + tm[3] * cm[2]
        d = tm[2] * cm[1] + tm[3] * cm[3]
        sideways = abs(b) > abs(a)
        if sideways:
            # Sideways text, e.g. landscape tables in annexes. Turn it so that
            # it reads from left to right, as in a PDF viewer.
            if b > 0:  # runs upwards
                x, y = y_from_bottom, x
            else:  # runs downwards
                x, y = page_height - y_from_bottom, page_width - x
        else:
            y = page_height - y_from_bottom  # PDFs count y from the bottom
        font = (font_dict or {}).get("/BaseFont", "unknown")
        pieces.append({
            "text": text,
            "x": x,
            "y": y,
            "font": str(font).lstrip("/"),
            # font_size is often 1.0, the real size is in the matrices
            "size": font_size * (c * c + d * d) ** 0.5,
        })

        pieces[-1]["sideways"] = sideways

    page.extract_text(visitor_text=collect)
    # On landscape pages the page header stays upright. Group it separately,
    # so it is not mixed with sideways text at the same height.
    groups = (
        group_by_y([p for p in pieces if not p["sideways"]])
        + group_by_y([p for p in pieces if p["sideways"]])
    )
    groups.sort(key=lambda group: group[0]["y"])
    return [
        make_line(group, page_number, seq)
        for seq, group in enumerate(groups, start=1)
    ]


def group_by_y(pieces: list[dict]) -> list[list[dict]]:
    """Put pieces with (almost) the same y into one group, top to bottom."""
    groups = []
    for piece in sorted(pieces, key=lambda p: p["y"]):
        if groups and piece["y"] - groups[-1][0]["y"] < LINE_TOLERANCE:
            groups[-1].append(piece)
        else:
            groups.append([piece])
    return groups


def make_line(group: list[dict], page_number: int, seq: int) -> RawLine:
    """Join the pieces of one line from left to right."""
    group = sorted(group, key=lambda p: p["x"])
    text = " ".join("".join(p["text"] for p in group).split())
    main = max(group, key=lambda p: len(p["text"]))  # font of the longest piece
    return RawLine(
        page_number=page_number,
        seq=seq,
        text=text,
        font=main["font"],
        font_size=round(main["size"], 2),
        bold="Bold" in main["font"],
        x=round(group[0]["x"], 2),
        y=round(group[0]["y"], 2),
    )


def remove_page_header_and_footer(lines: list[RawLine]) -> list[RawLine]:
    """Drop the running header and footer of every page and the masthead of page 1."""
    return [
        line for line in lines
        if not PAGE_HEADER_OR_FOOTER.match(line.text)
        and not (line.page_number == 1 and line.y < MASTHEAD_BOTTOM)
    ]


def is_footnote_start(lines: list[RawLine], i: int, middle_of_page: float) -> bool:
    """Does the first footnote of a page start at this line? Two layouts:
    - newer acts: a small number, then a line "() <text>" in small print
    - e.g. 2024/1772: one line "(1) <text>" in small print
    Footnotes are always in the lower half of the page."""
    line = lines[i]
    if line.y < middle_of_page:
        return False
    if line.font_size < BODY_SIZE and FOOTNOTE_WITH_NUMBER.match(line.text):
        return True
    if i + 1 >= len(lines):
        return False
    text = lines[i + 1]
    return (
        line.text.isdigit()
        and line.font_size < SUPERSCRIPT_SIZE
        and text.text.startswith("()")
        and text.font_size < BODY_SIZE
    )


def find_footnotes(lines: list[RawLine]) -> set[int]:
    """Indexes of all footnote lines. The footnotes fill the bottom of a page,
    so everything from the first footnote to the end of its page belongs to them."""
    # Middle between the highest and lowest line of each page. Landscape pages
    # are lower than portrait pages, so this cannot be one fixed number.
    top: dict[int, float] = {}
    bottom: dict[int, float] = {}
    for line in lines:
        top[line.page_number] = min(top.get(line.page_number, line.y), line.y)
        bottom[line.page_number] = max(bottom.get(line.page_number, line.y), line.y)

    footnotes = set()
    in_footnotes_of_page = None
    for i, line in enumerate(lines):
        middle = (top[line.page_number] + bottom[line.page_number]) / 2
        if in_footnotes_of_page != line.page_number and is_footnote_start(lines, i, middle):
            in_footnotes_of_page = line.page_number
        if in_footnotes_of_page == line.page_number:
            footnotes.add(i)
    return footnotes


def starts_section(section_type: str, line: RawLine, previous: RawLine | None) -> bool:
    """Is this line the start phrase of a section of this type?"""
    if section_type == "enacting_terms":
        # Starts right after the enacting formula, e.g. "Artikel 1", "KAPITEL I", "TITLE I"
        return previous is not None and ENACTING_FORMULA.match(previous.text) is not None
    return START_PHRASES[section_type].match(line.text) is not None


def next_section_type(current: str | None, line: RawLine, previous: RawLine | None) -> str | None:
    """The type of the section that starts at this line, or None if the line continues
    the current section. Sections only come in the order of SECTION_ORDER, and
    annexes can follow each other."""
    if current is None:
        return "header"
    if current == "annex" and starts_section("annex", line, previous):
        return "annex"
    position = SECTION_ORDER.index(current)
    if position + 1 < len(SECTION_ORDER):
        candidate = SECTION_ORDER[position + 1]
        if starts_section(candidate, line, previous):
            return candidate
    return None


def parse_sections(source_path: str, document_id: str) -> tuple[list[Section], list[SectionLine]]:
    """Split a PDF into sections and give every line the section it belongs to."""
    lines = remove_page_header_and_footer(read_lines(PdfReader(source_path)))
    footnotes = find_footnotes(lines)

    # Every section as (section_type, its lines), in reading order
    sections: list[tuple[str, list[RawLine]]] = []
    current_type = None  # type of the current main section (not footnotes)
    current_main: list[RawLine] = []
    footnotes_of_page: list[RawLine] = []
    previous = None  # previous line outside the footnotes

    for i, line in enumerate(lines):
        if i in footnotes:
            # One footnotes section per page
            if not footnotes_of_page or footnotes_of_page[0].page_number != line.page_number:
                footnotes_of_page = []
                sections.append(("footnotes", footnotes_of_page))
            footnotes_of_page.append(line)
            continue

        new_type = next_section_type(current_type, line, previous)
        if new_type is not None:
            current_type = new_type
            current_main = []
            sections.append((new_type, current_main))
        current_main.append(line)
        previous = line

    return build_models(sections, document_id)


def build_models(
    sections: list[tuple[str, list[RawLine]]], document_id: str
) -> tuple[list[Section], list[SectionLine]]:
    """Turn the grouped lines into Section and SectionLine objects."""
    section_models = []
    line_models = []
    for seq, (section_type, raw_lines) in enumerate(sections):
        section_id = f"{document_id}#{seq}"
        section_models.append(Section(
            section_id=section_id,
            document_id=document_id,
            seq=seq,
            section_type=section_type,
            heading=raw_lines[0].text,
            page_start=raw_lines[0].page_number,
            page_end=raw_lines[-1].page_number,
            parser_version=PARSER_VERSION,
        ))
        line_models.extend(
            SectionLine(
                section_id=section_id,
                seq=line.seq,
                page_number=line.page_number,
                font_size=line.font_size,
                font=line.font,
                bold=line.bold,
                x=line.x,
                y=line.y,
                text=line.text,
            )
            for line in raw_lines
        )
    return section_models, line_models
