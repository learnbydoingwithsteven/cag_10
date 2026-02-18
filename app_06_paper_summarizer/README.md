# App 06: Research Paper Summarizer

**CAG Technique: Hierarchical Summarization CAG**

## What This App Teaches
How CAG provides **structured summarization guidelines** to ensure the LLM produces multi-level summaries (TL;DR → Key Findings → Detailed Analysis) — teaching it the academic paper structure.

## Knowledge Base (7 items)
- `abstract_guide` — Claim/evidence/significance extraction
- `methodology_guide` — Experimental setup, datasets, baselines, metrics
- `results_guide` — Main results interpretation, statistical significance
- `citation_guide` — Citation context analysis (contrast vs building-upon)
- `limitations_guide` — Assumption checking, bias detection
- `hierarchy_guide` — L1-L4 summary levels
- `reproducibility` — Code availability, hyperparameters, compute requirements

## Test Results ✅

**Query**: _"Summarize a paper about transformer architecture and attention mechanisms"_

| Metric | Value |
|---|---|
| Response Length | 2,058 chars |
| Context Chunks | 5 (all structure guides) |
| Sources Retrieved | `abstract_guide`, `methodology_guide`, `results_guide`, `citation_guide`, `limitations_guide` |
| Avg Relevance | 0.52 |
| Generation Time | 3,744ms (fastest) |

## Quick Start
```bash
cd backend && py main.py    # Port 8006
cd frontend && npm start    # Port 3006
```
