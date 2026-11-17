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
BACKEND_DIR = SCRIPT_DIR.parents[3]
DATA_DIR = BACKEND_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
ACTIVE_PDF_DIR = PDF_DIR / "active"
DELETED_PDF_DIR = PDF_DIR / "deleted"
METADATA_DIR = DATA_DIR / "metadata"
STATE_DIR = DATA_DIR / "state"
STATE_FILE = STATE_DIR / "state.json"

# File-writing functions

def saveAsJsonFile(filePath: Path, data: Any) -> None:
    """Create the parent directory and save formatted UTF-8 JSON data."""
    filePath.parent.mkdir(parents=True, exist_ok=True)
    with filePath.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")

def saveAsPdfFile(filePath: Path, data: bytes) -> None:
    """Create the parent directory and save binary PDF data."""
    filePath.parent.mkdir(parents=True, exist_ok=True)
    filePath.write_bytes(data)

def getLocalPdfSha256(filePath: Path) -> str | None:
    """Calculate the SHA-256 hash of a local PDF, or return None if it is missing."""
    if not filePath.exists():
        return None

    sha256 = hashlib.sha256()
    with filePath.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

# Function for filtering JSON files by selected values

def filterJsonFile(
    jsonFilePath: Path,
    valuesToKeep: set[str],
    ):
    with jsonFilePath.open("r", encoding="utf-8") as file:
        data = json.load(file)

    def reduceValues(value: Any):
        """Recursively keep matching values and remove all other JSON values."""
        if isinstance(value, dict):
            reduced_value: dict[str, Any] = {}
            for key, item in value.items():
                if key in valuesToKeep:
                    reduced_value[key] = item
                    continue

                reduced_item = reduceValues(item)
                if reduced_item is not None:
                    reduced_value[key] = reduced_item

            return reduced_value or None

        if isinstance(value, list):
            reduced_items = [
                reduced_item
                for item in value
                if (reduced_item := reduceValues(item)) is not None
            ]
            return reduced_items or None

        return None

    reducedData = reduceValues(data)

    saveAsJsonFile(jsonFilePath, reducedData)

# Synchronization functions and synchronization checks

def syncDocuments(
    docsUrl: str,
    gatewayKey: str,
    metadataDir: Path,
    pdfDir: Path,
    stateFile: Path,
) -> dict[str, int]:
    """Query metadata, reconcile local PDFs by status, and update local metadata."""
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
        localPdfSha256 = getLocalPdfSha256(activePdfPath)
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

def main():
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