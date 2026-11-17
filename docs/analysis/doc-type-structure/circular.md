# `circular`

BaFin circulars (Rundschreiben). Two different structures: MaRisk on one side, BAIT and VAIT on the other. Additionally, the page layout differs between the documents.

## Documents

| ID | Title (API) | Pages | Variant | Layout |
|---|---|---:|---|---|
| `RS-06-2024-BA_DE` | Rundschreiben 06/2024 (BA): MaRisk | 56 | MaRisk | one column |
| `RS-05-2023-BA_EN` | Circular 05/2023 (BA): MaRisk | 119 | MaRisk | two columns |
| `RS-10-2017-BA_DE` | Rundschreiben 10/2017 (BA), Fassung 16.12.2024: BAIT | 32 | BAIT/VAIT | two columns |
| `RS-10-2017-BA_EN` | Circular 10/2017 (BA), version 16.12.2024: BAIT | 31 | BAIT/VAIT | two columns |
| `RS-10-2018-VA_DE` | Rundschreiben 10/2018 (VA), Fassung 03.03.2022: VAIT | 40 | BAIT/VAIT | one column, watermark |

Notes:

- The two MaRisk files are **different versions**, not translations of each other: DE is 06/2024, EN is 05/2023. The API lists `RS-06-2024-BA_DE` in `outdated_by` of the EN file.
- **Two-column layout:** left column requirement, right column explanation. `pdftotext` puts both columns on the same line, so a line-by-line parser mixes requirement and explanation. Affects MaRisk EN and both BAIT files.
- **VAIT watermark:** a diagonal watermark is extracted as scattered letter pairs (`Au`, `fg`, `eh`, `ob`, `en` …). Read in order it says "Aufgehoben mit Ablauf des 16.01.2025" (repealed as of 16.01.2025). The API still lists the document as `active`. The fragments have to be filtered out.

## Level 1: blocks

**Only partly the same.** Common to all: `header` (circular number, addressees, title) and `contents`. The body sections depend on the variant.

MaRisk:

| Section | EN begins with | DE begins with |
|---|---|---|
| `header` | `Minimum Requirements for Risk Management` | `Rundschreiben` |
| `contents` | `Contents` | `Inhalt` |
| `general_part_AT` | `AT 1 Preliminary remarks` | `AT 1 Vorbemerkung` |
| `special_part_BT` | `BT 1 Special requirements relating to the internal control system` | `BT 1 Besondere Anforderungen an das interne …` |

BAIT / VAIT:

| Section | EN begins with | DE begins with |
|---|---|---|
| `header` | `Circular 10/2017 (BA) in the version of …` | `Rundschreiben 10/2017 (BA) …` / `Rundschreiben 10/2018 (VA) …` |
| `contents` | `Contents` | `Inhalt` |
| `preliminary_remarks` | `I. Preliminary remarks` | `I. Vorbemerkung` |
| `requirements` | `II. Requirements` | `II. Anforderungen` |

## Level 2: grouping headings

**Differs between the variants.**

**MaRisk:** module codes with up to three levels, same scheme in DE and EN:

```
AT 1 … AT 9                 general part, e.g. AT 4 → AT 4.1 → AT 4.3.2
BT 1, BT 2, BT 3            special part
  BTO 1 … BTO 3             organisational requirements, e.g. BTO 1.2.3
  BTR 1 … BTR 4             risk control requirements, e.g. BTR 2.1
```

Module headings have the form `<code> <title>`, e.g. `AT 4.1 Risikotragfähigkeit`.

**BAIT / VAIT:** part II is split into subject chapters (BAIT: 12, one of them `[aufgehoben]`; VAIT: similar list), e.g. IT-Strategie, IT-Governance, Informationsrisikomanagement, …, IT-Notfallmanagement, Kritische Infrastrukturen. In the extracted text the chapter headings appear **without their number** (`IT-Strategie`), only as text.

## Level 3: numbered paragraphs (Textziffern)

**Differs between the variants.**

| Variant | Format | Example |
|---|---|---|
| MaRisk | number per module, restarting at 1 in each module | `AT 4.1` → `1   Auf der Grundlage …`, `2   Das Institut …` |
| BAIT / VAIT, part I | consecutive numbers | `1 Der Anwenderkreis …` |
| BAIT / VAIT, part II | `<chapter>.<number>.` | `2.3.  Das Institut hat …` (BAIT 79, VAIT 62 such paragraphs) |

Cross references use the same scheme: `AT 7.2 Tz. 2 MaRisk`.

## Level 4: points

**Differs between the variants.**

| Variant | Point | Other |
|---|---|---|
| MaRisk DE | `a)` | dashes `-` / `–` |
| MaRisk EN | `a)` | dashes `-` / `–` |
| BAIT DE / EN | `(a)`, rarely | in EN, explanations refer to points as `Re (a):` |
| VAIT | `(a)`, rarely | |
