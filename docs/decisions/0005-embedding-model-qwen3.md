# 0005: Embed chunks with qwen3-embedding through the gateway

- Status: Proposed
- Date: 2026-11-09
- Owner: SilviaSina

## Context

Retrieval needs one embedding model for the team's shared index. A German question must find English documents and the other way round.
All model calls go through the Deloitte model gateway, which blocks every model not on its list. The vectors go into Supabase with pgvector, our choosen Database.

## Decision

We embed all chunks and questions with `qwen3-embedding` through the gateway: 1024 dimensions, German and English in one vector space. We compare vectors by cosine similarity.
## Alternatives

| Option | Why not |
|---|---|
| Paid APIs: OpenAI, Cohere, Google Gemini | Cost money per request and do not run through the gateway |
| Self-hosted multilingual models: `multilingual-e5`, `BGE-M3` | Would bypass the gateway rule, and free servers are too weak to run them. `multilingual-e5` reads only 512 tokens |
| Free English-only models: `all-MiniLM-L6-v2`, `nomic-embed-text` | Cannot match German questions to English sources. MiniLM reads only about 256 tokens, so many articles would be cut off |

## Consequences

- Cheap: a full ingest of all documents costs about 6 cents from the gateway budget.
- Cross-lingual search works without translation.
- Embeddings are weak at exact terms such as numbers, names and article IDs. We plan to add Postgres keyword search next to the vectors (hybrid search), in a separate record.
