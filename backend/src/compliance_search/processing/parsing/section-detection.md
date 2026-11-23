# Section detection

Section detection assigns a `section_type` to every line of a delegated regulation (level 1). It uses text patterns, page numbers and layout signals such as font size and vertical position.

The code is in [`section_detection.py`](section_detection.py).

## Section types

| Value | Meaning |
|---|---|
| `header` | number, date and title of the act |
| `citations` | "THE EUROPEAN COMMISSION," and the legal bases ("Having regard to …") |
| `recitals` | the numbered reasons ("Whereas: (1) …") |
| `enacting_formula` | "HAS ADOPTED THIS REGULATION:" |
| `enacting_terms` | the articles |
| `final_formula` | "This Regulation shall be binding in its entirety …", "Done at Brussels, …" and everything after it (signatures) |
| `footnotes` | footnotes, including their continuation lines on the same page |

## Input

`detect_sections(lines)` expects the `SectionLine`s of one document in document order, already trimmed by [`trim_lines.py`](trim_lines.py) (running headers and footers removed). It uses `text`, `page_number`, `font_size` and `y` and sets `section_type` directly on each line. The lines are changed in place; no copy is made. The same list is returned.

## Order

`detect_sections` runs the detectors in this order:

1. `detect_enacting_formula_lines`
2. `detect_final_formula_lines`
3. `detect_enacting_terms_lines`
4. `detect_recitals_lines`
5. `detect_citations_lines`
6. `detect_header_lines`
7. `detect_footnote_lines`

The order matters. `enacting_terms` lie between the enacting formula and the final formula, so both must be found first. `recitals`, `citations` and `header` each stop where the next section begins, so they are filled backwards. Footnotes come last, because they overwrite lines that already belong to another section.

## Rules

### Enacting formula

Every line that starts with `HAS ADOPTED THIS REGULATION:` (DE: `HAT FOLGENDE VERORDNUNG ERLASSEN:`) becomes `enacting_formula`.

### Final formula

The line that starts with `This Regulation shall be binding in its entirety` (DE: `Diese Verordnung ist in allen ihren Teilen verbindlich`) and every line after it become `final_formula`. This binding clause stands after the last article and belongs to the whole regulation, not to the last article.

If a document has no binding clause, the final formula starts at the line that starts with `Done at Brussels,` (DE: `Brüssel, den`).

### Enacting terms

Every line after the `enacting_formula` that is not `final_formula` becomes `enacting_terms`.

### Recitals

From the line on page 1 that starts with `Whereas` (DE: `in Erwägung nachstehender Gründe:`) up to the `enacting_formula`.

### Citations

From the line on page 1 that starts with `THE EUROPEAN COMMISSION,` (DE: `DIE EUROPÄISCHE KOMMISSION`) up to the `recitals`.

### Header

Every line on page 1 before the `citations`. No start phrase is needed, because `trim_lines.py` has already removed every line at the very top (`y > 770`) and bottom (`y < 35`): the running header (on page 1 the long form `Official Journal EN` / `of the European Union L series`, after that e.g. `EN OJ L, 20.2.2025`) and the ELI footer. In the new layout the header therefore starts with the act's number and date (`2025/301 20.2.2025`), in the old layout with `REGULATIONS`.

### Footnotes

First the smallest font size of the document is determined. A line starts the footnotes of its page if all three are true:

1. `font_size` is at most 5 % above the smallest font size.
2. The text starts with a number such as `1` or `(1)`.
3. `y` is below `500`.

That line and every following line on the same page become `footnotes`. On the next page the check starts again.

An empty list raises a `ValueError`, because there is no smallest font size.

## Example

```python
lines = detect_sections(trim_lines(build_lines(parse_pdf(pdf_path))))

for line in lines:
    print(line.section_type, line.text)
```
