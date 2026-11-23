- Status: Proposed 
- Date: 16.11.2026
- Owner: Nahla Aljasem

## Context
After choosing PostgreSQL with pgvector, we needed a provider to host our database.
Our database must be accessible to the whole team, easy to manage and free to use because Deloitte requires a zero-cost solution.
We compared Supabase, Neon and Qdrant Cloud.


## Decision
We decided to use Supabase as our database provider.
Supabase offers a simple interface where we can create tables, manage our database and view stored information.
It also provides integrated APIs, which make it easier to connect our application to the database.
Another important reason is that Deloitte already recommends Supabase with PostgreSQL, pgvector and HNSW for our project.
Supabase also offers a free plan, which is important because our project must not cause any costs.
After presenting and discussing the different providers, we voted with Mentimeter. Supabase received 7 votes, while Neon and Qdrant Cloud received 0 votes.

## Alternatives

|Option|Why not|
|---|---|
|Neon|Neon also supports PostgreSQL with pgvector. It offers automatic scaling and Scale-to-Zero. However, these features are less important for our project. We preferred Supabase because of its simple management interface, integrated APIs and Deloitte's recommendation.|
|Qdrant Cloud|Qdrant Cloud is designed for hosting Qdrant. Since we decided to use PostgreSQL with pgvector, it is not the right choice for our selected database technology.|

## Consequences
* We can use one central database for the whole team.
* We can manage our PostgreSQL database through the Supabase interface.
* The integrated APIs make it easier to connect our application.
* The free plan has limited storage and resources.
* Supabase projects may be paused after longer periods of inactivity.
* We need to check that the database is available before tests and presentations.
* We must stay within the free plan to meet the zero-cost requirement.