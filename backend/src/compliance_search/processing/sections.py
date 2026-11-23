"""State of a document after the first split into sections (level 1).

Each document is stored as one JSONL file:

    <document_id>LinesParsed.jsonl   one SectionLine per line

Each line carries its section_type and its layout signals, so the chunking step
can reassemble paragraphs, articles and chunks from the bottom up. A section is
the run of consecutive lines with the same section_type.
Later the file becomes a Postgres table with the same columns.
"""
from typing import Literal

from pydantic import BaseModel

# Section names per doc_type, as in docs/analysis/doc-type-structure/doc_type_analysis.md
SectionType = Literal[
    # regulation, delegated_regulation, implementing_regulation
    "header",
    "citations",
    "recitals",
    "enacting_formula", # probably not chunked
    "enacting_terms",
    "final_formula", # probably not chunked (holds)
    "annex",
    # consolidated
    "notice",
    "amendments",
    # circular, guideline
    "contents",
    # circular: MaRisk
    "general_part_AT",
    "special_part_BT",
    # circular: BAIT, VAIT
    "preliminary_remarks",
    "requirements",
    # guideline
    "executive_summary",
    "background",
    "compliance_reporting",
    "subject_scope_definitions",
    "implementation",
    "guidelines",
    "accompanying_documents",
    # every doc_type: one section per page
    "footnotes",
]

class SectionLine(BaseModel):

    section_type: SectionType | Literal[""] = ""  # "" until section detection assigns one
    article: str | None = None  # "3" for Article 3 / Artikel 3, None outside articles
    recital: str | None = None  # "12" for recital (12), None outside recitals
    seq: int #number of line on page to order the lines
    page_number: int

    font_size: float
    font: str
    bold: bool

    x: float  # distance to left edge in points
    y: float  # distance to lower edge in points (PDF origin is bottom-left)

    text: str


class TextFragment(BaseModel):
    """One piece of text as pypdf delivers it, before it is grouped into lines."""

    page_number: int  # starting at 1
    x: float  # distance to left edge in points
    y: float  # distance to lower edge in points (PDF origin is bottom-left)
    font: str
    font_size: float  # size on the page in points
    bold: bool
    text: str  # raw text including spaces (build_lines uses them to separate words)
