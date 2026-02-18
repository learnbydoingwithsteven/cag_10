# CAG Applications Suite — Context-Augmented Generation with Ollama

## 🎓 What is CAG? (And How It Differs from RAG)

### RAG vs CAG: Key Differences

| Feature | **RAG** (Retrieval-Augmented Generation) | **CAG** (Context-Augmented Generation) |
|---|---|---|
| **Knowledge Storage** | External vector database (ChromaDB, Pinecone, etc.) | In-memory knowledge base, **preloaded at startup** |
| **Retrieval** | Embedding similarity search at query time | Keyword/rule-based matching from cached knowledge |
| **Latency** | Higher (embedding + vector search + LLM) | Lower (no embedding step, knowledge already in memory) |
| **Infrastructure** | Requires vector DB, embedding model, chunking pipeline | **Zero infrastructure** — knowledge is code |
| **Knowledge Update** | Re-embed + re-index documents | Update code and restart |
| **Best For** | Large, evolving document collections | Curated expert knowledge, domain rules, structured guidelines |
| **Trade-off** | More flexible, handles arbitrary documents | Faster, simpler, more predictable, easier to debug |

### The CAG 3-Step Pipeline

Every app in this suite follows the same **Retrieve → Augment → Generate** pipeline:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAG Pipeline (per request)                   │
│                                                                 │
│  1. RETRIEVE    ──→  Match query against in-memory knowledge    │
│     (< 1ms)          base using keyword scoring + relevance     │
│                                                                 │
│  2. AUGMENT     ──→  Build expert prompt with retrieved context │
│     (< 1ms)          + domain-specific instructions             │
│                                                                 │
│  3. GENERATE    ──→  Send augmented prompt to local Ollama LLM  │
│     (2-12s)          for response generation                    │
│                                                                 │
│  Total latency dominated by LLM generation, NOT retrieval.      │
└─────────────────────────────────────────────────────────────────┘
```

### Why CAG for Learning?

CAG is the **ideal starting point** for learning augmented generation because:
1. **No infrastructure needed** — no vector DBs, no embedding models, no cloud services
2. **Knowledge is transparent** — you can read the entire knowledge base in the source code
3. **Deterministic retrieval** — same query always retrieves same context (easy to debug)
4. **Focus on the pattern** — understand Retrieve → Augment → Generate without infrastructure noise

> **Note**: App 01 (Legal Analyzer) uses traditional **RAG** with ChromaDB for comparison.
> Apps 03-14 use **CAG** with in-memory knowledge bases.

---

## ✅ All Apps Tested & Verified

| # | App | CAG Technique | Response | Context | Avg Relevance | Latency | Status |
|---|-----|--------------|----------|---------|--------------|---------|--------|
| 03 | Code Review Bot | AST-aware Code Quality CAG | 2,168 chars | 5 chunks | 0.71 | 6.4s | ✅ |
| 04 | Customer Support Agent | Conversational Memory CAG | 1,439 chars | 1 chunk | 0.98 | 5.4s | ✅ |
| 05 | Financial Report Analyzer | Structured Data CAG | 3,688 chars | 5 chunks | 0.73 | 10.8s | ✅ |
| 06 | Research Paper Summarizer | Hierarchical Summarization CAG | 2,058 chars | 5 chunks | 0.52 | 3.7s | ✅ |
| 07 | Product Recommender | Hybrid Collaborative-Content CAG | 2,652 chars | 5 chunks | 0.91 | 7.0s | ✅ |
| 08 | Educational Tutor | Adaptive Difficulty CAG | 1,997 chars | 5 chunks | 0.59 | 6.7s | ✅ |
| 09 | Compliance Checker | Rule-based Compliance CAG | 1,192 chars | 5 chunks | 0.84 | 2.8s | ✅ |
| 10 | Fact Checker | Multi-source Verification CAG | 2,286 chars | 5 chunks | 0.40 | 6.9s | ✅ |
| 13 | Git Sync Assistant | Expert System CAG | 2,614 chars | 4 chunks | 0.96 | 7.0s | ✅ |
| 14 | Prompt Engineering Tutor | Pedagogical Scaffolding CAG | 4,766 chars | 5 chunks | 0.72 | 12.4s | ✅ |

> **Model Used**: `qwen2.5:1.5b` (dynamically auto-selected from available local Ollama models)
> **All apps tested on**: 2026-02-18

---

## 📦 Applications

### App 01: Legal Document Analyzer (Port 8001) — **RAG**
- **Technique**: Retrieval-Augmented Generation with Citation Tracking
- **Knowledge**: ChromaDB vector store with legal documents
- **Unique**: Uses **traditional RAG** with embeddings + vector search for comparison with CAG apps

### App 02: Medical Diagnosis Assistant (Port 8002) — **Multi-hop CAG**
- **Technique**: Multi-hop Reasoning with Neo4j Knowledge Graph
- **Knowledge**: Medical knowledge graph with symptom→disease→treatment relationships

### App 03: Code Review Bot (Port 8003) — **CAG**
- **Technique**: AST-aware Code Quality CAG
- **Knowledge**: 10 items (security, performance, style, error handling, code smells)
- **Test**: SQL injection detected → retrieved `security_input`, `error_handling`, `python_best`

### App 04: Customer Support Agent (Port 8004) — **CAG**
- **Technique**: Conversational Memory CAG
- **Knowledge**: 7 items (password reset, billing, shipping, returns, escalation guidelines)
- **Test**: "Forgot password" → retrieved `kb_password` with 98% relevance

### App 05: Financial Report Analyzer (Port 8005) — **CAG**
- **Technique**: Structured Data CAG
- **Knowledge**: 7 items (revenue, margins, liquidity, debt, cash flow, valuation, red flags)
- **Test**: "SaaS 60% gross margin" → retrieved `profit_margins`, `red_flags`, `valuation`

### App 06: Research Paper Summarizer (Port 8006) — **CAG**
- **Technique**: Hierarchical Summarization CAG
- **Knowledge**: 7 items (abstract, methodology, results, citations, limitations, hierarchy, reproducibility)
- **Test**: "Transformer paper" → retrieved all 5 structural sections for comprehensive summary

### App 07: Product Recommender (Port 8007) — **CAG**
- **Technique**: Hybrid Collaborative-Content CAG
- **Knowledge**: 7 items (collaborative, content, hybrid, catalog, segments, explainability, diversity)
- **Test**: "Budget student electronics" → retrieved `content_filtering`, `catalog`, `segments` (91% avg)

### App 08: Educational Tutor (Port 8008) — **CAG**
- **Technique**: Adaptive Difficulty CAG
- **Knowledge**: 7 items (Bloom's taxonomy, scaffolding, assessment, spaced repetition, analogies, growth mindset, subjects)
- **Test**: "Explain recursion" → retrieved `analogies`, `blooms_taxonomy`, `scaffolding`

### App 09: Compliance Checker (Port 8009) — **CAG**
- **Technique**: Rule-based Compliance CAG
- **Knowledge**: 7 items (GDPR Art.6, GDPR Art.17, data retention, contracts, SOX, risk scoring)
- **Test**: "10-year data retention GDPR" → retrieved `gdpr_art6`, `gdpr_art17`, `data_retention` (84% avg)

### App 10: Fact Checker (Port 8010) — **CAG**
- **Technique**: Multi-source Verification CAG
- **Knowledge**: 7 items (claim decomposition, source tiers, fallacies, statistics, verdict scale, cross-reference, temporal)
- **Test**: "90% startups fail" → retrieved all 5 methodology chunks for systematic analysis

### App 13: Git Sync Assistant (Port 8013) — **CAG**
- **Technique**: Expert System CAG
- **Knowledge**: 7 items (pull, push, merge, rebase, stash, fetch, status)
- **Test**: "Merge conflict after pull" → retrieved `git_basics`, `conflict_resolution` (96% avg)

### App 14: Prompt Engineering Tutor (Port 8014) — **CAG**
- **Technique**: Pedagogical Scaffolding CAG
- **Knowledge**: 12 items (zero-shot, few-shot, CoT, role prompting, structured output, anti-patterns, advanced)
- **Test**: "Chain-of-thought prompting" → retrieved `chain_of_thought` at 98% relevance

---

## 🏗 Architecture

### Shared CAG Engine (`shared/cag_engine/`)
```python
class CAGTechnique:
    async def process(self, request):
        # 1. RETRIEVE — match query against knowledge base
        context = await self.retrieve_context(request)
        
        # 2. AUGMENT — build expert prompt with context
        prompt = await self.augment_context(request, context)
        
        # 3. GENERATE — LLM response with augmented prompt
        response = await self.generate_response(prompt, request)
        
        return CAGResponse(answer=response, context_chunks=context)
