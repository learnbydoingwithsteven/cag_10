import os
import subprocess
import time
import requests
import json
import re
import psutil
from playwright.sync_api import sync_playwright

cag_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(cag_dir, "test_results")

# List of queries for screenshots
QUERIES = {
    "app_03_code_reviewer": "Review this Python code: def get_user(id): return db.execute('SELECT * FROM users WHERE id=' + id)",
    "app_04_support_agent": "I can't login to my account, I forgot my password",
    "app_05_financial_analyzer": "Analyze the profit margins for a SaaS company with 60% gross margin",
    "app_06_paper_summarizer": "Summarize a paper about transformer architecture and attention mechanisms",
    "app_07_product_recommender": "Recommend products for a budget-conscious college student who likes electronics",
    "app_08_educational_tutor": "Explain how recursion works in programming with an example",
    "app_09_compliance_checker": "Check if our data retention policy of keeping logs for 10 years is GDPR compliant",
    "app_10_fact_checker": "Fact check: 90% of startups fail in the first year",
    "app_11_agentic_researcher": "What are the key differences between supervised and unsupervised learning?",
    "app_12_graph_rag": "Albert Einstein developed the theory of relativity. He was born in Germany.",
    "app_13_git_sync": "I have a merge conflict after pulling from the remote branch",
    "app_14_prompt_tutor": "Explain chain-of-thought prompting and when to use it",
    "app_15_multi_agent_debater": "Should a startup focus on growth or profitability first?",
    "app_16_self_reflective_coder": "Write a Python function to find the longest common subsequence of two strings",
    "app_17_tree_of_thoughts_solver": "How can a small business reduce operational costs while maintaining quality?",
    "app_18_dynamic_few_shot_writer": "Write marketing copy for a new AI-powered fitness app",
    "app_19_temporal_rag_forecaster": "What is the likely next trend in the AI semiconductor market?",
    "app_20_constraint_planner": "Plan a 6-week launch for a B2B AI analytics product with 3 engineers and a $40k budget",
    "app_21_incident_commander": "We have elevated 500 errors and login failures after a deployment. Outline the incident response plan.",
    "app_22_negotiation_coach": "Help me negotiate a one-year enterprise renewal with a procurement team demanding a 25% discount",
    "app_23_guardrail_redteam": "Red-team an AI customer-support bot for prompt injection and data leakage weaknesses",
    "app_24_workflow_orchestrator": "Design an onboarding workflow for a fintech app that includes KYC checks and human escalation",
    "app_25_scenario_simulator": "Simulate base, bull, and bear scenarios for an AI SaaS company entering the EU market",
}

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except Exception:
        pass

def run_app_screenshot(app_name, port_suffix):
    app_dir = os.path.join(cag_dir, app_name)
    back_dir = os.path.join(app_dir, "backend")
    front_dir = os.path.join(app_dir, "frontend")
    
    if not os.path.exists(front_dir):
        print(f"Skipping {app_name}, no frontend.")
        return

    # Check node modules
    if not os.path.exists(os.path.join(front_dir, "node_modules", "react-scripts")) and not os.path.exists(os.path.join(front_dir, "node_modules", "vite")):
        print(f"[{app_name}] Running npm install...")
        subprocess.run(["npm", "install"], cwd=front_dir, shell=True)

    # Check package.json for start command
    front_port = 4000 + port_suffix
    back_port = 8000 + port_suffix
    
    with open(os.path.join(front_dir, "package.json"), "r") as f:
        pkg = json.load(f)
    scripts = pkg.get("scripts", {})

    env_path = os.path.join(front_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as env_file:
            for line in env_file:
                if line.startswith("PORT="):
                    try:
                        front_port = int(line.split("=", 1)[1].strip())
                    except ValueError:
                        pass

    start_script = scripts.get("start", "")
    port_match = re.search(r"PORT=(\d+)", start_script)
    if port_match:
        front_port = int(port_match.group(1))
    
    is_vite = "vite" in pkg.get("dependencies", {}) or "vite" in pkg.get("devDependencies", {}) or "dev" in scripts
    
    print(f"[{app_name}] Starting backend on :8000+{port_suffix}...")
    back_proc = subprocess.Popen(["py", "main.py"], cwd=back_dir, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    
    env = {**os.environ, "PORT": str(front_port), "BROWSER": "none", "CI": "true"}
    print(f"[{app_name}] Starting frontend on :{front_port} (Vite: {is_vite})...")
    
    if is_vite:
        front_cmd = f"npm run dev -- --port {front_port} --strictPort"
    else:
        front_cmd = "npm start"

    front_proc = subprocess.Popen(front_cmd, cwd=front_dir, env=env, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    
    time.sleep(20)  # give servers time to bootup
    
    screenshot_path = os.path.join(app_dir, f"screenshot.png")
    
    query_text = QUERIES.get(app_name, "Hello")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            
            
            # Navigate with retry logic
            max_retries = 15
            for attempt in range(max_retries):
                try:
                    page.goto(f"http://localhost:{front_port}", wait_until="domcontentloaded", timeout=30000)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(3)
            
            page.wait_for_timeout(5000)
            
            # Input logic
            textarea = page.locator("textarea, input[type='text']").first
            if textarea.count() > 0:
                textarea.fill(query_text)
                
                # Button click
                submit_btn = page.locator("button:has-text('Submit'), button:has-text('Search'), button:has-text('Analyze'), button:has-text('Process'), button:has-text('Start'), button:has-text('Debate'), button:has-text('Plan'), button:has-text('Run'), button:has-text('Simulate'), button:has-text('Extract'), button:has-text('Generate'), button:has-text('Build'), button[type='submit']").first
                if submit_btn.count() == 0:
                    submit_btn = page.locator("button:not([disabled])").first
                if submit_btn.count() > 0:
                    submit_btn.click()
                else:
                    page.keyboard.press("Enter")
                    
                # Wait for response
                try:
                    page.wait_for_timeout(20000)
                except Exception:
                    pass
                    
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[{app_name}] Screenshot saved to {screenshot_path}")
            
            # Embed in README
            readme_path = os.path.join(app_dir, "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as rf:
                    content = rf.read()
                if "![Screenshot]" not in content:
                    with open(readme_path, "a", encoding="utf-8") as wf:
                        wf.write("\n\n## Application Screenshot\n\n![Screenshot](./screenshot.png)\n")
                        
            browser.close()
    except Exception as e:
        print(f"[{app_name}] Error taking screenshot: {e}")
    finally:
        print(f"[{app_name}] Cleaning up processes...")
        kill_process_tree(back_proc.pid)
        kill_process_tree(front_proc.pid)
        time.sleep(2)

def main():
    apps = [d for d in os.listdir(cag_dir) if d.startswith("app_") and d not in ["app_01_legal_analyzer", "app_02_medical_assistant"]]
    apps.sort()
    
    for i, app in enumerate(apps):
        app_dir = os.path.join(cag_dir, app)
        if os.path.exists(os.path.join(app_dir, "screenshot.png")):
            print(f"[{app}] Already has screenshot, skipping.")
            continue
            
        port_suffix = int(app.split("_")[1])
        run_app_screenshot(app, port_suffix)

if __name__ == "__main__":
    main()
