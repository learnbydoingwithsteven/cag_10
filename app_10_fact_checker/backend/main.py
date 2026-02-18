"""
Fact Checker Backend - Multi-source Verification CAG
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from cag_engine.ollama_client import OllamaClient
from cag_engine.base import CAGRequest
from fact_check_rag import FactCheckerCAG

app = FastAPI(title="Fact Checker API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

ollama_client = OllamaClient(host="http://localhost:11434")
checker = FactCheckerCAG(ollama_client)

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
    return {"app": "Fact Checker", "technique": "Multi-source Verification CAG", "status": "running"}

@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Check facts using Multi-source Verification CAG"""
    try:
        cag_request = CAGRequest(query=request.query, context_limit=request.top_k)
        result = await checker.process(cag_request)
        return QueryResponse(
            query=request.query, response=result.answer,
            context=[{"content": c.content, "relevance": c.relevance_score, "source": c.source} for c in result.context_chunks],
            metadata=result.metadata,
            process_steps=[{"step": s.step_name, "description": s.description, "duration": s.duration_ms} for s in checker.process_steps]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
