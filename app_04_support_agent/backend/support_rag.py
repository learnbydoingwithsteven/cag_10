"""
Customer Support Agent - CAG Technique: Conversational Memory CAG
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

class SupportAgentCAG(CAGTechnique):
    def __init__(self, ollama_client):
        model = select_best_model(ollama_client)
        print(f"Support Agent selected model: {model}")
        ollama_client.model = model
        super().__init__("Conversational Memory CAG", {"model": model})
        self.ollama_client = ollama_client
        self.knowledge_base = [
            {"content": "Password Reset: Guide user to Settings > Security > Reset Password. If locked out, verify identity via email OTP, then issue temporary password valid for 24h.", "source": "kb_password", "category": "account", "relevance": 0.95},
            {"content": "Billing Issues: Check subscription status in admin panel. Common issues: expired card, duplicate charges (refund within 48h), plan downgrade takes effect at billing cycle end.", "source": "kb_billing", "category": "billing", "relevance": 0.9},
            {"content": "Shipping Delays: Standard 3-5 business days, Express 1-2 days. If delayed >7 days, escalate to logistics team. Offer tracking link and $5 credit for inconvenience.", "source": "kb_shipping", "category": "shipping", "relevance": 0.9},
            {"content": "Return Policy: 30-day returns for unused items in original packaging. Electronics have 15-day window. Initiate return via Order History > Return Item.", "source": "kb_returns", "category": "returns", "relevance": 0.85},
            {"content": "Technical Support: For app crashes, ask for OS version, app version, and steps to reproduce. Clear cache first. If persists, collect logs and escalate to engineering.", "source": "kb_tech", "category": "technical", "relevance": 0.85},
            {"content": "Tone Guidelines: Always be empathetic. Acknowledge the customer's frustration. Use 'I understand' and 'I'm happy to help'. Never blame the customer.", "source": "kb_tone", "category": "guidelines", "relevance": 0.8},
            {"content": "Escalation Policy: Escalate to Tier 2 if: issue unresolved after 3 interactions, customer requests manager, security breach suspected, or legal threat received.", "source": "kb_escalation", "category": "guidelines", "relevance": 0.85},
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
            elif any(kw in query_lower for kw in ["help","support","issue","problem"]): score = 0.4
            if score > 0:
                chunks.append(ContextChunk(content=kb['content'], source=kb['source'], relevance_score=min(score,1.0), metadata={"category": kb['category']}))
        if not chunks:
            chunks = [ContextChunk(content=kb['content'], source=kb['source'], relevance_score=0.4) for kb in self.knowledge_base[:3]]
        return sorted(chunks, key=lambda x: x.relevance_score, reverse=True)[:5]

    async def augment_context(self, request: CAGRequest, context_chunks: List[ContextChunk]) -> str:
        context_str = "\n".join([f"- [{c.source}] {c.content}" for c in context_chunks])
        return f"""You are a friendly Customer Support Agent. Help the customer with their issue using the knowledge base.

Knowledge Base:
{context_str}

Customer's Message: {request.query}

Respond with empathy and provide step-by-step solutions. If you cannot resolve, explain the escalation process."""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        return await self.ollama_client.generate(augmented_prompt)
