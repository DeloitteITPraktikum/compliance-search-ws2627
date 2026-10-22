# Setup

Scripts that check your access to the model gateway and the document API before you write any code.

```sh
cp .env.example .env                 # then paste your key into .env
uv run --env-file .env check.py      # five lines that start with ok
```

| Script | What it does |
|---|---|
| `check.py` | All checks in one run. Costs a fraction of a cent |
| `chat.py` | Streams one answer. `--model mock` costs nothing |
| `embed.py` | Embeds two texts, German and English |
| `list_documents.py` | Lists the documents with status, language and pages |
| `download_pdf.py` | Saves one PDF to `downloads/`, default `32025R0301_EN` |

`.env` also sets `KEY`, `DOCS_URL` and `GATEWAY_URL` for the [grader](../handbook/06-scoring.md#run-the-grader).
In CI, [`setup-check.yml`](../.github/workflows/setup-check.yml) runs `check.py` with the team key `CI_GATEWAY_KEY`.

Install steps and fixes for common errors: [Quickstart](../handbook/02-quickstart.md).
