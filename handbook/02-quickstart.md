# Quickstart

Ten minutes from your key to a streamed answer, an embedding and a PDF.

## 1. Install

| Tool | macOS, Linux | Windows (PowerShell) |
|---|---|---|
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Git | `git --version`, else git-scm.com | `winget install Git.Git` |
| VS Code | code.visualstudio.com | `winget install Microsoft.VisualStudioCode` |

uv brings Python 3.12 and the packages. You need no `pip` and no virtual environment of your own.

## 2. Clone and add your key

```sh
git clone https://github.com/DeloitteITPraktikum/compliance-search-ws2627
cd compliance-search-ws2627/setup
cp .env.example .env          # Windows: Copy-Item .env.example .env
```

Open `.env` and replace `sk-...` with your key. `.gitignore` keeps `.env` out of Git. Never commit it.

## 3. Check everything

```sh
uv run --env-file .env check.py
```

You should see five lines:

```text
ok    models             6 models
ok    chat, gpt-6-luna   OK
ok    embedding          1024 dimensions
ok    document list      34 documents
ok    PDF download       ... bytes
```

## 4. Try the scripts

All run from `setup/` with `uv run --env-file .env <script>`. Read the code after you run it: each is a few lines.

| Script | What it does |
|---|---|
| `chat.py` | Streams one answer from `gpt-6-luna`. `--model mock "hello"` costs nothing |
| `embed.py` | Embeds a German and an English text: 1024 numbers each |
| `list_documents.py` | Lists the documents with status, language and pages, and prints `server_time` |
| `download_pdf.py` | Saves one PDF to `setup/downloads/`. Default `32025R0301_EN`, five pages |

Keep `server_time` from the document list. Your next sync starts from it. See the [sync recipe](03-document-api.md#sync-recipe).

## With curl

uv puts the key into the scripts it runs, not into your shell. For curl, set it first.

```sh
export GATEWAY_KEY=sk-...
curl --fail -H "Authorization: Bearer $GATEWAY_KEY" "https://tud-docs.pgoell.com/documents"
```

On Windows, use PowerShell, write `curl.exe` and `$env:GATEWAY_KEY`, and keep each command on one line:

```powershell
$env:GATEWAY_KEY = "sk-..."
curl.exe --fail -H "Authorization: Bearer $env:GATEWAY_KEY" "https://tud-docs.pgoell.com/documents"
```

## If it fails

| You see | Fix |
|---|---|
| `GATEWAY_KEY is missing` | No `.env` in `setup/`, or you left out `--env-file .env` |
| `401` | The key is wrong. Check `.env`, or your shell for curl |
| `429` | Over 60 requests per minute. Wait a minute |
| `503` from the document API | It could not check your key. Try again |
| `uv: command not found` | Open a new terminal. Installed uv with pip: use `python -m uv` |
| `unexpected argument '--env-file'` | Your uv is too old: `uv self update` |

More in the [FAQ](09-faq.md).