```

Every app subclasses `CAGTechnique` and implements:
- `retrieve_context()` — domain-specific knowledge matching
- `augment_context()` — expert prompt construction
- `generate_response()` — Ollama LLM call

### Dynamic Model Selection
All apps auto-detect available local Ollama models and prefer chat models (filtering out embedding-only and cloud models):
```
Available: ['nomic-embed-text:latest', 'kimi-k2.5:cloud', 'tinyllama:latest', 'qwen2.5:1.5b']
Filtered:  ['tinyllama:latest', 'qwen2.5:1.5b']
Selected:  qwen2.5:1.5b
```

---

## 🚀 Quick Start

### Prerequisites
```bash
# Install Ollama and pull a model
ollama pull qwen2.5:1.5b   # or any chat model
```

### Run Any App
```bash
# Backend
cd app_03_code_reviewer/backend
py main.py
# → Runs on http://localhost:8003

# Frontend (in another terminal)
cd app_03_code_reviewer/frontend
npm install && npm start
# → Runs on http://localhost:3003
```

### Test All Apps
```bash
py test_all_apps.py
```

---

## 📁 Project Structure

```
cag_10/
├── shared/cag_engine/          # Core CAG engine (base class + Ollama client)
│   ├── base.py                 # CAGTechnique, CAGRequest, ContextChunk
│   └── ollama_client.py        # OllamaClient with generate/embed/list
├── app_01_legal_analyzer/      # RAG with ChromaDB (for comparison)
├── app_02_medical_assistant/   # Multi-hop with Neo4j
├── app_03_code_reviewer/       # AST-aware Code Quality CAG
├── app_04_support_agent/       # Conversational Memory CAG
├── app_05_financial_analyzer/  # Structured Data CAG
├── app_06_paper_summarizer/    # Hierarchical Summarization CAG
├── app_07_product_recommender/ # Hybrid Collaborative-Content CAG
├── app_08_educational_tutor/   # Adaptive Difficulty CAG
├── app_09_compliance_checker/  # Rule-based Compliance CAG
├── app_10_fact_checker/        # Multi-source Verification CAG
├── app_13_git_sync/            # Expert System CAG
├── app_14_prompt_tutor/        # Pedagogical Scaffolding CAG
├── test_all_apps.py            # Batch test script
└── README.md
```

Each app follows the same structure:
```
app_XX_name/
├── backend/
│   ├── main.py             # FastAPI server + endpoints
│   ├── *_rag.py            # CAGTechnique subclass + knowledge base
│   └── requirements.txt
├── frontend/
│   ├── src/App.js          # React UI
│   └── package.json
└── README.md               # App-specific docs with test results
```

---

## 📚 Learning Path

1. **Start with App 03** (Code Review) — simplest CAG, 10-item knowledge base
2. **Compare App 01 vs App 03** — see RAG (vector DB) vs CAG (in-memory) trade-offs
3. **Study App 09** (Compliance) — see how rule-based knowledge maps to CAG
4. **Explore App 14** (Prompt Tutor) — learn prompting while seeing CAG in action
5. **Build your own** — subclass `CAGTechnique`, add domain knowledge, done!
