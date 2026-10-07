# Document API

A small read-only API for the regulation corpus.
You poll it to keep your own copy of the PDFs and their metadata in sync.

Base URL: `https://tud-docs.pgoell.com`

The documents go online on 2026-10-20.
After that, documents arrive, change and disappear without warning.

## Auth

Send your key as a bearer token on every route but `/health`.
It is the same key you use for the models.

```text
Authorization: Bearer <your key>
```

## Routes

| Route | Returns |
|---|---|
| `GET /health` | `{"status":"ok"}`. Needs no key. |
| `GET /documents` | All documents: `{"server_time": "...", "documents": [...]}`. |
| `GET /documents?changed_since=<time>` | Only documents whose `updated_at` is at or after that time. |
| `GET /documents/{id}` | The metadata of one document. |
| `GET /documents/{id}/file` | The PDF. |

There is no pagination. The corpus has fewer than 200 documents.

```sh
curl "https://tud-docs.pgoell.com/health"
```

```sh
curl -H "Authorization: Bearer $GATEWAY_KEY" \
  "https://tud-docs.pgoell.com/documents?changed_since=2026-10-20T00:00:00Z"
```

```sh
curl -H "Authorization: Bearer $GATEWAY_KEY" "https://tud-docs.pgoell.com/documents/32022R2554_EN"
```

### Timestamps

Write times as ISO 8601 with `Z` or an offset: `2026-10-21T00:00:00Z` or `2026-10-21T02:00:00+02:00`.
In a URL, write the `+` as `%2B`.
A time the API cannot read gets `422`.

### The file and its ETag

The `ETag` of the file is the document's `sha256` in quotes.
Send the hash of your copy in `If-None-Match`. If your copy is current, you get `304` and no body.

```sh
SHA=$(curl -s -H "Authorization: Bearer $GATEWAY_KEY" \
  "https://tud-docs.pgoell.com/documents/32025R0301_EN" | python3 -c "import json,sys; print(json.load(sys.stdin)['sha256'])")

curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $GATEWAY_KEY" \
  -H "If-None-Match: \"$SHA\"" "https://tud-docs.pgoell.com/documents/32025R0301_EN/file"
```

This prints `304`.

## Fields

| Field | Meaning |
|---|---|
| `id` | Stable id of this one version of a document. Matches `[A-Za-z0-9_-]+`. Never reused. |
| `family_id` | Groups all versions and language editions of the same regulation. |
| `language` | Language of the text: `DE` or `EN`. |
| `title` | Title of the document. |
| `doc_type` | Kind of document, such as `regulation`, `delegated_regulation`, `implementing_regulation`, `consolidated`, `guideline`, `circular` or `corrigendum`. |
| `version_date` | Date this version was issued. Use it as `version` in your citations. |
| `status` | `active`, `superseded`, `repealed` or `deleted`. |
| `updated_at` | Time of the last change to this record. Drives the sync. |
| `sha256` | Hash of the PDF. Also the `ETag` of the file. |
| `pages` | Page count of the PDF. |
| `size_bytes` | Size of the PDF in bytes. |
| `source_url` | Where the PDF was published. |
| `attribution` | Who issued the document. Show it. |
| `binding_note` | Says whether this text is legally binding or a courtesy copy. Show it. |
| `supersedes` | Ids of older versions this document replaces. |
| `superseded_by` | Ids of newer versions that replace this document. |
| `corrects` | Ids of documents this corrigendum corrects. |
| `corrected_by` | Ids of corrigenda that correct this document. |
| `repealed_by` | Ids of documents that repeal this one. |

## Sync recipe

1. First run: `GET /documents`. Store every record. Fetch every file whose status is not `deleted`. Store `server_time`.
2. Each later run: `GET /documents?changed_since=<stored server_time>`. Then store the new `server_time`.
3. The bound is inclusive, so you may see a record twice. Upsert by `id` and that does no harm.
4. For each record you get back, act on its status. See the next table.
5. Follow `corrected_by`. See [Corrigenda](#corrigenda).

Use the `server_time` from the answer, not your own clock.

## Status values

| Status | What it means | What your index must do |
|---|---|---|
| `active` | Current in this corpus. | Upsert the metadata. Fetch the file with `If-None-Match`. A `304` means your copy is current. |
| `superseded` | A newer version replaced it. | Take it out of answers about current rules. Answer from the ids in `superseded_by`. Keep it if you build point-in-time questions. |
| `repealed` | The rule no longer applies. | Keep the record, mark it, and point to `repealed_by`. Do not cite it as a current rule. |
| `deleted` | A tombstone. The file is gone. | Remove the file and all text, chunks and vectors you built from it. The file route now gets `410`. |

`active` means "current in this corpus". It does not mean "in force".
A deleted document stays in the list as a record with status `deleted`, so you can see that it went away.

## Corrigenda

A corrigendum is its own document. It fixes an error in an act and so changes what the act says.

When a corrigendum arrives, two records change:

| Record | What changes |
|---|---|
| The corrigendum | A new record. `corrects` names the act. |
| The corrected act | `corrected_by` gains the corrigendum's id. `updated_at` moves. The PDF and its `sha256` stay the same. |

When `corrected_by` changes on an act, fetch the corrigendum document and decide how your index treats the corrected passage.
There is nothing to download again for the act itself.

> **Warning: Do not sync by hash alone**
>
> The corrected act keeps its PDF and its `sha256`.
> A client that only compares hashes misses the correction and keeps giving the uncorrected answer.
> Use `updated_at` to decide what changed. Use `sha256` only to decide whether to download the file again.

## Rate limit

60 requests per minute per key.
Over that you get `429` with a `Retry-After` header in seconds. Wait that long and try again.

## Status codes

| Code | Meaning |
|---|---|
| `200` | OK. |
| `304` | Your copy of the file is current. |
| `401` | Key missing or unknown. |
| `403` | You sent `as_of`. That parameter is for staff. |
| `404` | Unknown id, or not yet published. |
| `410` | The document is deleted. |
| `422` | Cannot read the timestamp. |
| `429` | Too many requests. See `Retry-After`. |
| `503` | The API could not reach the model gateway to check your key. Try again. |

A new key that you try too early can stay locked out for up to 5 minutes.
