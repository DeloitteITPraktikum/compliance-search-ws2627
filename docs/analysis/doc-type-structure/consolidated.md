# `consolidated`

Consolidated versions from EUR-Lex: the base act with all later amendments merged in. They are documentation texts, not the Official Journal versions, and differ in layout from the original texts (`regulation`, `delegated_regulation`).

## Documents

| ID | Title (API) | Pages | Level 2 | Articles | Annexes |
|---|---|---:|---|---:|---:|
| `02013L0036-20260111_EN` | Directive 2013/36/EU (CRD), consolidated 11.01.2026 | 224 | 10 titles, 16 chapters, sections, sub-sections | 189 | 2 |
| `02013R0575-20260101_DE` / `_EN` | Regulation (EU) No 575/2013 (CRR), consolidated 01.01.2026 | 897 | 10 parts, 21 titles, 33 chapters, 76 sections, 41 sub-sections | ~746 | 4 |
| `02023R1114-20240109_DE` / `_EN` | Regulation (EU) 2023/1114 (MiCA), consolidated 09.01.2024 | 222 | 9 titles, 18 chapters | 150 | 6 |
| `02024R1689-20240712_DE` | Regulation (EU) 2024/1689 (AI Act), consolidated 12.07.2024 | 137 | 13 chapters, 16 sections | 113 | 13 |

Article counts include inserted articles (e.g. `Article 8a`).

## Level 1: blocks

**Same in all documents.**

```
Notice "This text is meant purely as a documentation tool …" / "Dieser Text dient lediglich zu Informationszwecken …"
Base act title with ►B
"Amended by" / "Geändert durch" list (M1, M2, …)
Articles
Annexes
```

Differences to the original texts:

- **No recitals, no enacting formula, no final formula.** The notice states that the preambles are only in the Official Journal versions.
- **Running header on every page**, e.g. `02023R1114 — EN — 09.01.2024 — 001.003 — 13`. Has to be removed before parsing.
- **Amendment markers** `▼B`, `▼M9`, `►M17` etc. on their own lines or inside the text (CRR: about 2,200 marker lines). They show which act a passage comes from and have to be removed or stored as metadata.

Annex contents:

| Document | Annexes |
|---|---|
| CRD | I list of activities subject to mutual recognition, II correlation table |
| CRR | I classification of off-balance-sheet items, II types of derivatives, III items for supplementary reporting of liquid assets, IV correlation table |
| MiCA | I–III disclosure items for white papers, IV minimum capital requirements, V–VI lists of infringements |
| AI Act DE | I–XIII, same as the English original |

## Level 2: grouping headings

**Differs between documents.** Same between DE and EN of one document.

| Document | Hierarchy |
|---|---|
| CRR | `PART` / `TEIL` → `TITLE` → `CHAPTER` → `SECTION` → `Sub-section` / `Unterabschnitt` |
| CRD | `TITLE` → `CHAPTER` → `Section` (Roman: `Section I`) → `Sub-section` |
| MiCA | `TITLE` → `CHAPTER` |
| AI Act | `CHAPTER` → `SECTION` |

- The deepest hierarchy of all documents is in the CRR (five levels).
- CRR parts: EN `PART ONE`, DE `TEIL 1`.
- Sub-section spelling varies within the English CRR (`Sub-Section 1`, `Subsection 2`).

## Level 3: articles

**Same.** `Article N` / `Artikel N` on its own line, followed by a title. Amendment markers can stand between the article heading and the text.

## Level 4: paragraphs and points

**Same within a language, different between DE and EN.**

| Element | EN | DE |
|---|---|---|
| Paragraph | `1.` | `(1)` |
| Point | `(a)` | `a)` |
| Sub-point | `(i)` | `i)` |
| Numbered definition | `(1)` | `1.` |

Example CRR Article 4: EN `1.` → `(1) 'credit institution' …` → `(a)`; DE `(1)` → `1. „Kreditinstitut“ …` → `a)`.
