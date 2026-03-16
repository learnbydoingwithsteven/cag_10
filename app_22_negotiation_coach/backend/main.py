"""
Enterprise Negotiation Coach Backend
Strategy Playbook CAG
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
    {
        "source": "batna",
        "title": "BATNA Framing",
        "keywords": ["batna", "alternative", "walk away", "leverage", "renewal", "enterprise"],
        "content": "Define your best alternative, renewal floor, and non-price levers before you negotiate. Strong negotiators separate what is desirable from what is required.",
    },
    {
        "source": "anchoring",
        "title": "Anchoring Strategy",
        "keywords": ["anchor", "price", "discount", "rate", "proposal", "commercial"],
        "content": "Set the commercial anchor around business value, risk transfer, or expanded scope. Do not open with concessions; open with a justified frame.",
    },
    {
        "source": "concession_ladder",
        "title": "Concession Ladder",
        "keywords": ["concession", "trade", "multi-year", "term", "package", "give"],
        "content": "Every concession should be conditional and traded for something: longer term, broader scope, reference rights, faster close, or payment timing.",
    },
    {
        "source": "stakeholder_mapping",
        "title": "Stakeholder Mapping",
        "keywords": ["procurement", "champion", "legal", "security", "stakeholder", "executive"],
        "content": "Map each stakeholder by motive: procurement wants leverage, champions want continuity, legal wants reduced risk, and executives want predictable outcomes.",
    },
    {
        "source": "objection_handling",
        "title": "Objection Handling",
        "keywords": ["objection", "pushback", "budget", "competitive", "discount", "compare"],
        "content": "Respond to price pressure by diagnosing the objection first. Affordability, value skepticism, competitive pressure, and negotiation theater require different replies.",
    },
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
    return [
        {"source": item["source"], "title": item["title"], "content": item["content"], "relevance": round(score / max_score, 2)}
        for score, item in selected
    ]


app = FastAPI(title="Enterprise Negotiation Coach API")

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
print(f"Negotiation Coach selected model: {selected_model}")


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
    return {"app": "Enterprise Negotiation Coach", "technique": "Strategy Playbook CAG", "status": "running"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        context = retrieve_context(request.query, request.top_k)
        process_steps = [
            {"step": "playbook_retrieval", "description": "Retrieved negotiation heuristics matching the commercial context"},
            {"step": "talk_track_augmentation", "description": "Augmented the prompt with BATNA, anchor, concession, and stakeholder guidance"},
        ]
        formatted_context = "\n\n".join(
            f"{item['title']} ({item['source']}): {item['content']}" for item in context
        )
        prompt = f"""You are an enterprise negotiation strategist helping close a high-stakes commercial deal.

Scenario:
{request.query}

Retrieved negotiation playbook:
{formatted_context}

Respond with these sections:
1. Negotiation diagnosis
2. Recommended anchor and value framing
3. Concession ladder
4. Talk track for the next call
5. Risks and red lines
6. Concrete next steps to close

Keep the tone executive and practical."""
        response, _ = await ollama_client.generate(prompt=prompt)
        process_steps.append({"step": "strategy_generation", "description": "Generated a negotiation strategy and talk track"})
        return QueryResponse(
            query=request.query,
            response=response,
            context=context,
            metadata={"model": selected_model, "technique": "Strategy Playbook CAG"},
            process_steps=process_steps,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8022)
