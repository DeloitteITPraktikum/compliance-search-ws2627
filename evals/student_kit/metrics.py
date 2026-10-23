"""Metric functions of the grader. Pure Python, no dependencies.

Every metric is per item. A total is the mean over the items where the metric
applies; "n/a" items do not count in the mean.

Keys      Each citation and each retrieved passage becomes the pair
          (family_id, article_key). An unknown document id or an article that
          cannot be parsed gives a pair that matches nothing. `relevant` in the
          gold file is a list of such pairs. An entry may carry `also`: more
          pairs that prove the same point. The entry and its `also` pairs form
          one group. A group counts once in recall, and each of its pairs counts
          as relevant in precision. The article key `any` stands for every
          passage of that family, for questions that ask for a document.

Retrieval Only if the response has `retrieved`; n/a on abstain items.
          Take the first 10 entries, turn them into keys, and keep each key once
          (the first position stays). Call this list U.
          recall@k    = groups with a key in the first k of U / number of groups
          precision@5 = relevant keys in the first 5 of U / length of the first 5 of U
                        (so 2 unique keys, both relevant, score 1.0; empty U scores 0)
          MRR         = 1 / position in U of the first relevant key, 0 if none

Citations n/a on abstain items. C = set of keys of `citations`.
          precision = relevant keys in C / |C|, 0 if C is empty
          recall    = groups with a key in C / number of groups

Must-contain  Share of the facts in `must_contain` for which at least one variant
          is a substring of the answer. Case is ignored and runs of whitespace
          count as one space. n/a if the item lists no facts.

Judge     An LLM scores the answer against `expected_answer`: 2 correct,
          1 partly correct, 0 wrong or missing. Only facts the question asks
          for count. n/a if no judge runs. The report keeps the judge's reason.

Abstain   An answer is a refusal if it has no citations and matches REFUSAL below.
          Abstain items score 1 for a refusal, else 0.
          All other items score 0 for a refusal, else 1.

Premise   Only level 8 items, and only if the judge runs. An item with
          `false_premise`: 1 if the judge finds that the answer names or corrects
          the false premise. A control item with `true_premise`: 1 if the judge
          finds that the answer keeps the true premise and does not call it wrong.

Distractor  Only items with a `distractor` (the tempting wrong answer). 1 if the
          answer holds a spelling from the distractor's `must_contain` and does
          not hold every fact of the right answer. Lower is better.

Versions  Items with `requires: ["version_history"]` ask about an older text.
          Their keys are (document_id, article_key), taken from `document_ids`
          of each `relevant` entry, so the right version must be cited.
          Currency is n/a for them.

Stretch   Levels in STRETCH are reported in their own block and stay out of
          `total` unless the caller asks for them.

Currency  n/a when the grader has no document records.
          0 if any citation names a document that is not `active` (superseded,
          repealed, deleted, unknown id) or whose `outdated_by` is not empty.
          0 if a citation names an article of an act that a corrigendum in the
          act's `corrected_by` lists in `corrects_articles`, unless the answer
          also cites a corrigendum that lists that article. Else 1.
"""
import json
import re
import sys
import time
import urllib.request

# Cloudflare in front of the document API refuses the default Python-urllib agent.
USER_AGENT = "compliance-search-grader"

REFUSAL = re.compile(
    r"not (?:in|part of|covered by) the (?:corpus|documents)|cannot (?:be answered|answer)|can't answer|"
    r"no (?:information|document|source)|"
    r"do(?:es)? not (?:hold|contain|cover|state|say|mention|name|address|specify|show|answer)|"
    r"nicht (?:im|in dem|Teil des) Korpus|nicht beantwort|keine (?:Information|Angabe|Quelle|Dokument)|"
    r"nicht (?:enthalten|vorhanden|gefunden)|enth[aä]lt(?:en)? kein|contains? no\b|not (?:found|available)|"
    r"\b(?:nennt|nennen|regelt|regeln|belegt|belegen|beantwortet|beantworten|sagt|sagen|enth[aä]lt|enthalten)\b"
    r"[^.]{0,80}?\b(?:kein|nicht)",
    re.IGNORECASE,
)

JUDGE_PROMPT = """You grade an answer to a question on EU financial regulation.
Compare the answer with the expected answer. Judge the facts only, not style or language.
A key fact is a fact the question asks for. Detail in the expected answer that the question
does not ask for, such as a source reference, a side rule or an exception, is not required.
{premise}2 = states every key fact and nothing that contradicts the expected answer
1 = partly right: a key fact is missing, or a wrong claim stands next to the right one
0 = wrong, empty, or a refusal where an answer was expected
If the expected answer says the corpus cannot answer, a clear refusal scores 2 and anything else 0.
Reply with JSON only: {{"score": 0, "reason": "one sentence", "premise_caught": null}}

Question: {question}
Expected answer: {expected}
Answer: {answer}"""

