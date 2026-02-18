"""
Financial Report Analyzer - CAG Technique: Structured Data CAG
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

class FinancialCAG(CAGTechnique):
    def __init__(self, ollama_client):
        model = select_best_model(ollama_client)
        print(f"Financial Analyzer selected model: {model}")
        ollama_client.model = model
        super().__init__("Structured Data CAG", {"model": model})
        self.ollama_client = ollama_client
        self.knowledge_base = [
            {"content": "Revenue Analysis: Compare YoY and QoQ growth rates. Revenue CAGR = (End/Start)^(1/years) - 1. Flag if growth rate deviates >20% from industry average.", "source": "revenue_analysis", "category": "metrics", "relevance": 0.95},
            {"content": "Profit Margins: Gross Margin = (Revenue - COGS)/Revenue. Operating Margin = EBIT/Revenue. Net Margin = Net Income/Revenue. Healthy SaaS gross margins are 70-85%.", "source": "profit_margins", "category": "metrics", "relevance": 0.95},
            {"content": "Liquidity Ratios: Current Ratio = Current Assets/Current Liabilities (healthy >1.5). Quick Ratio excludes inventory. Cash Ratio is most conservative.", "source": "liquidity", "category": "ratios", "relevance": 0.9},
            {"content": "Debt Analysis: Debt-to-Equity = Total Debt/Shareholders Equity. Interest Coverage = EBIT/Interest Expense. High leverage >3x D/E is risky.", "source": "debt_analysis", "category": "ratios", "relevance": 0.9},
            {"content": "Cash Flow: Operating Cash Flow should exceed Net Income (quality of earnings). Free Cash Flow = OCF - CapEx. Negative FCF may indicate heavy investment or trouble.", "source": "cash_flow", "category": "cash", "relevance": 0.9},
            {"content": "Valuation: P/E Ratio = Price/EPS. P/S = Market Cap/Revenue. EV/EBITDA is preferred for comparing companies with different capital structures.", "source": "valuation", "category": "valuation", "relevance": 0.85},
            {"content": "Red Flags: Watch for revenue recognition changes, growing receivables faster than revenue, declining operating margins, frequent one-time charges, and auditor changes.", "source": "red_flags", "category": "risk", "relevance": 0.9},
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
            elif any(kw in query_lower for kw in ["financial","revenue","profit","report","analysis"]): score = 0.4
            if score > 0:
                chunks.append(ContextChunk(content=kb['content'], source=kb['source'], relevance_score=min(score,1.0), metadata={"category": kb['category']}))
        if not chunks:
            chunks = [ContextChunk(content=kb['content'], source=kb['source'], relevance_score=0.4) for kb in self.knowledge_base[:3]]
        return sorted(chunks, key=lambda x: x.relevance_score, reverse=True)[:5]

    async def augment_context(self, request: CAGRequest, context_chunks: List[ContextChunk]) -> str:
        context_str = "\n".join([f"- [{c.source}] {c.content}" for c in context_chunks])
        return f"""You are a Financial Analyst. Analyze the financial data or question using the reference material.

Financial Reference Material:
{context_str}

User Query: {request.query}

Provide analysis with specific metrics, ratios, and actionable insights. Use tables where appropriate."""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        return await self.ollama_client.generate(augmented_prompt)
