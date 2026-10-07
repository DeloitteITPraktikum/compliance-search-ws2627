# Pitfalls we hit

We built this app ourselves before we handed you the task. These are our notes on what went wrong and how we noticed.
The fixes are yours to find. Most numbers are from our first build, on 28 documents and 3,223 chunks. The start set has grown since; the cost table at the end shows today's figures.

## The five worst

1. Plain vector search buried the article the question named. It ranked 34th.
2. `active` does not mean "the current rule".
3. Two chunker bugs lost whole articles and recitals, and no metric showed it.
4. The model answered in the language of the passages, not of the question.
5. Ingest time is nearly all embedding. Without a cache, each small fix costs minutes.

## Sync

| What went wrong | How we noticed |
|---|---|
| Before 2026-10-20 the document list is empty. The API answers `200` with no documents and no error. | We debugged a sync that worked. |
| A sync that compares hashes misses a corrigendum. The corrected act keeps its file and its `sha256`; only `updated_at` and `corrected_by` move. | The file route answered `304` for every corrected act. A hash-only client saw no change at all. |
| The cursor was saved before the downloads finished. A failed download was then never asked for again. | By reasoning, then a test that fails one download. Save the cursor last. |
| `changed_since` is inclusive, so a record can come back a second time. | Harmless if you upsert by `id`. Wasteful if each repeat starts a re-ingest. |
| A deleted document left its vectors behind. | The app still quoted a document that the API no longer serves. Delete means the file and all you built from it. |
| A timestamp without a zone, or a `+02:00` not written as `%2B`, gets `422`. | Both tried with curl. Send `server_time` back as you got it, and let your HTTP library encode it. |
| 62 quick calls ran into the rate limit. | `429` with `Retry-After: 60`. One full sync fits into a minute. Two in a row do not. |

## `active` does not mean current

This one costs currency points and wrong answers, and the status field alone will not save you.

| What went wrong | How we noticed |
|---|---|
| Two texts of one circular are `active` at once. The German MaRisk is 06/2024. The English one is 05/2023 and is not a translation of it. Relations stay inside a language, so nothing marks the English text as older. | A German MaRisk question got most of its passages from the older English text. Look at `version_date` on your citations. |
| "Take the newest version in each family" is no fix. | It would throw out the only English text of the family. |
| An amending act can sit next to the consolidated text it changed. Both are `active`, both hold the rule, and no relation links them. | The same question cited one in German and the other in English. Decide which one your app prefers, and write down why. |
| `active` is not "in force". | VAIT is `active`, and its cover says "Aufgehoben mit Ablauf des 16.01.2025". |
| A corrigendum holds the wrong wording next to the right one ("for:" and "read:"). The act's own text still holds the wrong one. | A question that pulled the act but not the corrigendum got the old answer. A quote check passes on either half. |
| `version_date` means different things: the date of the act, of the consolidation, or of the circular. | Sorting by it across sources gave nonsense. |

## Parsing

| What went wrong | How we noticed |
|---|---|
| pypdf put spaces inside words in consolidated texts. | "auswä hlen", "financial hol ding" on pages where PyMuPDF gave whole words. Compare libraries on the same page before you pick one. |
| Soft hyphens (U+00AD) at line ends. One German act has over 2,500. | Exact phrases from the PDF found nothing in our text. |
| A hyphen at a line end is sometimes a split word and sometimes a real compound. One rule does not cover both. | "Kontrollrah-men" must join. "IKT-Drittdienstleister" and "third-party" must keep the hyphen. We still have a few wrong joins. |
| Our header filter ate recital numbers. It dropped lines that repeat at the top of many pages, with all digits treated as equal. A bare "(17)" at a page top looks just like "(1)" on every other page. | The German DORA had lost nine recitals, and one recital was 38 chunks long. No score moved. |
| Some circulars print the chapter title above the running header. A filter that stops at the first line that does not repeat leaves the header in. | "Seite N von 40" inside 37 chunks of one document. |
| Consolidation markers (►B, ▼M1, ◄) stand alone on lines and inside sentences. One consolidated text has 590. | They showed up in quotes. |
| Footnotes print at the page bottom, so they land in the middle of an article that runs over the page. In the recitals, a footnote that starts with "(17)" looks like recital 17. | Odd recital labels. |
| Each table cell comes out as its own line, not always in row order. | Chunks that held only a column code. |

## Chunking

Test your chunker on real pages, and count what it produces. Count articles per document and compare with the PDF. Then look at the largest chunks and the largest label groups.
Our share of unlabelled chunks was 3.4 % and looked fine all through the two worst bugs.

