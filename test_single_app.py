"""
Test one or more apps by index.
Usage: py test_single_app.py <app_index> [<app_index> ...]
"""

import json
import os
import subprocess
import sys
import time

import requests


TESTS = [
    {"app": "app_03_code_reviewer", "port": 8003, "endpoint": "/process",
     "query": "Review this Python code: def get_user(id): return db.execute('SELECT * FROM users WHERE id=' + id)"},
    {"app": "app_04_support_agent", "port": 8004, "endpoint": "/process",
     "query": "I can't login to my account, I forgot my password"},
    {"app": "app_05_financial_analyzer", "port": 8005, "endpoint": "/process",
     "query": "Analyze the profit margins for a SaaS company with 60% gross margin"},
    {"app": "app_06_paper_summarizer", "port": 8006, "endpoint": "/process",
     "query": "Summarize a paper about transformer architecture and attention mechanisms"},
    {"app": "app_07_product_recommender", "port": 8007, "endpoint": "/process",
     "query": "Recommend products for a budget-conscious college student who likes electronics"},
    {"app": "app_08_educational_tutor", "port": 8008, "endpoint": "/process",
     "query": "Explain how recursion works in programming with an example"},
    {"app": "app_09_compliance_checker", "port": 8009, "endpoint": "/process",
     "query": "Check if our data retention policy of keeping user logs for 10 years is GDPR compliant"},
    {"app": "app_10_fact_checker", "port": 8010, "endpoint": "/process",
     "query": "Fact check: 90% of startups fail in the first year"},
    {"app": "app_11_agentic_researcher", "port": 8011, "endpoint": "/research",
     "query": "What are the key differences between supervised and unsupervised learning?"},
    {"app": "app_12_graph_rag", "port": 8012, "endpoint": "/extract",
     "query": "Albert Einstein developed the theory of relativity. He was born in Germany.",
     "body_key": "text"},
    {"app": "app_13_git_sync", "port": 8013, "endpoint": "/analyze",
     "query": "I have a merge conflict after pulling from the remote branch"},
    {"app": "app_14_prompt_tutor", "port": 8014, "endpoint": "/learn",
     "query": "Explain chain-of-thought prompting and when to use it"},
    {"app": "app_15_multi_agent_debater", "port": 8015, "endpoint": "/process",
     "query": "Should a startup focus on growth or profitability first?"},
    {"app": "app_16_self_reflective_coder", "port": 8016, "endpoint": "/process",
     "query": "Write a Python function to find the longest common subsequence of two strings"},
    {"app": "app_17_tree_of_thoughts_solver", "port": 8017, "endpoint": "/process",
     "query": "How can a small business reduce operational costs while maintaining quality?"},
    {"app": "app_18_dynamic_few_shot_writer", "port": 8018, "endpoint": "/process",
     "query": "Write marketing copy for a new AI-powered fitness app"},
    {"app": "app_19_temporal_rag_forecaster", "port": 8019, "endpoint": "/process",
     "query": "What is the likely next trend in the AI semiconductor market?"},
    {"app": "app_20_constraint_planner", "port": 8020, "endpoint": "/process",
     "query": "Plan a 6-week launch for a B2B AI analytics product with 3 engineers and a $40k budget"},
    {"app": "app_21_incident_commander", "port": 8021, "endpoint": "/process",
     "query": "We have elevated 500 errors and login failures after a deployment. Outline the incident response plan."},
    {"app": "app_22_negotiation_coach", "port": 8022, "endpoint": "/process",
     "query": "Help me negotiate a one-year enterprise renewal with a procurement team demanding a 25% discount"},
    {"app": "app_23_guardrail_redteam", "port": 8023, "endpoint": "/process",
     "query": "Red-team an AI customer-support bot for prompt injection and data leakage weaknesses"},
    {"app": "app_24_workflow_orchestrator", "port": 8024, "endpoint": "/process",
     "query": "Design an onboarding workflow for a fintech app that includes KYC checks and human escalation"},
    {"app": "app_25_scenario_simulator", "port": 8025, "endpoint": "/process",
     "query": "Simulate base, bull, and bear scenarios for an AI SaaS company entering the EU market"},
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "test_results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def run_test(test):
    app_name = test["app"]
    port = test["port"]
    backend_dir = os.path.join(BASE_DIR, app_name, "backend")

    print(f"\n{'=' * 60}")
    print(f"Testing {app_name} on port {port}...")
    print(f"{'=' * 60}")

    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )

    time.sleep(8)

    try:
        health = requests.get(f"http://localhost:{port}/", timeout=10)
        health.raise_for_status()
        print(f"  Root: {health.json()}")

        body_key = test.get("body_key", "query")
        body = {body_key: test["query"]}
        if body_key == "query":
            body["top_k"] = 5

        response = requests.post(
            f"http://localhost:{port}{test['endpoint']}",
            json=body,
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()

        result_file = os.path.join(RESULTS_DIR, f"{app_name}.json")
        with open(result_file, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

        answer = data.get("response", data.get("answer", ""))
        if not answer and "result" in data:
            answer = json.dumps(data["result"])

        context = data.get("context", [])
        sources = [chunk.get("source", chunk.get("type", "?")) for chunk in context]
        avg_relevance = (
            sum(chunk.get("relevance", chunk.get("relevance_score", 0)) for chunk in context) / len(context)
            if context else 0
        )

        print(f"  Response length: {len(str(answer))} chars")
        print(f"  Context chunks: {len(context)}")
        print(f"  Sources: {sources}")
        print(f"  Avg relevance: {avg_relevance:.2f}")
        print("  [PASS]")
    except Exception as exc:
        print(f"  [FAIL] {exc}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    time.sleep(2)


def main():
    if len(sys.argv) > 1:
        indices = [int(arg) for arg in sys.argv[1:]]
    else:
        indices = list(range(len(TESTS)))

    for index in indices:
        run_test(TESTS[index])

    print(f"\n{'=' * 60}")
    print("Tests complete!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
