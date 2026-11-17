# Document structure by `doc_type`

This folder describes, for each `doc_type` returned by the document API, which documents belong to it and how far their structure is the same on each level. It is meant as the basis for choosing a parser per document and for splitting documents into sections.

It complements [`../analyisis-compliance-documents.md`](../analyisis-compliance-documents.md). That analysis groups the documents into five structural classes by hand. The API field `doc_type` splits them into six types, and it is available for every new document, so the parser can be selected from it.

## Files

| `doc_type` | Documents | File |
|---|---:|---|
| `delegated_regulation` | 13 | [delegated_regulation.md](delegated_regulation.md) |
| `regulation` | 3 | [regulation.md](regulation.md) |
| `implementing_regulation` | 5 | [implementing_regulation.md](implementing_regulation.md) |
| `consolidated` | 6 | [consolidated.md](consolidated.md) |
| `guideline` | 2 | [guideline.md](guideline.md) |
| `circular` | 5 | [circular.md](circular.md) |

Mapping to the classes of the earlier analysis:

| Earlier class | `doc_type` |
|---|---|
| 1. European primary and secondary legislation | `regulation` (original texts) and `consolidated` (consolidated texts); `32016R0098` is `delegated_regulation` |
| 2. Regulatory Technical Standards (RTS) | `delegated_regulation` |
| 3. Implementing Technical Standards (ITS) | `implementing_regulation` |
| 4. EBA Guidelines | `guideline` |
| 5. BaFin circulars | `circular` |

## Levels

| Level | Meaning | Example |
|---|---|---|
| 1 | Large blocks of the document | recitals, enacting terms (articles), final formula, annexes |
| 2 | Grouping headings above the smallest numbered unit | Part, Title, Chapter, Section; MaRisk modules |
| 3 | Smallest numbered unit with its own heading or number | Article; numbered paragraph (Randnummer / Textziffer) |
| 4 | Parts inside that unit | paragraphs, points, sub-points |

Each file states per level how the documents are split, whether all documents of the type are the same, and where they differ.

## Summary: how far `doc_type` determines the structure

| `doc_type` | Level 1 | Level 2 | Level 3 | Level 4 |
|---|---|---|---|---|
| `delegated_regulation` | same in all | differs (none to three levels) | same (articles with title) | same per language, differs between DE and EN |
| `regulation` | same, annexes optional | differs | same | same per language, differs between DE and EN |
| `implementing_regulation` | same | none in the articles | same in the articles; annexes differ per document | same per language in the articles |
| `consolidated` | same | differs | same | same per language, differs between DE and EN |
| `guideline` | differs between DE and EN | same (Titles I–V, numbered sections) | same (paragraphs 1–119) | same (`a.`, `i.`) |
| `circular` | only "contents + body" in common | differs (MaRisk vs. BAIT/VAIT) | differs | differs |

Consequences for parsing:

- `doc_type` selects the parser. For the four EU types, level 1 is fixed by `doc_type`.
- Level 2 is not fixed by `doc_type` for any EU type. The parser has to detect which headings occur (Part, Title, Chapter, Section, Sub-section) and build the hierarchy from them. Section headings are sometimes extracted letter-spaced (`Se cti on I`, in DORA and `32024R1774`), and section numbers are Roman in some documents and Arabic in others.
- Level 4 depends on the language. In EU texts, English numbers paragraphs `1.` and points `(a)`; German numbers paragraphs `(1)` and points `a)`. Numbered definitions are the other way round (EN `(1)`, DE `1.`).
- For `guideline` and `circular`, the parser also has to recognise the variant of the document from its content.

## Method

- All 34 PDFs were downloaded with `setup/download_all_pdfs.py` and converted with `pdftotext -layout` (poppler).
- Headings and numbering were counted with regular expressions on the text. Each difference named in these files was also checked by reading the text.
- `doc_type`, titles and status come from `setup/documents.json` (API `/documents`).
- Counts can be off by a few hits, for example where a heading is split across a page break. They show the structure, they are not exact totals.
- Analysis date: 2026-11-16.
