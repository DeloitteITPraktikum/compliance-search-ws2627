# 0010: Chunk Delegated Regulations by article and recital

- Status: Proposed
- Date: 2026-11-22
- Owner: EliasGodschalk

## Context

After parsing, every line of a Delegated Regulation has a `section_type`, inside `enacting_terms` the number of its `article`, and inside `recitals` the number of its `recital` (see `docs/analysis/doc-type-structure/delegated_regulation.md`). The next step groups these lines into chunks for embedding and search.

What constrains the choice:

- The grader counts a hit as `(family_id, article_key)`, for example `art:5` or `recital:12`. Paragraph and page do not count, and several chunks of one article count once (`handbook/06-scoring.md`). Every chunk must carry a label that `keys.normalize_article` can read.
- `qwen3-embedding` gives no error on oversized input (`handbook/04-models.md`), so we must know our chunk sizes.
- Embeddings do not read article numbers well (`handbook/08-pitfalls.md`, item 1).

Measured on the 13 documents (tokens estimated as characters / 3.5):

| | Count | Median | 90th percentile | Max |
|---|---:|---:|---:|---:|
| Articles | 210 | ~420 | ~1,050 | ~1,690 |
| Recitals | 204 | ~170 | ~320 | ~515 |

German texts are about 10 % longer than English ones.

## Decision

One article is one chunk, labelled `Article N`. One recital is one chunk, labelled `Recital N`. We do not split long articles for now.

Each chunk is embedded with a context line in front of its text: the document title, the grouping headings above it (title, chapter, section) and the article heading, for example `Article 5 – ICT risk management framework`.

`header`, `citations`, `enacting_formula`, `final_formula` and `footnotes` are not chunked. The header text is document metadata.

## Alternatives

| Option | Why not |
|---|---|
| One chunk per numbered paragraph | The grader does not score paragraphs. Short paragraphs lose the context of their article, and articles without numbered paragraphs need a second rule anyway |
| Fixed-size windows (for example 500 tokens with overlap) | Chunks would cross article borders and carry the wrong label, so citations would miss |
| Split articles above a token limit (for example 1,500) at their paragraphs | Affects only about 4 articles, and the largest article is far below the input limit of the embedding model. We add it only if the evaluation shows that long articles are found badly |
| Also chunk citations and footnotes | They hold legal bases and publication references, not rules a question asks about |

## Consequences

- Labels come straight from the parser, so every chunk is citable without extra work.
- One rule for all articles keeps the chunker short and every chunk equal to one grader key.
- Long articles (up to ~1,700 tokens, mostly in `32024R1774`) may embed less sharply than short ones. Watch their rank in the first evaluation run.
- Each chunk stores `document_id`, `family_id`, `version`, `language`, its label, `page_start`, `page_end`, `chunker_version` and a hash of its text, for citations and the embedding cache.
- Other doc types (regulation with annexes, guidelines with paragraphs, circulars with Textziffern) get their own records.
