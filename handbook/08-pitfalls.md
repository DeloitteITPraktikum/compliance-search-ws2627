# Lessons from our build

We built this app ourselves before we handed you the task. These are the ten mistakes that cost us most.
The fixes are yours to find.

1. **Plain vector search buried the article the question named.** A question about DORA Article 5 found it at rank 34. Embeddings do not read identifiers such as article numbers or column codes.
2. **`active` does not mean current.** Two MaRisk texts are `active` at once. Read `outdated_by` and `corrected_by`, not just `status`.
3. **A sync that compares hashes misses corrigenda.** The corrected act keeps its PDF and hash. Only `updated_at` and `corrected_by` move.
4. **Deleted documents left their vectors behind.** The app kept quoting a document the API no longer serves.
5. **Our header filter ate recital numbers, and no metric noticed.** Count articles per document and compare with the PDF.
6. **Soft hyphens, line-end hyphens and consolidation markers broke exact matches.** Compare PDF libraries on the same page before you pick one.
7. **Tables fell apart into loose lines.** Answers were right but citations wrong, because template chunks carried the wrong label.
8. **The model answered in the language of the passages, not of the question.** One prompt line was not enough.
9. **The same call gave different results.** Run an evaluation several times before you believe a small gain.
10. **Ingest time is nearly all embedding.** Without a cache, every small fix costs minutes. See [Models](04-models.md#cache-your-embeddings).
