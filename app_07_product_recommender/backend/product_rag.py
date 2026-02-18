"""
Product Recommender - CAG Technique: Hybrid Collaborative + Content CAG
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

class ProductRecommenderCAG(CAGTechnique):
    def __init__(self, ollama_client):
        model = select_best_model(ollama_client)
        print(f"Product Recommender selected model: {model}")
        ollama_client.model = model
        super().__init__("Hybrid Collaborative-Content CAG", {"model": model})
        self.ollama_client = ollama_client
        self.knowledge_base = [
            {"content": "Collaborative Filtering: Users who bought X also bought Y. Based on user-item interaction matrix. Cold-start problem for new users/items.", "source": "collab_filtering", "category": "technique", "relevance": 0.95},
            {"content": "Content-Based Filtering: Recommend items similar to what user liked before. Uses item features (category, brand, price range, description embeddings).", "source": "content_filtering", "category": "technique", "relevance": 0.95},
            {"content": "Hybrid Approach: Combine collaborative and content signals. Weighted hybrid: score = α*collab + (1-α)*content. Switch hybrid: use collab when data available, content otherwise.", "source": "hybrid", "category": "technique", "relevance": 0.9},
            {"content": "Product Catalog: Electronics (laptops, phones, accessories), Clothing (casual, formal, sportswear), Home (furniture, kitchen, decor), Books (fiction, non-fiction, technical).", "source": "catalog", "category": "data", "relevance": 0.85},
            {"content": "User Segments: Budget-conscious (<$50 avg), Mid-range ($50-200), Premium (>$200). Frequency: Daily browsers, Weekly shoppers, Seasonal buyers.", "source": "segments", "category": "data", "relevance": 0.85},
            {"content": "Recommendation Explanation: Always explain WHY an item is recommended. 'Because you bought X', 'Popular in your area', 'Trending this week' improve click-through by 30%.", "source": "explainability", "category": "ux", "relevance": 0.9},
            {"content": "Diversity & Serendipity: Don't just recommend similar items. Mix in 20% exploration items from adjacent categories to avoid filter bubbles.", "source": "diversity", "category": "quality", "relevance": 0.85},
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
            elif any(kw in query_lower for kw in ["recommend","product","buy","similar","suggest"]): score = 0.4
            if score > 0:
                chunks.append(ContextChunk(content=kb['content'], source=kb['source'], relevance_score=min(score,1.0), metadata={"category": kb['category']}))
        if not chunks:
            chunks = [ContextChunk(content=kb['content'], source=kb['source'], relevance_score=0.4) for kb in self.knowledge_base[:3]]
        return sorted(chunks, key=lambda x: x.relevance_score, reverse=True)[:5]

    async def augment_context(self, request: CAGRequest, context_chunks: List[ContextChunk]) -> str:
        context_str = "\n".join([f"- [{c.source}] {c.content}" for c in context_chunks])
        return f"""You are a Product Recommendation Engine. Recommend products based on user preferences and behavior patterns.

Recommendation Knowledge:
{context_str}

User Request: {request.query}

Provide 3-5 specific product recommendations with explanations for each. Include category, price range, and why it's recommended."""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        return await self.ollama_client.generate(augmented_prompt)
