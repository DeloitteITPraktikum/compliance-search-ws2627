# Document API

A read-only API for the regulation corpus. You poll it to keep your copy of the PDFs and their metadata in sync.
It is the source of truth: documents arrive, change and disappear without warning.

Base URL: `https://tud-docs.pgoell.com`. Send your key as `Authorization: Bearer <key>` on every route but `/health`.
OpenAPI file: [`openapi/document-api.json`](../openapi/document-api.json).

## Routes

| Route | Returns |
|---|---|
| `GET /health` | `{"status":"ok"}`. No key needed |
| `GET /documents` | All documents: `{"server_time": "...", "documents": [...]}`. No pagination, fewer than 200 documents |
| `GET /documents?changed_since=<time>` | Only documents with `updated_at` at or after that time |
| `GET /documents/{id}` | One document's metadata |
| `GET /documents/{id}/file` | The PDF. Its `ETag` is the `sha256` in quotes: send it as `If-None-Match` and get `304` if your copy is current |

Times are ISO 8601 with `Z` or an offset. In a URL, write `+` as `%2B`.

## Fields

| Field | Meaning |
|---|---|
| `id` | One version in one language. Never reused. Your citations use it as `document_id` |
| `family_id` | Groups all versions and languages of one act. The grader matches on it |
| `language` | `DE` or `EN` |
| `title`, `doc_type` | Title and kind: `regulation`, `consolidated`, `circular`, `corrigendum` and so on |
| `version_date` | Your citations use it as `version` |
| `status` | `active`, `superseded`, `repealed` or `deleted` |
| `updated_at` | Last change to this record. Drives the sync |
| `sha256`, `pages`, `size_bytes`, `source_url` | About the PDF |
| `attribution`, `binding_note` | The legal notice. Show both in your UI |
| `supersedes`, `superseded_by` | Older and newer versions |
| `corrects`, `corrected_by` | Corrigenda and the acts they fix |
| `corrects_articles` | On a corrigendum: the articles or column codes it changes |
| `repealed_by` | Acts that repeal this one |
| `outdated_by` | Documents that hold the current text of this `active` one, possibly in the other language |

## Sync recipe

1. First run: `GET /documents`. Store every record, fetch every file that is not `deleted`, store `server_time`.
2. Later runs: `GET /documents?changed_since=<stored server_time>`, then store the new `server_time`. Use the server's time, not your clock.
3. The bound is inclusive. Upsert by `id` so a repeat does no harm.
4. Act on each record's status (table below), then check `corrected_by` and `outdated_by`.
5. Save `server_time` last, after all downloads succeeded.

Decide what changed by `updated_at`. Use `sha256` only to decide whether to download the file again: a corrected act keeps its PDF and its hash.

## Status values

| Status | Meaning | Your index |
|---|---|---|
| `active` | Current in this corpus. Not the same as "in force" | Upsert. Fetch the file with `If-None-Match` |
| `superseded` | A newer version replaced it | Take it out of answers. Answer from `superseded_by` |
| `repealed` | The rule no longer applies | Keep the record, never cite it as current |
| `deleted` | The file is gone. The record stays as a tombstone | Remove the file and every chunk and vector built from it |

## Corrigenda and outdated texts

| Case | What happens | What you do |
|---|---|---|
| A corrigendum arrives | A new record with `corrects`. The act gains it in `corrected_by`; its PDF stays the same | If you cite an article listed in `corrects_articles`, cite the corrigendum too |
| An `active` text is older than another | `outdated_by` names the current one. Example: the English MaRisk 05/2023 points to the German 06/2024 | Answer from the documents in `outdated_by` |

Both rules decide the currency score. See [How we score you](06-scoring.md#the-metrics).

## Status codes

| Code | Meaning |
|---|---|
| `304` | Your copy of the file is current |
| `401` | Key missing or unknown. A brand-new key can take up to 5 minutes |
| `404` | Unknown id |
| `410` | The document is deleted |
| `422` | Unreadable timestamp |
| `429` | Over 60 requests per minute. Wait for `Retry-After` seconds |
| `503` | The API could not check your key. Try again |
