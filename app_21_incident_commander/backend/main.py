"""
Incident Command Copilot Backend
Runbook-Guided Incident Response CAG
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


RUNBOOKS = [
    {
        "source": "sev_triage",
        "title": "Severity and Command",
        "keywords": ["sev", "severity", "critical", "incident", "outage", "login", "500"],
        "content": "Assign a single incident commander, define severity from user impact, and publish a timestamped incident channel. Avoid parallel command structures.",
    },
    {
        "source": "containment",
        "title": "Containment First",
        "keywords": ["rollback", "containment", "mitigation", "disable", "feature flag", "deployment"],
        "content": "If a fresh deployment correlates with elevated failures, prioritize rollback, traffic shedding, or feature-flag disablement before deep root-cause work.",
    },
    {
        "source": "diagnostics",
        "title": "Diagnostic Sweep",
        "keywords": ["logs", "metrics", "trace", "dashboard", "dependency", "database", "auth"],
        "content": "Triangulate incidents with errors, latency, and dependency health. Compare request cohorts, release markers, and auth or database behavior.",
    },
    {
        "source": "stakeholder_comms",
        "title": "Stakeholder Communications",
        "keywords": ["customer", "status page", "executive", "support", "communication", "eta"],
        "content": "Internal updates should state impact, mitigation status, and next update time. External updates should be factual and avoid speculative root causes.",
    },
    {
        "source": "stabilization",
        "title": "Stabilization",
        "keywords": ["monitor", "stabilize", "verify", "postmortem", "follow-up", "action item"],
        "content": "Keep the incident open until error rate and user flows are stable across multiple observation windows. Capture decisions for the postmortem while details are fresh.",
    },
]


def tokenize(text):
    return set(re.findall(r"[a-z0-9+-]+", text.lower()))


def retrieve_context(query, top_k):
    query_lower = query.lower()
    query_terms = tokenize(query)
    scored = []
    for item in RUNBOOKS:
        keyword_hits = sum(1 for keyword in item["keywords"] if keyword in query_lower)
        content_hits = len(query_terms & tokenize(item["content"]))
        score = (keyword_hits * 2) + content_hits
        if score > 0:
            scored.append((score, item))
    if not scored:
        scored = [(1, item) for item in RUNBOOKS]
    scored.sort(key=lambda entry: entry[0], reverse=True)
    selected = scored[: min(top_k, len(scored))]
    max_score = selected[0][0] if selected else 1
    return [
        {"source": item["source"], "title": item["title"], "content": item["content"], "relevance": round(score / max_score, 2)}
        for score, item in selected
    ]


app = FastAPI(title="Incident Command Copilot API")

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
print(f"Incident Commander selected model: {selected_model}")


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
    return {"app": "Incident Command Copilot", "technique": "Runbook-Guided Incident Response CAG", "status": "running"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        context = retrieve_context(request.query, request.top_k)
        process_steps = [
            {"step": "runbook_retrieval", "description": "Retrieved incident runbooks relevant to the failure pattern"},
            {"step": "response_augmentation", "description": "Structured the prompt around triage, containment, communication, and recovery"},
        ]
        formatted_context = "\n\n".join(
            f"{item['title']} ({item['source']}): {item['content']}" for item in context
        )
        prompt = f"""You are an experienced incident commander operating a SOTA production system.

Incident report:
{request.query}

Relevant runbook context:
{formatted_context}

Respond with these sections:
1. Severity assessment
2. First 15 minutes
3. Containment and rollback options
4. Diagnostics to run next
5. Stakeholder communication plan
6. Recovery and follow-up

Be concise, operational, and sequence actions clearly."""
        response, _ = await ollama_client.generate(prompt=prompt)
        process_steps.append({"step": "incident_generation", "description": "Generated a runbook-aligned incident action plan"})
        return QueryResponse(
            query=request.query,
            response=response,
            context=context,
            metadata={"model": selected_model, "technique": "Runbook-Guided Incident Response CAG"},
            process_steps=process_steps,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8021)
