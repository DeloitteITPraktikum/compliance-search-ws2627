# 0002: One repository with a fixed top-level layout

- Status: Proposed
- Date: 2026-11-06
- Owner: Team

## Context

The team needs to know where backend, frontend, database migrations, tests, evaluations and docs belong, so that every member puts a file in the same place.
The repo already holds `setup/`, `handbook/`, `openapi/`, `evals/student_kit/` and the `docs/` sections from the kick-off. These stay unchanged.

## Decision

Everything lives in this one repository: `backend/` (Python package `compliance_search` in a `src/` layout, one subpackage per pipeline step: sync, processing, index, retrieval, answer, api, clients), `frontend/`, `db/migrations/`, `evals/gold/` and `evals/history/`, with workflows in `.github/workflows/`.

## Alternatives

| Option | Why not |
|---|---|
| None | The team adopted the layout directly, without comparing other layouts |

## Consequences

Each team member finds the place for a file without asking, and the subpackages match the pipeline steps, so work splits along the Jira tickets.
The backend is its own `uv` project, separate from `setup/`, so its dependencies do not mix with the setup scripts.
Empty folders carry a `.gitkeep` or an empty placeholder file until they get real files. If a step needs a different split, the layout changes through a new record.
