import os

APPS_DATA = {
    15: {
        "name": "multi_agent_debater",
        "title": "Multi-Agent Strategy Debater",
        "technique": "Multi-Agent Debate CAG",
        "model": "llama3",
        "port": 8015,
        "content": '''"""
Multi-Agent Strategy Debater Backend
Multi-Agent Debate CAG
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient

app = FastAPI(title="Multi-Agent Strategy Debater API")

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
        "app": "Multi-Agent Strategy Debater",
        "technique": "Multi-Agent Debate CAG",
        "status": "running"
    }

@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using Multi-Agent Debate CAG"""
    try:
        process_steps = []
        context = []
        
        # Persona 1: Optimist
        prompt_opt = f"You are an Optimist. Review this query and provide an unconditionally positive and ambitious perspective: {request.query}"
        resp_opt = ollama_client.generate(prompt=prompt_opt, model="llama3")
        process_steps.append({"step": "generation_optimist", "description": "Generated optimist perspective"})
        context.append({"type": "optimist_perspective", "content": resp_opt, "relevance": 1.0})

        # Persona 2: Pessimist
        prompt_pes = f"You are a Pessimist. Review this query and the optimist's perspective, then provide a critical, risk-averse, and cautious perspective. Query: {request.query}. Optimist: {resp_opt}"
        resp_pes = ollama_client.generate(prompt=prompt_pes, model="llama3")
        process_steps.append({"step": "generation_pessimist", "description": "Generated pessimist perspective"})
        context.append({"type": "pessimist_perspective", "content": resp_pes, "relevance": 1.0})

        # Persona 3: Analyst (Synthesizer)
        prompt_syn = f"You are an Analyst synthesising perspectives. Query: {request.query}\\nOptimist: {resp_opt}\\nPessimist: {resp_pes}\\nProvide a final, balanced strategy and conclusion."
        final_response = ollama_client.generate(prompt=prompt_syn, model="llama3")
        process_steps.append({"step": "generation_analyst", "description": "Generated synthesized analysis"})
        context.append({"type": "analyst_synthesis", "content": final_response, "relevance": 1.0})

        return QueryResponse(
            query=request.query,
            response=final_response,
            context=context,
            metadata={"model": "llama3", "technique": "Multi-Agent Debate CAG"},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
'''
    },
    16: {
        "name": "self_reflective_coder",
        "title": "Self-Reflective Code Generator",
        "technique": "Reflexion-based CAG",
        "model": "codellama",
        "port": 8016,
        "content": '''"""
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
        prompt_ref = f"You are a code reviewer. Review the following code for potential bugs, inefficiencies, or missing logic. Provide a very brief critique.\\nQuery: {request.query}\\nCode: {code_gen1}"
        critique = ollama_client.generate(prompt=prompt_ref, model="codellama")
        process_steps.append({"step": "reflection", "description": "Generated code critique (Reflection)"})
        context.append({"type": "critique", "content": critique, "relevance": 1.0})

        # Refinement (Generation 2)
        prompt_gen2 = f"You are an expert coder. Rewrite the code using the reviewer's critique. Provide the final updated code.\\nQuery: {request.query}\\nOriginal Code:\\n{code_gen1}\\nCritique:\\n{critique}"
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
'''
    },
    17: {
        "name": "tree_of_thoughts_solver",
        "port": 8017,
        "content": '''"""
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
        prompt_eval = f"Given the problem: '{request.query}', evaluate the merits and drawbacks of each approach proposed here:\\n{approaches}\\nIdentify the single best approach from the list."
        evaluation = ollama_client.generate(prompt=prompt_eval, model="llama3")
        process_steps.append({"step": "evaluation", "description": "Evaluated generated approaches"})
        context.append({"type": "evaluation", "content": evaluation, "relevance": 0.9})

        # Step 3: Detailed execution of the best approach
        prompt_exec = f"Based on the evaluation:\\n{evaluation}\\nProvide the final, detailed, step-by-step solution to the problem: '{request.query}' using the best approach identified."
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
'''
    },
    18: {
        "name": "dynamic_few_shot_writer",
        "port": 8018,
        "content": '''"""
Dynamic Few-Shot Copywriter Backend
Dynamic Context Selection CAG
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient

app = FastAPI(title="Dynamic Few-Shot Copywriter API")

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

# Simulated database of past successful marketing copy
PAST_COPY = [
    {"type": "SaaS", "copy": "Stop wrestling with spreadsheets. Simplify your workflows with our automation tool today!"},
    {"type": "Fitness", "copy": "Unleash your inner beast. Try our 30-day challenge and see real results."},
    {"type": "Finance", "copy": "Stop throwing money away! Start investing today and watch your wealth grow with zero hidden fees."},
    {"type": "Education", "copy": "Upskill on your schedule. Learn code from experts without breaking the bank."}
]

@app.get("/")
async def root():
    return {
        "app": "Dynamic Few-Shot Copywriter",
        "technique": "Dynamic Context Selection CAG",
        "status": "running"
    }

@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using Dynamic Context Selection CAG"""
    try:
        process_steps = []
        context = []
        
        # 1. Selection Step: Use an LLM call to pick the best related example, or simply pass all if small.
        # We will dynamically pick by having the LLM select the most relevant category.
        prompt_select = f"Which of the following categories best matches this query '{request.query}'? Categories: SaaS, Fitness, Finance, Education. Return ONLY the category name."
        category = ollama_client.generate(prompt=prompt_select, model="llama3").strip()
        
        selected_example = next((item for item in PAST_COPY if item["type"].lower() in category.lower()), PAST_COPY[0])
        
        process_steps.append({"step": "dynamic_selection", "description": f"Selected few-shot example for category: {category}"})
        context.append({"type": f"few_shot_example_{selected_example['type']}", "content": selected_example["copy"], "relevance": 0.95})

        # 2. Generation Step
        prompt_gen = f"""You are an expert copywriter. Write tight, punchy, high-converting copy for the following request.
Use the tone and structure of this successful past example: '{selected_example['copy']}'

Request: {request.query}
Copy:"""
        final_copy = ollama_client.generate(prompt=prompt_gen, model="llama3")
        process_steps.append({"step": "generation", "description": "Generated final copy using dynamic few-shot context"})

        return QueryResponse(
            query=request.query,
            response=final_copy,
            context=context,
            metadata={"model": "llama3", "technique": "Dynamic Context Selection CAG"},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018)
'''
    },
    19: {
        "name": "temporal_rag_forecaster",
        "port": 8019,
        "content": '''"""
Temporal Market Forecaster Backend
Temporal RAG CAG
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.ollama_client import OllamaClient

app = FastAPI(title="Temporal Market Forecaster API")

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

# Simulated database of temporally sensitive events
EVENTS = [
    {"date": "2023-01-10", "content": "Tech stocks slide as interest rate hike fears continue."},
    {"date": "2023-06-15", "content": "AI boom drives Nasdaq to 52-week highs."},
    {"date": "2023-11-01", "content": "Fed signals pause on rate hikes, market rallies."},
    {"date": "2024-02-20", "content": "Semiconductor earnings beat expectations, driving further AI speculation."}
]

@app.get("/")
async def root():
    return {
        "app": "Temporal Market Forecaster",
        "technique": "Temporal RAG CAG",
        "status": "running"
    }

@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process query using Temporal RAG CAG"""
    try:
        process_steps = []
        context = []
        
        # 1. Temporal Sorting/Retrieval Step
        # Sort events by date natively so the LLM sees the chronological timeline
        sorted_events = sorted(EVENTS, key=lambda x: x["date"])
        
        formatted_timeline = "\\n".join([f"[{e['date']}] {e['content']}" for e in sorted_events])
        
        process_steps.append({"step": "temporal_retrieval", "description": "Retrieved and chronologically ordered historical context"})
        for e in sorted_events:
            context.append({"type": "historical_event", "content": f"[{e['date']}] {e['content']}", "relevance": 1.0})

        # 2. Forecasting Generation Step
        prompt_gen = f"""You are a temporal market forecaster. 
Analyze the explicit chronological progression of the following historical timeline and forecast the next logical market trend relation to this query: '{request.query}'.
Make sure your answer explicitly references how the timeline builds up to your forecast.

Historical Timeline:
{formatted_timeline}

Forecast Analysis:"""
        
        forecast = ollama_client.generate(prompt=prompt_gen, model="llama3")
        process_steps.append({"step": "temporal_generation", "description": "Generated forecast from chronological timeline"})

        return QueryResponse(
            query=request.query,
            response=forecast,
            context=context,
            metadata={"model": "llama3", "technique": "Temporal RAG CAG"},
            process_steps=process_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8019)
'''
    }
}

base_dir = os.path.dirname(os.path.abspath(__file__))

for app_num, app_data in APPS_DATA.items():
    app_dir_name = f"app_{app_num:02d}_{app_data['name']}"
    file_path = os.path.join(base_dir, app_dir_name, "backend", "main.py")
    
    with open(file_path, "w") as f:
        f.write(app_data['content'])
        
    print(f"Updated {file_path}")

print("Successfully updated all 5 app backends!")
