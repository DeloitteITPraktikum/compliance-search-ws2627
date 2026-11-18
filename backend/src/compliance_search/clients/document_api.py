from pathlib import Path
from typing import Any
import json
import time
from collections import deque
from threading import Lock
import requests

requestTimes: deque[float] = deque()
requestLock = Lock()
MAX_REQUESTS_PER_MINUTE = 60

def sendApiRequest(
    session: requests.Session,
    method: str,
    url: str,
    *,
    params: dict[str, str] | None = None,
    timeout: int = 60,
) -> requests.Response:
    """Send an API request with sliding-window rate limiting and Retry-After handling."""
    for attempt in range(5):
        with requestLock:
            now = time.monotonic()
            while requestTimes and now - requestTimes[0] >= 60:
                requestTimes.popleft()

            if len(requestTimes) >= MAX_REQUESTS_PER_MINUTE:
                waitSeconds = 60 - (now - requestTimes[0]) + 0.1
                time.sleep(waitSeconds)

            requestTimes.append(time.monotonic())

        response = session.request(method, url, params=params, timeout=timeout)

        if response.status_code != 429:
            response.raise_for_status()
            return response

        retryAfter = response.headers.get("Retry-After")
        try:
            waitSeconds = float(retryAfter) if retryAfter else 2 ** attempt
        except (TypeError, ValueError):
            waitSeconds = 2 ** attempt
        time.sleep(max(waitSeconds, 0.1))

    raise requests.HTTPError(
        "API request limit persisted after five retries.",
        response=response,
    )

def startSession(gatewayKey: str) -> requests.Session:
    """Create an HTTP session and configure the gateway key as a Bearer token."""
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {gatewayKey}"
    return session

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