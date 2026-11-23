import json

import pytest

from compliance_search.processing.document_types import (
    get_document_type,
    load_document_metadata,
)


def write_metadata(path, documents):
    path.write_text(json.dumps({"documents": documents}), encoding="utf-8")


def test_load_document_metadata_indexes_documents_by_id(tmp_path):
    metadata_path = tmp_path / "documents.json"
    write_metadata(
        metadata_path,
        [{"id": "32022R2554_EN", "doc_type": "regulation"}],
    )

    documents = load_document_metadata(metadata_path)

    assert get_document_type("32022R2554_EN", documents) == "regulation"


def test_get_document_type_rejects_unknown_document_id():
    with pytest.raises(KeyError, match="No metadata found"):
        get_document_type("unknown", {})


def test_get_document_type_rejects_unknown_type():
    documents = {"document": {"id": "document", "doc_type": "unknown"}}

    with pytest.raises(ValueError, match="Invalid doc_type"):
        get_document_type("document", documents)


def test_load_document_metadata_requires_documents_list(tmp_path):
    metadata_path = tmp_path / "documents.json"
    metadata_path.write_text(json.dumps({}), encoding="utf-8")

    with pytest.raises(ValueError, match="documents.*list"):
        load_document_metadata(metadata_path)
