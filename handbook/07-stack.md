# Reference stack

You choose your stack. This is a zero-cost starting point, checked on 22.09.2026. Free tiers change, so check again before you commit to one.
Whatever you pick, including this, gets a [decision record](10-docs.md).

## The stack we recommend

| Layer | Recommendation | Why |
|---|---|---|
| Repo | Public, in our GitHub organization, MIT licence | Unlimited Actions minutes, secrets, push protection |
| Data and vectors | **One shared Supabase project** (Frankfurt): Postgres with pgvector and an HNSW index | One index for the whole team. Ingest once; everyone, the UI included, works against it. The corpus needs about 150 of the 500 MB |
| Sync schedule | A Python job in GitHub Actions, started by cron-job.org through `workflow_dispatch` | GitHub's own `schedule` trigger runs late or not at all |
| Evaluation | Our grader, plus promptfoo or Ragas if you want more, in CI | Free, with a gateway model as judge |
| Backend | Locally first. Later FastAPI in Docker on Render Free | `/ask` must be deployed by the first hidden run in December |
| Frontend | Locally first. Later Next.js on Vercel Hobby, or a static site on Cloudflare | Host it once the app works locally |

## Alternatives

| Stack | Good | Bad |
|---|---|---|
| Azure for Students: Container Apps, a Functions timer for the sync, Static Web Apps | Real cron and 100 USD credit, no credit card | Every student must pass verification with the TU email |
| Databricks Free Edition: jobs, Vector Search, MLflow tracing | Fewest moving parts | Its apps are not public, and a quota overrun stops compute for the day |

## Gotchas

| Gotcha | What to do |
|---|---|
| Free hosts sleep. Render takes about a minute to wake | Open the app ten minutes before a demo |
| Supabase pauses a project after 7 days idle, for example over Christmas | Let the sync run daily. Export a dump before the break |
| Secrets in a public repo leak | GitHub secrets only. Never put a key in the frontend |
| Free tiers change mid-project | Keep a Dockerfile, so the app moves to a new host in an hour |

Gone since this summer, do not plan with them: GitHub Models, DigitalOcean in the Student Pack, Docker Spaces on Hugging Face, the free tiers of Koyeb and Fly.io.
