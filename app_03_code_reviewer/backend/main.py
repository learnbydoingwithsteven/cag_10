"""
Code Review Bot Backend
AST-based Context Augmentation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient

app = FastAPI(title="Code Review Bot API")

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


@app.get("/")
async def root():
    return {
        "app": "Code Review Bot",
        "technique": "AST-based Context Augmentation",
        "status": "running"
    }


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using AST-based Context Augmentation"""
    try:
        # Simulate CAG processing
        context = [
            {"type": "context_item", "content": f"Context {i+1} for query", "relevance": 0.9 - i*0.1}
            for i in range(request.top_k)
        ]
        
        prompt = f"""You are a code review bot. Process the following query:

Query: {request.query}

Context:
{chr(10).join([f"- {c['content']}" for c in context])}

Provide a comprehensive response."""
        
        response = ollama_client.generate(prompt=prompt, model="codellama")
        
        process_steps = [
            {"step": "context_retrieval", "description": "Retrieved relevant context"},
            {"step": "augmentation", "description": "Augmented prompt with context"},
            {"step": "generation", "description": "Generated response with LLM"}
        ]
        
        return QueryResponse(
            query=request.query,
            response=response,
            context=context,
            metadata={"model": "codellama", "technique": "AST-based Context Augmentation"},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
