# The corpus

The start set holds 34 PDFs with 3,893 pages and 50.5 MB: 18 in English, 16 in German.
Almost half of the pages are one act, the CRR, with 897 pages in each language.
All of them are real, public regulation.
The set changes during the semester. Trust the [document API](03-document-api.md), not this page.

## What is in it

| Group | Documents | Languages |
|---|---|---|
| DORA | Regulation (EU) 2022/2554 on digital operational resilience | DE, EN |
| DORA technical standards | RTS 2024/1774 ICT risk management, RTS 2024/1772 incident classification, RTS 2024/1773 third-party policy, RTS 2025/301 incident report content, ITS 2025/302 incident report templates, RTS 2025/532 subcontracting | DE, EN |
| DORA technical standards | ITS 2024/2956 register of information | EN |
| Other EU acts | MiCA, consolidated 2024-01-09 | DE, EN |
| Other EU acts | CRD, consolidated 2026-01-11 | EN |
| Other EU acts | AI Act: Official Journal original in English, consolidated 2024-07-12 in German | DE, EN |
| DORA technical standards | RTS 2025/420 joint examination team for DORA oversight | DE, EN |
| Banking rules | CRR, Regulation (EU) No 575/2013 on capital requirements, consolidated 2026-01-01 | DE, EN |
| Banking rules | ITS 2024/3172 on Pillar 3 disclosures: the templates banks publish their figures in | DE, EN |
| Other EU acts | RTS 2016/98 colleges of supervisors | EN |
| BaFin circulars | MaRisk 06/2024 | DE |
| BaFin circulars | MaRisk 05/2023, annotated English text | EN |
| BaFin circulars | BAIT | DE, EN |
| BaFin circulars | VAIT | DE |
| EBA | Guidelines on outsourcing EBA/GL/2019/02 | DE, EN |

## Kinds of documents

| Kind | `doc_type` | What it is |
|---|---|---|
| EU regulation | `regulation` | A law that applies directly in every member state. The text in the Official Journal is the authentic one. |
| Technical standard (RTS, ITS) | `delegated_regulation`, `implementing_regulation` | A Commission act that fills in the detail of a regulation: thresholds, deadlines, templates. |
| Consolidated text | `consolidated` | An act with all its amendments worked in, as of one date. Handy to read, but not authentic. The CRR, CRD and MiCA files are of this kind. |
| Disclosure templates | `implementing_regulation` | ITS 2024/3172 is a short act with more than 40 annexes of table templates. The templates are empty forms: row numbers, row labels and column letters, no values. |
| Corrigendum | `corrigendum` | A short document that fixes an error in an act. |
| BaFin circular | `circular` | How the German supervisor reads the law: MaRisk, BAIT, VAIT. |
| EBA guideline | `guideline` | Guidance from the European Banking Authority. |

## Ids and families

A document id is `<designation>_<LANG>`. The language is the part after the last `_`.
Each version and each language has its own id. Ids are never reused.

| Source | Rule | Example |
|---|---|---|
| EUR-Lex act | The CELEX number | `32022R2554_EN` |
| EUR-Lex consolidated text | The CELEX number with the consolidation date | `02023R1114-20240109_DE` |
| EUR-Lex corrigendum | The CELEX number of the corrigendum with the brackets dropped: `R(01)` becomes `R01` | `<CELEX of the act>R01_EN` |
| BaFin | The circular number with `/` turned into `-` | `RS-06-2024-BA_DE` |
| EBA | The guideline number | `EBA-GL-2019-02_EN` |

The family id groups every version and language of one act.

| Source | Family rule | Example |
|---|---|---|
| EUR-Lex | The CELEX number of the base act: cut the date and the corrigendum suffix, write `3` as first digit | `32024R1689_EN` and `02024R1689-20240712_DE` both have family `32024R1689` |
| EUR-Lex corrigendum | The family of the act it corrects | |
| Amending or repealing act | Its own family | |
| BaFin | The short name across all versions | `MaRisk`, `BAIT`, `VAIT` |
| EBA | The guideline number | `EBA-GL-2019-02` |

Do not work the family out yourself. Read `family_id` from the API.

Relations (`supersedes`, `corrects` and so on) point both ways. As a rule they stay inside one language.
There is no `amends` or `repeals` field.

## How a human cites each type

Cite the smallest named unit, never the page alone. Pages differ between languages and versions.

| Type | Unit | Written as |
|---|---|---|
| EU act | Article, paragraph, point | `Article 19(4)`, in German `Art. 19 Abs. 4` |
| EU act, annex | Annex number in Roman numerals | `Annex III point 5`, `Anhang III` |
| EU act, lettered article | The letter is part of the number. 92a is not 92 | `Article 92a`, `Artikel 92a` |
| EU act, recital | Recital number | `Recital 12`, `Erwägungsgrund 12` |
| EU act, table inside an article | Article and table number | `Article 121, Table 1` |
| ITS table | Column code | `B_05.01.0090` |
| Pillar 3 template | Template code and row. Row numbers repeat across templates, so the code is a must | `Template EU OV1, row 26`, `EU KM1 row 14` |
| MaRisk | Module and Textziffer | `AT 4.3.4 Tz. 2`, `BTO 1.2` |
| BAIT, VAIT | Chapter and Textziffer | `Tz. 4.4`, `Kapitel 4` |
| EBA guidelines | Paragraph number | `paragraph 75`, `Tz. 75` |

