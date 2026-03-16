# App 14: Prompt Engineering Tutor

**State-of-the-Art (SOTA) Pedagogical Scaffolding CAG**

This application teaches prompt engineering techniques using a **Pedagogical Scaffolding CAG** approach — retrieving relevant technique knowledge and presenting it with before/after examples and practice exercises.

## CAG Learning Objective
Demonstrates how CAG can be used for **adaptive education**: the knowledge base contains categorized prompt engineering techniques, and the retrieval step selects the most relevant ones based on the student's question.

## SOTA Features
1.  **Dynamic Model Selection**: Auto-detects best available local Ollama model.
2.  **Pedagogical Scaffolding**: Responds with concept → example → explanation → exercise.
3.  **Categorized Knowledge Base**: Techniques, best practices, anti-patterns, and advanced patterns.
4.  **Quick Question Chips**: Pre-built questions for instant exploration.
5.  **Process Visualization**: Full CAG pipeline transparency.

## Architecture
- **Backend**: FastAPI + Ollama (auto-selected model).
- **CAG Technique**: Pedagogical Scaffolding with keyword-based retrieval across 12 knowledge items.
- **Frontend**: React + Material-UI with quick-question chips and accordion details.

## Verification

### Backend API (Port 8014) ✅
```
$ Invoke-WebRequest -Uri http://localhost:8014/
StatusCode: 200
Content: {"app":"Prompt Engineering Tutor","technique":"Pedagogical Scaffolding CAG","status":"running"}
```

### Swagger API Docs ✅
```
$ Invoke-WebRequest -Uri http://localhost:8014/docs -Method Head
StatusCode: 200 OK
```

### Dynamic Model Selection ✅
```
Available chat models: ['tinyllama:latest', 'qwen2.5:1.5b']
Prompt Tutor selected model: qwen2.5:1.5b
```

### Sample Query & Response ✅

**Query**: _"What is chain-of-thought prompting?"_

**Context Retrieved** (5 chunks, avg relevance: 0.72):
| Source | Relevance | Category |
|---|---|---|
| chain_of_thought | 98% | technique |
| react | 93% | advanced |
| anti_vague | 88% | anti_pattern |
| zero_shot | 40% | technique |
| few_shot | 40% | technique |

**Response** (1000 tokens, 12.4s latency):
> # Chain-Of-Thought Prompting
> ## What Is Chain-Of-Thought (CoT) Prompting?
> Chain-of-thought prompting involves providing explicit reasoning steps to guide the model through a problem-solving process...
> ### Example Before / After
> (Detailed examples with classifications)
> ### Practice Exercise
> Create 3 prompts using chain-of-thought prompting...

### CAG Process Steps ✅
| Step | Duration |
|---|---|
| Context Retrieval | <1ms |
| Context Augmentation | <1ms |
| LLM Generation | 12,369ms |

### Frontend (Port 3014) ✅
```
Compiled successfully!
Local: http://localhost:7184 (dev port)
```

## Quick Start
```bash
# Start Backend
cd backend
py main.py
# → Auto-selects best available local Ollama model
# → Runs on http://localhost:8014

# Start Frontend (in another terminal)
cd frontend
npm install
npm start
# → Runs on http://localhost:3014
```

## API Usage
```bash
# Health check
curl http://localhost:8014/

# Learn a prompt engineering concept
curl -X POST http://localhost:8014/learn \
     -H "Content-Type: application/json" \
     -d '{"query": "How do I write a good few-shot prompt?"}'
```

Response includes `response`, `context` (knowledge sources), `metadata`, and `process_steps`.
## Test Results ✅

**Query**: _Explain chain-of-thought prompting and when to use it_

| Metric | Value |
|---|---|
| Status | PASSED |
| Response Length | 1638 chars |
| Context Chunks | 5 |
| Sources Retrieved | `few_shot, chain_of_thought, zero_shot, role_prompting, structured_output` |
| Avg Relevance | 0.84 |
| Model | Auto-selected local model |


