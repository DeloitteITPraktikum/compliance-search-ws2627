# The corpus

The start set holds 34 real, public PDFs: 3,893 pages, 18 in English and 16 in German.
Almost half of the pages are one act, the CRR, with 897 pages in each language.
The set changes during the semester. Trust the [document API](03-document-api.md), not this page.

## What is in it

| Group | Documents | Languages |
|---|---|---|
| DORA | Regulation 2022/2554 and its technical standards (RTS, ITS) | DE, EN; ITS 2024/2956 EN only |
| Other EU acts | MiCA, CRD, AI Act, RTS 2016/98 | DE, EN; CRD and RTS 2016/98 EN only |
| Banking rules | CRR (575/2013) and the Pillar 3 templates (ITS 2024/3172) | DE, EN |
| BaFin circulars | MaRisk, BAIT, VAIT | MaRisk and BAIT DE, EN; VAIT DE only |
| EBA | Guidelines on outsourcing (EBA/GL/2019/02) | DE, EN |

The `doc_type` field tells regulations, technical standards, consolidated texts, corrigenda, circulars and guidelines apart.
A consolidated text has all amendments worked in. It is handy, but not the authentic text.

## Ids and families

An id is `<designation>_<LANG>`, for example `32022R2554_EN` or `RS-06-2024-BA_DE`. Each version and language has its own id.
`family_id` groups all versions and languages of one act: `32024R1689_EN` and `02024R1689-20240712_DE` are both family `32024R1689`.
Read `family_id` from the API. Do not work it out yourself.

## How to cite

Cite the smallest named unit, never the page alone: pages differ between languages and versions.
Keep this label on every chunk. The grader matches on it.

| Type | Written as |
|---|---|
| EU act | `Article 19(4)`, `Art. 19 Abs. 4`. A letter is part of the number: 92a is not 92 |
| Annex, recital | `Annex III point 5`, `Recital 12`, `Erwägungsgrund 12` |
| Table inside an article | `Article 121, Table 1` |
| ITS table | The column code: `B_05.01.0090` |
| Pillar 3 template | Template code and row: `EU KM1 row 14`. Row numbers repeat across templates |
| MaRisk | Module and Textziffer: `AT 4.3.4 Tz. 2` |
| BAIT, VAIT | `Tz. 4.4`, `Kapitel 4` |
| EBA guidelines | `paragraph 75` |

## The legal notice

Every document carries `attribution` (who issued it) and `binding_note` (whether the text is binding).
Show both, unchanged, next to each source. Do not change the PDFs: the sources allow storing and showing them as they are, with the source line.

## Known oddities

| Oddity | What it means for you |
|---|---|
| Consolidated texts carry markers (►B, ▼M1) and a header on every page | Strip them before you chunk |
| German texts carry soft hyphens (U+00AD) and hyphens at line ends | Normalise both, or exact phrases will not match |
| Tables come out as loose lines; Pillar 3 templates lose their columns | Keep each table with its article. Label template chunks with the template code |
| A deleted CRR article leaves only a rule line `__________` | It must not join the article before it |
| The English MaRisk is the annotated 05/2023 text, not a translation of 06/2024 | Its `outdated_by` points to the German text. BTR 5 has no English source |
| Some acts exist in one language only | A question in the other language must still find them |
| VAIT says "Aufgehoben" on its cover but is `active` | `active` means current in this corpus, not in force |
| Page numbers differ between PDF, Official Journal and header | Store the PDF page for the UI. Cite by article |
