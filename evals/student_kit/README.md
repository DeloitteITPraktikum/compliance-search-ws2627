# Evaluation kit

Grades your `POST /ask` endpoint on 20 sample questions. Needs Python 3.10 or later and nothing else.
What the questions test and how each metric works: [How we score you](../../handbook/06-scoring.md).

| File | What it is |
|---|---|
| `grade.py` | The grader |
| `metrics.py` | The metric functions. The docstring holds the exact definitions |
| `keys.py` | Turns a citation into a relevance key |
| `sample.jsonl` | 20 questions with answers and sources |

## Run it

From `setup/`, where `.env` sets `KEY`, `DOCS_URL` and `GATEWAY_URL`:

```sh
uv run --env-file .env ../evals/student_kit/grade.py --url http://localhost:8000 --out report.json
```

Without uv, export the three variables yourself and run `python grade.py --url http://localhost:8000 --out report.json` in this folder.
Leave `GATEWAY_URL` unset to skip the judge.

## Add your own questions

One JSON object per line, in the format of `sample.jsonl`:

| Field | Meaning |
|---|---|
| `id`, `level`, `difficulty`, `language` | Identity and kind of the question. `level` is 1 to 9 or `"abstain"` |
| `question`, `expected_answer` | What is asked and what a good answer says |
| `must_contain` | Facts the answer must state. Each fact is a list of accepted spellings |
| `relevant` | Relevance keys as `family_id` and `article_key`. `also` lists other passages that prove the same point |
| `evidence` | `document_id`, `page` and an exact `quote` |
| `abstain` | `true` if the corpus cannot answer |
| `false_premise`, `true_premise`, `distractor` | Only on levels 8 and 9 |

A `quote` is an exact substring of one PDF page after two steps: delete each soft hyphen (U+00AD) with the whitespace after it, then turn every run of whitespace into one space.
Point the grader at your file with `--gold`.
