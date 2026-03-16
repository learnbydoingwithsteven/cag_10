"""
Multi-Agent Strategy Debater Backend
Multi-Agent Debate CAG
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


app = FastAPI(title="Multi-Agent Strategy Debater API")

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
print(f"Multi-Agent Debater selected model: {selected_model}")

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
        "app": "Multi-Agent Strategy Debater",
        "technique": "Multi-Agent Debate CAG",
        "status": "running"
    }

@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using Multi-Agent Debate CAG"""
    try:
        process_steps = []
        context = []
        
        # Persona 1: Optimist
        prompt_opt = f"You are an Optimist. Review this query and provide an unconditionally positive and ambitious perspective: {request.query}"
        resp_opt, _ = await ollama_client.generate(prompt=prompt_opt)
        process_steps.append({"step": "generation_optimist", "description": "Generated optimist perspective"})
        context.append({"type": "optimist_perspective", "content": resp_opt, "relevance": 1.0})

        # Persona 2: Pessimist
        prompt_pes = f"You are a Pessimist. Review this query and the optimist's perspective, then provide a critical, risk-averse, and cautious perspective. Query: {request.query}. Optimist: {resp_opt}"
        resp_pes, _ = await ollama_client.generate(prompt=prompt_pes)
        process_steps.append({"step": "generation_pessimist", "description": "Generated pessimist perspective"})
        context.append({"type": "pessimist_perspective", "content": resp_pes, "relevance": 1.0})

        # Persona 3: Analyst (Synthesizer)
        prompt_syn = f"You are an Analyst synthesising perspectives. Query: {request.query}\nOptimist: {resp_opt}\nPessimist: {resp_pes}\nProvide a final, balanced strategy and conclusion."
        final_response, _ = await ollama_client.generate(prompt=prompt_syn)
        process_steps.append({"step": "generation_analyst", "description": "Generated synthesized analysis"})
        context.append({"type": "analyst_synthesis", "content": final_response, "relevance": 1.0})

        return QueryResponse(
            query=request.query,
            response=final_response,
            context=context,
            metadata={"model": selected_model, "technique": "Multi-Agent Debate CAG"},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
