# The task

Build an AI search over a bank's regulatory document system.
The document system stays the source of truth. Your search stays in sync with it.

## The setting

A compliance team at a mid-sized bank must follow EU financial regulation (DORA, MiCA, CRD, the AI Act and their technical standards) and BaFin circulars such as MaRisk and BAIT.
The documents sit in a document system with metadata and PDFs, but without content search.
The rules change often: new consolidated versions, corrigenda, repealed circulars.

## The seven parts

All seven are required.

| Part | Must do |
|---|---|
| 1. Sync | Poll our [document API](03-document-api.md) on a schedule. Detect new, changed and deleted documents. Superseded and deleted documents disappear from answers. |
| 2. Processing | Parse and clean the PDFs: soft hyphens, markers such as ►B and ▼M1, repeated page headers. Chunk by article or section, not by size. Keep document, version, language, article and page on each chunk. |
| 3. Retrieval | Embed through our gateway into one shared index for the whole team. A German question finds English documents, and the other way round. |
| 4. Answer | An LLM answer with citations. If the corpus holds no answer, say so. |
| 5. UI | A question field and an answer. Clickable citations that show the passage or the PDF page. Version, date and [legal notice](05-corpus.md#the-legal-notice) for each source. |
| 6. Quality | Our sample questions run in your CI. Track the score over time. Add your own test questions. |
| 7. Engineering | A repo in our GitHub organization, one owner per issue, reviewed pull requests, GitHub Actions, tests, a deployed app, [decision records](10-docs.md). |

## The interface we test

Your app answers `POST /ask`. We call it in our test runs.

```json
{"question": "How often must a financial entity run threat-led penetration tests?"}
```

```json
{
  "answer": "At least every 3 years.",
  "citations": [
    {"document_id": "32022R2554_EN", "version": "2022-12-14", "article": "Article 26(1)", "page": 46,
     "quote": "shall carry out at least every 3 years advanced testing by means of TLPT"}
  ],
  "retrieved": [{"document_id": "32022R2554_EN", "article": "Article 26"}]
}
```

| Field | Meaning |
|---|---|
| `answer` | The answer text. |
| `citations` | The sources the answer rests on. `document_id` and `version` are the `id` and `version_date` from the document API. |
| `retrieved` | Optional. The top 10 passages your search found, best first. Without it you get no retrieval scores. |

Develop locally first. By the first hidden run in December, `/ask` must be reachable on a deployed app.

## Stretch goals

Once the seven parts work. We agree the scope with you during the semester.

| Goal | What it means |
|---|---|
| What changed | A diff between two versions of a document. |
| Point in time | "What did MaRisk require in 2024?" |
| Agentic search | The app plans several searches for a comparison question. |
| Hybrid search and reranking | Proven with your own evaluation numbers. |
| Your own gold set | About 50 questions you verify yourselves, each backed by an exact quote. |
| Ablation study | What each choice buys: chunking, embedding or chat model, reranking. |
| Error analysis | Your worst 15 answers: what went wrong, at which step, and what would fix it. |

## Out of scope

Legal correctness beyond what the documents say. User accounts and permissions. Model training.

## Milestones

| When | Result |
|---|---|
| Tue 20.10.2026 | The documents are online. |
| Fri 23.10.2026 | Kick-off in Frankfurt. |
| November | Sync works end to end. CI runs. First decision records. |
| December | First answers with citations in the UI. First hidden run. |
| January | Improvements and stretch goals. Another hidden run. |
| Mid-February | Final hidden run. Demo day. |

Documents arrive, change and disappear during the semester without warning, and hidden runs come without warning too.
A team that syncs by hand loses the currency checks.
