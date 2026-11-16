#  0008: Selection of Database Type

- Status: Accepted
- Date: 16.11.2026
- Owner: Nahla
- Related Jira Issue: DEL-2



## Context

For our Compliance Search application, we need a database that can store regulatory documents, text chunks, metadata, and embeddings. It must support semantic vector search and allow us to link retrieved text passages to their original documents and versions.

## Alternatives Considered

**PostgreSQL with pgvector**
- Structured storage and relationships between documents and chunks
- Vector search through the pgvector extension
- Support for HNSW and full-text search
- Additional configuration required for vector indexes

**Qdrant**
- Specialized database optimized for vector search
- Supports HNSW and metadata filtering
- Does not provide the same relational SQL capabilities as PostgreSQL

## Decision and Rationale

We decided to use **PostgreSQL with pgvector**.

The main reason is that our application requires both structured document management and semantic vector search.

PostgreSQL allows us to organize documents, chunks, and metadata in related tables. This makes it easier to identify which document, article, and version a retrieved passage belongs to.

Although Qdrant is specifically optimized for vector search, we considered PostgreSQL's relational capabilities more important for our use case. With pgvector, we can combine structured data management and vector search in one system.

## Team Decision

After presenting and discussing both alternatives, we conducted a Mentimeter poll.

- PostgreSQL with pgvector: **3 votes**
- Qdrant: **0 votes**

The result confirmed the participating team members' preference for PostgreSQL with pgvector.

## Consequences

We can manage document information and embeddings within one database. However, pgvector and the vector search indexes must be configured and tested during implementation.
