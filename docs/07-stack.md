# Reference stack and free tiers

You choose your stack. This page is a recommendation, not a rule.

Two rules do apply:

1. Zero cost. Nothing may cost money.
2. Every choice needs a decision record in the repo: what you chose, what else you looked at, and why. That holds if you take our recommendation too.

We checked the offers below on 2026-09-22. Several free tiers vanished this summer, so check again before you commit to one.

## Claim in week 1

Both take days to weeks to verify. Apply at kick-off with your TU email.

| Program | What you get |
|---|---|
| [GitHub Student Developer Pack](https://education.github.com/pack) | Copilot, Codespaces with 180 core-hours per month, JetBrains tools |
| [Azure for Students](https://azure.microsoft.com/en-us/free/students) | 100 USD credit per year, no credit card, Container Apps and Functions free |

## The stack we recommend

For a team without strong preferences. No part needs a credit card.

| Layer | Recommendation | Why |
|---|---|---|
| Repo | Public repo in our GitHub organization, MIT licence | Unlimited Actions minutes, environment secrets, push protection. A private repo on the free plan loses all three. |
| Frontend | Next.js on Vercel Hobby, or a static site on Cloudflare | No sleep, no card. |
| Backend | FastAPI in Docker on Render Free | Runs any Python dependency. Sleeps after 15 minutes idle, so ping it with UptimeRobot. |
| Database and vectors | Supabase Free in Frankfurt, Postgres with pgvector (HNSW index) | One store for chunks, vectors and metadata. The corpus needs about 150 MB of the 500 MB. |
| Sync schedule | A Python job in GitHub Actions, started by cron-job.org through `workflow_dispatch` | GitHub's own `schedule` trigger runs hours late or not at all. |
| Evaluation | promptfoo or Ragas in CI, with one of our chat models as judge | Free. Runs next to our grader. |
| Fallback for local work | Gemini Flash-Lite free tier for chat, `bge-m3` through Ollama for embeddings | For when our gateway is down or your rate limit hits. Development only. |

Vectors from two embedding models do not mix. Never write fallback vectors into the index your app serves.

## Two alternatives

| Stack | Good | Bad |
|---|---|---|
| Azure for Students end to end: Container Apps, a Functions timer for the sync, Static Web Apps, Supabase for pgvector | Real cron and a 100 USD buffer | Every student must pass Azure verification. |
| Databricks Free Edition: jobs, Vector Search, MLflow tracing | Fewest moving parts | Its apps are not public, and a quota overrun stops compute for the day. |

## Gotchas

| # | Gotcha | What to do |
|---|---|---|
| 1 | Free tiers sleep. Render takes about a minute to wake. | Ping the app. Open it 10 minutes before a demo. Keep a local run as fallback. |
| 2 | Supabase pauses a project after 7 days idle. The Christmas break will pause it. | Let the sync job run daily. Export a dump before the break. |
| 3 | Secrets in a public repo leak. | Environment secrets only. A gitleaks pre-commit hook. Never put a key in the frontend. |
| 4 | GitHub's `schedule` trigger is unreliable. | Start the workflow from outside through `workflow_dispatch`. |
| 5 | Free LLM tiers have tight rate limits, some as low as 20 requests per day. | Use them for development only. Cache embeddings in the database, so a re-ingest never embeds twice. |
| 6 | Free tiers change mid-project. | Keep a Dockerfile and a compose file, so the app moves to a new host in an hour. |
| 7 | A repo in a personal account leaves with its owner. | The repo lives in our organization. |
| 8 | Mistral's free tier trains on your prompts by default. | Opt out or avoid it. |

## Gone since this summer

Do not plan with these: GitHub Models, DigitalOcean in the Student Pack, Docker Spaces on Hugging Face, the Koyeb free tier, the Fly.io free tier.
