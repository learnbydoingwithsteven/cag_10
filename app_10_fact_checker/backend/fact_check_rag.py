"""
Fact Checker - CAG Technique: Multi-source Verification CAG
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

class FactCheckerCAG(CAGTechnique):
    def __init__(self, ollama_client):
        model = select_best_model(ollama_client)
        print(f"Fact Checker selected model: {model}")
        ollama_client.model = model
        super().__init__("Multi-source Verification CAG", {"model": model})
        self.ollama_client = ollama_client
        self.knowledge_base = [
            {"content": "Claim Decomposition: Break complex claims into atomic, verifiable sub-claims. 'X causes Y in Z% of cases' has 3 checkable parts: causation, direction, and magnitude.", "source": "claim_decomposition", "category": "methodology", "relevance": 0.95},
            {"content": "Source Reliability Tiers: Tier 1 (peer-reviewed journals, official statistics), Tier 2 (major news agencies, government reports), Tier 3 (blogs, social media, opinion pieces).", "source": "source_tiers", "category": "methodology", "relevance": 0.95},
            {"content": "Logical Fallacies: Watch for correlation≠causation, cherry-picking data, appeal to authority, straw man arguments, and false equivalence in claims.", "source": "logical_fallacies", "category": "analysis", "relevance": 0.9},
            {"content": "Statistical Verification: Check sample size, confidence intervals, p-values. Beware of: base rate neglect, Simpson's paradox, selection bias, and survivorship bias.", "source": "statistics", "category": "analysis", "relevance": 0.9},
            {"content": "Verdict Scale: TRUE (supported by multiple reliable sources), MOSTLY TRUE (accurate but needs context), HALF TRUE (partially accurate), MOSTLY FALSE (significant errors), FALSE (contradicted by evidence), UNVERIFIABLE (insufficient evidence).", "source": "verdict_scale", "category": "output", "relevance": 0.95},
            {"content": "Cross-Reference: A claim is stronger when independently verified by 3+ sources from different organizations. Conflicting sources require noting the disagreement.", "source": "cross_reference", "category": "methodology", "relevance": 0.9},
            {"content": "Temporal Context: Check if statistics or claims are outdated. Data from 2015 may not reflect 2024 reality. Always note the recency of evidence.", "source": "temporal", "category": "context", "relevance": 0.85},
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
            elif any(kw in query_lower for kw in ["fact","check","true","false","claim","verify"]): score = 0.4
            if score > 0:
                chunks.append(ContextChunk(content=kb['content'], source=kb['source'], relevance_score=min(score,1.0), metadata={"category": kb['category']}))
        if not chunks:
            chunks = [ContextChunk(content=kb['content'], source=kb['source'], relevance_score=0.4) for kb in self.knowledge_base[:3]]
        return sorted(chunks, key=lambda x: x.relevance_score, reverse=True)[:5]

    async def augment_context(self, request: CAGRequest, context_chunks: List[ContextChunk]) -> str:
        context_str = "\n".join([f"- [{c.source}] {c.content}" for c in context_chunks])
        return f"""You are a Fact Checker. Analyze the claim systematically using the verification framework.

Fact-Checking Framework:
{context_str}

Claim to Verify: {request.query}

Provide:
1. **Claim Decomposition**: Break into verifiable sub-claims
2. **Evidence Assessment**: What supports or contradicts each sub-claim
3. **Source Quality**: Rate the reliability of available evidence
4. **Verdict**: TRUE / MOSTLY TRUE / HALF TRUE / MOSTLY FALSE / FALSE / UNVERIFIABLE
5. **Confidence**: How confident you are in the verdict (High/Medium/Low)"""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        return await self.ollama_client.generate(augmented_prompt)
