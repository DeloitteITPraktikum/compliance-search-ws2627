# Evaluation kit

Grades your `POST /ask` endpoint on 20 sample questions about the corpus: 12 standard and 8 hard.

| File | What it is |
|---|---|
| `keys.py` | Turns a citation into a relevance key |
| `metrics.py` | The metric functions, with every definition in the docstring |
| `grade.py` | The grader |
| `sample.jsonl` | 20 questions with answers and sources |

No dependencies beyond Python 3.10. Staff grade your app with the same metric code on more questions of the same kinds.

## The contract

`POST /ask {"question": "..."}` returns

```json
{"answer": "...",
 "citations": [{"document_id": "32022R2554_DE", "version": "2022-12-14", "article": "Art. 19 Abs. 4", "page": 42, "quote": "..."}],
 "retrieved": [{"document_id": "32022R2554_DE", "article": "Art. 19"}]}
```

`retrieved` is optional: the top 10 passages before answering, best first. Without it the grader skips the retrieval metrics.

## Run it

```bash
export DOCS_URL=https://DOCS_HOST          # the document API
export GATEWAY_URL=https://GATEWAY_HOST/v1 # the model gateway, for the judge
export KEY=sk-...                          # your key, the same for both
python grade.py --url http://localhost:8000 --out report.json
```

The grader checks your answers against the corpus as it is now. It asks the document API for every document record. A citation fails the currency check if its document is no longer `active`, if the document's `outdated_by` is not empty, or if it names an article that a corrigendum changes (`corrects_articles`) and the answer does not cite that corrigendum too. Keep your copy of the corpus in sync.

Leave `GATEWAY_URL` unset to skip the judge. All other metrics still run. Staff use a stronger judge model, so your judge score may differ slightly from theirs.

## In CI

Start your app, run the grader, then fail the build on the numbers you care about:

```bash
python grade.py --url http://localhost:8000 --out report.json
python -c "import json; t = json.load(open('report.json'))['total']; assert t['citation_recall'] >= 0.6, t"
```

0.6 is a starting point. Raise it as your app gets better.

Store `KEY` as a CI secret. Never commit it.

## Relevance keys

A hit is the pair `(family_id, article_key)`. Language, version, paragraph and page do not count, because pages differ between languages and versions.

| Source | You write | Key |
|---|---|---|
| EU act | `Article 19(4)`, `Art. 19 Abs. 4`, `Artikel 19` | `art:19` |
| EU act, annex | `Annex III point 5`, `Anhang III` | `annex:III` |
| EU act, recital | `Recital 12`, `Erwägungsgrund 12` | `recital:12` |
| ITS table column | `B_05.01.0090` | `col:B_05.01.0090` |
| MaRisk | `AT 4.3.4 Tz. 2`, `BTO 1.2`, `BTR 5` | the module: `AT 4.3.4` |
| BAIT, VAIT | `Tz. 4.4`, `Kapitel 4` | the chapter: `ch:4` |
| EBA guidelines | `paragraph 75`, `Tz. 75` | `para:75` |
| Pillar 3 template | `Template EU OV1`, `EU KM1 row 14` | `tpl:EU-OV1` |
| Corrigendum, cited without an article | `p. 1`, `S. 1` | `corrigendum` |

The family is the `family_id` field of the document API. A corrigendum has the family of the act it corrects.

Keep the article label on every chunk when you ingest. Check your labels with `keys.normalize_article(family_id, label)`: if it returns `None`, the grader cannot match the citation.

## Sample items

One JSON object per line: `id`, `level` (1 to 9 or `"abstain"`), `language` of the question, `question`, `expected_answer`, `must_contain` (each fact is a list of accepted spellings), `relevant` (keys), `evidence` (`document_id`, `page`, `quote`), `abstain`.

| Level | Kind |
|---|---|
| 1 | One fact from one document |
| 2 | Needs two documents |
| 3 | Needs a sweep over the corpus |
| 4 | The answer depends on the current state of the corpus. See the `note` |
| 5 | Question in one language, source in the other or in both. See the `note` |
| 6 | Table lookup: a value or label that sits in a table or a template. Hard |
| 7 | Many documents: three or more acts, or a full list where a missing member is wrong. Hard |
| 8 | Premise check: the question asserts something, often in a side clause. Most premises are false (`false_premise`): correct them and cite the text. Controls rest on a true premise (`true_premise`): keep it and answer. Hard |
| 9 | Near miss: two rules on one topic with different numbers; the wording decides which applies. `distractor` holds the tempting wrong answer. Hard |
| abstain | The corpus cannot answer. Say so and cite nothing |

Every item has `difficulty`, `standard` or `hard`, and the report shows a row for each. Staff also run stretch questions that ask how a text read in an earlier version. They are reported apart and do not count in the totals.

A `quote` is an exact substring of one page of the PDF text after two steps: delete each soft hyphen (U+00AD) with the whitespace after it, then turn every run of whitespace into one space. Pages are a help for humans. The grader never scores them.

## Metrics

The docstring of `metrics.py` holds the exact definitions. In short:

| Column | Meaning | Applies to |
|---|---|---|
| `R@5`, `R@10` | Share of the relevant entries hit by the first 5 or 10 unique keys of `retrieved` | items with `retrieved`, not abstain |
| `P@5` | Share of the first 5 unique keys that are relevant | same |
| `MRR` | 1 / rank of the first relevant key, 0 if none | same |
| `citP`, `citR` | Precision and recall of the cited keys against `relevant` | not abstain |
| `must` | Share of the `must_contain` facts found in the answer, case ignored | items with facts |
| `judge` | LLM score 0, 1 or 2 against `expected_answer`. Only facts the question asks for count. The report holds the reason | all, if the judge runs |
| `abst` | Abstain items: 1 if the answer declines and cites nothing. Other items: 0 if the answer declines | all |
| `prem` | 1 if the judge finds that the answer handles the premise right: it corrects a `false_premise` or keeps a `true_premise` | level 8, if the judge runs |
| `dist` | 1 if the answer gives the tempting wrong value from `distractor` and not the full right answer. Lower is better | items with a `distractor` |
| `curr` | 0 if a citation names a document that is not `active` or has a non-empty `outdated_by`, or names an article of a corrected act without the corrigendum that changes it | all |

Rules that tend to surprise:

- An entry of `relevant` may list `also`: other passages that prove the same point. Citing any one of them hits the entry, and none of them lowers precision.
- The article key `any` means every passage of that document family counts. It is used when the question asks for a document, not for a provision.
- `P@5` divides by the keys you return, so with one relevant entry and five different keys it cannot pass 0.2.
- The report holds your answer, citations and retrieved list per item.
- Several chunks of the same article count once. Ten chunks of one relevant article give `P@5` of 1.0 and take one rank.
- A citation with an unknown `document_id` or an unreadable `article` is a miss. It lowers precision, and it fails currency.
- An answer declines if it has no citations and matches the `REFUSAL` pattern in `metrics.py`, for example "not in the corpus", "the passages do not state" or "nicht im Korpus". Test your refusal wording with `metrics.is_refusal(answer, [])`.
- Totals are plain means over the items a metric applies to.
