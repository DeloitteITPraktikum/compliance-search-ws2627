# 0011: Database Structure for Documents and Chunks
- Status: Proposed 
- Date: 28.11.2026
- Owner: Nahla Aljasem

## Context
For our Compliance Search application, we need a database structure to store regulatory documents, their text chunks, metadata and embeddings.
The application processes regulatory PDF documents and divides them into smaller text sections called chunks. These chunks are later used to search for relevant information and generate answers with references to the original documents.
It is important that every chunk can be connected to its original document, including its language, version, article and page numbers. This allows our application to provide reliable and traceable sources.
The chunking team provided a structure containing 16 fields for each chunk. We therefore needed to adapt our database structure to these requirements.
We had already decided to use PostgreSQL with pgvector and Supabase as our database provider in previous decision records.

## Decision
We decided to use two connected tables in PostgreSQL: documents and chunks.

### 1. Documents Table
The documents table stores information about the original regulatory documents.
Each document has a unique id, which serves as its primary key.
We use separate columns for important information such as family_id, language, title, doc_type, version_date and source_url.
These fields help us identify documents, distinguish between different languages and versions, and find the original source.
We also store additional information such as status, sha256, pages, size_bytes and last_synced_at.
Fields such as supersedes, superseded_by, corrects and repealed_by allow us to represent relationships between regulatory documents.
This is important because regulations can be amended, corrected, replaced or repealed over time.
We chose separate metadata columns because important information can then be accessed, filtered and validated individually.

### 2. Chunks Table
The chunks table stores the individual text sections extracted from the documents.
We implemented the 16 fields specified by the chunking team.
Each chunk has a unique chunk_id, which serves as its primary key.
The document_id field is a foreign key that connects each chunk to its original document in the documents table.
We use family_id, version, language and doc_type to identify the document context of each chunk.
The fields unit_type, label, title and headings describe the structure of the original document.
We chose the PostgreSQL data type text[] for headings because a chunk can belong to several headings, such as a chapter and a section.
The fields page_start and page_end store the relevant page numbers. This makes it possible to locate and cite passages in the original PDF.
The field text stores the extracted text of a chunk.
The field embedding_text stores the prepared text that is sent to the embedding model. This text can include additional context, such as the document title and headings.
We also added embedding_vector with the PostgreSQL data type vector(1024).
An embedding model converts text into numerical vectors. Storing these vectors in PostgreSQL allows us to perform semantic similarity searches and find relevant passages based on their meaning.
The fields chunker_version and text_hash help us track how chunks were generated and identify changes to their text.

### 3. Data Integrity
We use primary keys to uniquely identify documents and chunks.
A foreign key connects chunks.document_id to documents.id.
We added database constraints to restrict language to DE or EN and unit_type to article, recital or annex.
These constraints prevent invalid values from being stored.
Our intended deletion policy is to preserve regulatory documents and their associated chunks. Documents that are referenced by chunks should not be deleted accidentally.
The final deletion rule must be verified before the database integration is considered complete.

## Alternatives

| Option | Why not |
|---|---|
|Store documents and chunks in one table |This would duplicate document information across many chunks and make document management more difficult.|
|Store all metadata in a single JSON column|JSON is flexible, but separate columns make important information easier to filter, validate and connect between tables.|
|Store only the original chunk text|The text alone would not provide enough structured information about document versions, articles, headings, pages and sources.|
|Store only embedding_text without numerical embeddings|This would not provide stored vectors for semantic similarity search directly within PostgreSQL.|

## Consequences
- Documents and chunks can be stored in separate, connected tables.
- Every chunk can be linked to its original document through document_id.
- The database can store information about document versions, languages, articles and page numbers.
- The structure supports traceable references to regulatory sources.
- Important metadata can be filtered and validated through separate columns.
- The chunks table matches the 16 fields provided by the chunking team.
- The database supports storing embeddings with 1024 dimensions for semantic search.
- Document relationships can be represented to support regulatory version management.
- The detailed structure requires coordination with the chunking and synchronization teams.
- Changes to the chunk format or embedding model may require future database adjustments.
- A final integration test and verification of the deletion rule are still required before the complete database setup can be considered finished.


