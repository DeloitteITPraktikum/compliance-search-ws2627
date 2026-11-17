# `implementing_regulation`

Commission Implementing Regulations, here Implementing Technical Standards (ITS). A short legal text followed by annexes that hold most of the content: templates, field catalogues, instructions. Highest table share of all types (9–23 % table-like lines).

## Documents

| ID | Title (API) | Pages | Articles | Annexes |
|---|---|---:|---:|---|
| `32024R2956_EN` | ITS on standard templates for the register of information (DORA) | 43 | 7 | I–IV |
| `32024R3172_DE` / `_EN` | ITS on public disclosures by institutions (CRR, Pillar 3) | 125 | 28 | I (heading not in text), II |
| `32025R0302_DE` / `_EN` | ITS on standard forms and templates for incident reporting (DORA) | 44 | 9 | I–IV |

## Level 1: blocks

**Same in all documents.**

```
Official Journal header
Citations
Recitals
Enacting formula
Articles
Final formula  + signature
Annexes
```

- The annexes follow the final formula.
- In `32024R3172` the heading `ANNEX I` does not appear in the extracted text; the annex content starts directly after the signature. Rule that works for all documents: everything after the final formula is annex content.

## Level 2: grouping headings

**None in the articles.** No document of this type has Parts, Titles, Chapters or Sections in the enacting terms.

The annexes have their own structure, see level 3.

## Level 3: articles and annex units

**Articles: same.** `Article N` / `Artikel N` with title, DE and EN equal.

**Annexes: different in every document.**

| Document | Annex content | Unit inside the annex |
|---|---|---|
| `32024R2956` | I instructions for the register of information, II list of activities by type of entity, III types of ICT services, IV instructions on "value of total assets" | 15 relational templates `B_01.01` … `B_99.01` |
| `32024R3172` | I disclosure templates and tables, II correlation table | 22 sections (`Section N – '…'`), inside them `Template EU …` (e.g. `EU OV1`, `EU KM1`) and `Table EU …` |
| `32025R0302` | I templates for major incidents, II data glossary and instructions for major incidents, III templates for significant cyber threats, IV data glossary and instructions for cyber threats | tables with columns `Data field` · `Description` · report type · `Field type` |

A parser for the annexes therefore has to handle three different formats; `doc_type` alone does not tell which one.

## Level 4: paragraphs and points

**Articles: same within a language** (EN `1.` / `(a)`, DE `(1)` / `a)`, as in `delegated_regulation`).

**Annexes:** table rows and columns. Not analysed in detail.
