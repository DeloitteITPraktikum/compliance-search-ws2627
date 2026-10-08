# How we score you

We send questions to your `POST /ask` and compare what comes back with answers and sources we wrote by hand.
You get the grader and 20 sample questions. Run them in your CI from the first week.

The kit is in [`../evals/student_kit/`](../evals/student_kit/). Your own repo receives a copy of that folder at kick-off.

| File | What it is |
|---|---|
| [`grade.py`](../evals/student_kit/grade.py) | The grader. |
| [`metrics.py`](../evals/student_kit/metrics.py) | The metric functions. Its docstring holds the exact definitions. |
| [`keys.py`](../evals/student_kit/keys.py) | Turns a citation into a relevance key. |
| [`sample.jsonl`](../evals/student_kit/sample.jsonl) | 20 questions with answers and sources: 12 standard, 8 hard. |
| [`README.md`](../evals/student_kit/README.md) | The kit's own short manual. |

The kit needs Python 3.10 and nothing else. We grade your app with the same metric code, on more questions of the same kinds.

## The question kinds

The sample holds 20 questions: 12 standard and 8 hard. Each item carries `difficulty`, and the report shows a row for each.

| Level | Kind | Tests | Sample |
|---|---|---|---|
| 1 | Single fact | One fact from one document. | S-01 to S-04 |
| 2 | Two documents | The answer needs two documents, such as a regulation and its technical standard. | S-05, S-06 |
| 3 | Corpus-wide | A sweep over the corpus: "Which documents require ...?" | S-07 |
| 4 | Sync | The answer depends on the current state of the corpus. It can change when the corpus changes. | S-08, S-09 |
| 5 | Cross-language | The question is in one language, the source in the other or in both. | S-10, S-11 |
| Abstain | No answer | The corpus holds no answer. Say so and cite nothing. | S-12 |
| 6 | Table lookup (hard) | A value or label that sits in a table or a template. | S-13, S-14 |
| 7 | Many documents (hard) | Three or more acts, or a full list where a missing member is wrong. | S-15, S-16 |
| 8 | Premise check (hard) | The question asserts something, often in a side clause. Most premises are false: correct them and cite the text. Some are true: keep them and answer. | S-17 (false), S-18 (true) |
| 9 | Near miss (hard) | Two rules on one topic with different numbers. The wording decides which applies. | S-19, S-20 |

Our own reference build answers the standard levels almost perfectly. On the hard levels it does clearly worse: it misses about one answer in five and one source in three.
So the hard levels are where teams differ.

Further kinds exist that need version history: what changed between two versions, and what applied on a given date.
We score them apart, as a stretch. They do not count in the totals, and the sample holds none.

### The hard kinds, one example each

**Level 6, table lookup: S-13.** Two loans to a public sector entity without its own rating, in a country whose central government is in credit quality step 2. One runs two years, one two months. Which risk weights apply?
50 % and 20 %, both from CRR Article 116: the first from its Table 2, the second from the rule for an original maturity of three months or less.
Several CRR articles hold a table that looks the same once the grid is lost, with other numbers in each cell.
Your chunker must keep each table with its article, and the model must apply the condition and read two cells.
The grader checks both facts (`50 %`, `20 %`) and the key (CRR `art:116`). Nothing new in the scoring: it is the parsing and the reading that are hard.

**Level 7, many documents: S-15.** Which documents require that exit plans are not only documented but also tested?
Three: DORA Article 28, RTS 2024/1773 Article 10 and the EBA guidelines paragraph 107. Other documents ask for an exit strategy without a test, and they do not count.
An answer with two of the three scores must-contain 2 / 3 and citation recall 2 / 3. One with a fourth, wrong document loses citation precision.
Ten passages from one or two documents will not carry this. Your search must reach across documents.

**Level 8, premise check: S-17 and S-18.** S-17 asks which criteria the national authorities must use when they designate a critical ICT provider under Article 31 DORA.
The premise sits in a side clause, and it is false: the European Supervisory Authorities designate, not the national authorities.
A good answer says so, gives the criteria and cites Article 31. An answer that lists the criteria and lets the premise stand gets judge 0.
S-18 is a control. Its premise, a weekly vulnerability scan in the RTS on ICT risk management, is true. A good answer keeps it and names the article.
The new column `prem` is 1 if the judge finds that your answer handles the premise right: it corrects a false one, or it keeps a true one.
So an app that calls every premise wrong loses on the controls. A refusal is wrong too: the text is there.

**Level 9, near miss: S-20.** How many working days does the authority have to decide on a complete application of a crypto-asset service provider?
40 working days, MiCA Article 63. The trap is MiCA Article 20: 60 working days, for issuers of asset-referenced tokens.
The new column `dist` is 1 if your answer gives the tempting wrong value and not the full right answer. Lower is better.
An answer of "60 working days" scores `dist` 1 and must-contain 0. An answer that gives 40 and mentions the 60 for the other case scores `dist` 0.

