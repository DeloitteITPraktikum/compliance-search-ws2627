
# 0002: Render Free as Backend Hosting Provider

- Status: Accepted
- Date: 2026-11-12
- Owner: VladimirLipa

## Context

We need a hosting provider for our backend that is free and publicly accessible. The backend should be reachable through the POST /ask endpoint so the grader can use it during the first run in December.

We also need a solution that supports Docker and is not too complicated to set up.

## Decision

We decided to use Render Free for hosting our backend. It meets our requirements and allows us to deploy the backend as a Docker container without hosting costs.

## Alternatives

| Option | Why not |
|---|---|
| Azure Container Apps | Render Free seems easier to set up and is sufficient for our current requirements. |

## Consequences

- Render Free is free to use, but has some limitations.
- After 15 minutes without requests, the backend goes to sleep.
- Starting it again can take around one minute.
- We discussed this with Pascal. Since the grader waits up to 120 seconds per question, this should normally be fine.
- If we get timeouts, we can increase the timeout or add a retry.
- Pascal provided us with a separate API key and its own budget.
- We will store this key as an environment variable in Render and not in the Git repository.
- The Docker setup and deployment will be done in the next task.
