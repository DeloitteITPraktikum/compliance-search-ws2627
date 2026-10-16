# The task

Build an AI search over a bank's regulatory document system.
The document system stays the source of truth. Your search stays in sync with it.

## The setting

A compliance team at a mid-sized bank must follow EU financial regulation (DORA, MiCA, CRD, the AI Act and their technical standards) and BaFin circulars such as MaRisk and BAIT.
The documents sit in a document system with metadata and PDFs but no content search.
The rules change often: new consolidated versions, corrigenda, repealed circulars.

## The seven parts

| Part | Must do |
|---|---|
| 1. Sync | Poll our document API on a schedule. Detect new, changed and deleted documents. Superseded and deleted documents disappear from answers. |
| 2. Processing | Parse the PDFs and clean the text: soft hyphens, consolidation markers such as ►B and ▼M1, repeated page headers. Chunk by article or section, not by fixed size. Keep metadata on each chunk: document, version, language, article, page. |
| 3. Retrieval | Embed through our gateway. Store vectors in a store of your choice. A German question must find English documents, and the other way round. |
| 4. Answer | An LLM answer with citations. If the corpus holds no answer, say so. |
| 5. UI | A question field and an answer. Clickable citations that show the passage or the PDF page. Version and date for each source. The [legal notice](05-corpus.md#the-legal-notice) for each source. |
| 6. Quality | Our sample questions run in your CI. You track the score over time. You add your own test questions. |
| 7. Engineering | A repo in our GitHub organization, one owner per issue, pull requests with review, CI/CD with GitHub Actions, tests, a deployed app, a short decision record for each technology choice. |

## The interface we test

We call your deployed app. It must answer `POST /ask` with a JSON body.

Request:

```json
{"question": "How often must a financial entity run threat-led penetration tests?"}
```

Response:

```json
{
  "answer": "At least every 3 years.",
  "citations": [
    {"document_id": "32022R2554_EN", "version": "2022-12-14", "article": "Article 26(1)", "page": 46, "quote": "shall carry out at least every 3 years advanced testing by means of TLPT"}
  ],
  "retrieved": [
    {"document_id": "32022R2554_EN", "article": "Article 26"}
  ]
}
```

| Field | Meaning |
|---|---|
| `answer` | The answer text. |
| `citations` | The sources the answer rests on. `document_id` and `version` come from the document API (`id` and `version_date`). |
| `retrieved` | Optional. The top 10 passages your search found before the model answered, best first. Without it you get no retrieval scores. |

## Stretch goals

Pick these up once the seven parts work. We agree the scope with you as the semester goes.

| Goal | What it means |
|---|---|
| "What changed" | A diff between two versions of a document. |
| Point-in-time questions | "What did MaRisk require in 2024?" |
| Agentic search | The app plans several searches for a comparison question. |
| Hybrid search and reranking | Proven with your own evaluation numbers. |
| Your own gold set | About 50 questions that you verify yourselves. Every expected answer is backed by an exact quote from the source, the way ours is. |
| Ablation study | Numbers for what each choice buys: chunking strategy, embedding or chat model, with and without reranking. |
| Error analysis | A written analysis of your worst 15 answers: what went wrong, at which step, and what would fix it. |

The first two rows are also question kinds in our hidden runs, scored apart from the totals. See [How we score you](06-scoring.md#the-question-kinds).
The last three build on the must-have in part 6. Running our sample questions in CI and tracking the score stays a must.

## Out of scope

- Legal correctness beyond what the documents say.
- User accounts and permissions.
- Model training.

## How we assess

We assess each of you on your own work, not the team's output.

- We look at the scope and quality of your merged pull requests. We do not count them.
- We look at your demos. You present your own part in every review.

The project is technical. You need Python, Git, HTTP APIs and some SQL.

## Team rules

- You are one team.
- Sub-roles follow the parts: sync, processing and retrieval, app, quality. We settle them in week 1.
- Each GitHub issue has one owner.
- All work lands as a reviewed pull request.
- The repo lives in our GitHub organization, never in a personal account.
- Zero cost is a hard rule.
- Each technology choice has a decision record.
- Personal keys never go into the repo or into CI. The team's CI key lives in the GitHub Actions secret `CI_GATEWAY_KEY`.

## Timeline

| When | Result |
|---|---|
| Tue 2026-10-20 | The documents are online. |
| Fri 23.10.2026 | Kick-off at Deloitte in Frankfurt: task, access, short tech intro, architecture discussion. |
| November | Sync from our API works end to end. CI runs. First decision records. |
| December | First answers with citations in the UI. First hidden test run. |
| Christmas | Buffer. No sprint. |
| January | Improvements and stretch goals. Another hidden test run. |
| February | Hardening, docs, final hidden test run. Demo day at the office in mid-February, before your exams. |

Documents arrive, change and disappear during the semester without warning.
We run the hidden questions without warning too.
A team that syncs by hand fails the currency checks.
