# compliance-search-ws2627

TU Darmstadt IT-Praktikum WS 2026/27: compliance search over EU financial regulation.

| Folder | Holds |
|---|---|
| [`setup/`](setup/README.md) | Start here: install uv, put your key in `.env`, run `uv run --env-file .env check.py` |
| [`docs/`](docs/README.md) | The handbook. Start with [docs/README.md](docs/README.md) |
| [`evals/student_kit/`](evals/student_kit/README.md) | Grade your app on the sample questions with your own key |
| [`openapi/`](openapi/) | OpenAPI specs: [document API](openapi/document-api.json) (`https://tud-docs.pgoell.com`) and [model gateway](openapi/model-gateway.json) (`https://tud-llm.pgoell.com`, student routes only) |

Both services take your personal student key as a bearer token.
