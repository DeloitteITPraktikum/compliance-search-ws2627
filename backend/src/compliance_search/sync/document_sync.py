import os
import hashlib
from pathlib import Path
from typing import Any
import json

from compliance_search.clients.document_api import (
    downloadDocuments,
    listDocuments,
    startSession,
)

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
ACTIVE_PDF_DIR = PDF_DIR / "active"
DELETED_PDF_DIR = PDF_DIR / "deleted"
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
        pdfDir: Root directory for active and deleted PDF subdirectories.
        stateFile: JSON file used to store the API server timestamp.

    Returns:
        A report containing the number of downloaded, skipped, and deleted documents.

    Side Effects:
        Creates directory structures, downloads PDFs, moves deleted PDFs to the
        deleted subdirectory, updates individual metadata files, and updates state.
    """
    session = startSession(gatewayKey)
    activePdfDir = pdfDir / "active"
    deletedPdfDir = pdfDir / "deleted"
    activePdfDir.mkdir(parents=True, exist_ok=True)
    deletedPdfDir.mkdir(parents=True, exist_ok=True)

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
        activePdfPath = activePdfDir / f"{documentId}.pdf"
        deletedPdfPath = deletedPdfDir / f"{documentId}.pdf"

        if remoteMetadata.get("status") == "deleted":
            deleted += 1

            if activePdfPath.exists():
                activePdfPath.replace(deletedPdfPath)
            elif deletedPdfPath.exists():
                pass
            elif (pdfDir / f"{documentId}.pdf").exists():
                (pdfDir / f"{documentId}.pdf").replace(deletedPdfPath)

            saveAsJsonFile(metadataPath, remoteMetadata)
            continue

        if deletedPdfPath.exists():
            deletedPdfPath.replace(activePdfPath)

        legacyPdfPath = pdfDir / f"{documentId}.pdf"
        if legacyPdfPath.exists():
            if activePdfPath.exists():
                legacyPdfPath.unlink()
            else:
                legacyPdfPath.replace(activePdfPath)

        # 3. Download only when the local PDF hash differs or the PDF is missing.
        remoteSha256 = remoteMetadata.get("sha256")
        localPdfSha256 = getPdfSha256(activePdfPath)
        if localPdfSha256 != remoteSha256:
            pdfData = downloadDocuments(session, docsUrl, documentId)
            saveAsPdfFile(activePdfPath, pdfData)
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
