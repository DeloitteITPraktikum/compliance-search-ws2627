# Analysis

Analyses made while building the parsing and chunking step (DEL-11). They answer one question: can the API field `doc_type` select the parser for a document, and how far is the structure of the documents the same within each type?

## Reading order

1. [`doc-type-structure/README.md`](doc-type-structure/README.md): overview of the six `doc_type`s, the four structure levels, and what this means for parsing.
2. The file for the `doc_type` you work on, for example [`doc-type-structure/regulation.md`](doc-type-structure/regulation.md): documents, sections and numbering per level.
3. [`doc-type-structure/doc_type_analysis.md`](doc-type-structure/doc_type_analysis.md): the opening phrase of every level-1 section for all types on one page (EN and DE). The section names in the code come from here.

## Folders

| Folder | Contents |
|---|---|
| [`doc-type-structure/`](doc-type-structure/) | The analysis itself, one Markdown file per `doc_type` |
| [`labeled-pdfs/`](labeled-pdfs/) | The source PDFs with their level-1 sections labeled, one subfolder per `doc_type` (`circular` is split into `MaRisk/` and `BAIT-VAIT/`) |
