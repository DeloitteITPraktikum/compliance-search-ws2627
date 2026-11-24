"""Trivial chunking: split the text of each PDF into chunks of fixed size with overlap."""
import json
import re
from pathlib import Path

from pypdf import PdfReader

# Folders with the PDFs and their metadata (both saved by the sync)
PDF_DIR = Path("../data/pdfs/active")
METADATA_DIR = Path("../data/metadata")


# Where the chunks are written (data/chunks/ is not in git )
CHUNKS_DIR = Path("../data/chunks/trivial")

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


def chunk_document(meta: dict) -> int:
    """Chunk one PDF and save its chunks as JSONL. Returns the number of chunks."""
    # Open the PDF that belongs to this metadata
    reader = PdfReader(PDF_DIR / f"{meta['id']}.pdf")

    # All chunks of the document, filled in the loop below
    all_chunks = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = clean(page.extract_text())
        pieces = cut(text, CHUNK_SIZE, OVERLAP)
        # Metadata needed for citations (document, version, page) and the grader (family_id).
        # Field names match processing/chunks.py.
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
    return len(all_chunks)

# Chunk every document that has a PDF
total = 0
for metadata_file in sorted(METADATA_DIR.glob("*.json")):
    meta = json.loads(metadata_file.read_text(encoding="utf-8"))
    if not (PDF_DIR / f"{meta['id']}.pdf").exists():
        continue
    total = total + chunk_document(meta)

print(f"done: {total} chunks")