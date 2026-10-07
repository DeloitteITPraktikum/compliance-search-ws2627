# Models

All model calls go through our gateway. It speaks the OpenAI API, so the OpenAI SDK works unchanged.

Base URL: `https://tud-llm.pgoell.com/v1`

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])
print([model.id for model in client.models.list().data])
```

## The models

We measured each chat model on one typical question: about 3,200 tokens of regulation text plus a question, answered in about 300 words.
The numbers are the median of three runs.

| Model | Seconds to first word | Seconds per answer | USD per 1,000 questions | Use it when |
|---|---|---|---|---|
| `gpt-6-luna` | 7.5 | 9.6 | 0.90 | Default choice. Cheap and good at tools and JSON. |
| `gpt-6-1-sol` | 4.1 | 10.6 | 11.03 | The cheap models get it wrong. |
| `glm-5-3-flash` | 22.3 | 24.5 | 2.41 | You want a cheap second model that thinks hard. Slow. |
| `glm-5-3-flash-fast` | 3.5 | 6.3 | 0.68 | Same model with little thinking. For bulk work. |
| `mock` | | | 0 | Fixed answer. For wiring up your code. |

`glm-5-3-flash-fast` is `glm-5-3-flash` with a default of `reasoning_effort="low"`. Its row shows `glm-5-3-flash` measured at that setting.

Any other model name gives HTTP 403.

## What the host offers

Your key and your login work on `https://tud-llm.pgoell.com`, for this and nothing else:

| You can | With | Path |
|---|---|---|
| Chat, streamed or not, with tools and JSON | key | `POST /v1/chat/completions` |
| Embed | key | `POST /v1/embeddings` |
| Use the Responses API | key | `POST /v1/responses` |
| List your models | key | `GET /v1/models` |
| Read spend, budget and reset date of your key | key | `GET /key/info` |
| See your key (masked), spend and budget | login | Dashboard page Virtual Keys |
| See your spend, requests and tokens per day and model | login | Dashboard page Usage |
| See each of your calls with prompt, answer, tokens and cost | login | Dashboard page Logs |

Every other path on that host answers 404. That is by design, not a fault, so do not report it.
The dashboard has exactly these three pages.

List prices per million tokens:

| Model | Input | Output |
|---|---|---|
| `gpt-6-luna` | 0.10 USD | 0.50 USD |
| `gpt-6-1-sol` | 2.00 USD | 10.00 USD |
| `glm-5-3-flash`, `glm-5-3-flash-fast` | 0.15 USD | 0.50 USD |
| `qwen3-embedding` | 0.02 USD | |

## How to choose

- Start with `gpt-6-luna`.
- Switch to `gpt-6-1-sol` only where your own evaluation numbers show that the cheap models fail. Its token price is 20 times that of `gpt-6-luna`. A measured question costs about 12 times as much.
- Use `glm-5-3-flash-fast` for work with many calls, such as labelling chunks.
- Write the choice and the numbers behind it into a decision record.

With 10 USD you can ask `gpt-6-luna` about 11,000 such questions a month, or `gpt-6-1-sol` about 900.

## Reasoning effort

These models think before they answer. Thinking produces reasoning tokens.
Reasoning tokens count as output tokens: you pay for them and you wait for them.
`gpt-6-luna` can spend over 1,000 of them on a short answer.

Set `reasoning_effort` to `"low"`, `"medium"` or `"high"`. Lower is faster and cheaper.

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])

response = client.chat.completions.create(
    model="gpt-6-luna",
    messages=[{"role": "user", "content": "Name the EU regulation known as DORA in one sentence."}],
    reasoning_effort="low",
)
print(response.choices[0].message.content)
print("reasoning tokens:", response.usage.completion_tokens_details.reasoning_tokens)
```

Measured at `reasoning_effort="low"` on the same question as above:

| Model | Seconds per answer | USD per 1,000 questions |
|---|---|---|
| `gpt-6-luna` | 7.0 | 0.60 |
| `gpt-6-1-sol` | 9.0 | 10.26 |
| `glm-5-3-flash` | 6.3 | 0.68 |

Two oddities:

- Both `glm` names treat `"high"` like `"low"`. Use `"medium"` if you want real reasoning from them.
- A value you send replaces the default of `glm-5-3-flash-fast`.

## Streaming

Pass `stream=True` and print each piece as it arrives. The [Quickstart](02-quickstart.md) shows the loop.
The last chunk carries `usage` with the token counts.

Stream the answers in your UI. Without streaming the user sees nothing for about ten seconds.

## Tool calls

Tool calling works on all four chat models, with one limit.

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])

tools = [{
    "type": "function",
    "function": {
        "name": "search",
        "description": "Search the regulation corpus.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
}]

response = client.chat.completions.create(
    model="gpt-6-luna",
    messages=[{"role": "user", "content": "Find the DORA rule on penetration tests. Use the search tool."}],
    tools=tools,
)
call = response.choices[0].message.tool_calls[0]
print(call.function.name, call.function.arguments)
```

