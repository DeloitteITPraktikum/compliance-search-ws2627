import json
from pathlib import Path

from compliance_search.processing.sections import Section, SectionLine


def save_json(data: dict | list, output_folder: Path, document_id: str) -> None:

    output_folder.mkdir(parents=True, exist_ok=True)

    file_path = output_folder / f"{document_id}LinesParsed.json"

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def save_jsonl(
    sections: list[Section],
    lines: list[SectionLine],
    output_folder: Path,
    document_id: str,
) -> None:
    """Write <document_id>.sections.jsonl and <document_id>.lines.jsonl, one object per line."""
    output_folder.mkdir(parents=True, exist_ok=True)

    sections_path = output_folder / f"{document_id}SectionsParsed.jsonl"
    lines_path = output_folder / f"{document_id}LinesParsed.jsonl"

    with sections_path.open("w", encoding="utf-8") as file:
        for section in sections:
            file.write(section.model_dump_json() + "\n")

    with lines_path.open("w", encoding="utf-8") as file:
        for line in lines:
            file.write(line.model_dump_json() + "\n")
