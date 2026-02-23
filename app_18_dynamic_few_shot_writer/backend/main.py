"""
Dynamic Few-Shot Copywriter Backend
Dynamic Context Selection CAG
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient

app = FastAPI(title="Dynamic Few-Shot Copywriter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_client = OllamaClient(base_url="http://ollama:11434")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    response: str
    context: list
    metadata: dict
    process_steps: list

# Simulated database of past successful marketing copy
PAST_COPY = [
    {"type": "SaaS", "copy": "Stop wrestling with spreadsheets. Simplify your workflows with our automation tool today!"},
    {"type": "Fitness", "copy": "Unleash your inner beast. Try our 30-day challenge and see real results."},
    {"type": "Finance", "copy": "Stop throwing money away! Start investing today and watch your wealth grow with zero hidden fees."},
    {"type": "Education", "copy": "Upskill on your schedule. Learn code from experts without breaking the bank."}
]

@app.get("/")
async def root():
    return {
        "app": "Dynamic Few-Shot Copywriter",
        "technique": "Dynamic Context Selection CAG",
        "status": "running"
    }

@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using Dynamic Context Selection CAG"""
    try:
        process_steps = []
        context = []
        
        # 1. Selection Step: Use an LLM call to pick the best related example, or simply pass all if small.
        # We will dynamically pick by having the LLM select the most relevant category.
        prompt_select = f"Which of the following categories best matches this query '{request.query}'? Categories: SaaS, Fitness, Finance, Education. Return ONLY the category name."
        category = ollama_client.generate(prompt=prompt_select, model="llama3").strip()
        
        selected_example = next((item for item in PAST_COPY if item["type"].lower() in category.lower()), PAST_COPY[0])
        
        process_steps.append({"step": "dynamic_selection", "description": f"Selected few-shot example for category: {category}"})
        context.append({"type": f"few_shot_example_{selected_example['type']}", "content": selected_example["copy"], "relevance": 0.95})

        # 2. Generation Step
        prompt_gen = f"""You are an expert copywriter. Write tight, punchy, high-converting copy for the following request.
Use the tone and structure of this successful past example: '{selected_example['copy']}'

Request: {request.query}
Copy:"""
        final_copy = ollama_client.generate(prompt=prompt_gen, model="llama3")
        process_steps.append({"step": "generation", "description": "Generated final copy using dynamic few-shot context"})

        return QueryResponse(
            query=request.query,
            response=final_copy,
            context=context,
            metadata={"model": "llama3", "technique": "Dynamic Context Selection CAG"},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018)
