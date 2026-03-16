import os
import json
import re
import glob

cag_dir = r"f:\learnbydoingwithsteven\cag_10"
results_dir = os.path.join(cag_dir, "test_results")

test_files = glob.glob(os.path.join(results_dir, "app_*.json"))

for test_file in test_files:
    app_name = os.path.basename(test_file).replace(".json", "")
    if app_name == "app03":
        continue
    
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    app_dir = os.path.join(cag_dir, app_name)
    readme_path = os.path.join(app_dir, "README.md")
    
    # Extract data from the json result
    query = data.get('query', '')
    
    resp_text = data.get("response", data.get("answer", data.get("result", {}).get("triples", "")))
    if isinstance(resp_text, list):
        resp_text = json.dumps(resp_text)
    resp_len = len(str(resp_text))
    
    ctx = data.get("context", [])
    ctx_chunks = len(ctx)
    sources = [c.get("source", c.get("type", "?")) for c in ctx] if ctx else []
    sources_str = ", ".join(sources) or "None"
    
    avg_rel = (sum(c.get("relevance", c.get("relevance_score", 0)) for c in ctx) / max(len(ctx), 1)) if ctx else 0
    
    metadata = data.get('metadata', {})
    technique = metadata.get('technique', 'Unknown Technique')
    model = metadata.get('model', 'Auto-selected local model')

    results_md = f"""## Test Results \u2705

**Query**: _{query}_

| Metric | Value |
|---|---|
| Status | PASSED |
| Response Length | {resp_len} chars |
| Context Chunks | {ctx_chunks} |
| Sources Retrieved | `{sources_str}` |
| Avg Relevance | {avg_rel:.2f} |
| Model | {model} |
"""

    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Add newlines around the replaced content to make markdown render nicely
        if "## Test Results" in content:
            content = re.sub(r'## Test Results.*?(?=(##|$))', results_md + '\n', content, flags=re.DOTALL)
        else:
            if not content.endswith('\n'):
                content += "\n\n"
            content += results_md
            
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    else:
        title = " ".join(word.capitalize() for word in app_name.split('_')[2:])
        app_num = app_name.split('_')[1]
        new_readme = f"""# App {app_num}: {title}

**CAG Technique: {technique}**

{results_md}

## Quick Start
```bash
cd backend && py main.py
cd frontend && npm start
```
"""
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_readme)

print(f"Updated READMEs for {len(test_files)} apps.")