Keep this label on every chunk when you ingest. The grader matches on it. See [How we score you](06-scoring.md#the-relevance-key).

## The legal notice

Your UI must show, for each source, who issued it and whether the text is binding.
Both strings come with every document: `attribution` and `binding_note`. Show them as they are.

| Source | `attribution` | `binding_note` |
|---|---|---|
| EUR-Lex, Official Journal | Source: EUR-Lex, https://eur-lex.europa.eu/. © European Union, 1998-2026. | Only European Union documents published in the Official Journal of the European Union are deemed authentic. |
| EUR-Lex, consolidated | The same, plus: Consolidated text, licensed under the Creative Commons Attribution 4.0 International licence. No changes made. | This text is meant purely as a documentation tool and has no legal effect. [...] |
| BaFin, German | © Bundesanstalt für Finanzdienstleistungsaufsicht / www.bafin.de | Deutscher Originaltext der BaFin, unverändert übernommen. |
| BaFin, English | © Federal Financial Supervisory Authority / www.bafin.de | This English version is provided for information purposes only. The original German text is binding in all respects. |
| EBA | Source: European Banking Authority, https://www.eba.europa.eu/ | [...] competent authorities and financial institutions must make every effort to comply with the guidelines. |

Do not change the PDFs. The terms of the sources allow you to store and show them unchanged, with the source line.

## Known oddities

| Oddity | What it means for you |
|---|---|
| MaRisk in English is the annotated text of 05/2023 with 119 pages. It is not a translation of the German 06/2024 circular. | What is new in 06/2024, such as BTR 5, has no English source. |
| The English EBA file is the final report with 125 pages and feedback tables. The German file holds only the guidelines on 43 pages. | Cite paragraph numbers, not pages. |
| The English AI Act is the Official Journal original. The German one is a consolidated text. | Page counts differ: 144 against 137. Cite by article. |
| Consolidated texts carry change markers (►B, ▼M1) and a header on every page. | Strip them before you chunk. |
| German texts carry soft hyphens (U+00AD) and hyphens at line ends. | Normalise both, or exact phrases will not match. |
| Page numbers differ between the Official Journal page, the PDF page and the header of a consolidated text. | Store the PDF page for the UI. Cite by article. |
| Annex tables in ITS 2024/2956 and ITS 2025/302 come out as row fragments. | Search them by column code such as `B_05.01.0090`. |
| MaRisk and BAIT mark binding text in bold. Text extraction loses it. BAIT is a two-column table. | Check what your parser makes of these pages. |
| VAIT says "Aufgehoben mit Ablauf des 16.01.2025" on its cover but is `active` in the API. | `active` means "current in this corpus", not "in force". |
| German Official Journal files carry the English `binding_note`. | Show it as it is. |
| Some acts exist in one language only, such as ITS 2024/2956 in English and VAIT in German. | A German question about them must still find the answer. |
| DORA has nine corrigenda that are not in the corpus. | Answer from what the corpus holds. |

### CRR and the Pillar 3 templates

| Oddity | What it means for you |
|---|---|
| 271 CRR articles carry a letter: 5a, 92a, 325a and so on. | A search for "Article 92" also hits 92a. Keep the letter in your label. |
| A deleted CRR article leaves only a rule line (`__________`), with no article number. There are about 40 such lines. | Your chunker sees no heading there. Do not let the line join the article before it. |
| Other parts of the CRR still point at deleted articles. | A cross-reference can lead to nothing. Say so in the answer; do not make up the text. |
| CRR section headings are letter-spaced: `S e c t i o n 2`, `O w n f u n d s`. | A phrase search on headings fails. |
| Many CRR rules are transitional and name their own end date. | Read the date from the text. `active` does not tell you. |
| Small tables sit inside CRR articles, such as the risk-weight tables. | The cells come out as a list of lines. Keep the table with its article, and test a lookup. |
| The Pillar 3 templates lose their column structure in PDF text. Headers and column letters come out on lines of their own, far from the cells. | Row lookups work: a row number is followed by its label. Do not trust a guess at which column holds what. |
| Row numbers repeat across the templates. Row `26` exists in several. | A row means nothing without its template code. Label each chunk with the code. |
| Some lists and their numbers sit in different places. The buckets of CRR Annex I are in the annex; their percentages are in an article. | One passage is often not enough. |
| ITS 2024/3172 has typos in the source. | Do not fix them in quotes. |

## What a full ingest costs

From our own build on the start set:

| Measure | Value |
|---|---|
| Chunks | about 5,700 |
| Embedding tokens | 2.8 million |
| Time | under four minutes |
| Cost | about 6 cents |

Parsing and chunking take seconds. The time goes into embedding.
So cache by file hash: a second run should embed nothing, and a new document should cost only itself. See [Models](04-models.md#cache-your-embeddings).