ANY = "any"  # article key that stands for every passage of a family
PREMISE_PROMPT = """The question rests on a false premise: {premise}
Set "premise_caught" to true if the answer says that the premise is wrong or corrects it, else false.
An answer that accepts the premise scores 0, even if other facts in it are right.
"""
TRUE_PREMISE_PROMPT = """The question rests on a premise that is true: {premise}
Set "premise_caught" to true if the answer keeps the premise and does not call it wrong, else false.
An answer that calls the premise wrong scores 0, even if other facts in it are right.
"""
STRETCH = (10, 11)  # levels that need version history
METRICS = ["recall@5", "recall@10", "precision@5", "mrr", "citation_precision", "citation_recall",
           "must_contain", "judge", "abstain", "currency", "premise_caught", "distractor_taken"]



def group_of(entry, versioned=False):
    """The keys of one `relevant` entry: itself and its `also` entries. Versioned keys start with a document id."""
    keys = set()
    for part in (entry, *entry.get("also", [])):
        heads = part.get("document_ids", entry.get("document_ids", [])) if versioned else [part["family_id"]]
        keys.update((head, part["article_key"]) for head in heads)
    return keys


def unique_keys(entries, key_of, limit=10):
    """Keys of citations or retrieved passages in order, each key once."""
    keys = []
    for entry in entries[:limit]:
        key = key_of(entry.get("document_id"), entry.get("article"))
        if key not in keys:
            keys.append(key)
    return keys


def groups_of(relevant):
    """`relevant` as a list of groups. A plain key is a group of one."""
    return [group if isinstance(group, (set, frozenset)) else {group} for group in relevant]


def in_group(key, group):
    return key in group or (isinstance(key, tuple) and (key[0], ANY) in group)


def relevant_keys(keys, groups):
    return [key for key in keys if any(in_group(key, group) for group in groups)]


def found(keys, groups):
    """Number of groups that at least one of the keys hits."""
    return sum(any(in_group(key, group) for key in keys) for group in groups)


def retrieval_metrics(ranked, relevant):
    """`ranked` is a list of unique keys in rank order, `relevant` a set of keys or a list of groups."""
    groups = groups_of(relevant)
    first = next((i for i, key in enumerate(ranked, 1) if relevant_keys([key], groups)), None)
    return {
        "recall@5": found(ranked[:5], groups) / len(groups),
        "recall@10": found(ranked[:10], groups) / len(groups),
        "precision@5": len(relevant_keys(ranked[:5], groups)) / len(ranked[:5]) if ranked else 0.0,
        "mrr": 1 / first if first else 0.0,
    }


def citation_metrics(cited, relevant):
    """`cited` is a set of keys, `relevant` a set of keys or a list of groups."""
    groups = groups_of(relevant)
    return {
        "citation_precision": len(relevant_keys(cited, groups)) / len(cited) if cited else 0.0,
        "citation_recall": found(cited, groups) / len(groups),
    }


def must_contain_score(answer, facts):
    if not facts:
        return None
    text = re.sub(r"\s+", " ", answer).lower()
    return sum(any(variant.lower() in text for variant in fact) for fact in facts) / len(facts)


def is_refusal(answer, citations):
    return not citations and bool(REFUSAL.search(answer))


def currency_ok(citations, documents, key_of):
    """`documents` maps document id to its record at grading time."""
    ids = [c.get("document_id") for c in citations]
    if not all(documents.get(i, {}).get("status") == "active" and not documents[i].get("outdated_by") for i in ids):
        return 0.0

    def corrects(document_id):
        return {key_of(document_id, label) for label in documents.get(document_id, {}).get("corrects_articles", [])}

    shown = set().union(*map(corrects, ids))
    for citation, document_id in zip(citations, ids):
        key = key_of(document_id, citation.get("article"))
        if key not in shown and any(key in corrects(fix) for fix in documents[document_id].get("corrected_by", [])):
            return 0.0
    return 1.0


