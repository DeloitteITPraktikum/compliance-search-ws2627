"""Stream one answer from the model gateway. Quickstart step 2.

    uv run --env-file .env chat.py "What is ICT risk? Two sentences."
    uv run --env-file .env chat.py --model mock "hello"
"""
import argparse
import os

from openai import OpenAI

p = argparse.ArgumentParser()
p.add_argument("question", nargs="?", default="What is ICT risk? Two sentences.")
p.add_argument("--model", default="gpt-6-luna")
args = p.parse_args()

client = OpenAI(base_url="https://tud-llm.pgoell.com/v1", api_key=os.environ["GATEWAY_KEY"])
stream = client.chat.completions.create(
    model=args.model,
    messages=[{"role": "user", "content": args.question}],
    stream=True,
    stream_options={"include_usage": True},
    reasoning_effort="low",
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.usage:
        print("\n", chunk.usage.prompt_tokens, "tokens in,", chunk.usage.completion_tokens, "tokens out")
