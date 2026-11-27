from pathlib import Path
from typing import Any
import json
import requests
from compliance_search.clients.general_REST_api import sendApiRequest

def healthCheck(session: requests.Session, docsUrl: str) -> bool:
    """Check whether the document API at the specified URL is reachable."""
    try: 
        sendApiRequest(session, "GET", f"{docsUrl}/health", timeout=10)
        return True
    except requests.RequestException:
        return False

def listDocuments(
    session: requests.Session,
    docsUrl: str,
    changedSince: str | None = None,
) -> dict[str, Any]:
    """Retrieve all documents or only documents changed since the specified timestamp."""
    params = {"changed_since": changedSince} if changedSince is not None else None
    response = sendApiRequest(
        session,
        "GET",
        f"{docsUrl}/documents",
        params=params,
        timeout=60,
    )
    return response.json()

def getChangedDocuments(
    session: requests.Session,
    docsUrl: str,
    stateFile: Path,
    changedSince: str | None = None,
) -> dict[str, Any]:
    """Retrieve changed documents, optionally using the timestamp stored in stateFile."""
    if changedSince is None and stateFile.exists():
        with stateFile.open("r", encoding="utf-8") as file:
            state = json.load(file)
        changedSince = state.get("server_time")

    result = listDocuments(session, docsUrl, changedSince)
    return result

def downloadMetadata(
    session: requests.Session,
    docsUrl: str,
    doc_id: str,
) -> dict[str, Any]:
    """Download and return the metadata for a document by its ID."""
    response = sendApiRequest(
        session,
        "GET",
        f"{docsUrl}/documents/{doc_id}",
        timeout=60,
    )
    return response.json()
    
def downloadDocuments(
    session: requests.Session,
    docsUrl: str,
    doc_id: str,
) -> bytes:
    """Download and return the binary file content for a document by its ID."""
    response = sendApiRequest(
        session,
        "GET",
        f"{docsUrl}/documents/{doc_id}/file",
        timeout=60,
    )
    return response.content