# 0007: The backend is a FastAPI app served by uvicorn

- Status: Proposed
- Date: 2026-11-10
- Owner: Team

## Context

Our app must answer `POST /ask` in the fixed JSON format from `handbook/01-task.md`. The grader, the frontend and the hidden test runs all call this one route.
The pipeline behind it (sync, processing, retrieval, answer) is Python, in one package (record 0002), and the model gateway speaks the OpenAI API, which has a Python SDK.
Most of the team is new to backend development, so the framework should need little code and have good documentation. It must cost nothing.

## Decision

The backend is a FastAPI app, served by uvicorn. Pydantic models in `backend/src/compliance_search/models.py` define the request and response of `/ask`.
This record covers the framework only. Where the app is hosted is a separate decision.

## Alternatives

| Option | Why not |
|---|---|
| Flask | Has no built-in validation or typed request and response models. We would write the checks for the fixed `/ask` format by hand |
| Django with Django REST Framework | Brings an ORM, an admin site and templates that we do not use. More to learn for a single route |
| A framework in another language, such as Express | The pipeline is Python. A second language would split the team and the code |

## Consequences

- FastAPI rejects a missing or empty `question` with `422` on its own, and generates interactive API docs at `/docs` from the models.
- The models are the single definition of the `/ask` format. A change to them is a change to the interface and needs the frontend and the grader in mind.
- Errors use FastAPI's default `{"detail": ...}` format, not one of our own.
- The handbook's recommended stack is FastAPI in Docker, so its hints apply to us without translation.
- FastAPI needs an ASGI server. The container must start uvicorn.
- FastAPI supports streaming responses, which the UI may need later for long answers.
