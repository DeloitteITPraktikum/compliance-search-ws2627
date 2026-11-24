"""State of a document after chunking.

Each document is stored as one JSONL file:

    <document_id>Chunks.jsonl   one Chunk per line

A chunk is one citable unit: one article, one recital or one annex
(see docs/decisions/0010-chunk-delegated-regulations-by-article.md).
Embedding and storage read this format. Later the file becomes a Postgres table
with the same columns.
"""
from typing import Literal

from pydantic import BaseModel

# Bump when the chunking rules change, so cached embeddings are rebuilt
CHUNKER_VERSION = "2"


class Chunk(BaseModel):

    chunk_id: str  # "<document_id>#<label>", e.g. "32025R0301_EN#Article 5"

    # from the document API metadata
    document_id: str  # "32025R0301_EN"
    family_id: str  # "32025R0301", the grader matches on it
    version: str  # version_date, e.g. "2024-10-23"
    language: Literal["DE", "EN"]
    doc_type: str  # "delegated_regulation"

    unit_type: Literal["article", "recital", "annex"]
    label: str  # "Article 5" / "Recital 12" / "Annex III", readable by keys.normalize_article
    title: str | None  # article or annex title, None for recitals
    headings: list[str]  # grouping headings above the article, outermost first, e.g. ["TITLE II …", "CHAPTER I …"]

    page_start: int
    page_end: int

    text: str  # the unit's own text, without number and title, for quotes
    embedding_text: str  # context line + text, the input for the embedding

    chunker_version: str
    text_hash: str  # sha256 of embedding_text, key for the embedding cache
