# CAG Apps Suite

25 compact applications that showcase Context-Augmented Generation (CAG) as a fast, local-first alternative to heavyweight retrieval stacks.

## What CAG Means Here

Each app follows the same loop:

1. Retrieve from a small in-memory knowledge base or expert playbook.
2. Augment the prompt with the matched context.
3. Generate an answer with a local Ollama model.

The repo is a collection of focused SOTA MVP experiments where the context is explicit, inspectable, and fast to debug.

## App Inventory

### Reference Patterns

| # | App | Pattern |
|---|---|---|
| 01 | Legal Document Analyzer | RAG with ChromaDB |
| 02 | Medical Diagnosis Assistant | Multi-hop graph reasoning |

### Core CAG Apps

| # | App | Technique |
|---|---|---|
| 03 | Code Review Bot | AST-aware Code Quality CAG |
| 04 | Customer Support Agent | Conversational Memory CAG |
| 05 | Financial Report Analyzer | Structured Data CAG |
| 06 | Research Paper Summarizer | Hierarchical Summarization CAG |
| 07 | Product Recommender | Hybrid Collaborative-Content CAG |
| 08 | Educational Tutor | Adaptive Difficulty CAG |
| 09 | Compliance Checker | Rule-based Compliance CAG |
| 10 | Fact Checker | Multi-source Verification CAG |
| 11 | Agentic Research Assistant | Agentic Research CAG |
| 12 | GraphRAG Explorer | Graph-based Knowledge Extraction CAG |
| 13 | Git Sync Assistant | Expert System CAG |
| 14 | Prompt Engineering Tutor | Pedagogical Scaffolding CAG |
| 15 | Multi-Agent Strategy Debater | Multi-Agent Debate CAG |
| 16 | Self-Reflective Code Generator | Reflexion-based CAG |
| 17 | Tree of Thoughts Problem Solver | Tree of Thoughts CAG |
| 18 | Dynamic Few-Shot Copywriter | Dynamic Context Selection CAG |
| 19 | Temporal Market Forecaster | Temporal RAG CAG |
| 20 | Constraint-Aware Launch Planner | Constraint-Satisfaction CAG |
| 21 | Incident Command Copilot | Runbook-Guided Incident Response CAG |
| 22 | Enterprise Negotiation Coach | Strategy Playbook CAG |
| 23 | LLM Guardrail Red-Team Lab | Adversarial Evaluation CAG |
| 24 | Workflow Orchestration Designer | State Machine CAG |
| 25 | Executive Scenario Simulator | Scenario Simulation CAG |

## New Additions In This Pass

- App 20 plans launches around budget, capacity, scope, and quality gates.
- App 21 turns incident runbooks into an operational response copilot.
- App 22 packages enterprise negotiation heuristics into a deal-strategy coach.
- App 23 evaluates LLM systems against prompt injection, leakage, and jailbreak risks.
- App 24 designs workflow state machines with automation boundaries and escalation logic.
- App 25 builds base, bull, and bear strategic scenarios with decision triggers.

## Verification Status

- Backend verification script: `py test_all_apps_comprehensive.py`
- Target coverage in this repo: apps `03` through `25`
- Latest pass in this workspace: `23/23` backend apps passed after the test harness was fixed to use the correct endpoints for apps `13` and `14`

Results are saved under `test_results/`.

## Screenshots

Use the screenshot runner to boot each frontend/backend pair and save `screenshot.png` into each app directory:

```bash
py screenshot_all_apps.py
```

The script skips apps that already have screenshots.

## Quick Start

### Backend

```bash
cd app_20_constraint_planner/backend
py main.py
```

### Frontend

```bash
cd app_20_constraint_planner/frontend
npm install
npm start
```

### Full Verification

```bash
py test_all_apps_comprehensive.py
py update_readmes.py
```

## Repo Notes

- Apps `01` and `02` need extra infrastructure and are kept as reference comparisons.
- Apps `03` through `25` are local-first CAG apps that use Ollama.
- Most frontends are lightweight React + MUI dashboards.
- The test and screenshot scripts are designed for Windows and local Ollama usage.

---
## 📦 Project Structure

```text
cag_10/
├── APPS_VERIFICATION.md
├── COMPLETE_IMPLEMENTATION_GUIDE.md
├── PROJECT_SUMMARY.md
├── QUICKSTART.md
├── README.md
├── TASK_STATUS.md
├── WALKTHROUGH.md
├── app_01_legal_analyzer/
  ├── README.md
  ├── assets/
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_02_medical_assistant/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_03_code_reviewer/
  ├── README.md
  ├── assets/
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_04_support_agent/
  ├── README.md
  ├── assets/
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_05_financial_analyzer/
  ├── README.md
  ├── assets/
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_06_paper_summarizer/
  ├── README.md
  ├── assets/
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_07_product_recommender/
  ├── README.md
  ├── assets/
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_08_educational_tutor/
  ├── README.md
  ├── assets/
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_09_compliance_checker/
  ├── README.md
  ├── assets/
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_10_fact_checker/
  ├── README.md
  ├── assets/
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_11_agentic_researcher/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_12_graph_rag/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_13_git_sync/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_14_prompt_tutor/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_15_multi_agent_debater/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_16_self_reflective_coder/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_17_tree_of_thoughts_solver/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_18_dynamic_few_shot_writer/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_19_temporal_rag_forecaster/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── app_20_constraint_planner/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_21_incident_commander/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_22_negotiation_coach/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_23_guardrail_redteam/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_24_workflow_orchestrator/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── app_25_scenario_simulator/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
  ├── screenshot.png
├── doc_assets/
  ├── project.meta.json
  ├── unified_dashboard_main.png
├── docker-compose.yml
├── fix_elevation.py
├── fix_rows.py
├── generate_apps_15_to_19.py
├── generate_remaining_apps.py
├── project.meta.json
├── projects.index.json
├── run_local.py
├── screenshot_all_apps.py
├── shared/
  ├── cag_engine/
  ├── evaluation/
  ├── project.meta.json
  ├── requirements.txt
├── start_all_apps.sh
├── start_dashboard.bat
├── summarize_results.py
├── test_all_apps.py
├── test_all_apps_comprehensive.py
├── test_results/
  ├── app03.json
  ├── app_03_code_reviewer.json
  ├── app_04_support_agent.json
  ├── app_05_financial_analyzer.json
  ├── app_06_paper_summarizer.json
  ├── app_07_product_recommender.json
  ├── app_08_educational_tutor.json
  ├── app_09_compliance_checker.json
  ├── app_10_fact_checker.json
  ├── app_11_agentic_researcher.json
  ├── app_12_graph_rag.json
  ├── app_13_git_sync.json
  ├── app_14_prompt_tutor.json
  ├── app_15_multi_agent_debater.json
  ├── app_16_self_reflective_coder.json
  ├── app_17_tree_of_thoughts_solver.json
  ├── app_18_dynamic_few_shot_writer.json
  ├── app_19_temporal_rag_forecaster.json
  ├── app_20_constraint_planner.json
  ├── app_21_incident_commander.json
  ├── app_22_negotiation_coach.json
  ├── app_23_guardrail_redteam.json
  ├── app_24_workflow_orchestrator.json
  ├── app_25_scenario_simulator.json
  ├── project.meta.json
  ├── test_summary.json
├── test_screenshot.py
├── test_single_app.py
├── unified_dashboard/
  ├── README.md
  ├── backend/
  ├── frontend/
  ├── project.meta.json
├── update_15_to_19.py
├── update_readmes.py
├── update_ui_15_to_19.py
```

## 🛠️ Technology Stack

- **Python 3**
