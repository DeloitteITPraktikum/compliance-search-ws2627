# POST /ask

The one interface the grader, the frontend and the hidden test runs call. Its format is fixed by [`handbook/01-task.md`](../../handbook/01-task.md#the-interface-we-test).

The answer is a placeholder for now: every question gets the same fixed example answer from `compliance_search/answer/placeholder.py`.

## Start the app

From `backend/`:

```sh
uv sync
uv run uvicorn compliance_search.api.app:app --port 8000
```

The app listens on `http://localhost:8000`. It needs no key and no `.env`.
FastAPI serves interactive docs at `http://localhost:8000/docs`.

## Request

```sh
curl -X POST http://localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question": "How often must a financial entity run threat-led penetration tests?"}'
```

| Field | Type | Meaning |
|---|---|---|
| `question` | string, required | The question. Leading and trailing whitespace is removed. Must not be empty |

## Response

Status `200`:

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

| Field | Type | Meaning |
|---|---|---|
| `answer` | string | The answer text |
| `citations` | list | The sources the answer rests on |
| `citations[].document_id` | string | `id` from the document API |
| `citations[].version` | string | `version_date` from the document API |
| `citations[].article` | string | The article label, for example `Article 26(1)` |
| `citations[].page` | integer or null | The PDF page of the passage |
| `citations[].quote` | string | The quoted passage |
| `retrieved` | list | The top 10 passages the search found, best first |
| `retrieved[].document_id` | string | `id` from the document API |
| `retrieved[].article` | string | The article label |

The models live in `backend/src/compliance_search/models.py`.

## Errors

Errors use FastAPI's default format: a JSON object with a `detail` field.

| Status | When | Body |
|---|---|---|
| `422` | `question` is missing, empty, only whitespace or not a string, or the body is not valid JSON | `{"detail": [{"type": "missing", "loc": ["body", "question"], "msg": "Field required", ...}]}` |
| `500` | An unexpected error inside the app. The details go to the server log | `{"detail": "Internal server error"}` |

## Tests

From `backend/`:

```sh
uv run pytest
```
