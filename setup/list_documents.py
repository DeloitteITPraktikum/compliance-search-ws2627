"""List the documents of the document API. Quickstart step 4.

    uv run --env-file .env list_documents.py

Before 2026-10-20 the list is empty. That is not an error.
"""
import os
import json
from pathlib import Path

import requests

DOCS = "https://tud-docs.pgoell.com"
headers = {"Authorization": f"Bearer {os.environ['GATEWAY_KEY']}"}

response = requests.get(f"{DOCS}/documents", headers=headers, timeout=30)
response.raise_for_status()
body = response.json()
output_file = Path(__file__).with_name("documents.json")
output_file.write_text(
    json.dumps(body, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print("server_time:", body["server_time"])
for doc in body["documents"]:
    print(doc["id"], doc["status"], doc["language"], doc["pages"], "pages")
print(len(body["documents"]), "documents")
