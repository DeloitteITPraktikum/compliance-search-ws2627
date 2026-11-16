import os
import time
from pathlib import Path
from typing import Any
import json

import requests

# Umgebungsvariblen 

DOCS_URL = os.environ.get("DOCS_URL")
GATEWAY_KEY = os.environ.get("GATEWAY_KEY")
if not GATEWAY_KEY:
    raise RuntimeError("GATEWAY_KEY fehlt!")

# relative Pfade

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parents[3]
DATA_DIR = BACKEND_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
METADATA_DIR = DATA_DIR / "metadata"
STATE_DIR = DATA_DIR / "state"
STATE_FILE = STATE_DIR / "state.json"

# Funktion zum Starten einer HTTP-Session

def startSession():
    global session
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {GATEWAY_KEY}"

# Funktionen zum Abrufen der verfügbaren Anwortarten der API

def healthCheck() -> bool:
    try: 
        response = session.get(f"{DOCS_URL}/health", timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

def listDocuments(changedSince: str | None = None) -> dict[str, Any]:
    params = {"changed_since": changedSince} if changedSince is not None else None
    response = session.get(
        f"{DOCS_URL}/documents",
        params=params,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()

def getChangedDocuments(changedSince: str | None = None) -> dict[str, Any]:
    if changedSince is None and STATE_FILE.exists():
        with STATE_FILE.open("r", encoding="utf-8") as file:
            state = json.load(file)
        changedSince = state.get("server_time")

    result = listDocuments(changedSince)
    saveAsJasonFile(STATE_FILE, {"server_time": result["server_time"]})
    return result

def downloadMetadata(doc_id: str) -> dict[str, Any]:
    response = session.get(f"{DOCS_URL}/documents/{doc_id}", timeout=60)
    response.raise_for_status()
    return response.json()
    
def downloadDocuments(doc_id: str) -> bytes:
    response = session.get(f"{DOCS_URL}/documents/{doc_id}/file", timeout=60)
    response.raise_for_status()
    return response.content

# Funktionen zum Speichern von Daten in Dateien

def saveAsJasonFile(filePath: Path, data: Any) -> None:
    filePath.parent.mkdir(parents=True, exist_ok=True)
    with filePath.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")

def saveAsPdfFile(filePath: Path, data: bytes) -> None:
    filePath.parent.mkdir(parents=True, exist_ok=True)
    filePath.write_bytes(data)

# Funktion zum Filtern der JSON-Dateien nach bestimmten Werten 

def filterJsonFile(
    jsonFilePath: Path,
    valuesToKeep: set[str],
    ):
    with jsonFilePath.open("r", encoding="utf-8") as file:
        data = json.load(file)

    # Rekursive Funktion die alle Ebenen des JSON-Dokuments durchläuft und nur die angegebenen Werte beibehält

    def reduceValues(value: Any):
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

    saveAsJasonFile(jsonFilePath, reducedData)

# Synicing Funktionen und Überprüfung des Syncs

def syncDocuments():
    startSession()
    documents = getChangedDocuments()
    for document in documents.get("documents", []):
        documentId = document["id"]
        metadataPath = METADATA_DIR / f"{documentId}.json"
        previousMetadata = {}
        if metadataPath.exists():
            with metadataPath.open("r", encoding="utf-8") as file:
                previousMetadata = json.load(file)

        saveAsJasonFile(metadataPath, document)

        if document.get("status") == "deleted":
            continue

        pdfPath = PDF_DIR / f"{documentId}.pdf"
        if (
            pdfPath.exists()
            and previousMetadata.get("sha256") == document.get("sha256")
        ):
            continue

        pdfData = downloadDocuments(documentId)
        saveAsPdfFile(pdfPath, pdfData)


def checkDocumentsWithCurrentMetadata() -> dict[str, list[str]]:
    metadata_ids = {
        metadata_path.stem
        for metadata_path in METADATA_DIR.glob("*.json")
    } if METADATA_DIR.exists() else set()
    pdf_ids = {
        pdf_path.stem
        for pdf_path in PDF_DIR.glob("*.pdf")
    } if PDF_DIR.exists() else set()

    return {
        "metadata_only": sorted(metadata_ids - pdf_ids),
        "pdf_only": sorted(pdf_ids - metadata_ids),
        "matching": sorted(metadata_ids & pdf_ids),
    }

def main():
    syncDocuments()
    report = checkDocumentsWithCurrentMetadata()
    print(json.dumps(report, indent=2, ensure_ascii=False))
if __name__ == "__main__":
    main()