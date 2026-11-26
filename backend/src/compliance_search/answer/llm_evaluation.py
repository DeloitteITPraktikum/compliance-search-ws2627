"""Compare the gateway chat models for answering /ask questions (DEL-10).

Every model answers 6 questions from evals/student_kit/sample.jsonl, each twice
(answers are not repeatable, see handbook/04-models.md). The script checks each
answer automatically and prints a summary table per model.

Run from backend/:
    uv run --env-file ../setup/.env python src/compliance_search/answer/llm_evaluation.py
"""
import json
import os
import time

from openai import OpenAI

# Address of the model gateway (from handbook/04-models.md)
GATEWAY_URL = "https://tud-llm.pgoell.com/v1"

# The 4 chat models from handbook/04-models.md
MODELS = ["gpt-6-luna", "glm-5-3-flash-fast", "glm-5-3-flash", "gpt-6-1-sol"]

# How often each question is asked per model
RUNS = 2

# Fixed refusal sentences that the grader recognises (see metrics.is_refusal)
REFUSAL_EN = "The documents do not contain information on this question."
REFUSAL_DE = "Die Dokumente enthalten keine Informationen zu dieser Frage."

# Fixed rules for every question: the 6 building blocks from the research
SYSTEM_PROMPT = f"""You are an assistant for EU and German financial regulation (DORA, CRR, MaRisk and others).
Rules:
1. Answer only with information from the numbered passages. Never use outside knowledge.
2. Support every statement with the passage number in brackets, e.g. [1].
3. If the passages do not answer the question, reply exactly with "{REFUSAL_EN}" (English question)
   or "{REFUSAL_DE}" (German question) and list no sources.
4. Only refuse if the passages really say nothing about the question.
5. If the question contains a wrong assumption, correct it and cite the passage that shows it.
6. Answer in the language of the question.
Reply in JSON with this format:
{{"answer": "<text>", "sources": [{{"passage": <number>, "quote": "<exact sentence from the passage>"}}]}}"""

# 6 questions from sample.jsonl. "facts": every fact must appear in the answer,
# each fact is a list of accepted spellings (like must_contain in the grader).
TESTS = [
    {
        "id": "S-01", "kind": "simple EN",
        "question": "How often must a financial entity that is in scope for threat-led penetration testing run such a test?",
        "passages": [{"document_id": "32022R2554_EN", "page_start": 46,
                      "text": "Financial entities ... shall carry out at least every 3 years advanced testing by means of TLPT."}],
        "facts": [["3 years", "three years"]],
        "refuse": False,
    },
    {
        "id": "S-02", "kind": "simple DE",
        "question": "Wie lange kann ein Kleinanleger den Kauf eines Kryptowerts, der kein vermögenswertereferenzierter Token und kein E-Geld-Token ist, widerrufen?",
        "passages": [{"document_id": "02023R1114-20240109_DE", "page_start": 22,
                      "text": "Kleinanleger haben eine Frist von 14 Kalendertagen, um ihre Zustimmung zum Kauf von anderen Kryptowerten als vermögenswertereferenzierten Token und E-Geld-Token gebührenfrei zu widerrufen."}],
        "facts": [["14 Kalendertag"]],
        "refuse": False,
    },
    {
        "id": "S-10", "kind": "DE question, EN source",
        "question": "Welchen Rang trägt der direkte IKT-Drittdienstleister im Informationsregister innerhalb der IKT-Dienstleistungskette?",
        "passages": [{"document_id": "32024R2956_EN", "page_start": 4,
                      "text": "The rank of the direct ICT third-party service provider in the ICT service supply chain shall always be '1'."}],
        "facts": [["Rang 1", "Rang „1“", "Rang '1'", "Rang ‚1‘", "Rang \"1\"", "Rang von 1"]],  # German spelling only
        "refuse": False,
    },
    {
        "id": "S-12", "kind": "refuse",
        "question": "Was verlangen die KAIT von Kapitalverwaltungsgesellschaften beim Berechtigungsmanagement?",
        "passages": [{"document_id": "32022R2554_DE", "page_start": 46,
                      "text": "Finanzunternehmen ... führen mindestens alle drei Jahre anhand von TLPT erweiterte Tests durch."}],
        "facts": [],
        "refuse": True,
    },
    {
        "id": "S-17", "kind": "false premise",
        "question": "Since Article 31 DORA leaves the designation of critical ICT third-party service providers to the national competent authorities, which criteria must they base that designation on?",
        "passages": [
            {"document_id": "32022R2554_EN", "page_start": 53,
             "text": "The ESAs, through the Joint Committee and upon recommendation from the Oversight Forum established pursuant to Article 32(1), shall designate the ICT third-party service providers that are critical for financial entities."},
            {"document_id": "32022R2554_EN", "page_start": 54,
             "text": "The designation referred to in paragraph 1, point (a), shall be based on all of the following criteria: the systemic impact on the stability, continuity or quality of the provision of financial services; the systemic character or importance of the financial entities that rely on the provider; the reliance of financial entities on the services in relation to critical or important functions; the degree of substitutability of the provider."},
        ],
        "facts": [["ESA"], ["substitutab"]],  # names the ESAs (corrects the premise) and the criteria
        "refuse": False,
    },
    {
        "id": "S-20", "kind": "trap 40 vs. 60",
        "question": "Once an application for authorisation as a crypto-asset service provider is complete, how many working days does the competent authority have to assess it?",
        "passages": [
            {"document_id": "02023R1114-20240109_EN", "page_start": 34,
             "text": "Competent authorities shall, within 60 working days of receipt of a complete application, assess whether the applicant issuer complies with the requirements of this Title."},
            {"document_id": "02023R1114-20240109_EN", "page_start": 95,
             "text": "Competent authorities shall, within 40 working days from the date of receipt of a complete application, assess whether the applicant crypto-asset service provider complies with this Title."},
        ],
        "facts": [["40 working days", "40 days", "forty working days"]],
        "refuse": False,
    },
]


