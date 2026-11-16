
# 0008: Selection of Database Type

- Status: Accepted
- Date: 2026-11-16
- Owner: Nahla Aljasem
- Jira: DEL-2

## Context

For our Compliance Search application, we need a database to store regulatory documents, chunks, metadata and embeddings.

The database must support vector search and allow us to connect text passages to their original documents, articles and versions. This is important because our AI application must provide clear and correct sources.

We compared PostgreSQL with pgvector and Qdrant to find the best solution for our project.

## Decision

We decided to use **PostgreSQL with pgvector**.

PostgreSQL allows us to store documents, chunks and metadata in different tables and connect them with each other. This makes it easier to find out which document, article and version a text passage belongs to.

With pgvector, we can also store embeddings and search for similar text passages. PostgreSQL supports HNSW to make vector search faster.

The main reason for our decision is that we need both structured data storage and vector search in one database.

After presenting the advantages and disadvantages, we voted with Mentimeter. PostgreSQL with pgvector received 3 votes, while Qdrant received 0 votes.

## Alternatives

| Option | Why not |
|---|---|
| Qdrant | Qdrant is designed especially for vector search and supports HNSW and metadata filtering. However, it does not offer the same relational SQL functions as PostgreSQL. For our project, connecting documents, chunks and metadata in tables is more important. Using Qdrant could also require an additional database for more complex data relationships. |

## Consequences

- We can store documents, chunks, metadata and embeddings in one database.
- We can connect text passages to their original documents and versions.
- We can use both vector search and full-text search.
- We need to set up pgvector and configure the search indexes.
- Additional optimization may be needed for larger amounts of data.
