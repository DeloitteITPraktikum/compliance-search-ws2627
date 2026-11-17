import os


from importlib.resources import open_binary
import json

def save_json(data: dict, output_folder: str) -> None:
    file_path = os.path.join(output_folder, "parsed_document.json")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)