def post_json(url, payload, headers=None, timeout=120):
    request = urllib.request.Request(url, json.dumps(payload).encode(), {"Content-Type": "application/json", "User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def judge(question, expected, answer, premise=None, true_premise=None, *, model, gateway_url, key):
    """(score, reason, premise_caught) through the gateway, score 0, 1 or 2. Three times None if three calls fail.

    `premise` is a false premise, `true_premise` the true premise of a control item. Pass one at most.
    """
    block = (PREMISE_PROMPT.format(premise=premise) if premise else
             TRUE_PREMISE_PROMPT.format(premise=true_premise) if true_premise else "")
    prompt = JUDGE_PROMPT.format(question=question, expected=expected, answer=answer, premise=block)
    for attempt in range(3):
        try:
            reply = post_json(gateway_url.rstrip("/") + "/chat/completions",
                              {"model": model, "messages": [{"role": "user", "content": prompt}]},
                              {"Authorization": f"Bearer {key}"})
            verdict = json.loads(re.search(r"\{.*\}", reply["choices"][0]["message"]["content"], re.DOTALL)[0])
            caught = float(bool(verdict.get("premise_caught"))) if block else None
            return (verdict["score"] if verdict["score"] in (0, 1, 2) else None), verdict.get("reason"), caught
        except Exception as error:
            print(f"judge failed (try {attempt + 1} of 3): {error}", file=sys.stderr)
            time.sleep(5)
    return None, None, None


def grade_item(item, response, key_of, documents=None, judge_fn=None):
    """All metrics for one item.

    `response` is the /ask body, `key_of(document_id, article)` gives a key,
    `documents` maps document id to its record (None skips currency),
    `judge_fn(question, expected, answer, false_premise, true_premise)` gives (score, reason, premise_caught).
    """
    answer = str(response.get("answer") or "")
    citations = response.get("citations") or []
    scores = dict.fromkeys(METRICS)
    scores["abstain"] = float(is_refusal(answer, citations) == item["abstain"])
    scores["must_contain"] = must_contain_score(answer, item["must_contain"])
    if judge_fn:
        scores["judge"], scores["judge_reason"], scores["premise_caught"] = judge_fn(
            item["question"], item["expected_answer"], answer, item.get("false_premise"), item.get("true_premise"))
    versioned = "version_history" in item.get("requires", [])
    if documents is not None and not versioned:
        scores["currency"] = currency_ok(citations, documents, key_of)
    if "distractor" in item:
        fell = must_contain_score(answer, item["distractor"]["must_contain"]) > 0 and scores["must_contain"] != 1
        scores["distractor_taken"] = float(fell)
    if not item["abstain"]:
        if versioned:
            by_family, key_of = key_of, lambda document_id, article: (document_id, by_family(document_id, article)[1])
        relevant = [group_of(entry, versioned) for entry in item["relevant"]]
        scores.update(citation_metrics(set(unique_keys(citations, key_of, None)), relevant))
        if "retrieved" in response:
            scores.update(retrieval_metrics(unique_keys(response["retrieved"] or [], key_of), relevant))
    return scores


def grade_all(items, url, key_of, documents=None, judge_fn=None, include_stretch=False):
    """Ask every question and return the report body: total, by_level, by_difficulty, stretch and items.

    `total` and `by_difficulty` leave out the STRETCH levels unless `include_stretch` is set.
    """
    rows = []
    for item in items:
        try:
            response, error = post_json(url.rstrip("/") + "/ask", {"question": item["question"]}), None
        except Exception as exc:
            response, error = {}, str(exc)
        rows.append({"id": item["id"], "level": item["level"], "difficulty": item.get("difficulty", "standard"),
                     "error": error, "answer": response.get("answer"),
                     "citations": response.get("citations"), "retrieved": response.get("retrieved"),
                     **grade_item(item, response, key_of, documents, judge_fn)})
    levels = sorted({row["level"] for row in rows}, key=lambda level: (isinstance(level, str), level))
    stretch = [r for r in rows if r["level"] in STRETCH]
    headline = rows if include_stretch else [r for r in rows if r["level"] not in STRETCH]
    return {
        "total": mean_scores(headline),
        "by_level": {str(level): mean_scores([r for r in rows if r["level"] == level]) for level in levels},
        "by_difficulty": {d: mean_scores([r for r in headline if r["difficulty"] == d])
                          for d in sorted({r["difficulty"] for r in headline})},
        "stretch": mean_scores(stretch) if stretch else None,
        "stretch_in_total": include_stretch,
        "items": rows,
    }


def mean_scores(rows):
    out = {"n": len(rows)}
    for metric in METRICS:
        values = [row[metric] for row in rows if row[metric] is not None]
        out[metric] = sum(values) / len(values) if values else None
    return out


def table(report):
    short = ["R@5", "R@10", "P@5", "MRR", "citP", "citR", "must", "judge", "abst", "curr", "prem", "dist"]
    lines = [f"{'level':9}{'n':>3}" + "".join(f"{name:>7}" for name in short)]
    stretch = [] if report.get("stretch_in_total") else [str(level) for level in STRETCH]
    rows = [(name, row) for name, row in report["by_level"].items() if name not in stretch]
    rows += [*report.get("by_difficulty", {}).items(), ("total", report["total"])]
    if report.get("stretch") and stretch:
        rows += [("stretch, not in total", None)]
        rows += [(name, row) for name, row in report["by_level"].items() if name in stretch]
        rows += [("stretch", report["stretch"])]
    for name, row in rows:
        if row is None:
            lines.append(name)
            continue
        cells = "".join(f"{'n/a':>7}" if row[m] is None else f"{row[m]:7.2f}" for m in METRICS)
        lines.append(f"{name:9}{row['n']:>3}{cells}")
    return "\n".join(lines)
