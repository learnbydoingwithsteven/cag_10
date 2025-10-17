"""
Medical Diagnosis Assistant Backend
Multi-hop reasoning with Neo4j knowledge graph
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient
from medical_multihop import MedicalMultiHopCAG

app = FastAPI(title="Medical Diagnosis Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize CAG system
ollama_client = OllamaClient(base_url="http://ollama:11434")
medical_cag = MedicalMultiHopCAG(
    ollama_client=ollama_client,
    neo4j_uri="bolt://neo4j:7687",
    neo4j_user="neo4j",
    neo4j_password="medical123"
)


class DiagnosisRequest(BaseModel):
    symptoms: str
    top_k: int = 5


class DiagnosisResponse(BaseModel):
    query: str
    diagnosis: str
    context: list
    metadata: dict
    process_steps: list


@app.get("/")
async def root():
    return {
        "app": "Medical Diagnosis Assistant",
        "technique": "Multi-hop Reasoning CAG",
        "status": "running"
    }


@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose(request: DiagnosisRequest):
    """
    Diagnose based on symptoms using multi-hop reasoning
    """
    try:
        result = medical_cag.process(request.symptoms, request.top_k)
        
        return DiagnosisResponse(
            query=result["query"],
            diagnosis=result["response"],
            context=result["context"],
            metadata=result["metadata"],
            process_steps=result["process_steps"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
