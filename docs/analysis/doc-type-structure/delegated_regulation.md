# `delegated_regulation`

Commission Delegated Regulations, mostly Regulatory Technical Standards (RTS). Original texts as published in the Official Journal. Recommended starting point for parsing: short, plain legal text, no tables, no annexes.

## Documents

| ID | Title (API) | Pages | Level 2 | Articles |
|---|---|---:|---|---:|
| `32025R0301_DE` / `_EN` | RTS on the content and time limits for reporting major ICT-related incidents (DORA) | 5 | none | 7 |
| `32025R0420_DE` / `_EN` | RTS on the composition of the joint examination team (DORA) | 6 | none | 6 |
| `32025R0532_DE` / `_EN` | RTS on subcontracting ICT services supporting critical or important functions (DORA) | 7 | none | 7 |
| `32024R1773_DE` / `_EN` | RTS on the policy on contractual arrangements for ICT services (DORA) | 9 | none | 11 |
| `32024R1772_DE` / `_EN` | RTS on the classification of ICT-related incidents and cyber threats (DORA) | 9 | 5 chapters | 13 |
| `32024R1774_DE` / `_EN` | RTS on ICT risk management tools, methods, processes and policies (DORA) | 37 | 4 titles, chapters, sections | 42 |
| `32016R0098_EN` | RTS on the general conditions for the functioning of colleges of supervisors (CRD) | 19 | 3 chapters, 6 sections | 38 |

The 12 DORA RTS exist in DE and EN; `32016R0098` only in EN.

## Level 1: blocks

**Same in all 13 documents.**

| Section | EN begins with | DE begins with |
|---|---|---|
| `header` | `COMMISSION DELEGATED REGULATION (EU) …` (2016/98: `REGULATIONS`) | `DELEGIERTE VERORDNUNG (EU) … DER KOMMISSION` |
| `citations` | `THE EUROPEAN COMMISSION,` | `DIE EUROPÄISCHE KOMMISSION —` |
| `recitals` | `Whereas:`, then (1), (2), … | `in Erwägung nachstehender Gründe:` |
| `enacting_formula` | `HAS ADOPTED THIS REGULATION:` | `HAT FOLGENDE VERORDNUNG ERLASSEN:` |
| `enacting_terms` | first grouping heading or `Article 1`, see level 2 | `KAPITEL I`, `TITEL I` or `Artikel 1` |
| `final_formula` | `This Regulation shall be binding in its entirety …`, then `Done at Brussels, <date>.` + signature | `Diese Verordnung ist in allen ihren Teilen verbindlich …`, then `Brüssel, den <date>` + signature |

- No document of this type has an `annex` section.
- `enacting_terms` starts with `CHAPTER 1` (2016/98, Arabic), `CHAPTER I` (1772), `TITLE I` (1774) or directly with `Article 1` (1773, 0301, 0420, 0532).

## Level 2: grouping headings

**Differs between documents.** Same between DE and EN of one document.

| Variant | Documents |
|---|---|
| no grouping, articles directly | `0301`, `0420`, `0532`, `1773` |
| `CHAPTER` / `KAPITEL` | `1772` (5 chapters) |
| `TITLE` → `CHAPTER` → `Section` | `1774` (4 titles; chapter numbering restarts in each title, e.g. Title II: Chapters I–V, Title III: Chapters I–IV; Title II Chapter I has Sections 1–8) |
| `CHAPTER` → `SECTION` | `32016R0098` (3 chapters, 6 sections) |

Headings stand alone on a line (`CHAPTER I`), the heading text follows on the next line.

Extraction differences in `1774`:

- With `pdftotext`, section and some chapter headings come out letter-spaced, e.g. `S ect io n 1`, `ABS CHN I TT 2`, `C HAP TER IV`. pypdf, which the parser uses, extracts all of them cleanly.
- The DE section headings are upper case (`ABSCHNITT 1`), except `Abschnitt 6`. A parser has to match both spellings.

## Level 3: articles

**Same in all documents.**

- Each article starts with a line containing only `Article N` / `Artikel N`.
- Every article has a title on the following line(s) (checked for all articles of the type).
- DE and EN have the same number of articles.

## Level 4: paragraphs and points

**Same within a language, different between DE and EN.**

| Element | EN | DE |
|---|---|---|
| Paragraph | `1.` | `(1)` |
| Point | `(a)` | `a)` |
| Sub-point | `(i)` | `i)` |

- Not every article has numbered paragraphs. Short articles (e.g. subject matter) consist of unnumbered text.
- Paragraphs can contain unnumbered sub-paragraphs (e.g. `32024R1773` Article 5(2)).
- Footnote markers like `(1)` also occur in the text; they are not paragraphs.
