"""
Executive Scenario Simulator Backend
Scenario Simulation CAG
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
    {"source": "scenario_frame", "title": "Scenario Framing", "keywords": ["scenario", "base", "bull", "bear", "market"], "content": "Scenario planning should define one base case, one upside case, and one downside case with meaningfully different assumptions."},
    {"source": "drivers", "title": "Key Drivers", "keywords": ["driver", "assumption", "pricing", "competition", "demand", "margin"], "content": "Focus scenarios on the few variables that move the business: demand, pricing power, sales velocity, churn, regulation, and supply constraints."},
    {"source": "leading_indicators", "title": "Leading Indicators", "keywords": ["indicator", "signal", "metric", "trigger", "forecast"], "content": "Each scenario needs observable signals that tell leadership which world is emerging. Lagging financials alone are too slow for action."},
    {"source": "decision_rules", "title": "Decision Rules", "keywords": ["decision", "trigger", "hire", "spend", "expand", "cut"], "content": "Translate scenarios into actions. Leadership should know which hires, spend changes, or market moves are triggered under each case."},
    {"source": "capital_allocation", "title": "Capital Allocation", "keywords": ["budget", "cash", "runway", "investment", "allocation"], "content": "Tie strategy to capital deployment and risk appetite. Optionality matters more than perfect precision when the environment shifts."},
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


app = FastAPI(title="Executive Scenario Simulator API")

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
print(f"Scenario Simulator selected model: {selected_model}")


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
    return {"app": "Executive Scenario Simulator", "technique": "Scenario Simulation CAG", "status": "running"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        context = retrieve_context(request.query, request.top_k)
        process_steps = [
            {"step": "scenario_retrieval", "description": "Retrieved scenario-planning heuristics relevant to the business case"},
            {"step": "simulation_augmentation", "description": "Built a prompt around assumptions, signals, and decision triggers"},
        ]
        formatted_context = "\n\n".join(f"{item['title']} ({item['source']}): {item['content']}" for item in context)
        prompt = f"""You are an executive strategist building scenario plans for a SOTA MVP business.

Business scenario:
{request.query}

Relevant planning context:
{formatted_context}

Respond with these sections:
1. Base case
2. Bull case
3. Bear case
4. Leading indicators to watch
5. Decision triggers and recommended moves

Keep the answer strategic but specific."""
        response, _ = await ollama_client.generate(prompt=prompt)
        process_steps.append({"step": "scenario_generation", "description": "Generated a multi-scenario executive planning brief"})
        return QueryResponse(query=request.query, response=response, context=context, metadata={"model": selected_model, "technique": "Scenario Simulation CAG"}, process_steps=process_steps)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8025)
