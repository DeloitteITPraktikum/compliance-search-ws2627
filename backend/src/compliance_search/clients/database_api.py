"""Supabase REST and Storage API client."""

import hashlib
import json
import math
import os
import uuid
from collections.abc import Mapping, Sequence
from typing import Any

import requests
from compliance_search.clients.general_api import sendApiRequest

# Constants for the Supabase REST and Storage API client.
SUPABASE_PROJECT_URL = os.environ.get("SUPABASE_URL", "https://lnzvigpjsxzxdlndesdb.supabase.co")   
SUPABASE_REST_URL = f"{SUPABASE_PROJECT_URL}/rest/v1"
SUPABASE_DOCUMENT_STORAGE_BUCKET = "documents"
SUPABASE_API_KEY = os.environ.get("SUPABASE_API_KEY")


# Standard table functions
def insertTableRow(
    session: requests.Session,
    table: str,
    row: Mapping[str, Any],
    *,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Insert one row into a Supabase table and return its representation.

    Args:
        session: Authenticated HTTP session.
        table: Name of the target table. Must not be empty or contain
            ``/``, ``?``, or ``#``.
        row: Column names and values for the row. Must not be empty.
        timeout: Request timeout in seconds.

    Returns:
        The inserted row as a list of dictionaries, or an empty list if the
        response has no content.

    Raises:
        ValueError: If the table name is invalid or the row is empty.
        requests.HTTPError: If the Supabase request fails.
    """
    if not table or any(character in table for character in "/?#"):
        raise ValueError("table is invalid.")
    if not row:
        raise ValueError("row must not be empty.")

    response = sendApiRequest(
        session,
        "POST",
        f"{SUPABASE_REST_URL}/{table}",
        jsonData=dict(row),
        headers={"Prefer": "return=representation"},
        timeout=timeout,
    )
    return response.json() if response.content else []


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


# Print every row in a table as formatted JSON.
def printTable(
    session: requests.Session,
    table: str,
    *,
    pageSize: int = 1000,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Print and return all rows in a table, fetching them in pages.

    Args:
        session: Authenticated Supabase session.
        table: Name of the table to print.
        pageSize: Number of rows to request per page.
        timeout: Request timeout in seconds.

    Returns:
        All rows returned by the table.

    Raises:
        ValueError: If the table name or page size is invalid.
        requests.HTTPError: If a table request fails.
    """
    if pageSize < 1:
        raise ValueError("pageSize must be at least 1.")

    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        page = searchTableRows(
            session,
            table,
            {},
            limit=pageSize,
            offset=offset,
            timeout=timeout,
        )
        rows.extend(page)
        if len(page) < pageSize:
            break
        offset += pageSize

    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return rows


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
        ValueError: If the table or column name is invalid.
        requests.HTTPError: If the delete request fails.
    """
    if not table or any(character in table for character in "/?#"):
        raise ValueError("table is invalid.")
    if not column or any(character in column for character in "/?#"):
        raise ValueError("column is invalid.")

    response = sendApiRequest(
        session,
        "DELETE",
        f"{SUPABASE_REST_URL}/{table}",
        params={column: f"eq.{value}"},
        headers={"Prefer": "return=representation"},
        timeout=timeout,
    )
    return response.json() if response.content else []


# Update one field on the row selected by a column and value.
def updateTableField(
    session: requests.Session,
    table: str,
    rowColumn: str,
    rowValue: str,
    column: str,
    value: Any,
    *,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Update one column on rows matching the supplied row identifier.

    Args:
        session: Authenticated Supabase session.
        table: Name of the target table.
        rowColumn: Column used to identify the row.
        rowValue: Exact value expected in the identifying column.
        column: Column to update.
        value: New value for the column.
        timeout: Request timeout in seconds.

    Returns:
        The updated rows returned by Supabase.

    Raises:
        ValueError: If the table or either column name is invalid.
        requests.HTTPError: If the update request fails.
    """
    if not table or any(character in table for character in "/?#"):
        raise ValueError("table is invalid.")
    for columnName in (rowColumn, column):
        if not columnName or any(character in columnName for character in "/?#"):
            raise ValueError("column is invalid.")

    response = sendApiRequest(
        session,
        "PATCH",
        f"{SUPABASE_REST_URL}/{table}",
        params={rowColumn: f"eq.{rowValue}"},
        jsonData={column: value},
        headers={"Prefer": "return=representation"},
        timeout=timeout,
    )
    return response.json() if response.content else []

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