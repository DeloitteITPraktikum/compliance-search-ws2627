# Quickstart

Ten minutes from your key to a streamed answer, an embedding and a PDF.

## 1. Set up

You need Python and the key we sent you.

```sh
pip install openai requests
export GATEWAY_KEY=sk-...   # your personal key, do not share or commit it
```

The same key works for the model gateway and for the document API.

## 2. First streamed answer

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])

stream = client.chat.completions.create(
    model="gpt-6-luna",
    messages=[{"role": "user", "content": "What is ICT risk? Two sentences."}],
    stream=True,
    reasoning_effort="low",
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.usage:
        print("\n", chunk.usage.prompt_tokens, "tokens in,", chunk.usage.completion_tokens, "tokens out")
```

The text arrives word by word. The last chunk carries the token counts.

While you wire up your code, use the model `mock`. It gives a fixed answer and costs nothing.

## 3. First embedding

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

With curl:

```sh
curl -H "Authorization: Bearer $GATEWAY_KEY" "https://tud-docs.pgoell.com/documents"
```

With Python:

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

## 5. Download one PDF

With curl:

```sh
curl -H "Authorization: Bearer $GATEWAY_KEY" \
  -o 32025R0301_EN.pdf "https://tud-docs.pgoell.com/documents/32025R0301_EN/file"
```

With Python:

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

## If it fails

| You see | Cause |
|---|---|
| `401` | The key is missing or wrong. Check `echo ${GATEWAY_KEY:0:3}` prints `sk-`. |
| An empty list, or `404` on a document | The documents are not yet published. They go online on 2026-10-20. A `404` can also mean an unknown id. |
| `429` | Over 60 requests per minute. Wait and retry. |
| `503` from the document API | It could not check your key with the gateway. Try again. |

More in the [FAQ](09-faq.md).
