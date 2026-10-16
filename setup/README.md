# Setup

A small uv project that checks your access before you write any code: the model gateway, the document API and your key. The scripts are the [Quickstart](../docs/02-quickstart.md) as files.

## 1. Install the tools

| Tool | macOS, Linux | Windows (PowerShell) |
|---|---|---|
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Git | `git --version`, else install from git-scm.com | `winget install Git.Git` |
| VS Code | code.visualstudio.com | `winget install Microsoft.VisualStudioCode` |

uv installs the right Python for you. You do not need `pip` or a virtual environment of your own.

Installed uv with `pip install uv` instead? That works too. If `uv` is not found, run `python -m uv` in its place. Your own Python does not matter: uv uses Python 3.12 from `.python-version` and downloads it if needed.

## 2. Put your key in `.env`

From the repo root:

| macOS, Linux | Windows (PowerShell) |
|---|---|
| `cd setup` | `cd setup` |
| `cp .env.example .env` | `Copy-Item .env.example .env` |

Open `.env` and replace `sk-...` with the key from your mail. `.gitignore` keeps `.env` out of Git. Never commit it.

## 3. Check everything

```sh
uv run --env-file .env check.py
```

The same command works on every system. The first run downloads Python and the packages. You should see five lines:

```
ok    models             6 models
ok    chat, gpt-6-luna   OK
ok    embedding          1024 dimensions
ok    document list      34 documents
ok    PDF download       ... bytes
```

Before 2026-10-20 10:00 the document list is empty and the PDF is not published yet. Both checks still say `ok`.

## The scripts

| Script | What it does |
|---|---|
| `check.py` | All checks in one run. Costs a fraction of a cent |
| `chat.py` | Streams one answer. `--model mock` costs nothing |
| `embed.py` | Embeds two texts, German and English |
| `list_documents.py` | Lists the documents with status, language and pages |
| `download_pdf.py` | Saves one PDF to `downloads/`, default `32025R0301_EN` |

Run each with `uv run --env-file .env <script>`.

## The grader

`.env` also sets `KEY`, `DOCS_URL` and `GATEWAY_URL` for the [evaluation kit](../evals/student_kit/README.md). Once your app answers `POST /ask`:

```sh
uv run --env-file .env ../evals/student_kit/grade.py --url http://localhost:8000 --out report.json
```

## In CI

The team's CI key is the repo secret `CI_GATEWAY_KEY`. [`.github/workflows/setup-check.yml`](../.github/workflows/setup-check.yml) runs `check.py` with it on Linux, macOS and Windows. Your personal key never goes into CI.

## If it fails

| You see | Cause |
|---|---|
| `GATEWAY_KEY is missing` | No `.env`, or you left out `--env-file .env` |
| `AuthenticationError` or `401` | The key in `.env` is wrong or has a typo |
| `429` | Over 60 requests per minute. Wait a minute |
| `uv: command not found` | Open a new terminal after installing uv. Installed with pip: use `python -m uv` |
| `unexpected argument '--env-file'` | Your uv is too old. `uv self update`, or `pip install -U uv` if you installed it with pip |

More in the [FAQ](../docs/09-faq.md).
