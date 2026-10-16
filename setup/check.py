"""Check your whole setup in one run: key, models, chat, embedding, documents, PDF.

    uv run --env-file .env check.py

Costs a fraction of a cent: one short answer from gpt-6-luna, the rest runs on
the free model `mock`. Exits 1 if a check fails.
"""
import os
import sys

import requests
from openai import OpenAI

GATEWAY = "https://tud-llm.pgoell.com/v1"
DOCS = "https://tud-docs.pgoell.com"

key = os.environ.get("GATEWAY_KEY", "")
if not key.startswith("sk-") or key == "sk-...":
    sys.exit("GATEWAY_KEY is missing. Copy .env.example to .env, paste your key, and run with --env-file .env")

client = OpenAI(base_url=GATEWAY, api_key=key)
headers = {"Authorization": f"Bearer {key}"}
results = []


def check(name, fn):
    try:
        results.append((name, True, fn()))
    except Exception as e:
        results.append((name, False, f"{type(e).__name__}: {e}"[:200]))


def chat(model):
    r = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": "Say OK."}], max_tokens=20, reasoning_effort="low"
    )
    return (r.choices[0].message.content or "").strip()[:60]


def documents():
    r = requests.get(f"{DOCS}/documents", headers=headers, timeout=30)
    r.raise_for_status()
    docs = r.json()["documents"]
    return f"{len(docs)} documents" + (" (empty until 2026-10-20 10:00)" if not docs else "")


def pdf():
    r = requests.get(f"{DOCS}/documents/32025R0301_EN/file", headers=headers, timeout=60)
    if r.status_code == 404:
        return "not published yet (online from 2026-10-20 10:00)"
    r.raise_for_status()
    assert r.content.startswith(b"%PDF"), "not a PDF"
    return f"{len(r.content)} bytes"


check("models", lambda: f"{len(client.models.list().data)} models")
check("chat, mock", lambda: chat("mock"))
check("chat, gpt-6-luna", lambda: chat("gpt-6-luna"))
check("embedding", lambda: f"{len(client.embeddings.create(model='qwen3-embedding', input=['test']).data[0].embedding)} dimensions")
check("document list", documents)
check("PDF download", pdf)

for name, ok, detail in results:
    print(f"{'ok  ' if ok else 'FAIL'}  {name:18} {detail}")
print("\nDashboard with your spend: https://tud-llm.pgoell.com/ui")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
