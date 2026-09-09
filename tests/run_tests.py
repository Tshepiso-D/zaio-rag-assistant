"""
Part 4: Runs every case in tests/test_cases.json against the live API
(POST /ask) and writes a Markdown + JSON report of Question / Source / Answer.

Usage:
    # in one terminal
    uvicorn main:app --port 8000

    # in another terminal
    python tests/run_tests.py
"""
import json
import os
import sys
import requests

API_URL = os.environ.get("ZAIO_API_URL", "http://localhost:8000/ask")
HERE = os.path.dirname(os.path.abspath(__file__))
CASES_PATH = os.path.join(HERE, "test_cases.json")
MD_OUT_PATH = os.path.join(HERE, "test_results.md")
JSON_OUT_PATH = os.path.join(HERE, "test_results.json")


def run():
    with open(CASES_PATH) as f:
        cases = json.load(f)

    results = []
    for case in cases:
        question = case["question"]
        try:
            resp = requests.post(API_URL, json={"question": question}, timeout=60)
            resp.raise_for_status()
            body = resp.json()
            answer = body.get("answer", "")
            source = body.get("source", "")
            status = "OK"
        except Exception as e:
            answer, source, status = f"ERROR: {e}", "", "FAIL"

        results.append({
            "id": case["id"],
            "question": question,
            "expected_source_type": case.get("expected_source_type"),
            "retrieved_source": source,
            "answer": answer,
            "status": status,
        })
        print(f"[{case['id']}] {question}\n  -> source={source!r}\n  -> answer={answer[:120]}\n")

    with open(JSON_OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    with open(MD_OUT_PATH, "w") as f:
        f.write("# ZAIO Student Assistant - Test Results\n\n")
        f.write("| # | Question | Retrieved Source | Answer |\n")
        f.write("|---|----------|-------------------|--------|\n")
        for r in results:
            q = r["question"].replace("|", "\\|")
            s = (r["retrieved_source"] or "*(none - refused)*").replace("|", "\\|")
            a = r["answer"].replace("|", "\\|").replace("\n", " ")
            f.write(f"| {r['id']} | {q} | {s} | {a} |\n")

    print(f"\nWrote {MD_OUT_PATH} and {JSON_OUT_PATH}")


if __name__ == "__main__":
    run()
