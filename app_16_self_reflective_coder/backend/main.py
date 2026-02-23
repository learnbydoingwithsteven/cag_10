"""
Self-Reflective Code Generator Backend
Reflexion-based CAG
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient

app = FastAPI(title="Self-Reflective Code Generator API")

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
        "app": "Self-Reflective Code Generator",
        "technique": "Reflexion-based CAG",
        "status": "running"
    }

@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using Reflexion-based CAG"""
    try:
        process_steps = []
        context = []
        
        # Generation 1
        prompt_gen1 = f"You are an expert coder. Write code for the following query. Do not provide explanations, just code. Query: {request.query}"
        code_gen1 = ollama_client.generate(prompt=prompt_gen1, model="codellama")
        process_steps.append({"step": "initial_generation", "description": "Generated initial code draft"})
        context.append({"type": "initial_draft", "content": code_gen1, "relevance": 0.8})

        # Reflection
        prompt_ref = f"You are a code reviewer. Review the following code for potential bugs, inefficiencies, or missing logic. Provide a very brief critique.\nQuery: {request.query}\nCode: {code_gen1}"
        critique = ollama_client.generate(prompt=prompt_ref, model="codellama")
        process_steps.append({"step": "reflection", "description": "Generated code critique (Reflection)"})
        context.append({"type": "critique", "content": critique, "relevance": 1.0})

        # Refinement (Generation 2)
        prompt_gen2 = f"You are an expert coder. Rewrite the code using the reviewer's critique. Provide the final updated code.\nQuery: {request.query}\nOriginal Code:\n{code_gen1}\nCritique:\n{critique}"
        final_code = ollama_client.generate(prompt=prompt_gen2, model="codellama")
        process_steps.append({"step": "refinement", "description": "Generated refined code based on critique"})
        context.append({"type": "final_code", "content": final_code, "relevance": 1.0})

        return QueryResponse(
            query=request.query,
            response=final_code,
            context=context,
            metadata={"model": "codellama", "technique": "Reflexion-based CAG"},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8016)
