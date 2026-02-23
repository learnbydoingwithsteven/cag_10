"""
Tree of Thoughts Problem Solver Backend
Tree of Thoughts (ToT) CAG
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient

app = FastAPI(title="Tree of Thoughts Problem Solver API")

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
        "app": "Tree of Thoughts Problem Solver",
        "technique": "Tree of Thoughts (ToT) CAG",
        "status": "running"
    }

@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using Tree of Thoughts (ToT) CAG"""
    try:
        process_steps = []
        context = []
        
        # Step 1: Brainstorming multiple approaches
        prompt_branch = f"You are a problem solver. Given the following problem, propose 3 distinctly different high-level approaches to solve it. Respond ONLY with a numbered list of the 3 approaches. Problem: {request.query}"
        approaches = ollama_client.generate(prompt=prompt_branch, model="llama3")
        process_steps.append({"step": "branching", "description": "Generated 3 possible approaches"})
        context.append({"type": "approaches", "content": approaches, "relevance": 0.8})

        # Step 2: Evaluating the approaches
        prompt_eval = f"Given the problem: '{request.query}', evaluate the merits and drawbacks of each approach proposed here:\n{approaches}\nIdentify the single best approach from the list."
        evaluation = ollama_client.generate(prompt=prompt_eval, model="llama3")
        process_steps.append({"step": "evaluation", "description": "Evaluated generated approaches"})
        context.append({"type": "evaluation", "content": evaluation, "relevance": 0.9})

        # Step 3: Detailed execution of the best approach
        prompt_exec = f"Based on the evaluation:\n{evaluation}\nProvide the final, detailed, step-by-step solution to the problem: '{request.query}' using the best approach identified."
        final_solution = ollama_client.generate(prompt=prompt_exec, model="llama3")
        process_steps.append({"step": "execution", "description": "Developed detailed final solution"})

        return QueryResponse(
            query=request.query,
            response=final_solution,
            context=context,
            metadata={"model": "llama3", "technique": "Tree of Thoughts (ToT) CAG"},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8017)
