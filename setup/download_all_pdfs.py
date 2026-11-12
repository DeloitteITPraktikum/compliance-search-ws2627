"""Download every available PDF into downloads/ without replacing existing files.

    uv run --env-file .env download_all_pdfs.py
"""
import os
from pathlib import Path

import requests

DOCS = os.environ.get("DOCS_URL", "https://tud-docs.pgoell.com").rstrip("/")
DOWNLOADS = Path(__file__).parent / "downloads"


def main() -> None:
    headers = {"Authorization": f"Bearer {os.environ['GATEWAY_KEY']}"}
    response = requests.get(f"{DOCS}/documents", headers=headers, timeout=30)
    response.raise_for_status()
    documents = response.json()["documents"]
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0
    for document in documents:
        if document["status"] == "deleted":
            continue

        output = DOWNLOADS / f"{document['id']}.pdf"
        if output.exists():
            print("skip", output)
            skipped += 1
            continue

        file_response = requests.get(
            f"{DOCS}/documents/{document['id']}/file",
            headers=headers,
            timeout=60,
        )
        file_response.raise_for_status()
        output.write_bytes(file_response.content)
        print("saved", output, len(file_response.content), "bytes")
        downloaded += 1

    print(f"downloaded {downloaded}, skipped {skipped}")


if __name__ == "__main__":
    main()
