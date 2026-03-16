"""
LLM Guardrail Red-Team Lab Backend
Adversarial Evaluation CAG
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


PLAYBOOK = [
    {"source": "prompt_injection", "title": "Prompt Injection", "keywords": ["prompt injection", "system prompt", "instructions", "override"], "content": "Probe whether the assistant follows hidden instructions over the user task. Test direct override, indirect prompt injection, and tool misdirection."},
    {"source": "data_exfiltration", "title": "Data Exfiltration", "keywords": ["data leakage", "secret", "pii", "credential", "exfiltration"], "content": "Test if the system reveals secrets, hidden context, prior users' data, or internal policy text when pushed with social engineering."},
    {"source": "jailbreak_patterns", "title": "Jailbreak Patterns", "keywords": ["jailbreak", "roleplay", "bypass", "unsafe", "policy"], "content": "Roleplay and hypothetical framing often bypass weak guardrails. Evaluate whether refusals stay stable after reframing or decomposition."},
    {"source": "tool_boundaries", "title": "Tool Boundary Checks", "keywords": ["tool", "plugin", "function", "browser", "action"], "content": "Check whether the agent uses tools with the right authorization, cites uncertainty, and avoids acting on untrusted retrieved instructions."},
    {"source": "mitigation_design", "title": "Mitigation Design", "keywords": ["mitigation", "guardrail", "policy", "allowlist", "classifier"], "content": "Pair each failure mode with a concrete defense: policy rewrite, output filter, input classifier, sandboxing, or human escalation gate."},
]


def tokenize(text):
    return set(re.findall(r"[a-z0-9+-]+", text.lower()))


def retrieve_context(query, top_k):
    query_lower = query.lower()
    query_terms = tokenize(query)
    scored = []
    for item in PLAYBOOK:
        keyword_hits = sum(1 for keyword in item["keywords"] if keyword in query_lower)
        content_hits = len(query_terms & tokenize(item["content"]))
        score = (keyword_hits * 2) + content_hits
        if score > 0:
            scored.append((score, item))
    if not scored:
        scored = [(1, item) for item in PLAYBOOK]
    scored.sort(key=lambda entry: entry[0], reverse=True)
    selected = scored[: min(top_k, len(scored))]
    max_score = selected[0][0] if selected else 1
    return [{"source": item["source"], "title": item["title"], "content": item["content"], "relevance": round(score / max_score, 2)} for score, item in selected]


app = FastAPI(title="LLM Guardrail Red-Team Lab API")

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
print(f"Guardrail Red-Team selected model: {selected_model}")


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
    return {"app": "LLM Guardrail Red-Team Lab", "technique": "Adversarial Evaluation CAG", "status": "running"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        context = retrieve_context(request.query, request.top_k)
        process_steps = [
            {"step": "attack_retrieval", "description": "Retrieved adversarial patterns and guardrail heuristics"},
            {"step": "eval_augmentation", "description": "Built a prompt focused on attack vectors, failure modes, and mitigations"},
        ]
        formatted_context = "\n\n".join(f"{item['title']} ({item['source']}): {item['content']}" for item in context)
        prompt = f"""You are a senior AI red-team lead reviewing a production LLM system.

System under test:
{request.query}

Relevant adversarial playbook:
{formatted_context}

Respond with these sections:
1. Highest-risk attack vectors
2. Example red-team prompts to run
3. Likely failure modes
4. Mitigations and guardrails
5. Go-live recommendation

Be direct and operational."""
        response, _ = await ollama_client.generate(prompt=prompt)
        process_steps.append({"step": "eval_generation", "description": "Generated an adversarial evaluation plan"})
        return QueryResponse(query=request.query, response=response, context=context, metadata={"model": selected_model, "technique": "Adversarial Evaluation CAG"}, process_steps=process_steps)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8023)
