"""Document types and the lookup of a document's type."""

import json
from pathlib import Path
from typing import Literal

DocumentType = Literal[
    "regulation",
    "delegated_regulation",
    "implementing_regulation",
    "consolidated",
    "guideline",
    "circular",
]


def get_document_type(document_id: str, metadata_folder: Path) -> DocumentType:
    """Return the doc_type from <metadata_folder>/<document_id>.json."""
    metadata_path = metadata_folder / f"{document_id}.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return metadata["doc_type"]
