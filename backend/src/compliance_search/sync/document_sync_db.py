"""Synchronize document metadata and PDFs with Supabase."""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

from compliance_search.clients.database_api import (
    deletePdf,
    getTableField,
    insertTableRow,
    uploadPdf,
)
from compliance_search.clients.document_api import downloadDocuments, listDocuments
from compliance_search.clients.general_REST_api import startSession

DOCS_URL = os.environ.get("DOCS_URL")
GATEWAY_KEY = os.environ.get("GATEWAY_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_API_KEY = os.environ.get("SUPABASE_API_KEY")
DOCUMENTS_TABLE = "documents"


def syncDocuments(
    docsUrl: str,
    gatewayKey: str,
    supabaseUrl: str,
    supabaseApiKey: str,
) -> dict[str, int]:
    """Synchronize all document metadata and PDFs to Supabase.

    PDFs are stored in the configured document bucket. Each metadata row is
    upserted by document ID, with ``last_synced_at`` set after its file work
    succeeds.
    """
    documentSession = startSession(gatewayKey)
    databaseSession = startSession(
        supabaseApiKey,
        headers={"apikey": supabaseApiKey},
    )
    documentResult = listDocuments(documentSession, docsUrl.rstrip("/"))

    downloaded = 0
    skipped = 0
    deleted = 0

    for remoteMetadata in documentResult["documents"]:
        documentId = remoteMetadata.get("id")
        if not documentId:
            raise ValueError("Document API returned a document without an id.")

        if remoteMetadata.get("status") == "deleted":
            try:
                existingStatus = getTableField(
                    databaseSession,
                    supabaseUrl,
                    DOCUMENTS_TABLE,
                    "id",
                    documentId,
                    "status",
                )
            except LookupError:
                existingStatus = None

            if existingStatus is not None and existingStatus != "deleted":
                deletePdf(
                    databaseSession,
                    supabaseUrl,
                    documentId,
                )

            row = dict(remoteMetadata)
            row["last_synced_at"] = datetime.now(timezone.utc).isoformat()
            insertTableRow(
                databaseSession,
                supabaseUrl,
                DOCUMENTS_TABLE,
                row,
                conflictColumn="id",
            )
            deleted += 1
            continue

        remoteSha256 = remoteMetadata.get("sha256")
        try:
            storedSha256 = getTableField(
                databaseSession,
                supabaseUrl,
                DOCUMENTS_TABLE,
                "id",
                documentId,
                "sha256",
            )
        except LookupError:
            storedSha256 = None

        if remoteSha256 is None or storedSha256 != remoteSha256:
            pdfData = downloadDocuments(documentSession, docsUrl.rstrip("/"), documentId)
            downloadedSha256 = hashlib.sha256(pdfData).hexdigest()
            if remoteSha256 is not None and downloadedSha256 != remoteSha256:
                raise ValueError(
                    f"Downloaded PDF hash does not match metadata for {documentId}."
                )
            uploadPdf(
                databaseSession,
                supabaseUrl,
                pdfData,
                documentId,
            )
            downloaded += 1
        else:
            skipped += 1

        row: dict[str, Any] = dict(remoteMetadata)
        row["last_synced_at"] = datetime.now(timezone.utc).isoformat()
        insertTableRow(
            databaseSession,
            supabaseUrl,
            DOCUMENTS_TABLE,
            row,
            conflictColumn="id",
        )

    return {
        "downloaded": downloaded,
        "skipped": skipped,
        "deleted": deleted,
    }


def main() -> None:
    if not DOCS_URL:
        raise RuntimeError("DOCS_URL fehlt!")
    if not GATEWAY_KEY:
        raise RuntimeError("GATEWAY_KEY fehlt!")
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL fehlt!")
    if not SUPABASE_API_KEY:
        raise RuntimeError("SUPABASE_API_KEY fehlt!")

    syncReport = syncDocuments(
        DOCS_URL,
        GATEWAY_KEY,
        SUPABASE_URL,
        SUPABASE_API_KEY,
    )
    print(json.dumps(syncReport, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()