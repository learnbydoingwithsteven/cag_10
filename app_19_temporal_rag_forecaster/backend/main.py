"""
Temporal Market Forecaster Backend
Temporal RAG CAG
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient


def select_best_model(ollama_client):
    """Dynamic model selection - pick best available LOCAL chat model."""
    try:
        available_models = ollama_client.list_models()
        embedding_keywords = ["embed", "nomic-embed", "bge", "e5"]
        chat_models = [
            m for m in available_models
            if not any(kw in m.lower() for kw in embedding_keywords)
            and ":cloud" not in m.lower()
        ]
        preferred = ["llama3", "qwen2.5", "qwen2", "mistral",
                      "gemma", "llama2", "tinyllama", "phi"]
        for pref in preferred:
            for m in chat_models:
                if pref in m.lower():
                    return m
        return chat_models[0] if chat_models else "llama3"
    except Exception:
        return "llama3"


app = FastAPI(title="Temporal Market Forecaster API")

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
print(f"Temporal Forecaster selected model: {selected_model}")

# Simulated database of temporally sensitive events
EVENTS = [
    {"date": "2023-01-10", "content": "Tech stocks slide as interest rate hike fears continue."},
    {"date": "2023-06-15", "content": "AI boom drives Nasdaq to 52-week highs."},
    {"date": "2023-11-01", "content": "Fed signals pause on rate hikes, market rallies."},
    {"date": "2024-02-20", "content": "Semiconductor earnings beat expectations, driving further AI speculation."}
]

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
    return {
        "app": "Temporal Market Forecaster",
        "technique": "Temporal RAG CAG",
        "status": "running"
    }

@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using Temporal RAG CAG"""
    try:
        process_steps = []
        context = []
        
        # 1. Temporal Sorting/Retrieval Step
        sorted_events = sorted(EVENTS, key=lambda x: x["date"])
        
        formatted_timeline = "\n".join([f"[{e['date']}] {e['content']}" for e in sorted_events])
        
        process_steps.append({"step": "temporal_retrieval", "description": "Retrieved and chronologically ordered historical context"})
        for e in sorted_events:
            context.append({"type": "historical_event", "content": f"[{e['date']}] {e['content']}", "relevance": 1.0})

        # 2. Forecasting Generation Step
        prompt_gen = f"""You are a temporal market forecaster. 
Analyze the explicit chronological progression of the following historical timeline and forecast the next logical market trend relation to this query: '{request.query}'.
Make sure your answer explicitly references how the timeline builds up to your forecast.

Historical Timeline:
{formatted_timeline}

Forecast Analysis:"""
        
        forecast, _ = await ollama_client.generate(prompt=prompt_gen)
        process_steps.append({"step": "temporal_generation", "description": "Generated forecast from chronological timeline"})

        return QueryResponse(
            query=request.query,
            response=forecast,
            context=context,
            metadata={"model": selected_model, "technique": "Temporal RAG CAG"},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8019)
