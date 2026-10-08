# FAQ and help

## Who to ask

- Technical contact, for keys, the model gateway, the document API, the grader and the corpus: Pascal Göllner, pgoellner@deloitte.de
- Organisational contact, for dates, rooms, the university side and how the course runs: Benedikt Völker, bvoelker@deloitte.de
- Reviews: Max Bosch, mbosch@deloitte.de

Never send a key, not by mail and not in an issue.

## A service is down

First check which one:

```sh
curl "https://tud-docs.pgoell.com/health"
```

```sh
curl "https://tud-llm.pgoell.com/health/liveliness"
```

The first prints `{"status":"ok"}`, the second `"I'm alive!"`.

| What you see | What to do |
|---|---|
| Both answer, but your call fails | Read the status code. See the tables on [Document API](03-document-api.md#status-codes) and [Models](04-models.md#budget-and-spend). |
| `503` from the document API | It could not reach the gateway to check your key. Try again in a minute. |
| The document API is down | Keep working on the PDFs and metadata you already synced. Your sync catches up on its next run. |
| The gateway is down | Use the [fallback for local work](07-stack.md#the-stack-we-recommend). Do not write fallback vectors into your real index. |
| Down for more than a few minutes | Mail the technical contact. |

Your app should stay up when our services are not. Catch the errors and show a clear message.

## I lost my key

Tell the technical contact. Nobody can show a key again after hand-out: the dashboard shows only `sk-...` and the last four characters.
We delete the old key and issue a new one. The old key stops working.

What you have spent carries over. A new key does not bring a fresh budget.
A new key can take up to 5 minutes to work on the document API.

## My key leaked

If a key lands in a commit, a log or a chat, tell the technical contact at once.
We delete it and issue a new one. Deleting the commit is not enough. The team's CI key is a separate key; if that one leaks, say which.

## My budget is used up

Calls fail with HTTP 422 and "Budget has been exceeded".
The budget is 10 USD per month and resets on the 1st.

1. Open the [dashboard](https://tud-llm.pgoell.com/ui) and look at the Logs page to see what used it.
2. Fix the cause. The usual ones are an ingest that embeds everything again, a loop without a stop, and a strong model with high reasoning effort.
3. If you cannot wait for the 1st, ask the technical contact and say what happened.

## My invite link for the dashboard no longer works

The link lasts 7 days. Ask the technical contact for a new one.

## Which key goes into CI?

Not yours. The team gets one extra key for CI, with its own budget. Store it as a GitHub Actions secret.
Personal keys never go into the repo or into CI.

## The document list is empty

Before 2026-10-20 the API answers `200` with an empty list. That is not an error.

## I get 429

You sent more than 60 requests in a minute. The limit holds for the gateway and, on its own count, for the document API.
Wait and retry. The document API tells you how long in the `Retry-After` header.

## I get 404 on tud-llm.pgoell.com

That is by design. The host answers only the model API paths (chat completions, embeddings, responses, model list, your key info) and the three dashboard pages (Virtual Keys, Usage, Logs).
Every other path gives 404. It is not a bug, so there is no need to report it. The list is on [Models](04-models.md#what-the-host-offers).

## I get 403 on a model

Your key works for `gpt-6-luna`, `gpt-6-1-sol`, `glm-5-3-flash`, `glm-5-3-flash-fast`, `qwen3-embedding` and `mock`. Any other name gives 403.

## A document I synced is gone

That is the corpus changing, not a fault. See [Status values](03-document-api.md#status-values).

## May I use a tool that costs money?

No. Zero cost is a hard rule. See [Reference stack and free tiers](07-stack.md).
