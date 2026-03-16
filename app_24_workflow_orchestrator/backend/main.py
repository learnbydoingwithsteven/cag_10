"""
Workflow Orchestration Designer Backend
State Machine CAG
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


PATTERNS = [
    {"source": "state_design", "title": "State Design", "keywords": ["workflow", "state", "step", "handoff", "queue"], "content": "Model workflows as explicit states with entry conditions, exit conditions, and ownership. Hidden transitions create operational ambiguity."},
    {"source": "automation_boundaries", "title": "Automation Boundaries", "keywords": ["automation", "manual", "human", "review", "escalation"], "content": "Automate deterministic checks and calculations. Route judgment-heavy, risky, or exception states to a human with clear SLAs."},
    {"source": "compliance_checkpoints", "title": "Compliance Checkpoints", "keywords": ["kyc", "audit", "compliance", "approval", "policy"], "content": "Insert compliance checkpoints before activation or payout events. Capture evidence and reason codes for every hold, approval, or rejection."},
    {"source": "failure_recovery", "title": "Failure Recovery", "keywords": ["retry", "fallback", "timeout", "dead letter", "recovery"], "content": "Every orchestration should define retry policy, timeout behavior, and dead-letter handling. Do not bury failures inside background jobs."},
    {"source": "metrics", "title": "Operational Metrics", "keywords": ["metric", "sla", "conversion", "latency", "throughput"], "content": "Track volume, conversion, SLA adherence, and exception rate at each state. Metrics should tell you where work stalls and why."},
]


def tokenize(text):
    return set(re.findall(r"[a-z0-9+-]+", text.lower()))


def retrieve_context(query, top_k):
    query_lower = query.lower()
    query_terms = tokenize(query)
    scored = []
    for item in PATTERNS:
        keyword_hits = sum(1 for keyword in item["keywords"] if keyword in query_lower)
        content_hits = len(query_terms & tokenize(item["content"]))
        score = (keyword_hits * 2) + content_hits
        if score > 0:
            scored.append((score, item))
    if not scored:
        scored = [(1, item) for item in PATTERNS]
    scored.sort(key=lambda entry: entry[0], reverse=True)
    selected = scored[: min(top_k, len(scored))]
    max_score = selected[0][0] if selected else 1
    return [{"source": item["source"], "title": item["title"], "content": item["content"], "relevance": round(score / max_score, 2)} for score, item in selected]


app = FastAPI(title="Workflow Orchestration Designer API")

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
print(f"Workflow Orchestrator selected model: {selected_model}")


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
    return {"app": "Workflow Orchestration Designer", "technique": "State Machine CAG", "status": "running"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        context = retrieve_context(request.query, request.top_k)
        process_steps = [
            {"step": "pattern_retrieval", "description": "Retrieved orchestration patterns for the requested workflow"},
            {"step": "workflow_augmentation", "description": "Built a prompt around states, automation boundaries, failures, and metrics"},
        ]
        formatted_context = "\n\n".join(f"{item['title']} ({item['source']}): {item['content']}" for item in context)
        prompt = f"""You are a workflow architect designing a production-grade orchestration for a SOTA MVP.

Workflow request:
{request.query}

Relevant orchestration context:
{formatted_context}

Respond with these sections:
1. State machine overview
2. Each step with owner and trigger
3. Automation vs human review boundaries
4. Failure handling and escalation
5. Metrics and SLA recommendations

Keep the answer implementation-oriented."""
        response, _ = await ollama_client.generate(prompt=prompt)
        process_steps.append({"step": "workflow_generation", "description": "Generated a state-machine oriented workflow design"})
        return QueryResponse(query=request.query, response=response, context=context, metadata={"model": selected_model, "technique": "State Machine CAG"}, process_steps=process_steps)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8024)
