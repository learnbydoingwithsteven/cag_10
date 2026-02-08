
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add shared path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from cag_engine.ollama_client import OllamaClient
from agent_engine import AgenticCAG

app = FastAPI(title="Agentic Research Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Client and Agent
ollama_client = OllamaClient(host="http://localhost:11434")
agent = AgenticCAG(ollama_client)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str
    steps: list
    critique: dict

@app.get("/")
async def root():
    return {"app": "Agentic Research Assistant", "status": "running"}

@app.post("/research", response_model=QueryResponse)
async def research(request: QueryRequest):
    try:
        result = await agent.run(request.query)
        return QueryResponse(
            query=request.query,
            answer=result["answer"],
            steps=result["steps"],
            critique=result["critique"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
