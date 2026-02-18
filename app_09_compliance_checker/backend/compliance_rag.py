"""
Compliance Checker - CAG Technique: Rule-based Compliance CAG
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

class ComplianceCAG(CAGTechnique):
    def __init__(self, ollama_client):
        model = select_best_model(ollama_client)
        print(f"Compliance Checker selected model: {model}")
        ollama_client.model = model
        super().__init__("Rule-based Compliance CAG", {"model": model})
        self.ollama_client = ollama_client
        self.knowledge_base = [
            {"content": "GDPR Article 6: Processing is lawful only if consent given, contractual necessity, legal obligation, vital interests, public task, or legitimate interests. Must document legal basis.", "source": "gdpr_art6", "category": "gdpr", "relevance": 0.95},
            {"content": "GDPR Article 17: Right to Erasure ('Right to be Forgotten'). Data subject can request deletion when data no longer necessary, consent withdrawn, or unlawfully processed.", "source": "gdpr_art17", "category": "gdpr", "relevance": 0.9},
            {"content": "Data Retention: Personal data must not be kept longer than necessary. Define retention periods per data category. Implement automated deletion schedules.", "source": "data_retention", "category": "data", "relevance": 0.9},
            {"content": "Contract Clause: Force Majeure must specify covered events (natural disasters, pandemics, war). Notification period typically 30 days. Both parties' obligations during force majeure.", "source": "force_majeure", "category": "contract", "relevance": 0.85},
            {"content": "Contract Clause: Indemnification should specify scope (IP infringement, data breach, negligence), caps on liability, and whether it covers direct and indirect damages.", "source": "indemnification", "category": "contract", "relevance": 0.85},
            {"content": "SOX Compliance: Public companies must maintain internal controls over financial reporting. CEO/CFO certify accuracy. Material weaknesses must be disclosed.", "source": "sox", "category": "financial", "relevance": 0.9},
            {"content": "Risk Scoring: Critical (immediate action, regulatory penalty risk), High (action within 30 days), Medium (action within 90 days), Low (best practice recommendation).", "source": "risk_scoring", "category": "methodology", "relevance": 0.9},
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
            elif any(kw in query_lower for kw in ["compliance","gdpr","contract","legal","regulation"]): score = 0.4
            if score > 0:
                chunks.append(ContextChunk(content=kb['content'], source=kb['source'], relevance_score=min(score,1.0), metadata={"category": kb['category']}))
        if not chunks:
            chunks = [ContextChunk(content=kb['content'], source=kb['source'], relevance_score=0.4) for kb in self.knowledge_base[:3]]
        return sorted(chunks, key=lambda x: x.relevance_score, reverse=True)[:5]

    async def augment_context(self, request: CAGRequest, context_chunks: List[ContextChunk]) -> str:
        context_str = "\n".join([f"- [{c.source}] {c.content}" for c in context_chunks])
        return f"""You are a Compliance Analyst. Check the contract or scenario against regulatory requirements.

Compliance Rules & Guidelines:
{context_str}

Contract/Scenario to Check: {request.query}

Provide:
1. **Compliance Status**: Compliant / Non-Compliant / Partially Compliant
2. **Issues Found**: List each with risk level (Critical/High/Medium/Low)
3. **Remediation Steps**: Specific actions to achieve compliance
4. **Relevant Regulations**: Which rules apply"""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        return await self.ollama_client.generate(augmented_prompt)
