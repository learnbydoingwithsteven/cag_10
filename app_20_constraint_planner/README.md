# App 20: Constraint-Aware Launch Planner

**CAG Technique: Constraint-Satisfaction CAG**

## What This App Teaches
How CAG can preload launch heuristics, resource constraints, and quality gates so the model plans around reality instead of producing generic roadmaps.

## Core Workflow
- Retrieve planning rules for budget, capacity, timeline, GTM readiness, and quality control.
- Augment the prompt with the strongest matching launch constraints.
- Generate a week-by-week plan with scope cuts, risks, and metrics.

## Quick Start
```bash
cd backend && py main.py
cd frontend && npm start
```

## Application Screenshot

![Screenshot](./screenshot.png)
## Test Results ✅

**Query**: _Plan a 6-week launch for a B2B AI analytics product with 3 engineers and a $40k budget_

| Metric | Value |
|---|---|
| Status | PASSED |
| Response Length | 4121 chars |
| Context Chunks | 5 |
| Sources Retrieved | `phased_delivery, constraint_triage, gtm_alignment, risk_buffering, quality_gates` |
| Avg Relevance | 0.60 |
| Model | qwen2.5:1.5b |
