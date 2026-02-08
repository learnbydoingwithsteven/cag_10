
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add shared path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from cag_engine.ollama_client import OllamaClient
from graph_engine import GraphEngine

app = FastAPI(title="GraphRAG Explorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_client = OllamaClient(host="http://localhost:11434")
graph = GraphEngine(ollama_client)

class TextQuery(BaseModel):
    text: str

class GraphResponse(BaseModel):
    triples: list
    message: str

@app.get("/")
async def root():
    return {"app": "GraphRAG Explorer", "version": "1.0.0"}

@app.post("/extract")
async def extract_graph(request: TextQuery):
    try:
        result = await graph.extract_knowledge(request.text)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph")
async def get_graph():
    return graph.get_graph_data()

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
