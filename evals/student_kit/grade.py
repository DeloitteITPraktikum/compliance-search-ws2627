"""Grade your `POST /ask` endpoint against the sample questions.

    export DOCS_URL=https://DOCS_HOST  GATEWAY_URL=https://GATEWAY_HOST/v1  KEY=sk-...
    python grade.py --url http://localhost:8000 [--gold sample.jsonl]
                    [--judge-model gpt-6-1-sol] [--out report.json]

The grader checks your answers against the corpus as it is now. It reads
`id`, `family_id` and `status` of every document from the document API
(DOCS_URL), with your own key (KEY). A citation of a document that is not
`active` at this moment fails the currency check.

The judge runs through the model gateway (GATEWAY_URL) with the same key. Leave
GATEWAY_URL unset to skip it. Staff grade with a stronger judge model, so your
judge score may differ slightly from theirs. All other metrics are the same code.

`metrics.py` holds the exact definition of every metric.
"""
import argparse
import json
import os
from functools import partial
from pathlib import Path

from keys import fetch_documents, key_of
from metrics import grade_all, judge, table


def run(url, gold_path, judge_model=None):
    items = [json.loads(line) for line in Path(gold_path).read_text(encoding="utf-8").splitlines() if line.strip()]
    documents = fetch_documents()
    families = {doc["id"]: doc["family_id"] for doc in documents}
    statuses = {doc["id"]: doc["status"] for doc in documents}
    corrigenda = {doc["id"] for doc in documents if doc.get("doc_type") == "corrigendum"}
    gateway = os.environ.get("GATEWAY_URL")
    judge_fn = partial(judge, model=judge_model, gateway_url=gateway, key=os.environ["KEY"]) if judge_model and gateway else None
    return {"url": url, "gold": str(gold_path),
            "judge": judge_model if judge_fn else "skipped: GATEWAY_URL is not set",
            **grade_all(items, url, partial(key_of, families=families, corrigenda=corrigenda), statuses, judge_fn)}


def main():
    parser = argparse.ArgumentParser(description="Grade a POST /ask endpoint against the sample questions.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--gold", default=str(Path(__file__).resolve().parent / "sample.jsonl"))
    parser.add_argument("--judge-model", default="gpt-6-1-sol")
    parser.add_argument("--out", default="report.json")
    args = parser.parse_args()
    report = run(args.url, args.gold, args.judge_model)
    print(table(report))
    print(f"judge: {report['judge']} (scale 0 to 2)")
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"report: {args.out}")


if __name__ == "__main__":
    main()
