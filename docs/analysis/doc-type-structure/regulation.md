# `regulation`

Regulations of the European Parliament and of the Council, original texts as published in the Official Journal. Same pattern as `delegated_regulation`, but longer, with deeper grouping and in some cases annexes.

## Documents

| ID | Title (API) | Pages | Level 2 | Articles | Annexes |
|---|---|---:|---|---:|---:|
| `32022R2554_DE` / `_EN` | Regulation (EU) 2022/2554 (DORA) | 79 | 9 chapters, 3 of them with sections | 64 | 0 |
| `32024R1689_EN` | Regulation (EU) 2024/1689 (AI Act) | 144 | 13 chapters, 16 sections | 113 | 13 |

The German AI Act is not in this type: `02024R1689-20240712_DE` is a consolidated text (see [consolidated.md](consolidated.md)).

## Level 1: blocks

**Same in all documents, annexes optional.**

| Section | EN begins with | DE begins with |
|---|---|---|
| `header` | `I` / `(Legislative acts)` (DORA), `REGULATION (EU) 2024/1689 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL` (AI Act) | `I` (DORA) |
| `citations` | `THE EUROPEAN PARLIAMENT AND THE COUNCIL OF THE EUROPEAN UNION,` | `DAS EUROPÄISCHE PARLAMENT UND DER RAT DER EUROPÄISCHEN UNION —` |
| `recitals` | `Whereas:` | `in Erwägung nachstehender Gründe:` |
| `enacting_formula` | `HAVE ADOPTED THIS REGULATION:` | `HABEN FOLGENDE VERORDNUNG ERLASSEN:` |
| `enacting_terms` | `CHAPTER I` | `KAPITEL I` |
| `final_formula` | `Done at Strasbourg, <date>.` (DORA), `Done at Brussels, <date>.` (AI Act) + signatures | `Geschehen zu Straßburg am <date>.` (DORA) |
| `annex` | `ANNEX I`, `ANNEX II`, … (AI Act only) | – |

- The final formula comes before the annexes. The DE column covers DORA only.
- AI Act annexes: lists (Union legislation, criminal offences, high-risk systems), required contents of technical documentation, conformity procedures. Text and lists, no data tables.

## Level 2: grouping headings

**Differs between documents.**

| Document | Hierarchy |
|---|---|
| DORA | `CHAPTER` (9); Chapters II, V and IX each split into `Section I` and `Section II` |
| AI Act | `CHAPTER` (13) → `SECTION` (16) |

- DORA section headings come out letter-spaced in both languages, e.g. `Se cti on I I`, `Abschn i tt I`. A parser has to remove the spaces before matching.
- DORA numbers sections with Roman numerals, the AI Act with Arabic numerals.

## Level 3: articles

**Same.** `Article N` / `Artikel N` on its own line, followed by a title. DE and EN of DORA have the same 64 articles.

## Level 4: paragraphs and points

**Same within a language, different between DE and EN.** Same conventions as `delegated_regulation`:

| Element | EN | DE |
|---|---|---|
| Paragraph | `1.` | `(1)` |
| Point | `(a)` | `a)` |
| Sub-point | `(i)` | `i)` |

Definitions articles number the defined terms: EN `(1)`, DE `1.`.
