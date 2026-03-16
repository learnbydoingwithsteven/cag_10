# App 24: Workflow Orchestration Designer

**CAG Technique: State Machine CAG**

## What This App Teaches
How CAG can preload state-machine, automation-boundary, and failure-recovery patterns so workflow design stays operational instead of vague.

## Core Workflow
- Retrieve orchestration patterns for state design, compliance checks, retries, and SLAs.
- Augment the prompt with workflow architecture guidance.
- Generate a production-style workflow with owners, triggers, and escalation rules.

## Quick Start
```bash
cd backend && py main.py
cd frontend && npm start
```

## Application Screenshot

![Screenshot](./screenshot.png)
## Test Results ✅

**Query**: _Design an onboarding workflow for a fintech app that includes KYC checks and human escalation_

| Metric | Value |
|---|---|
| Status | PASSED |
| Response Length | 4825 chars |
| Context Chunks | 5 |
| Sources Retrieved | `automation_boundaries, compliance_checkpoints, state_design, failure_recovery, metrics` |
| Avg Relevance | 0.42 |
| Model | qwen2.5:1.5b |