## The relevance key

A hit is the pair `(family_id, article_key)`.
Language, version, paragraph and page do not count, because pages differ between languages and versions.
So `Art. 19 Abs. 4` of the German DORA and `Article 19(1)` of the English DORA are the same hit.

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

A lettered article keeps its letter: `Article 92a` gives `art:92a`, not `art:92`.

The grader builds the key from the `document_id` and `article` you return. It looks up the family in the document API, and `keys.py` reads the article.
Check your chunk labels with it:

```python
from keys import normalize_article

print(normalize_article("32022R2554", "Art. 19 Abs. 4"))    # art:19
print(normalize_article("MaRisk", "AT 4.3.4 Tz. 2"))        # AT 4.3.4
print(normalize_article("EBA-GL-2019-02", "paragraph 75"))  # para:75
print(normalize_article("32013R0575", "Article 92a"))      # art:92a
print(normalize_article("32024R3172", "EU OV1 row 26"))    # tpl:EU-OV1
print(normalize_article("MaRisk", "Seite 12"))              # None
```

The first argument is the document's `family_id`.
If the function returns `None`, the grader cannot match your citation. It then counts as a miss.

## The metrics

Each metric is scored per question. A total is the plain mean over the questions the metric applies to.

The examples use sample question S-05. Its relevant keys are DORA `art:19` and RTS 2025/301 `art:5`.

Two forms in `relevant` widen what counts:

| Form | Meaning | Sample |
|---|---|---|
| `also` | Other passages that prove the same point. The entry and its `also` keys form one group. Hitting any of them hits the group, and none of them lowers precision. | S-14, S-18 |
| Article key `any` | Every passage of that document family counts. Used when the question asks for a document, not for a provision. | |

### Retrieval: recall@5, recall@10, precision@5, MRR

These need `retrieved` in your response. They do not apply to abstain questions.

The grader takes your first 10 retrieved passages, turns each into a key and drops repeats. Call this list U.
Several chunks of one article count once and take one rank.

Say U holds these six keys:

| Rank | Key | Relevant |
|---|---|---|
| 1 | DORA `art:18` | no |
| 2 | DORA `art:19` | yes |
| 3 | RTS 2024/1772 `art:9` | no |
| 4 | ITS 2025/302 `art:1` | no |
| 5 | DORA `art:20` | no |
| 6 | RTS 2025/301 `art:5` | yes |

| Metric | Definition | Example |
|---|---|---|
| recall@5 | Relevant keys in the first 5 of U, divided by the number of relevant keys. | 1 / 2 = 0.5 |
| recall@10 | The same over the first 10 of U. | 2 / 2 = 1.0 |
| precision@5 | Relevant keys in the first 5 of U, divided by the length of that slice. Empty U scores 0. With one relevant key and five different keys it cannot pass 0.2, so do not chase it. | 1 / 5 = 0.2 |
| MRR | 1 divided by the rank of the first relevant key. 0 if there is none. | 1 / 2 = 0.5 |

### Citation precision and recall

These look at the keys of your `citations`. They do not apply to abstain questions.

Say your answer cites DORA `art:19`, RTS 2025/301 `art:5` and RTS 2025/301 `art:6`.

| Metric | Definition | Example |
|---|---|---|
| Citation precision | Cited keys that are relevant, divided by all cited keys. 0 if you cite nothing. | 2 / 3 = 0.67 |
| Citation recall | Cited keys that are relevant, divided by the number of relevant keys. | 2 / 2 = 1.0 |

A citation with an unknown `document_id` or an unreadable `article` is a miss. It lowers precision.

### Must-contain

Each question lists facts the answer must state. Each fact has several accepted spellings, in German and English.
The score is the share of facts for which one spelling appears in your answer. Case does not count, and runs of whitespace count as one space.

S-05 lists five facts: `4 hours`, `24 hours`, `72 hours`, `one month` and `2025/301`.
An answer that names the first three and the regulation but says "four weeks" scores 4 / 5 = 0.8.

The match is on exact substrings. Text with split words or stray soft hyphens fails it.

### Judge score

An LLM compares your answer with the expected answer. It judges the facts, not the style or the language.
Only facts the question asks for count. The report keeps the judge's reason for each item.

| Score | Meaning |
|---|---|
| 2 | States every key fact and nothing that contradicts it. |
| 1 | Partly right: a key fact is missing, or a wrong claim stands next to the right one. |
| 0 | Wrong, empty, or a refusal where an answer was expected. |

For S-05, an answer with all three deadlines and the right regulation scores 2. One that gives only the 4-hour deadline is partly right, so it gets a 1.

### Abstain

Your answer counts as a refusal if it has no citations and says so in words the grader knows, such as "not in the corpus", "cannot be answered", "nicht im Korpus" or "keine Information".
The full pattern is `REFUSAL` in `metrics.py`. Test your own wording with `metrics.is_refusal(answer, [])`.

