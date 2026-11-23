"""Document type definitions and metadata lookup."""

import json
from pathlib import Path
from typing import Literal, Mapping, cast

DocumentType = Literal[
    "regulation",
    "delegated_regulation",
    "implementing_regulation",
    "consolidated",
    "guideline",
    "circular",
]

DOCUMENT_TYPES: frozenset[str] = frozenset(
    {
        "regulation",
        "delegated_regulation",
        "implementing_regulation",
        "consolidated",
        "guideline",
        "circular",
    }
)

DocumentMetadata = Mapping[str, object]


def load_document_metadata(
    metadata_path: Path,
) -> dict[str, DocumentMetadata]:
    """Load document metadata indexed by document ID."""
    with metadata_path.open(encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)

    documents = metadata.get("documents")
    if not isinstance(documents, list):
        raise ValueError("Document metadata must contain a 'documents' list.")

    indexed_documents: dict[str, DocumentMetadata] = {}
    for document in documents:
        if not isinstance(document, dict):
            raise ValueError("Every document metadata entry must be an object.")

        document_id = document.get("id")
        if not isinstance(document_id, str) or not document_id:
            raise ValueError("Every document metadata entry must have a non-empty 'id'.")

        indexed_documents[document_id] = document

    return indexed_documents


def get_document_type(
    document_id: str,
    documents: Mapping[str, DocumentMetadata],
) -> DocumentType:
    """Return the validated document type for a document ID."""
    try:
        document = documents[document_id]
    except KeyError as error:
        raise KeyError(f"No metadata found for document '{document_id}'.") from error

    document_type = document.get("doc_type")
    if not isinstance(document_type, str) or document_type not in DOCUMENT_TYPES:
        raise ValueError(
            f"Invalid doc_type for document '{document_id}': {document_type!r}."
        )

    return cast(DocumentType, document_type)
