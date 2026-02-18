# App 08: Educational Tutor

**CAG Technique: Adaptive Difficulty CAG**

## What This App Teaches
How CAG uses **pedagogy frameworks** (Bloom's Taxonomy, scaffolding, spaced repetition) to teach the LLM how to be a good tutor — explaining concepts at the right level with examples and practice problems.

## Knowledge Base (7 items)
- `blooms_taxonomy` — Remember → Understand → Apply → Analyze → Evaluate → Create
- `scaffolding` — Break complex concepts, provide hints, gradually remove support
- `assessment` — Formative assessment, misconception detection
- `spaced_repetition` — Interval review (1, 3, 7, 14 days), active recall
- `analogies` — Concrete before abstract, multiple representations
- `growth_mindset` — Praise effort, frame mistakes as learning
- `subjects` — Mathematics, science, programming, language

## Test Results ✅

**Query**: _"Explain how recursion works in programming with an example"_

| Metric | Value |
|---|---|
| Response Length | 1,997 chars |
| Context Chunks | 5 |
| Sources Retrieved | `analogies`, `subjects`, `blooms_taxonomy`, `scaffolding`, `assessment` |
| Avg Relevance | 0.59 |
| Generation Time | 6,706ms |

The CAG retrieved pedagogy guidelines to structure the response: concept → analogy → example → practice.

## Quick Start
```bash
cd backend && py main.py    # Port 8008
cd frontend && npm start    # Port 3008
```
