"""Trivial chunking: split the text of each PDF into chunks of fixed size with overlap."""
import json
import re
from pathlib import Path

from pypdf import PdfReader

# Path to one test PDF, seen from the backend folder
PDF_PATH = Path("../data/pdfs/active/32025R0532_DE.pdf")

# Metadata of the same document (from the document API, saved by the sync)
METADATA_PATH = Path("../data/metadata/32025R0532_DE.json")

# Where the chunks are written (data/chunks/ is not in git )
CHUNKS_DIR = Path("../data/chunks")

CHUNK_SIZE = 2000  # characters per chunk (about 500 tokens)
OVERLAP = 200 # characters of overlap between chunks (10 %)

def clean (text : str) -> str:
    """Replace line breaks and multiple spaces with a single space."""
    return re.sub(r"\s+", " ", text).strip()

def cut (text : str, size: int, overlap: int) -> list[str]:
    """Cut text into pieces of `size` characters; each piece shares `overlap` characters with the next."""    
    chunks = []
    start =0
    while start < len(text):
       chunks.append(text[start:start+size])
       if start + size >= len(text):
              break
       start = start + size -overlap 
    return chunks


# Open the PDF
reader = PdfReader(PDF_PATH)

# Read the metadata: title, family_id, language, version ...
meta = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

# All chunks of the document, filled in the loop below
all_chunks = []

# Go through all pages and print the page number and the length of the text
for page_number, page in enumerate(reader.pages, start=1):
    text = clean(page.extract_text())
    pieces = cut(text, CHUNK_SIZE, OVERLAP)

    for number, piece in enumerate(pieces, start=1):
        all_chunks.append({
            "chunk_id": f"{meta['id']}#p{page_number}-{number}",
            "document_id": meta["id"],
            "family_id": meta["family_id"],
            "version": meta["version_date"],
            "language": meta["language"],
            "doc_type": meta["doc_type"],
            "page_start": page_number,
            "page_end": page_number,
            "text": piece,
        })

 # Save all chunks: one JSON object per line (JSONL)
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
chunks_file = CHUNKS_DIR / f"{meta['id']}TrivialChunks.jsonl"
with chunks_file.open("w", encoding="utf-8") as file:
    for chunk in all_chunks:
        file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print(f"{meta['id']}: {len(all_chunks)} chunks -> {chunks_file}")
