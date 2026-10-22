# FAQ and help

## Who to ask

| For | Contact |
|---|---|
| Keys, gateway, document API, grader, corpus | Pascal Göllner, pgoellner@deloitte.de |
| Dates, rooms, the university side | Benedikt Völker, bvoelker@deloitte.de |
| Reviews | Max Bosch, mbosch@deloitte.de |

Never send a key, not by mail and not in an issue.

## A service is down

```sh
curl "https://tud-docs.pgoell.com/health"            # {"status":"ok"}
curl "https://tud-llm.pgoell.com/health/liveliness"  # "I'm alive!"
```

| What you see | What to do |
|---|---|
| Both answer, but your call fails | Read the status code: [Document API](03-document-api.md#status-codes), [Models](04-models.md#budget-and-spend) |
| The document API is down | Work on what you already synced. Your next sync catches up |
| The gateway is down | Wait. Your app shows a clear error instead of crashing. Wire up code with `mock` once it is back |
| Down for more than a few minutes | Mail the technical contact |

## My key is lost or leaked

Tell the technical contact at once. We delete the old key and issue a new one; deleting a commit is not enough.
Your spend carries over. A new key can take up to 5 minutes to work on the document API.

## My budget is used up

Calls fail with `422` "Budget has been exceeded". The budget resets on the 1st.
Check the Logs page of the [dashboard](https://tud-llm.pgoell.com/ui) for the cause: usually an ingest without an embedding cache, a loop without a stop, or a strong model at high reasoning effort.
If you cannot wait, ask the technical contact and say what happened.

## Short answers

| Question | Answer |
|---|---|
| Which key goes into CI? | The team key in the secret `CI_GATEWAY_KEY`. Never a personal key |
| My dashboard invite link expired | It works until 06.11.2026, 23:59. After that, ask for a new one |
| `429` | Over 60 requests per minute. Wait for `Retry-After` seconds |
| `404` on tud-llm.pgoell.com | By design: the host only serves the model API and the dashboard |
| `403` on a model | Only the models on [Models](04-models.md#the-models) work |
| A synced document is gone | The corpus changed. See [Status values](03-document-api.md#status-values) |
| May I use a paid tool? | No. Zero cost is a hard rule |
