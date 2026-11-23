"""Chunk every parsed document: data/pdfs/parsed/ -> data/chunks/.

Run the parser first (processing/parsing/main.py). The document metadata comes
from data/metadata/<document_id>.json, written by the document sync.
"""
import json
from pathlib import Path

from compliance_search.processing.chunking.build_chunks import build_chunks
from compliance_search.processing.chunking.group_units import group_units
from compliance_search.processing.chunks import Chunk
from compliance_search.processing.sections import SectionLine

REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
DATA_FOLDER = REPOSITORY_ROOT / "data"
PARSED_FOLDER = DATA_FOLDER / "pdfs" / "parsed"
METADATA_FOLDER = DATA_FOLDER / "metadata"
OUTPUT_FOLDER = DATA_FOLDER / "chunks"


def read_lines(path: Path) -> list[SectionLine]:
    with path.open(encoding="utf-8") as file:
        return [SectionLine.model_validate_json(row) for row in file]


def save_chunks(document_id: str, chunks: list[Chunk]) -> None:
    """Write <document_id>Chunks.jsonl, one chunk object per row."""
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_FOLDER / f"{document_id}Chunks.jsonl").open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(chunk.model_dump_json() + "\n")


def main() -> None:
    parsed_files = sorted(PARSED_FOLDER.glob("*LinesParsed.jsonl"))
    print(f"Chunking {len(parsed_files)} documents from {PARSED_FOLDER.relative_to(REPOSITORY_ROOT)}")

    for parsed_file in parsed_files:
        document_id = parsed_file.name.removesuffix("LinesParsed.jsonl")
        metadata = json.loads((METADATA_FOLDER / f"{document_id}.json").read_text(encoding="utf-8"))

        chunks = build_chunks(group_units(read_lines(parsed_file)), metadata)
        save_chunks(document_id, chunks)

        articles = sum(chunk.unit_type == "article" for chunk in chunks)
        largest = max(chunks, key=lambda chunk: len(chunk.embedding_text))
        print(f"  {document_id}: {articles} articles · {len(chunks) - articles} recitals · "
              f"largest {largest.label} ({len(largest.embedding_text):,} characters)")

    print(f"Written to {OUTPUT_FOLDER.relative_to(REPOSITORY_ROOT)}")


if __name__ == "__main__":
    main()
