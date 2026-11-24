"""Supabase REST and Storage API client."""

import hashlib
import os
import time
from collections import deque
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

import requests

# Constants for the Supabase REST and Storage API client.
SUPABASE_PROJECT_URL = "https://lnzvigpjsxzxdlndesdb.supabase.co"
SUPABASE_REST_URL = f"{SUPABASE_PROJECT_URL}/rest/v1"
SUPABASE_DOCUMENT_STORAGE_BUCKET = "documents"
MAX_REQUESTS_PER_MINUTE = 60
SUPABASE_API_KEY = os.environ.get("SUPABASE_API_KEY")

requestTimes: deque[float] = deque()
requestLock = Lock()


# General API functions

# Send a rate-limited request to the Supabase API.
def sendApiRequest(
    session: requests.Session,
    method: str,
    url: str,
    *,
    params: dict[str, str] | None = None,
    jsonData: Mapping[str, Any] | list[Mapping[str, Any]] | None = None,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 60,
) -> requests.Response:
    """Send a rate-limited Supabase API request with Retry-After handling.

    Args:
        session: Authenticated requests session.
        method: HTTP method, for example ``GET`` or ``POST``.
        url: Complete Supabase API URL.
        params: Optional query parameters.
        jsonData: Optional mapping or list of mappings encoded as JSON.
        data: Optional raw request-body bytes.
        headers: Optional HTTP headers.
        timeout: Request timeout in seconds.

    Returns:
        The HTTP response after a successful request.

    Raises:
        requests.HTTPError: If the response has an HTTP error status or if
            the request limit remains active after five retries.
    """
    for attempt in range(5):
        with requestLock:
            now = time.monotonic()
            while requestTimes and now - requestTimes[0] >= 60:
                requestTimes.popleft()

            if len(requestTimes) >= MAX_REQUESTS_PER_MINUTE:
                waitSeconds = 60 - (now - requestTimes[0]) + 0.1
                time.sleep(waitSeconds)

            requestTimes.append(time.monotonic())

        response = session.request(
            method,
            url,
            params=params,
            json=dict(jsonData) if isinstance(jsonData, Mapping) else jsonData,
            data=data,
            headers=headers,
            timeout=timeout,
        )

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


# Create an authenticated Supabase session.
def startSession(apiKey: str | None = None) -> requests.Session:
    """Create a session authenticated with the Supabase API key.

    Args:
        apiKey: Supabase API key. If omitted, ``SUPABASE_API_KEY`` is used.

    Returns:
        A requests session configured for Supabase REST and Storage requests.

    Raises:
        RuntimeError: If no API key is available.
    """
    key = apiKey or SUPABASE_API_KEY
    if not key:
        raise RuntimeError("SUPABASE_API_KEY is missing.")

    session = requests.Session()
    session.headers.update({
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    })
    return session


# Table functions

# List the available tables and their column names.
def listTablesAndHeaders(
    session: requests.Session,
    timeout: int = 30,
) -> dict[str, list[str]]:
    """Return table names and their column names from the Supabase API schema.

    Args:
        session: Authenticated Supabase session.
        timeout: Request timeout in seconds.

    Returns:
        A mapping from table names to their column names.

    Raises:
        requests.HTTPError: If the schema request fails.
    """
    response = sendApiRequest(
        session,
        "GET",
        f"{SUPABASE_REST_URL}/",
        headers={"Accept": "application/openapi+json"},
        timeout=timeout,
    )
    schema = response.json()

    tables: dict[str, list[str]] = {}
    for definitionName, definition in schema.get("definitions", {}).items():
        properties = definition.get("properties", {})
        tables[definitionName] = list(properties)

    if tables:
        return tables

    for path in schema.get("paths", {}):
        tableName = path.strip("/")
        if tableName and "/" not in tableName:
            tables.setdefault(tableName, [])
    return tables


