"""Turn the units of one document into chunks: one chunk per article or recital.

The context line in front of the embedding text names the document, the grouping
headings and the article, because embeddings do not read article numbers well
(handbook/08-pitfalls.md, item 1). Example:

    Delegated Regulation (EU) 2025/301: RTS on … | CHAPTER I … | Article 5 – Time limits
"""
import hashlib

from compliance_search.processing.chunking.group_units import Unit
from compliance_search.processing.chunks import CHUNKER_VERSION, Chunk

LABEL_WORD = {"article": "Article", "recital": "Recital"}


def build_chunks(units: list[Unit], metadata: dict) -> list[Chunk]:
    """Build one Chunk per unit. metadata is the document's record from the document API."""
    chunks = []
    for unit in units:
        label = f"{LABEL_WORD[unit.unit_type]} {unit.number}"
        heading = f"{label} – {unit.title}" if unit.title else label
        context_line = " | ".join([metadata["title"], *unit.headings, heading])
        embedding_text = f"{context_line}\n{unit.text}"

        chunks.append(Chunk(
            chunk_id=f"{metadata['id']}#{label}",
            document_id=metadata["id"],
            family_id=metadata["family_id"],
            version=metadata["version_date"],
            language=metadata["language"],
            doc_type=metadata["doc_type"],
            unit_type=unit.unit_type,
            label=label,
            title=unit.title,
            headings=unit.headings,
            page_start=min(unit.pages),
            page_end=max(unit.pages),
            text=unit.text,
            embedding_text=embedding_text,
            chunker_version=CHUNKER_VERSION,
            text_hash=hashlib.sha256(embedding_text.encode("utf-8")).hexdigest(),
        ))
    return chunks
