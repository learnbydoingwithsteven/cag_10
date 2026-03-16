"""
Constraint-Aware Launch Planner Backend
Constraint-Satisfaction CAG
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from cag_engine.ollama_client import OllamaClient


def select_best_model(ollama_client):
    try:
        available_models = ollama_client.list_models()
        embedding_keywords = ["embed", "nomic-embed", "bge", "e5"]
        chat_models = [
            model for model in available_models
            if not any(keyword in model.lower() for keyword in embedding_keywords)
            and ":cloud" not in model.lower()
        ]
        preferred = ["llama3", "qwen2.5", "qwen2", "mistral", "gemma", "llama2", "tinyllama", "phi"]
        for candidate in preferred:
            for model in chat_models:
                if candidate in model.lower():
                    return model
        return chat_models[0] if chat_models else "llama3"
    except Exception:
        return "llama3"


KNOWLEDGE_BASE = [
    {
        "source": "constraint_triage",
        "title": "Constraint Triage",
        "keywords": ["budget", "time", "deadline", "team", "engineer", "constraint", "scope"],
        "content": "Freeze non-negotiables first: budget, deadline, team capacity, and success metric. If one constraint tightens, reduce scope before compressing quality gates.",
    },
    {
        "source": "phased_delivery",
        "title": "Three-Phase Delivery",
        "keywords": ["phase", "launch", "beta", "ga", "milestone", "week", "roadmap"],
        "content": "Use three phases for MVP planning: foundation, proof of value, and launch readiness. Each phase should have explicit deliverables and one accountable owner.",
    },
    {
        "source": "risk_buffering",
        "title": "Risk Buffering",
        "keywords": ["risk", "buffer", "contingency", "delay", "dependency"],
        "content": "Reserve 15-20 percent of the timeline for integration defects, stakeholder rework, and dependency delays. Keep one fallback cutline that can be dropped safely.",
    },
    {
        "source": "gtm_alignment",
        "title": "Go-To-Market Alignment",
        "keywords": ["sales", "marketing", "customer", "launch", "enablement", "demo"],
        "content": "Strong launches run product, GTM, and customer readiness in parallel. Do not leave pricing, demo flow, or onboarding assets to the final week.",
    },
    {
        "source": "quality_gates",
        "title": "Quality Gates",
        "keywords": ["quality", "qa", "security", "checklist", "release", "rollback"],
        "content": "Speed comes from fewer features, not fewer controls. Every MVP launch still needs critical-path testing, rollback steps, and launch-day instrumentation.",
    },
]


def tokenize(text):
    return set(re.findall(r"[a-z0-9$+-]+", text.lower()))


def retrieve_context(query, top_k):
    query_lower = query.lower()
    query_terms = tokenize(query)
    scored = []
    for item in KNOWLEDGE_BASE:
        keyword_hits = sum(1 for keyword in item["keywords"] if keyword in query_lower)
        content_hits = len(query_terms & tokenize(item["content"]))
        score = (keyword_hits * 2) + content_hits
        if score > 0:
            scored.append((score, item))
    if not scored:
        scored = [(1, item) for item in KNOWLEDGE_BASE]
    scored.sort(key=lambda entry: entry[0], reverse=True)
    selected = scored[: min(top_k, len(scored))]
    max_score = selected[0][0] if selected else 1
    return [
        {
            "source": item["source"],
            "title": item["title"],
            "content": item["content"],
            "relevance": round(score / max_score, 2),
        }
        for score, item in selected
    ]


app = FastAPI(title="Constraint-Aware Launch Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_client = OllamaClient(host="http://localhost:11434")
selected_model = select_best_model(ollama_client)
ollama_client.model = selected_model
print(f"Constraint Planner selected model: {selected_model}")


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResponse(BaseModel):
    query: str
    response: str
    context: list
    metadata: dict
    process_steps: list


@app.get("/")
async def root():
    return {"app": "Constraint-Aware Launch Planner", "technique": "Constraint-Satisfaction CAG", "status": "running"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        context = retrieve_context(request.query, request.top_k)
        process_steps = [
            {"step": "constraint_retrieval", "description": "Matched launch planning heuristics to the request constraints"},
            {"step": "plan_augmentation", "description": "Built a plan prompt with scope, GTM, and quality guidance"},
        ]
        formatted_context = "\n\n".join(
            f"{item['title']} ({item['source']}): {item['content']}" for item in context
        )
        prompt = f"""You are an elite product launch planner helping craft a SOTA MVP delivery plan.

User request:
{request.query}

Retrieved planning context:
{formatted_context}

Write a pragmatic answer with these sections:
1. Launch objective and hard constraints
2. Recommended 6-week plan by week
3. Scope cuts to protect quality
4. Launch risks and mitigations
5. Metrics to watch on launch day

Keep the response concrete and operational."""
        response, _ = await ollama_client.generate(prompt=prompt)
        process_steps.append({"step": "plan_generation", "description": "Generated a constraint-aware launch plan"})
        return QueryResponse(
            query=request.query,
            response=response,
            context=context,
            metadata={"model": selected_model, "technique": "Constraint-Satisfaction CAG"},
            process_steps=process_steps,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8020)
