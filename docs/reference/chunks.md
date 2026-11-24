# Chunks

The output of the chunker and the input of embedding and storage. One chunk is one citable unit: one article or one recital. Why: [decision 0010](../decisions/0010-chunk-delegated-regulations-by-article.md).

For now only documents of doc_type `delegated_regulation` are chunked.

## Run it

From `backend/`, after the parser:

```sh
uv run python -m compliance_search.processing.parsing.main
uv run python -m compliance_search.processing.chunking.main
```

The chunker reads `data/pdfs/parsed/<document_id>LinesParsed.jsonl` and `data/metadata/<document_id>.json`, and writes `data/chunks/<document_id>Chunks.jsonl`, one chunk per line. `data/chunks/` is not in git.

## Fields

Defined in `backend/src/compliance_search/processing/chunks.py`.

| Field | Example | Meaning |
|---|---|---|
| `chunk_id` | `32025R0301_EN#Article 5` | `<document_id>#<label>`, unique |
| `document_id` | `32025R0301_EN` | `id` from the document API |
| `family_id` | `32025R0301` | From the document API. The grader matches on it |
| `version` | `2024-10-23` | `version_date` from the document API |
| `language` | `EN` | `DE` or `EN` |
| `doc_type` | `delegated_regulation` | From the document API |
| `unit_type` | `article` | `article` or `recital` |
| `label` | `Article 5`, `Recital 12` | The citation label. `keys.normalize_article` reads it as `art:5`, `recital:12` |
| `title` | `Time limits` | The article title. `null` for recitals |
| `headings` | `["CHAPTER I GENERAL PROVISIONS"]` | Grouping headings above the article (title, chapter, section), outermost first. Empty for recitals |
| `page_start`, `page_end` | `2`, `3` | PDF pages the unit covers |
| `text` | `The initial notification shall …` | The unit's text without its number and title. Use it for quotes |
| `embedding_text` | `<context line>\n<text>` | The input for the embedding. The context line is document title, headings and `<label> – <title>`, joined with ` \| ` |
| `chunker_version` | `1` | Rises when the chunking rules change |
| `text_hash` | `3f1c…` | SHA-256 of `embedding_text`. Key for the embedding cache |

## What is not chunked

`header`, `citations`, `enacting_formula`, `final_formula` and `footnotes`, and the introduction line before recital 1 (`Whereas:` / `in Erwägung nachstehender Gründe:`).
