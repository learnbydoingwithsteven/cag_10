"""
Comprehensive test for all CAG apps (3-25).
Starts each backend, sends a test query, saves results to JSON, and updates summaries.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime

import requests


TESTS = [
    {"app": "app_03_code_reviewer", "port": 8003, "endpoint": "/process",
     "query": "Review this Python code: def get_user(id): return db.execute(\"SELECT * FROM users WHERE id=\" + id)",
     "technique": "AST-aware Code Quality CAG"},
    {"app": "app_04_support_agent", "port": 8004, "endpoint": "/process",
     "query": "I can't login to my account, I forgot my password",
     "technique": "Conversational Memory CAG"},
    {"app": "app_05_financial_analyzer", "port": 8005, "endpoint": "/process",
     "query": "Analyze the profit margins for a SaaS company with 60% gross margin",
     "technique": "Structured Data CAG"},
    {"app": "app_06_paper_summarizer", "port": 8006, "endpoint": "/process",
     "query": "Summarize a paper about transformer architecture and attention mechanisms",
     "technique": "Hierarchical Summarization CAG"},
    {"app": "app_07_product_recommender", "port": 8007, "endpoint": "/process",
     "query": "Recommend products for a budget-conscious college student who likes electronics",
     "technique": "Hybrid Collaborative-Content CAG"},
    {"app": "app_08_educational_tutor", "port": 8008, "endpoint": "/process",
     "query": "Explain how recursion works in programming with an example",
     "technique": "Adaptive Difficulty CAG"},
    {"app": "app_09_compliance_checker", "port": 8009, "endpoint": "/process",
     "query": "Check if our data retention policy of keeping user logs for 10 years is GDPR compliant",
     "technique": "Rule-based Compliance CAG"},
    {"app": "app_10_fact_checker", "port": 8010, "endpoint": "/process",
     "query": "Fact check: 90% of startups fail in the first year",
     "technique": "Multi-source Verification CAG"},
    {"app": "app_11_agentic_researcher", "port": 8011, "endpoint": "/research",
     "query": "What are the key differences between supervised and unsupervised learning?",
     "technique": "Agentic Research CAG"},
    {"app": "app_12_graph_rag", "port": 8012, "endpoint": "/extract",
     "query": "Albert Einstein developed the theory of relativity. He was born in Germany and later moved to the United States.",
     "technique": "Graph-based Knowledge Extraction CAG",
     "body_key": "text"},
    {"app": "app_13_git_sync", "port": 8013, "endpoint": "/analyze",
     "query": "I have a merge conflict after pulling from the remote branch, how do I resolve it?",
     "technique": "Expert System CAG"},
    {"app": "app_14_prompt_tutor", "port": 8014, "endpoint": "/learn",
     "query": "Explain chain-of-thought prompting and when to use it",
     "technique": "Pedagogical Scaffolding CAG"},
    {"app": "app_15_multi_agent_debater", "port": 8015, "endpoint": "/process",
     "query": "Should a startup focus on growth or profitability first?",
     "technique": "Multi-Agent Debate CAG"},
    {"app": "app_16_self_reflective_coder", "port": 8016, "endpoint": "/process",
     "query": "Write a Python function to find the longest common subsequence of two strings",
     "technique": "Reflexion-based CAG"},
    {"app": "app_17_tree_of_thoughts_solver", "port": 8017, "endpoint": "/process",
     "query": "How can a small business reduce operational costs while maintaining quality?",
     "technique": "Tree of Thoughts (ToT) CAG"},
    {"app": "app_18_dynamic_few_shot_writer", "port": 8018, "endpoint": "/process",
     "query": "Write marketing copy for a new AI-powered fitness app",
     "technique": "Dynamic Context Selection CAG"},
    {"app": "app_19_temporal_rag_forecaster", "port": 8019, "endpoint": "/process",
     "query": "What is the likely next trend in the AI semiconductor market?",
     "technique": "Temporal RAG CAG"},
    {"app": "app_20_constraint_planner", "port": 8020, "endpoint": "/process",
     "query": "Plan a 6-week launch for a B2B AI analytics product with 3 engineers and a $40k budget",
     "technique": "Constraint-Satisfaction CAG"},
    {"app": "app_21_incident_commander", "port": 8021, "endpoint": "/process",
     "query": "We have elevated 500 errors and login failures after a deployment. Outline the incident response plan.",
     "technique": "Runbook-Guided Incident Response CAG"},
    {"app": "app_22_negotiation_coach", "port": 8022, "endpoint": "/process",
     "query": "Help me negotiate a one-year enterprise renewal with a procurement team demanding a 25% discount",
     "technique": "Strategy Playbook CAG"},
    {"app": "app_23_guardrail_redteam", "port": 8023, "endpoint": "/process",
     "query": "Red-team an AI customer-support bot for prompt injection and data leakage weaknesses",
     "technique": "Adversarial Evaluation CAG"},
    {"app": "app_24_workflow_orchestrator", "port": 8024, "endpoint": "/process",
     "query": "Design an onboarding workflow for a fintech app that includes KYC checks and human escalation",
     "technique": "State Machine CAG"},
    {"app": "app_25_scenario_simulator", "port": 8025, "endpoint": "/process",
     "query": "Simulate base, bull, and bear scenarios for an AI SaaS company entering the EU market",
     "technique": "Scenario Simulation CAG"},
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

    result_entry = {
        "app": app_name,
        "port": port,
        "technique": test["technique"],
        "status": "FAILED",
        "query": test["query"],
    }

    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )

    time.sleep(8)

    try:
        health = requests.get(f"http://localhost:{port}/", timeout=10)
        health.raise_for_status()
        print(f"  Status: {health.json()}")

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

        answer = data.get("response", data.get("answer", data.get("result", {}).get("triples", "")))
        if isinstance(answer, list):
            answer = json.dumps(answer)

        context = data.get("context", [])
        sources = [chunk.get("source", chunk.get("type", "?")) for chunk in context] if context else []
        avg_relevance = (
            sum(chunk.get("relevance", chunk.get("relevance_score", 0)) for chunk in context) / len(context)
            if context else 0
        )

        result_entry.update(
            {
                "status": "PASSED",
                "response_length": len(str(answer)),
                "context_chunks": len(context),
                "sources": sources,
                "avg_relevance": round(avg_relevance, 2),
                "response_preview": str(answer)[:200],
            }
        )

        print(f"  Response length: {len(str(answer))} chars")
        print(f"  Context chunks: {len(context)}")
        print(f"  Avg relevance: {avg_relevance:.2f}")
        print("  [PASS]")
    except Exception as exc:
        result_entry["error"] = str(exc)
        print(f"  [FAIL] {exc}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    time.sleep(3)
    return result_entry


def main():
    results = [run_test(test) for test in TESTS]

    summary_file = os.path.join(RESULTS_DIR, "test_summary.json")
    with open(summary_file, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "test_date": datetime.now().isoformat(),
                "total_apps": len(TESTS),
                "passed": sum(1 for entry in results if entry["status"] == "PASSED"),
                "failed": sum(1 for entry in results if entry["status"] == "FAILED"),
                "results": results,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n{'=' * 60}")
    print("Test Summary")
    print(f"{'=' * 60}")
    passed = sum(1 for entry in results if entry["status"] == "PASSED")
    failed = sum(1 for entry in results if entry["status"] == "FAILED")
    print(f"  Passed: {passed}/{len(TESTS)}")
    print(f"  Failed: {failed}/{len(TESTS)}")
    for entry in results:
        icon = "[PASS]" if entry["status"] == "PASSED" else "[FAIL]"
        print(f"  {icon} {entry['app']}: {entry['status']}")
    print(f"\nResults saved to: {RESULTS_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
