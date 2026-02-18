"""
Batch test all CAG apps (3-10, 13-14)
Starts each backend, sends a test query, saves results, then stops backend.
"""
import subprocess
import requests
import json
import time
import os
import signal

TESTS = [
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
]

results_dir = os.path.join(os.path.dirname(__file__), "test_results")
os.makedirs(results_dir, exist_ok=True)

for test in TESTS:
    app_name = test["app"]
    port = test["port"]
    backend_dir = os.path.join(os.path.dirname(__file__), app_name, "backend")
    
    print(f"\n{'='*60}")
    print(f"Testing {app_name} on port {port}...")
    print(f"{'='*60}")
    
    # Start backend
    proc = subprocess.Popen(
        ["py", "main.py"],
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    
    # Wait for startup
    time.sleep(5)
    
    try:
        # Health check
        r = requests.get(f"http://localhost:{port}/")
        info = r.json()
        print(f"  Status: {info.get('status', 'unknown')}")
        print(f"  Technique: {info.get('technique', 'unknown')}")
        
        # Test query
        r = requests.post(
            f"http://localhost:{port}{test['endpoint']}",
            json={"query": test["query"]},
            timeout=120
        )
        data = r.json()
        
        # Save result
        result_file = os.path.join(results_dir, f"{app_name}.json")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Summary
        ctx = data.get("context", [])
        steps = data.get("process_steps", [])
        gen_time = next((s["duration"] for s in steps if "generat" in s.get("step","").lower()), 0)
        
        print(f"  Response length: {len(data.get('response', ''))}")
        print(f"  Context chunks: {len(ctx)}")
        print(f"  Sources: {[c.get('source','?') for c in ctx]}")
        print(f"  Avg relevance: {sum(c.get('relevance',0) for c in ctx)/max(len(ctx),1):.2f}")
        print(f"  Generation time: {gen_time:.0f}ms")
        print(f"  ✅ PASSED")
        
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
    
    finally:
        # Stop backend
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
    
    time.sleep(2)

print(f"\n{'='*60}")
print("All tests complete!")
print(f"{'='*60}")
