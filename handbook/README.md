# Start here

You build a web app that answers questions about EU financial regulation.
A compliance analyst asks in German or English and gets an answer with citations: document, version and article.
The answer rests only on documents that are current in our document system, and your app keeps itself in sync with it.

The project runs from the kick-off on Friday 23.10.2026 to demo day in mid-February 2027.

## Pages

| # | Page | Read it when |
|---|---|---|
| 1 | [The task](01-task.md) | First. The seven parts, the `/ask` interface, stretch goals |
| 2 | [Quickstart](02-quickstart.md) | On kick-off day. From your key to a first answer and a first PDF |
| 3 | [Document API](03-document-api.md) | You build the sync |
| 4 | [Models](04-models.md) | You call the gateway |
| 5 | [The corpus](05-corpus.md) | You parse, chunk and cite |
| 6 | [How we score you](06-scoring.md) | You set up the grader and CI |
| 7 | [Reference stack](07-stack.md) | You pick your tools |
| 8 | [Lessons from our build](08-pitfalls.md) | Before you trust your first numbers |
| 9 | [FAQ and help](09-faq.md) | Something fails |
| 10 | [How you document](10-docs.md) | You write docs or a decision record |

## What you get from us

| Thing | Where |
|---|---|
| A personal key for the gateway and the document API | Sent by mail. It goes into `setup/.env` and nowhere else |
| A team key for CI, with its own budget | GitHub secret `CI_GATEWAY_KEY` |
| Document API: PDFs and metadata | `https://tud-docs.pgoell.com` |
| Model gateway: four chat models, one embedding model | `https://tud-llm.pgoell.com/v1` |
| Budget | 10 USD per month and 60 requests per minute, per person |
| Dashboard with your spend | `https://tud-llm.pgoell.com/ui` |
| Grader and 20 sample questions | [`evals/student_kit/`](../evals/student_kit/) |

At kick-off your team repo in our GitHub organization receives a copy of `handbook/`, the empty `docs/` structure and `evals/student_kit/`.

## Two rules

1. **Zero cost.** Nothing you use may cost money.
2. **A decision record for every technology choice**, in [`docs/decisions/`](../docs/decisions/README.md). That holds if you take our [reference stack](07-stack.md) too.

Everything else is yours to choose: hosting, vector store, framework, languages.

## Checklist for week 1

- [ ] Claim the [GitHub Student Developer Pack](https://education.github.com/pack) with your TU email today. Verification can take days.
- [ ] Accept the invite to our GitHub organization.
- [ ] Open your dashboard invite link and set a password by Friday 06.11.2026, 23:59.
- [ ] Run the setup check: `uv run --env-file .env check.py`. See [Quickstart](02-quickstart.md).
- [ ] Make a first model call and a first embedding, list the documents, download one PDF.
- [ ] Run a first full sync on your laptop. See the [sync recipe](03-document-api.md#sync-recipe).
- [ ] Read [The task](01-task.md) and [How we score you](06-scoring.md).

[Azure for Students](https://azure.microsoft.com/en-us/free/students) is only needed if you pick the Azure stack. See [Reference stack](07-stack.md#alternatives).
