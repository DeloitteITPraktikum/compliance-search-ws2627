"""Hand-over format between parsing and chunking, and the chunk for the index."""
from typing import Literal

from pydantic import BaseModel, Field


class Block(BaseModel):
    """One piece of text from the PDF, in reading order."""

    order: int = Field(ge=0)  # position in reading order
    block_type: Literal["section_heading", "heading", "paragraph", "table"]
    text: str = Field(min_length=1)  # cleaned text, numbering like (16) kept
    page: int = Field(ge=1)  # PDF page where the block starts


class ParsedDocument(BaseModel):
    """Everything parsing hands over for one document."""

    document_id: str  # 'id' from the document API, e.g. 32022R2554_EN
    family_id: str  # 'family_id' from the document API
    language: Literal["DE", "EN"]
    version: str  # 'version_date' from the document API
    title: str  # 'title' from the document API
    blocks: list[Block]  # all blocks in reading order

class Chunk(BaseModel):
    """One unit that is embedded and stored in the index."""

    chunk_id: str  # unique id, e.g. 32022R2554_EN:art:19:1
    # from the document (same names as Citation in models.py)
    document_id: str
    family_id: str
    language: Literal["DE", "EN"]
    version: str
    # from the section
    article: str  # label as written, e.g. "Article 19"
    article_key: str | None  # grader key, e.g. "art:19"; None if unreadable
    heading: str | None  # title of the section, if any
    # position inside the section
    part: int = Field(ge=1)  # this is part 2 ...
    parts: int = Field(ge=1)  # ... of 4
    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)
    # content
    text: str  # original text, for quotes and keyword search
    embed_text: str  # title line + text, the input for the embedding    """One unit that is embedded and stored in the index."""

    # TODO: document fields + article, article_key, heading,
    #       part, parts, page_start, page_end, text, embed_text