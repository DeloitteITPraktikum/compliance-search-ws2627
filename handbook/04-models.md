# Models

All model calls go through our gateway. It speaks the OpenAI API, so the OpenAI SDK works unchanged.

```python
import os
from openai import OpenAI

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])
```

## The models

Measured on one typical question: about 3,200 tokens of regulation text, an answer of about 300 words, median of three runs.

| Model | Seconds per answer | USD per 1,000 questions | Use it when |
|---|---|---|---|
| `gpt-6-luna` | 9.6 | 0.90 | Default. Cheap, good at tools and JSON |
| `gpt-6-1-sol` | 10.6 | 11.03 | Your own evaluation shows the cheap models fail |
| `glm-5-3-flash` | 24.5 | 2.41 | A second model that thinks hard. Slow |
| `glm-5-3-flash-fast` | 6.3 | 0.68 | Bulk work, such as labelling chunks |
| `qwen3-embedding` | | 0.02 per million tokens | Embeddings: 1024 dimensions, German and English in one space |
| `mock` | | 0 | A fixed answer, for wiring up your code |

Any other model name gives `403`. With 10 USD a month you get about 11,000 such questions from `gpt-6-luna`, or about 900 from `gpt-6-1-sol`.
Write your choice and the numbers behind it into a decision record.

## Reasoning effort

The chat models think before they answer. Reasoning tokens count as output: you pay and wait for them.
Send `reasoning_effort="low"`, `"medium"` or `"high"`. Low is often enough and much faster.
`glm-5-3-flash-fast` defaults to low. Both `glm` models treat `"high"` like `"low"`.

## Good to know

| Topic | Rule |
|---|---|
| Streaming | `stream=True`. Stream answers in your UI: otherwise the user waits ten seconds for nothing |
| Tool calls | Work on all chat models. The `glm` models at low effort fail without streaming (HTTP 500): stream, or use default effort |
| JSON | `response_format` works as JSON mode and JSON schema. In JSON mode, the word "JSON" must be in a user message |
| Embedding batches | At most 150 texts per call. Each call counts once against the rate limit |
| Long inputs | An oversized text gives no error. Check your chunk sizes yourself |
| Repeatability | Temperature 0 is not repeatable. Run evaluations more than once before you trust a small gain |

## Cache your embeddings

Store each vector next to a hash of the text, your chunker version and the model name. Look up the hash before you embed.
A re-ingest then embeds only what changed. A full ingest of the start set costs about 6 cents and four minutes; without a cache you pay that on every fix.

## Budget and spend

| Limit | Value | When you pass it |
|---|---|---|
| Budget | 10 USD per month, resets on the 1st | `422` "Budget has been exceeded". Catch it and show a clear message, do not retry |
| Rate | 60 requests per minute | `429`. Wait and retry |

The [dashboard](https://tud-llm.pgoell.com/ui) shows your masked key, spend, usage per day and model, and your request log.
In code, `GET /key/info` returns spend, budget and reset date, and each response carries its cost in the header `x-litellm-response-cost`.