> **Warning: The one known limit of `glm-5-3-flash-fast`**
>
> A tool call without streaming fails with HTTP 500 and the message `litellm.APIConnectionError: 'content'`.
> Stream the call, or use `glm-5-3-flash`.

With streaming, the tool call arrives in pieces. Join the `arguments` strings:

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])

tools = [{
    "type": "function",
    "function": {
        "name": "search",
        "description": "Search the regulation corpus.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
}]

stream = client.chat.completions.create(
    model="glm-5-3-flash-fast",
    messages=[{"role": "user", "content": "Find the DORA rule on penetration tests. Use the search tool."}],
    tools=tools,
    stream=True,
)
name, arguments = "", ""
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.tool_calls:
        piece = chunk.choices[0].delta.tool_calls[0].function
        name += piece.name or ""
        arguments += piece.arguments or ""
print(name, arguments)
```

## JSON output

`response_format` works on all four chat models, as JSON mode and as JSON schema.
In JSON mode the word "JSON" must stand in a user message, or you get HTTP 400. The system prompt does not count.
Use a schema when your code parses the answer, for example to get citations as fields.

```python
import json
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])

schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "cited_answer",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {"answer": {"type": "string"}, "article": {"type": "string"}},
            "required": ["answer", "article"],
            "additionalProperties": False,
        },
    },
}

response = client.chat.completions.create(
    model="gpt-6-luna",
    messages=[{
        "role": "user",
        "content": "Text: 'Article 26(1): financial entities shall carry out TLPT at least every 3 years.' "
                   "Question: How often is TLPT required? Reply as JSON.",
    }],
    response_format=schema,
)
data = json.loads(response.choices[0].message.content)
print(data["answer"], "|", data["article"])
```

## Embeddings

`qwen3-embedding` turns a text into a vector of 1024 numbers. It is multilingual: a German text and its English twin land close to each other.

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])

texts = [
    "Meldung schwerwiegender IKT-Vorfälle",
    "reporting of major ICT incidents",
    "right of withdrawal for crypto-assets",
]
result = client.embeddings.create(model="qwen3-embedding", input=texts)
german, english, other = [item.embedding for item in result.data]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


print("same topic, two languages:", round(dot(german, english), 2))
print("different topic:", round(dot(german, other), 2))
```

The vectors have length 1, so the dot product is the cosine similarity.
The first pair scores about 0.83, the second about 0.43.

Send several texts in one call, at most 150. Over that you get HTTP 400.
Each call counts against your 60 requests per minute, however many texts it holds.
A text that is too long gives no error, so check your chunk sizes yourself.

### Cache your embeddings

Store each vector in your database next to a hash of the text and the model name.
Before you embed a chunk, look up its hash.
A re-ingest then embeds only chunks that are new or changed.

This saves budget, and it keeps a re-ingest fast when a document changes.

## Budget and spend

| Limit | Value | When you pass it |
|---|---|---|
| Budget | 10 USD per month, resets on the 1st | HTTP 422, see below |
| Rate | 60 requests per minute | HTTP 429, wait and retry |

The gateway books the cost after each call.

The team also gets one extra key for CI, with its own budget. Personal keys never go into the repo or into CI.

### See your spend

Open the invite link you got with your key and set a password. The link lasts 7 days.
Then log in at [https://tud-llm.pgoell.com/ui](https://tud-llm.pgoell.com/ui) with your email.

| Page | Shows |
|---|---|
| Virtual Keys | Your key in masked form (`sk-...` and the last four characters), your spend, your budget and its reset date. |
| Usage | Spend, requests and tokens per day and per model. |
| Logs | Each of your calls with prompt, answer, tokens and cost. |

You see only your own data. The dashboard has no other pages.
Nobody can show your key again after hand-out, not you and not us. Keep it safe.

In code, each answer carries the cost in its headers:

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])

raw = client.chat.completions.with_raw_response.create(
    model="gpt-6-luna",
    messages=[{"role": "user", "content": "Say ok."}],
    reasoning_effort="low",
)
print("this call, USD:", raw.headers["x-litellm-response-cost"])
print("key spend, USD:", raw.headers["x-litellm-key-spend"])
print(raw.parse().choices[0].message.content)
```

With your key, the answer also carries `x-litellm-key-max-budget`.
Spend, budget and reset date as JSON:

```sh
curl -H "Authorization: Bearer $GATEWAY_KEY" "https://tud-llm.pgoell.com/key/info"
```

### What a budget error looks like

Over budget, every call fails with HTTP 422 and a message of this form:

```text
Budget has been exceeded! ... Current cost: ..., Max budget: ...
```

In Python the OpenAI SDK raises `openai.UnprocessableEntityError`.
The budget resets on the 1st of the month. If you cannot wait, ask us. See the [FAQ](09-faq.md#my-budget-is-used-up).

Catch this error in your app and show a clear message. Do not retry it.