def build_user_message(question: str, passages: list[dict]) -> str:
    """Build the user message for the LLM from the found passages and the question.

    Each passage gets a number and its metadata (document, page), so the model
    can cite it as [1], [2], ... and our code can turn the number back into a citation.

    Args:
        question: The question typed by the user.
        passages: Chunks with the keys document_id, page_start and text.

    Returns:
        One text: the numbered passages, the question and "Answer in JSON."
    """
    lines = ["Passages:"]
    for number, passage in enumerate(passages, start=1):
        lines.append(f"[{number}] {passage['document_id']} | page {passage['page_start']}")
        lines.append(passage["text"])
        lines.append("")  # empty line between passages
    lines.append(f"Question: {question}")
    lines.append("Answer in JSON.")  # the gateway needs the word JSON in the user message
    return "\n".join(lines)


def check_answer(raw_answer: str, test: dict) -> tuple[bool, bool, str]:
    """Check one model answer against the expected result of a test.

    Returns:
        (json_ok, correct, note): json_ok is True if the answer is valid JSON in our
        format, correct is True if the content is right, note explains a failure.
    """
    # 1. Is it valid JSON in our format?
    try:
        data = json.loads(raw_answer)
    except json.JSONDecodeError:
        return False, False, "no valid JSON"
    answer = str(data.get("answer", ""))
    sources = data.get("sources") or []
    numbers = [source.get("passage") for source in sources if isinstance(source, dict)]
    json_ok = all(isinstance(n, int) and 1 <= n <= len(test["passages"]) for n in numbers)

    # 2. Refusal test: fixed sentence and no sources
    if test["refuse"]:
        refused = (REFUSAL_EN in answer or REFUSAL_DE in answer) and not sources
        return json_ok, refused, "" if refused else "did not refuse"

    # 3. Normal test: no refusal, at least one source, every fact in the answer
    if REFUSAL_EN in answer or REFUSAL_DE in answer:
        return json_ok, False, "refused although answerable"
    if not sources:
        return json_ok, False, "no sources"
    text = answer.lower()
    missing = [fact[0] for fact in test["facts"] if not any(v.lower() in text for v in fact)]
    if missing:
        return json_ok, False, f"missing: {', '.join(missing)}"
    return json_ok, True, "" if json_ok else "passage number not an int"


def ask_model(client: OpenAI, model: str, test: dict) -> tuple[str, float, float]:
    """Ask one model one question. Returns (raw answer, seconds, cost in USD)."""
    start = time.time()
    raw = client.chat.completions.with_raw_response.create(
        model=model,
        reasoning_effort="low",                   # less thinking: faster and cheaper
        response_format={"type": "json_object"},  # force valid JSON
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(test["question"], test["passages"])},
        ],
    )
    seconds = time.time() - start
    cost = float(raw.headers.get("x-litellm-response-cost") or 0)  # cost header of the gateway
    return raw.parse().choices[0].message.content, seconds, cost


def main() -> None:
    """Run every model on every test, print each result and a summary table."""
    # The key comes from setup/.env, never write it into the code
    client = OpenAI(base_url=GATEWAY_URL, api_key=os.environ["GATEWAY_KEY"])
    summary = []

    for model in MODELS:
        print(f"\n===== {model} =====")
        correct_count, json_count, total_seconds, total_cost, calls = 0, 0, 0.0, 0.0, 0
        for test in TESTS:
            for run in range(1, RUNS + 1):
                calls += 1
                try:
                    raw_answer, seconds, cost = ask_model(client, model, test)
                except Exception as error:  # one failed call should not stop the whole test
                    print(f"{test['id']} run {run}: ERROR {error}")
                    continue
                json_ok, correct, note = check_answer(raw_answer, test)
                correct_count += correct
                json_count += json_ok
                total_seconds += seconds
                total_cost += cost
                mark = "OK  " if correct else "FAIL"
                print(f"{mark} {test['id']} ({test['kind']}) run {run}  {seconds:.1f} s  {note}")
                if not correct:
                    print(f"     answer: {raw_answer[:300]}")
        summary.append((model, correct_count, json_count, calls, total_seconds / calls, total_cost))

    print("\n===== Summary =====")
    print(f"{'Model':<20} {'Correct':>9} {'JSON ok':>9} {'Avg time':>9} {'Cost USD':>10}")
    for model, correct_count, json_count, calls, avg_seconds, cost in summary:
        print(f"{model:<20} {correct_count:>4}/{calls:<4} {json_count:>4}/{calls:<4} {avg_seconds:>7.1f} s {cost:>10.5f}")


# Only run the test when the file is started directly, not when it is imported
if __name__ == "__main__":
    main()