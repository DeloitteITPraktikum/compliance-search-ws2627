import os
import math
from collections.abc import Iterable, Sequence
from typing import Any

from openai import OpenAI

# Constants for the embedding API client.
MODEL_NAME = "qwen3-embedding"
GATEWAY_URL = "https://tud-llm.pgoell.com/v1"
MAX_TEXTS_PER_REQUEST = 150
DIMENSIONS = 1024

# Start an OpenAI-compatible client for the embedding gateway.
def startEmbeddingClient(
    apiKey: str | None = None,
    baseUrl: str | None = None,
    maxRetries: int = 2,
) -> OpenAI:
    """Create an OpenAI-compatible client for the model gateway.

    Args:
        apiKey: Gateway key sent as the Bearer token. If omitted, the
            ``GATEWAY_KEY`` environment variable is used.
        baseUrl: Base URL of the OpenAI-compatible gateway. If omitted,
            ``https://tud-llm.pgoell.com/v1`` is used.
        maxRetries: Number of retries the OpenAI SDK may perform for
            retryable HTTP and network failures.

    Returns:
        A configured ``OpenAI`` client with the embedding gateway URL.

    Raises:
        RuntimeError: If neither ``apiKey`` nor ``GATEWAY_KEY`` is available.
    """
    key = apiKey or os.environ.get("GATEWAY_KEY")
    if not key:
        raise RuntimeError("GATEWAY_KEY is missing!")

    return OpenAI(
        base_url= baseUrl or GATEWAY_URL,
        api_key=key,
        max_retries=maxRetries,
    )

# Create a single embedding vector for one text.
def createEmbedding(
    client: OpenAI,
    text: str,
) -> list[float]:
    """Create one 1024-dimensional vector for a single text.

    Args:
        client: Configured OpenAI-compatible gateway client.
        text: Text to embed. It must be a non-empty string.

    Returns:
        A list of exactly 1024 floating-point embedding values.

    Raises:
        TypeError: If ``text`` is not a string.
        ValueError: If ``text`` is empty or contains only whitespace.
        RuntimeError: If the gateway returns no vector or an invalid size.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string.")
    if not text.strip():
        raise ValueError("text must not be empty.")

    result = client.embeddings.create(
        model=MODEL_NAME,
        input=[text],
    )
    if not result.data:
        raise RuntimeError("The embedding API returned no vectors.")

    embedding = result.data[0].embedding
    if len(embedding) != DIMENSIONS:
        raise RuntimeError(
            f"Expected {DIMENSIONS} embedding dimensions, "
            f"but received {len(embedding)}."
        )
    return embedding

# Create embedding vectors for multiple texts with batching.
def createEmbeddings(
    client: OpenAI,
    texts: Iterable[str],
) -> list[list[float]]:
    """Create vectors for multiple texts with gateway-compatible batching.

    Args:
        client: Configured OpenAI-compatible gateway client.
        texts: Iterable of non-empty text strings to embed.

    Returns:
        A list of embedding vectors in input order. Every vector contains
        exactly 1024 values.

    Raises:
        TypeError: If an input item is not a string.
        ValueError: If an input text is empty or contains only whitespace.
        RuntimeError: If the gateway returns an unexpected vector count or
            a vector with invalid dimensions.
    """
    textList = list(texts)
    if not textList:
        return []
    if any(not isinstance(text, str) for text in textList):
        raise TypeError("Every input text must be a string.")
    if any(not text.strip() for text in textList):
        raise ValueError("Input texts must not be empty.")

    embeddingList: list[list[float]] = []
    for start in range(0, len(textList), MAX_TEXTS_PER_REQUEST):
        batch = textList[start:start + MAX_TEXTS_PER_REQUEST]
        result = client.embeddings.create(
            model=MODEL_NAME,
            input=batch,
        )

        if len(result.data) != len(batch):
            raise RuntimeError(
                f"The embedding API returned {len(result.data)} vectors "
                f"for {len(batch)} input texts."
            )

        batchEmbeddings = [item.embedding for item in result.data]
        for embedding in batchEmbeddings:
            if len(embedding) != DIMENSIONS:
                raise RuntimeError(
                    f"Expected {DIMENSIONS} embedding dimensions, "
                    f"but received {len(embedding)}."
                )
        embeddingList.extend(batchEmbeddings)

    return embeddingList

def embeddingDimensions() -> int:
    """Return the configured qwen3-embedding vector dimension."""
    return DIMENSIONS


