"""
Educational Tutor - CAG Technique: Adaptive Difficulty CAG
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

class EducationalTutorCAG(CAGTechnique):
    def __init__(self, ollama_client):
        model = select_best_model(ollama_client)
        print(f"Educational Tutor selected model: {model}")
        ollama_client.model = model
        super().__init__("Adaptive Difficulty CAG", {"model": model})
        self.ollama_client = ollama_client
        self.knowledge_base = [
            {"content": "Bloom's Taxonomy Levels: Remember → Understand → Apply → Analyze → Evaluate → Create. Adapt questions to match student's current level.", "source": "blooms_taxonomy", "category": "pedagogy", "relevance": 0.95},
            {"content": "Scaffolding: Break complex concepts into smaller, manageable steps. Provide hints before full answers. Gradually remove support as student demonstrates mastery.", "source": "scaffolding", "category": "pedagogy", "relevance": 0.95},
            {"content": "Formative Assessment: Use quick checks (multiple choice, fill-in-blank) to gauge understanding before moving on. Misconceptions caught early are easier to correct.", "source": "assessment", "category": "methodology", "relevance": 0.9},
            {"content": "Spaced Repetition: Review material at increasing intervals (1 day, 3 days, 7 days, 14 days). Active recall is more effective than re-reading.", "source": "spaced_repetition", "category": "methodology", "relevance": 0.9},
            {"content": "Analogies & Examples: Connect new concepts to what students already know. Use concrete examples before abstract formulas. Multiple representations (visual, verbal, symbolic) aid understanding.", "source": "analogies", "category": "teaching", "relevance": 0.9},
            {"content": "Growth Mindset: Praise effort over intelligence. Frame mistakes as learning opportunities. 'You haven't mastered this yet' vs 'You can't do this'.", "source": "growth_mindset", "category": "motivation", "relevance": 0.85},
            {"content": "Subject Areas: Mathematics (algebra, calculus, statistics), Science (physics, chemistry, biology), Programming (Python, algorithms, data structures), Language (grammar, writing).", "source": "subjects", "category": "content", "relevance": 0.8},
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
            elif any(kw in query_lower for kw in ["learn","teach","explain","understand","help"]): score = 0.4
            if score > 0:
                chunks.append(ContextChunk(content=kb['content'], source=kb['source'], relevance_score=min(score,1.0), metadata={"category": kb['category']}))
        if not chunks:
            chunks = [ContextChunk(content=kb['content'], source=kb['source'], relevance_score=0.4) for kb in self.knowledge_base[:3]]
        return sorted(chunks, key=lambda x: x.relevance_score, reverse=True)[:5]

    async def augment_context(self, request: CAGRequest, context_chunks: List[ContextChunk]) -> str:
        context_str = "\n".join([f"- [{c.source}] {c.content}" for c in context_chunks])
        return f"""You are an Adaptive Educational Tutor. Teach the concept using scaffolding and appropriate difficulty level.

Teaching Guidelines:
{context_str}

Student's Question: {request.query}

Respond as a patient tutor: explain the concept, give an example, then provide a practice problem. Adjust complexity based on how the question is phrased."""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        return await self.ollama_client.generate(augmented_prompt)