| Question | You refuse | You answer |
|---|---|---|
| Abstain question, such as S-12 on KAIT | 1 | 0 |
| Any other question | 0 | 1 |

A refusal that still lists citations is not a refusal. It scores 0 on S-12.

### Premise caught and distractor taken

These two apply to the hard kinds only. The examples are [above](#the-hard-kinds-one-example-each).

| Column | Applies to | Score |
|---|---|---|
| `prem` | Level 8, if the judge runs | Items with `false_premise`: 1 if the judge finds that your answer names or corrects the false premise. Controls with `true_premise`: 1 if your answer keeps the true premise and does not call it wrong. |
| `dist` | Items with a `distractor`, level 9 | 1 if your answer holds the tempting wrong value and not every fact of the right answer. Lower is better. |

### Currency

Currency applies to every question.

The grader asks the document API for every document record, at the moment it runs.
You score 0 if any citation breaks one of three rules. Otherwise you score 1.

| Rule | Fails when your citation names |
|---|---|
| Status | A document that is not `active` right now: superseded, repealed, deleted or unknown. |
| Outdated text | An `active` document whose `outdated_by` is not empty. Another document holds its current text. |
| Corrected article | An article of an act that a corrigendum changes, while your answer does not cite that corrigendum. The corrigendum's `corrects_articles` names the articles. |

Examples:

- The old version of an act is `superseded` and you still cite it. Currency is 0, even if the answer text is right.
- You answer a MaRisk question from the English text of 05/2023. Its `outdated_by` names the current German circular. Currency is 0. Cite the German text: the relevance key is the same.
- A corrigendum lists `Article 7` in `corrects_articles`. You cite Article 7 of the corrected act alone. Currency is 0. Cite the corrigendum next to it, or in its place.

The corrected-article rule works on the relevance key, so it covers the whole article, not one paragraph.
Label corrigendum chunks with the article they change (`Article 7`), not only with a page. Then the extra citation also counts as relevant.

## Run the grader

Start your app. Then, in the kit folder:

```sh
export DOCS_URL=https://tud-docs.pgoell.com
export GATEWAY_URL=https://tud-llm.pgoell.com/v1
export KEY=$GATEWAY_KEY
python grade.py --url http://localhost:8000 --out report.json
```

The grader prints one row per level, one each for `standard` and `hard`, and a total.
It writes every score to `report.json`, with your answer, citations, retrieved list and the judge's reason per item. Start there when a number drops.

| Setting | Meaning |
|---|---|
| `--url` | Where your app runs. The grader calls `<url>/ask`. |
| `--gold` | The question file. Default: `sample.jsonl` next to `grade.py`. Point it at your own questions too. |
| `--judge-model` | The model that judges. Default: `gpt-6-1-sol`. |
| `--out` | Where the report goes. Default: `report.json`. |
| `DOCS_URL` | The document API. The grader reads `id`, `family_id` and `status` of every document from it. |
| `GATEWAY_URL` | The model gateway, for the judge. Leave it unset to skip the judge: its column shows `n/a` and all other metrics still run. |
| `KEY` | Your key. The same one for both. |

The judge costs money: 20 calls to `gpt-6-1-sol` per run. In a pipeline that runs on every push, pass `--judge-model gpt-6-luna` or skip the judge.

The grader checks your answers against the corpus as it is now. If your copy is out of sync, currency drops.

### In CI

Start your app, run the grader, then fail the build on the numbers you care about. `report.json` holds them under `total`, `by_level` and `by_difficulty`.

```sh
python -c "
import json
total = json.load(open('report.json'))['total']
print(total)
assert total['citation_recall'] >= 0.6, total
"
```

0.6 is a starting point. Raise it as your app gets better.

In GitHub Actions, run the same commands in a step.

```yaml
- name: Grade the sample questions
  env:
    KEY: ${{ secrets.CI_GATEWAY_KEY }}
    DOCS_URL: https://tud-docs.pgoell.com
    GATEWAY_URL: https://tud-llm.pgoell.com/v1
  run: python grade.py --url http://localhost:8000 --judge-model gpt-6-luna --out report.json
```

The team gets one extra key for CI, with its own budget. Store it as a secret.
Your personal key never goes into the repo or into CI.

Keep each `report.json` as a build artifact, so you can track the score over time.
Add your own questions in the same format as `sample.jsonl`.

## How a hidden run differs

| | Your sample run | Our hidden run |
|---|---|---|
| Questions | The 20 you have. | More questions of the same kinds, plus the stretch kinds that need version history. Tuning your app to the 20 does not carry over. |
| Target | Wherever you point `--url`. | Your deployed app. |
| When | When your CI runs. | Without warning, more than once in the semester. |
| Corpus | The document API at that moment. | The same. A stale index loses currency points. |
| Judge | `gpt-6-1-sol`, or the model you pass. | A stronger model. Your judge score may differ slightly from ours. |
| Metric code | `metrics.py`. | The same. |