| What went wrong | How we noticed |
|---|---|
| A reference broken over two lines read as a heading. A sentence ran "... 2016/679, / Article 10 / of Directive ...", and the line "Article 10" passed as the start of Article 10. Our rule that article numbers must rise then threw away several real articles. | One label with 15 parts, and Articles 4 to 9 missing from that document. Only a count per document showed it. |
| The header filter above. | The same count: recital numbers with gaps. |
| Recital numbers from 100 on share their line with the text. | DORA stopped at recital 99. |
| In consolidated texts, paragraph numbers stand alone on a line like recital numbers do. | A "Recital 8" from the middle of an act. |
| An amending act quotes the new articles it inserts. Each quoted heading read as a real one. | A chunk with the right text and the wrong article label, so the citation was wrong while the answer was right. |
| The table of contents matches every heading pattern. | MaRisk modules that held one line and a page number. |
| A module with a heading and no text of its own became a tiny chunk. | A 30-character chunk ranked high for any MaRisk question. |
| The English EBA file is mostly feedback tables, which follow the last numbered paragraph. | One paragraph ran on for 61 chunks. |
| The ITS on incident report templates has no column codes. | Its Annex II is one label with 20 parts. We have no good unit for it. |
| We missed the annex headings of the Pillar 3 ITS. Every template landed under the label of the last article before the annexes. | Right answers with wrong citations: the table questions scored full marks on the answer and a quarter on the sources. |
| BAIT is a two-column table. The explanation runs into the requirement. | Joined words across cells, such as "Informa-Die". Still open on our side. |

## Retrieval

Measure retrieval on its own, before you look at answers. Return `retrieved` from `/ask` and read recall@10 and MRR.

| What went wrong | How we noticed |
|---|---|
| Cosine search alone buried the article the question named. A question that named Article 5 of DORA put that article at rank 34. Five of the top ten were recitals. | The app abstained on a question whose answer was in the corpus. |
| The embedding does not read identifiers. | A question that named column `B_05.01.0090` found ten other column codes. Plan for matching references in the question against your chunk labels, in both languages. |
| Reference matching does not help a question that names no article. | The right chunk ranked 29th for one of them. Plan for a second ranking step over a wider candidate list, and measure what it buys: ours cost one more model call and about 2 seconds. |
| A general rule often does not name the specific case. The article that sets a date for a whole act does not mention the systems the question asks about. | It ranked 113th, outside any list we reranked. The answer cited a neighbouring article and said the passages name no date. Still open on our side. |
| "Which documents require ..." questions. Ten passages from two documents fill the list. | Two of four expected documents missing. |
| Letting the model write several search queries first. | Slower by 3 to 7 seconds, no better, and the model wrote a date from its own memory into the queries. We dropped it. Your numbers may differ. |
| A German question ranks the German chunk of a pair about 0.1 above the English one. | Fine when both exist. When only one language holds the answer, it is still found: cross-language search worked from the start. |

## Answers

| What went wrong | How we noticed |
|---|---|
| The model answers in the language of the passages. An English question with German passages got a German answer. | With "answer in the language of the question" in the system prompt it still happened in 2 of 3 runs. It took a firmer measure, and 12 runs in a row, before we trusted it. |
| A question with a wrong premise. Article 5(1) of DORA speaks to the financial entity; the management body is in paragraph 2. Asked what 5(1) requires of the management body, the model once explained that and once refused. | Two runs, two outcomes. Decide what your app does when a question names a provision but gets its content wrong. |
| Quotes that are not in the passage. | We check each quote against the passage text before we return it. Our model copied well when told to quote word for word. |
| The quote is a span of your cleaned text, not of the raw PDF. | It will not match raw PDF text with soft hyphens and line breaks. |
| `page` is where the chunk starts. | A quote from the end of a long chunk sits on the next page. Cite by article. |
| The same provision has two labels: "Article 5" and "Artikel 5", "Annex III" and "Anhang III". | Run both through `normalize_article`. See [How we score you](06-scoring.md#the-relevance-key). |

## Gateway and models

| What went wrong | How we noticed |
|---|---|
| More than 150 inputs in one embedding call. | `400`: "Input embeddings size is too large, exceeding 150 limit". |
| An oversized input gives no error. One text of 28,000 tokens was accepted and billed, with no sign of whether the model cut it. | Only by checking our own chunk sizes. |
| JSON mode needs the word "JSON" in the user message. Saying it in the system prompt did not count. | `400`: "Response input messages must contain the word 'json'". |
| Reasoning tokens. `gpt-6-luna` spent about 400 of them and 5.8 seconds to return a list of ten numbers. | The `usage` field. With `reasoning_effort="low"` the same call took about 2 seconds with the same result. `"minimal"` is rejected. |
| Temperature 0 is not repeatable. The same call twice gave two rankings, and answers change wording between runs. Once the substance changed. | Run your evaluation several times before you believe a small gain. Test on facts, not on strings. |
| Speed varies. The same ingest took 121, 136, 144 and once 347 seconds. One question took 5 to 19 seconds on the same code. | Do not tune timeouts on one run. Turn retries on. |

## Cost and time

| Step | What we measured |
|---|---|
| Parse and chunk the start set, 3,893 pages | seconds |
| Embed the start set, about 5,700 chunks | 2.8 million tokens, about 6 cents, under four minutes |
| One question | about 0.2 cents, median 9 seconds |

Ingest time is nearly all embedding. Cache by file hash, chunker version and model name, so a second run embeds nothing and a new document costs only itself.
A change to the chunker embeds everything again. That costs a few cents and a few minutes here, so do not build a finer cache.

## Hosting

The traps of free hosting are on their own page: [Gotchas](07-stack.md#gotchas).
