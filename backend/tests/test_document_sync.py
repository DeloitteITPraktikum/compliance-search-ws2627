import hashlib
import os

os.environ.setdefault("GATEWAY_KEY", "test-key")

from compliance_search.sync import document_sync  # noqa: E402


def metadata(documentId, docType, status="active", content=b"pdf"):
    return {
        "id": documentId,
        "doc_type": docType,
        "status": status,
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def runSync(tmp_path, monkeypatch, documents):
    monkeypatch.setattr(document_sync, "startSession", lambda key: None)
    monkeypatch.setattr(
        document_sync,
        "listDocuments",
        lambda session, url: {"server_time": "2026-11-23T00:00:00Z", "documents": documents},
    )
    monkeypatch.setattr(document_sync, "downloadDocuments", lambda session, url, documentId: b"pdf")
    return document_sync.syncDocuments(
        docsUrl="http://test",
        gatewayKey="test-key",
        metadataDir=tmp_path / "metadata",
        pdfDir=tmp_path / "pdfs",
        stateFile=tmp_path / "state" / "state.json",
    )


def test_each_document_is_saved_in_its_document_class_folder(tmp_path, monkeypatch):
    runSync(tmp_path, monkeypatch, [
        metadata("32025R0532_EN", "delegated_regulation"),
        metadata("RS-10-2017-BA_DE", "circular"),
    ])

    assert (tmp_path / "pdfs/active/delegated_regulation/32025R0532_EN.pdf").exists()
    assert (tmp_path / "pdfs/active/circular/RS-10-2017-BA_DE.pdf").exists()


def test_document_class_is_kept_in_the_metadata_file(tmp_path, monkeypatch):
    runSync(tmp_path, monkeypatch, [metadata("32025R0532_EN", "delegated_regulation")])

    text = (tmp_path / "metadata/32025R0532_EN.json").read_text(encoding="utf-8")
    assert '"doc_type": "delegated_regulation"' in text


def test_unknown_document_class_goes_to_unclassified(tmp_path, monkeypatch, capsys):
    runSync(tmp_path, monkeypatch, [metadata("X_EN", "something_new")])

    assert (tmp_path / "pdfs/active/unclassified/X_EN.pdf").exists()
    assert "WARNING" in capsys.readouterr().out


def test_deleted_document_moves_to_deleted_folder(tmp_path, monkeypatch):
    runSync(tmp_path, monkeypatch, [metadata("32025R0532_EN", "delegated_regulation")])
    runSync(tmp_path, monkeypatch, [metadata("32025R0532_EN", "delegated_regulation", status="deleted")])

    assert not (tmp_path / "pdfs/active/delegated_regulation/32025R0532_EN.pdf").exists()
    assert (tmp_path / "pdfs/deleted/delegated_regulation/32025R0532_EN.pdf").exists()


def test_superseded_document_moves_to_superseded_folder(tmp_path, monkeypatch):
    runSync(tmp_path, monkeypatch, [metadata("32025R0532_EN", "delegated_regulation")])
    runSync(tmp_path, monkeypatch, [metadata("32025R0532_EN", "delegated_regulation", status="superseded")])

    assert (tmp_path / "pdfs/superseded/delegated_regulation/32025R0532_EN.pdf").exists()
    assert not (tmp_path / "pdfs/active/delegated_regulation/32025R0532_EN.pdf").exists()


def test_old_flat_active_folder_is_sorted_into_class_folders(tmp_path, monkeypatch):
    oldPath = tmp_path / "pdfs/active/32025R0532_EN.pdf"
    oldPath.parent.mkdir(parents=True)
    oldPath.write_bytes(b"pdf")

    report = runSync(tmp_path, monkeypatch, [metadata("32025R0532_EN", "delegated_regulation")])

    assert not oldPath.exists()
    assert (tmp_path / "pdfs/active/delegated_regulation/32025R0532_EN.pdf").exists()
    assert report["skipped"] == 1
