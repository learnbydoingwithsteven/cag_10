# App 23: LLM Guardrail Red-Team Lab

**CAG Technique: Adversarial Evaluation CAG**

## What This App Teaches
How CAG can preload adversarial playbooks so the model evaluates prompt injection, data leakage, jailbreaks, and tool-boundary risks in a structured way.

## Core Workflow
- Retrieve attack heuristics and mitigation patterns that match the system description.
- Augment the prompt with red-team methodology.
- Generate an evaluation report with test prompts, failure modes, and defenses.

## Quick Start
```bash
cd backend && py main.py
cd frontend && npm start
```

## Application Screenshot

![Screenshot](./screenshot.png)
## Test Results ✅

**Query**: _Red-team an AI customer-support bot for prompt injection and data leakage weaknesses_

| Metric | Value |
|---|---|
| Status | PASSED |
| Response Length | 3017 chars |
| Context Chunks | 4 |
| Sources Retrieved | `prompt_injection, data_exfiltration, jailbreak_patterns, tool_boundaries` |
| Avg Relevance | 0.50 |
| Model | qwen2.5:1.5b |
