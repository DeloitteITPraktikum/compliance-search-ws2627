from pathlib import Path

from compliance_search.processing.sections import SectionLine


def save_jsonl(
    document_id: str,
    lines: list[SectionLine],
    output_folder: Path,
) -> None:
    """Write <document_id>LinesParsed.jsonl, one line object per row."""
    output_folder.mkdir(parents=True, exist_ok=True)

    lines_path = output_folder / f"{document_id}LinesParsed.jsonl"

    with lines_path.open("w", encoding="utf-8") as file:
        for line in lines:
            file.write(line.model_dump_json() + "\n")
