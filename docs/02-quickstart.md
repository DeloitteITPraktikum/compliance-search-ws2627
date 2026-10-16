# Quickstart

Ten minutes from your key to a streamed answer, an embedding and a PDF.

Each code example below is also a script in [`setup/`](https://github.com/DeloitteITPraktikum/compliance-search-ws2627/blob/main/setup/README.md) of your repo. Run the script, then read the code.

## 1. Set up

You need [uv](https://docs.astral.sh/uv/) and the key we sent you. uv brings Python 3.12 and the packages, so you need no `pip` and no virtual environment of your own.

| | macOS, Linux | Windows (PowerShell) |
|---|---|---|
| Install uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Go to `setup/`, from the repo root | `cd setup` | `cd setup` |
| Make your `.env` | `cp .env.example .env` | `Copy-Item .env.example .env` |

Open `.env` and replace `sk-...` with your key. `.gitignore` keeps `.env` out of Git. Never commit it, and never share your key.

Then check everything in one run. The same command works on every system:

```shell
uv run --env-file .env check.py
```

You should see six lines that start with `ok`. The [setup README](https://github.com/DeloitteITPraktikum/compliance-search-ws2627/blob/main/setup/README.md) shows them and lists the fixes when one fails.

The same key works for the model gateway and for the document API. All commands below run in `setup/`.

## 2. First streamed answer

```shell
uv run --env-file .env chat.py
```

This is `chat.py`:

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])

stream = client.chat.completions.create(
    model="gpt-6-luna",
    messages=[{"role": "user", "content": "What is ICT risk? Two sentences."}],
    stream=True,
    stream_options={"include_usage": True},
    reasoning_effort="low",
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.usage:
        print("\n", chunk.usage.prompt_tokens, "tokens in,", chunk.usage.completion_tokens, "tokens out")
```

The text arrives word by word. The last chunk carries the token counts.

While you wire up your code, use the model `mock`: `uv run --env-file .env chat.py --model mock "hello"`. It gives a fixed answer and costs nothing.

## 3. First embedding

```shell
uv run --env-file .env embed.py
```

This is `embed.py`:

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])

result = client.embeddings.create(
    model="qwen3-embedding",
    input=["Meldung schwerwiegender IKT-Vorfälle", "reporting of major ICT incidents"],
)
vectors = [item.embedding for item in result.data]
print(len(vectors), "vectors with", len(vectors[0]), "dimensions each")
```

You get one vector with 1024 numbers for each text. More on [Models](04-models.md).

## 4. List the documents

```shell
uv run --env-file .env list_documents.py
```

This is `list_documents.py`:

```python
import os
import requests

DOCS = "https://tud-docs.pgoell.com"
headers = {"Authorization": f"Bearer {os.environ['GATEWAY_KEY']}"}

response = requests.get(f"{DOCS}/documents", headers=headers, timeout=30)
response.raise_for_status()
body = response.json()

print("server_time:", body["server_time"])
for doc in body["documents"]:
    print(doc["id"], doc["status"], doc["language"], doc["pages"], "pages")
```

Keep `server_time`. Your next sync starts from it. See the [sync recipe](03-document-api.md#sync-recipe).

### With curl

uv puts the key from `.env` only into the scripts it runs. For curl, set it in your shell first:

| macOS, Linux | Windows (PowerShell) |
|---|---|
| `export GATEWAY_KEY=sk-...` | `$env:GATEWAY_KEY = "sk-..."` |

On macOS and Linux:

```sh
curl --fail -H "Authorization: Bearer $GATEWAY_KEY" "https://tud-docs.pgoell.com/documents"
```

On Windows, in PowerShell:

```powershell
curl.exe --fail -H "Authorization: Bearer $env:GATEWAY_KEY" "https://tud-docs.pgoell.com/documents"
```

On Windows, write `curl.exe`, not `curl`: in Windows PowerShell 5.1, `curl` is a short name for `Invoke-WebRequest`. Write `$env:GATEWAY_KEY`: in PowerShell, `$GATEWAY_KEY` is empty. Use PowerShell, not cmd: cmd sends `$env:GATEWAY_KEY` as plain text. Keep each command on one line.

## 5. Download one PDF

```shell
uv run --env-file .env download_pdf.py 32025R0301_EN
```

The script saves the file to `setup/downloads/`, which `.gitignore` keeps out of Git. This is `download_pdf.py` without its argument handling:

```python
import os
import requests

DOCS = "https://tud-docs.pgoell.com"
headers = {"Authorization": f"Bearer {os.environ['GATEWAY_KEY']}"}
doc_id = "32025R0301_EN"

response = requests.get(f"{DOCS}/documents/{doc_id}/file", headers=headers, timeout=60)
response.raise_for_status()
with open(f"{doc_id}.pdf", "wb") as file:
    file.write(response.content)
print("saved", len(response.content), "bytes, ETag", response.headers["ETag"])
```

`32025R0301_EN` is a five-page act on incident reports. It makes a good first test file.

With curl, on macOS and Linux:

```sh
curl --fail -o 32025R0301_EN.pdf -H "Authorization: Bearer $GATEWAY_KEY" "https://tud-docs.pgoell.com/documents/32025R0301_EN/file"
```

On Windows, in PowerShell:

```powershell
curl.exe --fail -o 32025R0301_EN.pdf -H "Authorization: Bearer $env:GATEWAY_KEY" "https://tud-docs.pgoell.com/documents/32025R0301_EN/file"
```

`--fail` makes curl stop on an HTTP error. Without it, curl saves the error message as `32025R0301_EN.pdf`.

## If it fails

| You see | Cause |
|---|---|
| `GATEWAY_KEY is missing` or `KeyError: 'GATEWAY_KEY'` | No `.env` in `setup/`, or you left out `--env-file .env`. |
| `401` | The key is missing or wrong. Check the key in `.env`. For curl, check the key in your shell. |
| `401` or an `Invoke-WebRequest` error on Windows | You wrote `curl` or `$GATEWAY_KEY` in PowerShell, or used cmd. Write `curl.exe` and `$env:GATEWAY_KEY` in PowerShell. |
| An empty list, or `404` on a document | The documents are not yet published. They go online on 2026-10-20. A `404` can also mean an unknown id. |
| `429` | Over 60 requests per minute. Wait and retry. |
| `503` from the document API | It could not check your key with the gateway. Try again. |

More in the [setup README](https://github.com/DeloitteITPraktikum/compliance-search-ws2627/blob/main/setup/README.md) and the [FAQ](09-faq.md).
