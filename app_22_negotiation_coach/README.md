# App 22: Enterprise Negotiation Coach

**CAG Technique: Strategy Playbook CAG**

## What This App Teaches
How CAG can preload structured negotiation heuristics so the model produces anchors, concession ladders, and close plans instead of generic sales advice.

## Core Workflow
- Retrieve negotiation tactics for BATNA framing, anchoring, concessions, and stakeholder mapping.
- Augment the prompt with enterprise deal strategy context.
- Generate a talk track and close plan tuned to the scenario.

## Quick Start
```bash
cd backend && py main.py
cd frontend && npm start
```

## Application Screenshot

![Screenshot](./screenshot.png)
## Test Results ✅

**Query**: _Help me negotiate a one-year enterprise renewal with a procurement team demanding a 25% discount_

| Metric | Value |
|---|---|
| Status | PASSED |
| Response Length | 4749 chars |
| Context Chunks | 4 |
| Sources Retrieved | `batna, anchoring, stakeholder_mapping, objection_handling` |
| Avg Relevance | 0.62 |
| Model | qwen2.5:1.5b |
