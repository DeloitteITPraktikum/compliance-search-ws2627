# Start here

You build a web app that answers questions about EU financial regulation.
A compliance analyst at a bank asks in German or English and gets an answer with citations: document, version and article.
The answer rests only on documents that are current in our document system.
Your app keeps itself in sync with that system, with no manual steps.
We test it with questions you have not seen.

The project runs from the kick-off on Friday 23.10.2026 to demo day in mid-February 2027.

> **Warning: We log every prompt and every answer**
>
> Everything you send and every answer you get is logged with your email, on the gateway
> server and in a Databricks workspace run by staff, and staff can read it.
> You see your own requests in the dashboard's Logs page.
>
> Do not send personal data or secrets.

## Contents

| # | Page | What it covers |
|---|---|---|
| | Start here | This page |
| 1 | [The task](01-task.md) | The seven parts, stretch goals, assessment, team rules, timeline |
| 2 | [Quickstart](02-quickstart.md) | From your key to a streamed answer, an embedding and a PDF |
| 3 | [Document API](03-document-api.md) | Contract, fields, sync recipe, status values, corrigenda, errors |
| 4 | [Models](04-models.md) | Model table, reasoning effort, tools, JSON, embeddings, budget and spend |
| 5 | [The corpus](05-corpus.md) | Document kinds, ids and families, how to cite, legal notice, oddities |
| 6 | [How we score you](06-scoring.md) | Each metric with an example, the grader, CI, hidden runs |
| 7 | [Reference stack and free tiers](07-stack.md) | A zero-cost stack we recommend, and its gotchas |
| 8 | [Pitfalls we hit](08-pitfalls.md) | What went wrong in our own build and how we noticed |
| 9 | [FAQ and help](09-faq.md) | Who to ask, outages, lost keys, used-up budgets |
| 10 | [How you document](10-docs.md) | Where your own docs go, decision records, the pull request rule |

The evaluation kit is in [`../evals/student_kit/`](../evals/student_kit/).
At kick-off your own repo receives a copy of that folder and of this `docs/` folder.

## What you get from us

| Thing | What it is | Page |
|---|---|---|
| One personal key | Works for the model gateway and for the document API | [Quickstart](02-quickstart.md) |
| One team key for CI | With its own budget, stored as the repo secret `CI_GATEWAY_KEY`. Personal keys never go into the repo or into CI | [How we score you](06-scoring.md#in-ci) |
| Document API | `https://tud-docs.pgoell.com`, the PDFs and their metadata, published on 2026-10-20 | [Document API](03-document-api.md) |
| Model gateway | `https://tud-llm.pgoell.com/v1`, four chat models and one embedding model | [Models](04-models.md) |
| Budget | 10 USD per month and 60 requests per minute, per student | [Models](04-models.md#budget-and-spend) |
| Sample questions and grader | 20 questions with answers, and the grader, in [`../evals/student_kit/`](../evals/student_kit/) | [How we score you](06-scoring.md) |
| Dashboard | `https://tud-llm.pgoell.com/ui`, three pages: your key (masked) with spend and budget, your usage, your request log | [Models](04-models.md#see-your-spend) |
| A GitHub organization | Your repo lives there | [The task](01-task.md#team-rules) |

## What is yours to choose

You pick the hosting, the vector store, the framework and the programming languages.
Two rules apply.

1. Zero cost. Nothing you use may cost money.
2. Every choice gets a short decision record in [`decisions/`](../docs/decisions/README.md).

If you have no strong view, start from our [reference stack](07-stack.md).

## What we fix

| Interface | Rule |
|---|---|
| Our document API | You read from it. It is the source of truth. |
| Your `POST /ask` | We call it in our test runs. The format is in [The task](01-task.md#the-interface-we-test). |

## Checklist for week 1

Do the first two on kick-off day. Both can take days to verify.

- [ ] Claim the [GitHub Student Developer Pack](https://education.github.com/pack) with your TU email.
- [ ] Claim [Azure for Students](https://azure.microsoft.com/en-us/free/students) with your TU email. It needs no credit card.
- [ ] Accept the invite to our GitHub organization.
- [ ] Get your personal key and your invite link for the dashboard from us.
- [ ] Open the invite link by Friday 2026-11-06, 23:59 Berlin time, and set a password.
- [ ] Run the setup check in [`setup/`](https://github.com/DeloitteITPraktikum/compliance-search-ws2627/blob/main/setup/README.md): `uv run --env-file .env check.py`.
- [ ] Make your first model call and your first embedding. See [Quickstart](02-quickstart.md).
- [ ] List the documents and download one PDF. See [Quickstart](02-quickstart.md#4-list-the-documents).
- [ ] Run a first full sync on your laptop. See the [sync recipe](03-document-api.md#sync-recipe).
- [ ] Read [The task](01-task.md) and [How we score you](06-scoring.md).
