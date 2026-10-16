"""Download one PDF into downloads/. Quickstart step 5.

    uv run --env-file .env download_pdf.py 32025R0301_EN
"""
import argparse
import os
from pathlib import Path

import requests

DOCS = "https://tud-docs.pgoell.com"
p = argparse.ArgumentParser()
p.add_argument("doc_id", nargs="?", default="32025R0301_EN")
args = p.parse_args()
headers = {"Authorization": f"Bearer {os.environ['GATEWAY_KEY']}"}

response = requests.get(f"{DOCS}/documents/{args.doc_id}/file", headers=headers, timeout=60)
response.raise_for_status()
out = Path(__file__).parent / "downloads" / f"{args.doc_id}.pdf"
out.parent.mkdir(exist_ok=True)
out.write_bytes(response.content)
print("saved", out, len(response.content), "bytes, ETag", response.headers["ETag"])
