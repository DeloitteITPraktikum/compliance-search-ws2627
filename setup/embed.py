"""Embed two texts through the gateway. Quickstart step 3.

    uv run --env-file .env embed.py
"""
import os

from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])
result = client.embeddings.create(
    model="qwen3-embedding",
    input=["Meldung schwerwiegender IKT-Vorfälle", "reporting of major ICT incidents"],
)
vectors = [item.embedding for item in result.data]
print(len(vectors), "vectors with", len(vectors[0]), "dimensions each")
