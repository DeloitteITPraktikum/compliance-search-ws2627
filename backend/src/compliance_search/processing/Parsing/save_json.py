import json
from pathlib import Path

from compliance_search.processing.sections import Section, SectionLine


def save_json(data: dict | list, output_folder: Path) -> None:

    output_folder.mkdir(parents=True, exist_ok=True)

    file_path = output_folder / "parsed_document.json"

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def save_jsonl(sections: list[Section], lines: list[SectionLine], output_folder: Path, document_id: str) -> None:
    """Write <document_id>.sections.jsonl and <document_id>.lines.jsonl, one object per line."""
    output_folder.mkdir(parents=True, exist_ok=True)

    for name, rows in (("sections", sections), ("lines", lines)):
        with open(output_folder / f"{document_id}.{name}.jsonl", 'w', encoding='utf-8') as file:
            for row in rows:
                file.write(row.model_dump_json() + "\n")
