
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add shared path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from cag_engine.ollama_client import OllamaClient
from graph_engine import GraphEngine


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


app = FastAPI(title="GraphRAG Explorer API")

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
print(f"GraphRAG Explorer selected model: {selected_model}")
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
