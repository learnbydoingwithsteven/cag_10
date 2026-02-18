"""
Code Review Bot Backend - AST-aware Code Quality CAG
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient
from cag_engine.base import CAGRequest
from code_review_rag import CodeReviewCAG

app = FastAPI(title="Code Review Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_client = OllamaClient(host="http://localhost:11434")
reviewer = CodeReviewCAG(ollama_client)


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
        "technique": "AST-aware Code Quality CAG",
        "status": "running"
    }


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Review code using AST-aware Code Quality CAG"""
    try:
        cag_request = CAGRequest(query=request.query, context_limit=request.top_k)
        result = await reviewer.process(cag_request)
        
        return QueryResponse(
            query=request.query,
            response=result.answer,
            context=[{
                "content": c.content,
                "relevance": c.relevance_score,
                "source": c.source
            } for c in result.context_chunks],
            metadata=result.metadata,
            process_steps=[{
                "step": s.step_name,
                "description": s.description,
                "duration": s.duration_ms
            } for s in reviewer.process_steps]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
