"""
Prompt Engineering Tutor Backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient
from cag_engine.base import CAGRequest
from prompt_tutor_rag import PromptTutorCAG

app = FastAPI(title="Prompt Engineering Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Client and CAG Technique
ollama_client = OllamaClient(host="http://localhost:11434")
tutor = PromptTutorCAG(ollama_client)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response: str
    context: list
    metadata: dict
    process_steps: list

@app.get("/")
async def root():
    return {
        "app": "Prompt Engineering Tutor",
        "technique": "Pedagogical Scaffolding CAG",
        "status": "running"
    }

@app.post("/learn", response_model=QueryResponse)
async def learn_prompting(request: QueryRequest):
    """Learn prompt engineering techniques."""
    try:
        cag_request = CAGRequest(query=request.query)
        result = await tutor.process(cag_request)
        
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
            } for s in tutor.process_steps]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8014)
