"""
Research Paper Summarizer - CAG Technique: Hierarchical Summarization CAG
"""
import sys, os
from typing import List, Dict, Any, Tuple
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from cag_engine.base import CAGTechnique, CAGRequest, ContextChunk
from cag_engine.ollama_client import OllamaClient

def select_best_model(ollama_client):
    try:
        available = ollama_client.list_models()
        chat = [m for m in available if not any(kw in m.lower() for kw in ["embed","nomic-embed","bge","e5"]) and ":cloud" not in m.lower()]
        for pref in ["llama3","qwen2.5","qwen2","mistral","gemma","tinyllama","phi"]:
            for m in chat:
                if pref in m.lower(): return m
        return chat[0] if chat else (available[0] if available else "llama3")
    except: return "llama3"

class PaperSummarizerCAG(CAGTechnique):
    def __init__(self, ollama_client):
        model = select_best_model(ollama_client)
        print(f"Paper Summarizer selected model: {model}")
        ollama_client.model = model
        super().__init__("Hierarchical Summarization CAG", {"model": model})
        self.ollama_client = ollama_client
        self.knowledge_base = [
            {"content": "Abstract Extraction: The abstract contains the paper's main contribution, methodology, and key results. Extract claim, evidence, and significance.", "source": "abstract_guide", "category": "structure", "relevance": 0.95},
            {"content": "Methodology Summary: Identify the experimental setup, datasets used, baselines compared, and evaluation metrics. Note any novel architectural choices.", "source": "methodology_guide", "category": "structure", "relevance": 0.95},
            {"content": "Results Interpretation: Focus on the main results table. Note improvements over baselines (absolute and relative). Check if improvements are statistically significant.", "source": "results_guide", "category": "analysis", "relevance": 0.9},
            {"content": "Citation Context: Key citations indicate related work and positioning. 'In contrast to [X]' shows differentiation. 'Building upon [Y]' shows foundation.", "source": "citation_guide", "category": "context", "relevance": 0.85},
            {"content": "Limitations & Future Work: Authors often understate limitations. Check assumptions, dataset biases, computational costs, and failure cases explicitly.", "source": "limitations_guide", "category": "critical", "relevance": 0.9},
            {"content": "Hierarchical Summary Levels: L1=One sentence (<25 words), L2=Key findings paragraph, L3=Detailed section-by-section, L4=Full critical analysis.", "source": "hierarchy_guide", "category": "format", "relevance": 0.9},
            {"content": "Reproducibility Check: Note if code is available, hyperparameters specified, random seeds set, and compute requirements stated.", "source": "reproducibility", "category": "quality", "relevance": 0.85},
        ]

    async def retrieve_context(self, request: CAGRequest) -> List[ContextChunk]:
        chunks = []
        query_lower = request.query.lower()
        words = [w for w in query_lower.split() if len(w) > 3]
        for kb in self.knowledge_base:
            score = 0
            kb_lower = kb['content'].lower()
            match_count = sum(1 for w in words if w in kb_lower)
            if match_count > 0: score = kb['relevance'] + (match_count * 0.03)
            elif any(kw in query_lower for kw in ["paper","research","summary","abstract","results"]): score = 0.4
            if score > 0:
                chunks.append(ContextChunk(content=kb['content'], source=kb['source'], relevance_score=min(score,1.0), metadata={"category": kb['category']}))
        if not chunks:
            chunks = [ContextChunk(content=kb['content'], source=kb['source'], relevance_score=0.4) for kb in self.knowledge_base[:3]]
        return sorted(chunks, key=lambda x: x.relevance_score, reverse=True)[:5]

    async def augment_context(self, request: CAGRequest, context_chunks: List[ContextChunk]) -> str:
        context_str = "\n".join([f"- [{c.source}] {c.content}" for c in context_chunks])
        return f"""You are a Research Paper Summarizer. Provide a hierarchical summary of the paper or answer the question about academic papers.

Summarization Guidelines:
{context_str}

User Input: {request.query}

Provide a multi-level summary: 1-sentence TL;DR, key findings, methodology overview, and critical assessment."""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        return await self.ollama_client.generate(augmented_prompt)
