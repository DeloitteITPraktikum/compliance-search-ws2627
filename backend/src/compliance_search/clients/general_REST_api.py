"""General HTTP helpers shared by API clients."""

from collections import deque
from collections.abc import Mapping
from threading import Lock
import time
from typing import Any

import requests

MAX_REQUESTS_PER_MINUTE = 60

requestTimes: deque[float] = deque()
requestLock = Lock()


def sendApiRequest(
    session: requests.Session,
    method: str,
    url: str,
    *,
    params: dict[str, str] | None = None,
    jsonData: Mapping[str, Any] | list[Mapping[str, Any]] | list[str] | None = None,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 60,
) -> requests.Response:
    """Send a rate-limited HTTP request with Retry-After handling."""
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


def startSession(
    apiKey: str,
    *,
    headers: dict[str, str] | None = None,
) -> requests.Session:
    """Create an authenticated HTTP session."""
    if not apiKey:
        raise RuntimeError("API key is missing.")

    session = requests.Session()
    session.headers.update(headers or {})
    session.headers["Authorization"] = f"Bearer {apiKey}"
    session.headers.setdefault("Content-Type", "application/json")
    return session
