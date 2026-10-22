# How we score you

We send questions to your `POST /ask` and compare the answers with answers and sources we wrote by hand.
The grader and 20 sample questions already exist in [`evals/student_kit/`](../evals/student_kit/). You build the app and run the grader in your CI from the first week.

## The question kinds

The sample holds 12 standard and 8 hard questions. The report shows a row per level and per difficulty.

| Level | Kind | Tests |
|---|---|---|
| 1 | Single fact | One fact from one document |
| 2 | Two documents | For example a regulation and its technical standard |
| 3 | Corpus-wide | "Which documents require ...?" |
| 4 | Sync | The answer depends on the current state of the corpus |
| 5 | Cross-language | Question in one language, source in the other |
| abstain | No answer | The corpus holds none. Say so and cite nothing |
| 6 | Table lookup (hard) | A value in a table or template |
| 7 | Many documents (hard) | Three or more acts, or a complete list |
| 8 | Premise check (hard) | The question asserts something, often false. Correct it, or keep it if it is true |
| 9 | Near miss (hard) | Two rules with different numbers. The wording decides which applies |

## The relevance key

A hit is the pair `(family_id, article_key)`. Language, version, paragraph and page do not count.
`Art. 19 Abs. 4` of the German DORA and `Article 19(1)` of the English DORA are the same hit: `art:19`.
Check your chunk labels with `keys.normalize_article(family_id, label)`. If it returns `None`, the grader cannot match the citation.

## The metrics

| Metric | Measures | Needs |
|---|---|---|
| recall@5, recall@10 | Share of relevant passages in your top 5 or 10 | `retrieved` |
| precision@5, MRR | How clean your top 5 is, and the rank of the first hit | `retrieved` |
| Citation precision, recall | Share of your citations that are relevant, and share of relevant passages you cite | `citations` |
| Must-contain | Share of required facts that appear in the answer text | |
| Judge | An LLM scores the answer 0, 1 or 2 against ours. Facts count, style does not | |
| Abstain | Declining when the corpus holds no answer, and only then | |
| Premise, distractor | Hard levels: was a false premise corrected, was the tempting wrong number avoided | |
| Currency | 0 if any citation names a document that is not `active`, has a non-empty `outdated_by`, or names an article a corrigendum changes without citing that corrigendum | |

Several chunks of one article count once. An unknown `document_id` or unreadable `article` is a miss.
An answer declines if it has no citations and says so in words the grader knows. Test your wording with `metrics.is_refusal(answer, [])`.
Exact definitions are in the docstring of `metrics.py`.

## Run the grader

From `setup/`, with your app running:

```sh
uv run --env-file .env ../evals/student_kit/grade.py --url http://localhost:8000 --out report.json
```

The report holds every score, with your answer, citations and the judge's reason per item.
The default judge is `gpt-6-1-sol`: 20 calls per run. Pass `--judge-model gpt-6-luna` to save budget, or leave `GATEWAY_URL` unset to skip the judge.

## In CI

Use the team key, never a personal one. Fail the build on the numbers you care about, and keep each `report.json` as an artifact.

```yaml
- name: Grade the sample questions
  env:
    KEY: ${{ secrets.CI_GATEWAY_KEY }}
    DOCS_URL: https://tud-docs.pgoell.com
    GATEWAY_URL: https://tud-llm.pgoell.com/v1
  run: |
    python evals/student_kit/grade.py --url http://localhost:8000 --judge-model gpt-6-luna --out report.json
    python -c "import json; t = json.load(open('report.json'))['total']; assert t['citation_recall'] >= 0.6, t"
```

Start at 0.6 and raise it as your app gets better. Add your own questions in the format of `sample.jsonl`.

## Hidden runs

We run more questions of the same kinds against your deployed app, without warning, several times in the semester.
They also hold questions on what changed and what applied on a date; those are scored apart.
Tuning to the 20 sample questions does not carry over, and a stale index loses currency points.