# Insert or upsert one or more table rows.
def saveTableRows(
    session: requests.Session,
    table: str,
    rows: Mapping[str, Any] | list[Mapping[str, Any]],
    *,
    onConflict: str | None = None,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Insert or upsert one row or multiple rows in a Supabase table.

    Args:
        session: Authenticated Supabase session.
        table: Name of the target table.
        rows: One row mapping or a list of row mappings.
        onConflict: Optional column used for merge-duplicate upserts.
        timeout: Request timeout in seconds.

    Returns:
        The inserted or updated rows returned by Supabase.

    Raises:
        ValueError: If the table name or row payload is invalid.
        requests.HTTPError: If the insert or upsert request fails.
    """
    if not table or any(character in table for character in "/?#"):
        raise ValueError("table is invalid.")
    if isinstance(rows, Mapping):
        payload: Mapping[str, Any] | list[Mapping[str, Any]] = dict(rows)
    else:
        payload = [dict(row) for row in rows]
    if not payload:
        raise ValueError("rows must not be empty.")

    headers = {
        "Prefer": (
            "resolution=merge-duplicates,return=representation"
            if onConflict
            else "return=representation"
        ),
    }
    params = {"on_conflict": onConflict} if onConflict else None
    response = sendApiRequest(
        session,
        "POST",
        f"{SUPABASE_REST_URL}/{table}",
        params=params,
        jsonData=payload,
        headers=headers,
        timeout=timeout,
    )
    return response.json() if response.content else []


# Download table rows in JSON or CSV format.
def downloadTable(
    session: requests.Session,
    table: str,
    *,
    dataFormat: str = "json",
    filters: Mapping[str, str] | None = None,
    timeout: int = 30,
) -> list[dict[str, Any]] | str:
    """Download table rows as JSON or CSV without saving a local file.

    Args:
        session: Authenticated Supabase session.
        table: Name of the source table.
        dataFormat: Output format, either ``json`` or ``csv``.
        filters: Optional PostgREST query filters.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON rows or CSV text.

    Raises:
        ValueError: If the table name or data format is invalid.
        requests.HTTPError: If the download request fails.
    """
    if not table or any(character in table for character in "/?#"):
        raise ValueError("table is invalid.")

    normalizedFormat = dataFormat.lower()
    if normalizedFormat not in {"json", "csv"}:
        raise ValueError("dataFormat must be 'json' or 'csv'.")

    headers = {
        "Accept": (
            "application/json"
            if normalizedFormat == "json"
            else "text/csv"
        ),
    }
    response = sendApiRequest(
        session,
        "GET",
        f"{SUPABASE_REST_URL}/{table}",
        params=dict(filters or {}),
        headers=headers,
        timeout=timeout,
    )
    if normalizedFormat == "csv":
        return response.text
    return response.json()


# Search table rows using PostgREST filters.
def searchTableRows(
    session: requests.Session,
    table: str,
    filters: Mapping[str, str],
    *,
    columns: str = "*",
    limit: int | None = None,
    offset: int | None = None,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Search rows by column entries and return matching rows.

    Filters use Supabase/PostgREST syntax, for example:
    ``{"status": "eq.active", "doc_type": "eq.consolidated"}``.

    Args:
        session: Authenticated Supabase session.
        table: Name of the source table.
        filters: PostgREST filter parameters.
        columns: Comma-separated columns to select.
        limit: Optional maximum number of returned rows.
        offset: Optional number of rows to skip.
        timeout: Request timeout in seconds.

    Returns:
        A list of matching table rows.

    Raises:
        ValueError: If the table, columns, limit, or offset is invalid.
        requests.HTTPError: If the search request fails.
    """
    if not table or any(character in table for character in "/?#"):
        raise ValueError("table is invalid.")
    if not columns.strip():
        raise ValueError("columns must not be empty.")
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1.")
    if offset is not None and offset < 0:
        raise ValueError("offset must not be negative.")

    params: dict[str, str] = {
        "select": columns,
        **dict(filters),
    }
    if limit is not None:
        params["limit"] = str(limit)
    if offset is not None:
        params["offset"] = str(offset)

    response = sendApiRequest(
        session,
        "GET",
        f"{SUPABASE_REST_URL}/{table}",
        params=params,
        timeout=timeout,
    )
    return response.json()


# Download exactly one matching table row.
def downloadTableRow(
    session: requests.Session,
    table: str,
    column: str,
    value: str,
    *,
    columns: str = "*",
    timeout: int = 30,
) -> dict[str, Any] | None:
    """Download exactly one table row by a column value.

    Args:
        session: Authenticated Supabase session.
        table: Name of the source table.
        column: Column used to identify the row.
        value: Exact value expected in the column.
        columns: Comma-separated columns to select.
        timeout: Request timeout in seconds.

    Returns:
        The first matching row, or ``None`` if no row exists.

    Raises:
        ValueError: If the table, column, or selected columns are invalid.
        requests.HTTPError: If the download request fails.
    """
    if not table or any(character in table for character in "/?#"):
        raise ValueError("table is invalid.")
    if not column or "/" in column or "?" in column or "#" in column:
        raise ValueError("column is invalid.")
    if not columns.strip():
        raise ValueError("columns must not be empty.")

    response = sendApiRequest(
        session,
        "GET",
        f"{SUPABASE_REST_URL}/{table}",
        params={
            "select": columns,
            column: f"eq.{value}",
            "limit": "1",
        },
        timeout=timeout,
    )
    rows = response.json()
    return rows[0] if rows else None


# Delete table rows that match all supplied filters.
def deleteTableRows(
    session: requests.Session,
    table: str,
    filters: Mapping[str, str],
    *,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Delete matching table rows and return the deleted rows.

    Args:
        session: Authenticated Supabase session.
        table: Name of the source table.
        filters: Required PostgREST filter parameters.
        timeout: Request timeout in seconds.

    Returns:
        The deleted rows when Supabase returns representations.

    Raises:
        ValueError: If the table name is invalid or no filters are supplied.
        requests.HTTPError: If the delete request fails.
    """
    if not table or any(character in table for character in "/?#"):
        raise ValueError("table is invalid.")
    if not filters:
        raise ValueError("At least one delete filter is required.")

    response = sendApiRequest(
        session,
        "DELETE",
        f"{SUPABASE_REST_URL}/{table}",
        params=dict(filters),
        headers={"Prefer": "return=representation"},
        timeout=timeout,
    )
    return response.json() if response.content else []


# Delete rows identified by one exact column value.
def deleteTableRow(
    session: requests.Session,
    table: str,
    column: str,
    value: str,
    *,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Delete exactly matching rows identified by a column value.

    Args:
        session: Authenticated Supabase session.
        table: Name of the source table.
        column: Column used to identify the rows.
        value: Exact value expected in the column.
        timeout: Request timeout in seconds.

    Returns:
        The deleted rows returned by Supabase.

    Raises:
        ValueError: If the column name is invalid.
        requests.HTTPError: If the delete request fails.
    """
    if not column or "/" in column or "?" in column or "#" in column:
        raise ValueError("column is invalid.")

    return deleteTableRows(
        session,
        table,
        {column: f"eq.{value}"},
        timeout=timeout,
    )


# Store document metadata in the documents table.
def uploadDocument(
    session: requests.Session,
    metadata: Mapping[str, Any],
    *,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Upload one document metadata row to the documents table.

    Args:
        session: Authenticated Supabase session.
        metadata: Document metadata containing at least a unique ``id``.
        timeout: Request timeout in seconds.

    Returns:
        The inserted or updated document row.

    Raises:
        ValueError: If metadata does not contain a non-empty document ID.
        requests.HTTPError: If the table upsert fails.
    """
    documentId = metadata.get("id")
    if not isinstance(documentId, str) or not documentId.strip():
        raise ValueError("metadata must contain a unique 'id'.")

    now = datetime.now(timezone.utc).isoformat()
    row = {
        "id": documentId,
        "doc_type": metadata.get("doc_type"),
        "sha256": metadata.get("sha256"),
        "last_synced_at": now,
        "version_date": metadata.get("version_date"),
        "status": metadata.get("status", "active"),
        "metadata": dict(metadata),
    }
    return saveTableRows(
        session,
        "documents",
        row,
        onConflict="id",
        timeout=timeout,
    )


# PDF storage functions

# Upload PDF bytes to Supabase Storage.
def uploadPdf(
    session: requests.Session,
    pdfBytes: bytes,
    documentId: str,
    *,
    bucket: str = SUPABASE_DOCUMENT_STORAGE_BUCKET,
    timeout: int = 60,
) -> dict[str, Any]:
    """Upload PDF bytes to Supabase Storage and return storage information.

    Args:
        session: Authenticated Supabase session.
        pdfBytes: Non-empty PDF file content.
        documentId: Document identifier used as the storage filename.
        bucket: Supabase Storage bucket name.
        timeout: Request timeout in seconds.

    Returns:
        Storage response data enriched with bucket, path, SHA-256, and size.

    Raises:
        ValueError: If the document ID or PDF bytes are invalid.
        requests.HTTPError: If the upload request fails.
    """
    if not documentId or "/" in documentId or "\\" in documentId:
        raise ValueError("documentId is invalid.")
    if not pdfBytes:
        raise ValueError("pdfBytes must not be empty.")

    sha256 = hashlib.sha256(pdfBytes).hexdigest()
    storagePath = f"{documentId}.pdf"
    response = sendApiRequest(
        session,
        "PUT",
        f"{SUPABASE_PROJECT_URL}/storage/v1/object/{bucket}/{storagePath}",
        data=pdfBytes,
        headers={
            "Content-Type": "application/pdf",
            "x-upsert": "true",
        },
        timeout=timeout,
    )

    result = response.json() if response.content else {}
    if isinstance(result, dict):
        result.update({
            "bucket": bucket,
            "path": storagePath,
            "sha256": sha256,
            "size_bytes": len(pdfBytes),
        })
    return result


# Download a PDF from Supabase Storage.
def downloadPdf(
    session: requests.Session,
    documentId: str,
    *,
    bucket: str = SUPABASE_DOCUMENT_STORAGE_BUCKET,
    timeout: int = 60,
) -> bytes:
    """Download a PDF by document ID and return its bytes.

    Args:
        session: Authenticated Supabase session.
        documentId: Document identifier used as the storage filename.
        bucket: Supabase Storage bucket name.
        timeout: Request timeout in seconds.

    Returns:
        The PDF file content.

    Raises:
        ValueError: If the document ID is invalid.
        requests.HTTPError: If the download request fails.
    """
    if not documentId or "/" in documentId or "\\" in documentId:
        raise ValueError("documentId is invalid.")

    storagePath = f"{documentId}.pdf"
    response = sendApiRequest(
        session,
        "GET",
        f"{SUPABASE_PROJECT_URL}/storage/v1/object/{bucket}/{storagePath}",
        timeout=timeout,
    )
    return response.content


# Delete a PDF from Supabase Storage.
def deletePdf(
    session: requests.Session,
    documentId: str,
    *,
    bucket: str = SUPABASE_DOCUMENT_STORAGE_BUCKET,
    timeout: int = 60,
) -> list[dict[str, Any]]:
    """Delete a document PDF from Supabase Storage.

    Args:
        session: Authenticated Supabase session.
        documentId: Document identifier used as the storage filename.
        bucket: Supabase Storage bucket name.
        timeout: Request timeout in seconds.

    Returns:
        The Storage API deletion result, or an empty list.

    Raises:
        ValueError: If the document ID is invalid.
        requests.HTTPError: If the delete request fails.
    """
    if not documentId or "/" in documentId or "\\" in documentId:
        raise ValueError("documentId is invalid.")

    storagePath = f"{documentId}.pdf"
    response = sendApiRequest(
        session,
        "DELETE",
        f"{SUPABASE_PROJECT_URL}/storage/v1/object/{bucket}",
        jsonData={"prefixes": [storagePath]},
        headers={"Content-Type": "application/json"},
        timeout=timeout,
    )
    result = response.json() if response.content else []
    return result if isinstance(result, list) else []