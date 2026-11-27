import os
import hashlib
from pathlib import Path
from typing import Any
import json

from compliance_search.clients.document_api import (
    downloadDocuments,
    listDocuments,
)
from compliance_search.clients.general_REST_api import startSession

# Environment variables

DOCS_URL = os.environ.get("DOCS_URL")
GATEWAY_KEY = os.environ.get("GATEWAY_KEY")
if not GATEWAY_KEY:
    raise RuntimeError("GATEWAY_KEY fehlt!")

# Relative paths

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parents[3]
DATA_DIR = ROOT_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
METADATA_DIR = DATA_DIR / "metadata"
STATE_DIR = DATA_DIR / "state"
STATE_FILE = STATE_DIR / "state.json"

# File-writing functions

def saveAsJsonFile(filePath: Path, data: Any) -> None:
    """Create a file's parent directory and save data as formatted UTF-8 JSON.

    Args:
        filePath: Destination path for the JSON file.
        data: JSON-serializable value written to the destination.

    Returns:
        None.
    """
    filePath.parent.mkdir(parents=True, exist_ok=True)
    with filePath.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")

def saveAsPdfFile(filePath: Path, data: bytes) -> None:
    """Create a file's parent directory and save binary PDF data.

    Args:
        filePath: Destination path for the PDF file.
        data: Raw bytes written to the destination.

    Returns:
        None.
    """
    filePath.parent.mkdir(parents=True, exist_ok=True)
    filePath.write_bytes(data)

def getPdfSha256(filePath: Path) -> str | None:
    """Calculate a local PDF file's SHA-256 hash.

    Args:
        filePath: Path to the local PDF file.

    Returns:
        The lowercase hexadecimal SHA-256 hash, or None if the file does not exist.
    """
    if not filePath.exists():
        return None

    sha256 = hashlib.sha256()
    with filePath.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

# Document class (DEL-91)

# All doc_type values the document API knows (openapi/document-api.json).
KNOWN_DOC_TYPES = {
    "regulation",
    "delegated_regulation",
    "implementing_regulation",
    "consolidated",
    "corrigendum",
    "circular",
    "guideline",
}

# All status values the document API knows. Each status gets its own folder.
KNOWN_STATUSES = {"active", "superseded", "repealed", "deleted"}

# Folder for documents whose doc_type is missing or unknown.
UNCLASSIFIED = "unclassified"

def getDocumentClass(metadata: dict[str, Any]) -> str:
    """Return the document class (doc_type) of a document.

    Args:
        metadata: Metadata of one document from the document API.

    Returns:
        The doc_type, or "unclassified" if it is missing or unknown.
    """
    docType = metadata.get("doc_type")
    if docType in KNOWN_DOC_TYPES:
        return docType

    print(
        f"WARNING: Dokument {metadata.get('id')} hat keine bekannte "
        f"Dokumentenklasse (doc_type={docType!r}) und wird in "
        f"'{UNCLASSIFIED}' abgelegt."
    )
    return UNCLASSIFIED

def getTargetPdfPath(pdfDir: Path, metadata: dict[str, Any]) -> Path:
    """Return where a document's PDF belongs: pdfs/<status>/<doc_type>/<id>.pdf.

    Args:
        pdfDir: Root directory for all PDFs.
        metadata: Metadata of one document from the document API.

    Returns:
        The path of the PDF inside its status and document class folder.
    """
    status = metadata.get("status")
    if status not in KNOWN_STATUSES:
        status = "active"
    return pdfDir / status / getDocumentClass(metadata) / f"{metadata['id']}.pdf"

def moveExistingPdf(pdfDir: Path, documentId: str, targetPath: Path) -> None:
    """Move an existing local copy of a PDF to its target path.

    Finds the PDF anywhere below pdfDir (old flat folders included), moves it
    to targetPath and removes any further copies.

    Args:
        pdfDir: Root directory for all PDFs.
        documentId: ID of the document.
        targetPath: Path where the PDF belongs.

    Returns:
        None.
    """
    for existingPath in list(pdfDir.rglob(f"{documentId}.pdf")):
        if existingPath == targetPath:
            continue
        if targetPath.exists():
            existingPath.unlink()
        else:
            targetPath.parent.mkdir(parents=True, exist_ok=True)
            existingPath.replace(targetPath)

# Synchronization functions and synchronization checks

def syncDocuments(
    docsUrl: str,
    gatewayKey: str,
    metadataDir: Path,
    pdfDir: Path,
    stateFile: Path,
) -> dict[str, int]:
    """Synchronize document metadata and PDFs with the document API.

    Args:
        docsUrl: Base URL of the document API.
        gatewayKey: Bearer key used to authenticate API requests.
        metadataDir: Directory containing one JSON metadata file per document ID.
        pdfDir: Root directory for the PDFs, sorted as <status>/<doc_type>/<id>.pdf.
        stateFile: JSON file used to store the API server timestamp.

    Returns:
        A report containing the number of downloaded, skipped, and deleted documents.

    Side Effects:
        Creates directory structures, downloads PDFs, moves each PDF into its
        status and document class folder, updates individual metadata files,
        and updates state.
    """
    session = startSession(gatewayKey)
    pdfDir.mkdir(parents=True, exist_ok=True)

    # 1. Query every document so orphan PDFs and missing metadata are also reconciled.
    documentResult = listDocuments(session, docsUrl)

    downloaded = 0
    skipped = 0
    deleted = 0

    for remoteMetadata in documentResult.get("documents", []):
        documentId = remoteMetadata.get("id")
        if not documentId:
            continue

        metadataPath = metadataDir / f"{documentId}.json"

        # 2. Every PDF lives in pdfs/<status>/<doc_type>/<id>.pdf (DEL-91).
        #    If the status or the doc_type changed, the PDF is moved.
        targetPdfPath = getTargetPdfPath(pdfDir, remoteMetadata)
        moveExistingPdf(pdfDir, documentId, targetPdfPath)

        if remoteMetadata.get("status") == "deleted":
            # The file route returns 410 for deleted documents: nothing to download.
            deleted += 1
            saveAsJsonFile(metadataPath, remoteMetadata)
            continue

        # 3. Download only when the local PDF hash differs or the PDF is missing.
        remoteSha256 = remoteMetadata.get("sha256")
        localPdfSha256 = getPdfSha256(targetPdfPath)
        if localPdfSha256 != remoteSha256:
            pdfData = downloadDocuments(session, docsUrl, documentId)
            saveAsPdfFile(targetPdfPath, pdfData)
            downloaded += 1
        else:
            skipped += 1

        # 4. Update the individual metadata file for this document.
        saveAsJsonFile(metadataPath, remoteMetadata)

    saveAsJsonFile(stateFile, {"server_time": documentResult["server_time"]})
    return {
        "downloaded": downloaded,
        "skipped": skipped,
        "deleted": deleted,
    }

def main() -> None:
    sessionReport = syncDocuments(
        docsUrl=DOCS_URL,
        gatewayKey=GATEWAY_KEY,
        metadataDir=METADATA_DIR,
        pdfDir=PDF_DIR,
        stateFile=STATE_FILE,
    )
    print(json.dumps(sessionReport, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
