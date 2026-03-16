# App 21: Incident Command Copilot

**CAG Technique: Runbook-Guided Incident Response CAG**

## What This App Teaches
How CAG can preload operational runbooks so the model responds like an incident commander: severity first, containment before analysis, and clear stakeholder communication throughout.

## Core Workflow
- Retrieve incident runbooks aligned with the reported failure.
- Augment the prompt with containment, diagnostics, communication, and recovery guidance.
- Generate an action plan for the first minutes, next hour, and post-incident cleanup.

## Quick Start
```bash
cd backend && py main.py
cd frontend && npm start
```

## Application Screenshot

![Screenshot](./screenshot.png)
## Test Results ✅

**Query**: _We have elevated 500 errors and login failures after a deployment. Outline the incident response plan._

| Metric | Value |
|---|---|
| Status | PASSED |
| Response Length | 2676 chars |
| Context Chunks | 5 |
| Sources Retrieved | `sev_triage, containment, stabilization, diagnostics, stakeholder_comms` |
| Avg Relevance | 0.47 |
| Model | qwen2.5:1.5b |
