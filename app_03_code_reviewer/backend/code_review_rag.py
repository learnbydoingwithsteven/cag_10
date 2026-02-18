"""
Code Review Bot - CAG Technique: AST-aware Code Quality CAG
"""
import sys
import os
from typing import List, Dict, Any, Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.base import CAGTechnique, CAGRequest, ContextChunk
from cag_engine.ollama_client import OllamaClient


def select_best_model(ollama_client):
    """Dynamic model selection - pick best available LOCAL chat model."""
    try:
        available_models = ollama_client.list_models()
        embedding_keywords = ["embed", "nomic-embed", "bge", "e5"]
        chat_models = [
            m for m in available_models
            if not any(kw in m.lower() for kw in embedding_keywords)
            and ":cloud" not in m.lower()
        ]
        preferred = ["codellama", "llama3", "qwen2.5", "qwen2", "mistral",
                      "gemma", "llama2", "tinyllama", "phi"]
        for pref in preferred:
            for m in chat_models:
                if pref in m.lower():
                    return m
        return chat_models[0] if chat_models else (available_models[0] if available_models else "llama3")
    except Exception:
        return "llama3"


class CodeReviewCAG(CAGTechnique):
    def __init__(self, ollama_client):
        selected_model = select_best_model(ollama_client)
        print(f"Code Review Bot selected model: {selected_model}")
        ollama_client.model = selected_model
        super().__init__("AST-aware Code Quality CAG", {"model": selected_model})
        self.ollama_client = ollama_client
        
        # Code review knowledge base with best practices and patterns
        self.knowledge_base = [
            {"content": "Security: Never store secrets (API keys, passwords) in source code. Use environment variables or secret managers like AWS Secrets Manager or HashiCorp Vault.", "source": "security_secrets", "category": "security", "relevance": 0.95},
            {"content": "Security: Always validate and sanitize user input to prevent SQL injection, XSS, and command injection attacks. Use parameterized queries for database operations.", "source": "security_input", "category": "security", "relevance": 0.95},
            {"content": "Performance: Avoid N+1 query problems in ORMs. Use eager loading (prefetch_related, select_related in Django; include() in SQLAlchemy) for related objects.", "source": "perf_n_plus_one", "category": "performance", "relevance": 0.9},
            {"content": "Performance: Use caching strategically (Redis, Memcached) for expensive computations and frequent database queries. Set appropriate TTLs.", "source": "perf_caching", "category": "performance", "relevance": 0.85},
            {"content": "Style: Follow the Single Responsibility Principle — each function/class should do one thing well. Functions over 30 lines likely need refactoring.", "source": "style_srp", "category": "style", "relevance": 0.9},
            {"content": "Style: Use meaningful variable names. Avoid single-letter names except for loop counters. 'user_count' is better than 'n' or 'uc'.", "source": "style_naming", "category": "style", "relevance": 0.85},
            {"content": "Error handling: Never use bare except clauses. Always catch specific exceptions. Log the error with context before re-raising or returning an error response.", "source": "error_handling", "category": "best_practice", "relevance": 0.9},
            {"content": "Testing: Aim for at least 80% code coverage. Write unit tests for business logic, integration tests for API endpoints, and E2E tests for critical user flows.", "source": "testing", "category": "best_practice", "relevance": 0.85},
            {"content": "Python-specific: Use type hints for function signatures. Use dataclasses or Pydantic models for structured data. Prefer f-strings over .format() or % formatting.", "source": "python_best", "category": "language", "relevance": 0.85},
            {"content": "Code smell: Deeply nested conditionals (more than 3 levels) indicate the need for early returns, guard clauses, or strategy pattern refactoring.", "source": "smell_nesting", "category": "code_smell", "relevance": 0.9},
        ]

    async def retrieve_context(self, request: CAGRequest) -> List[ContextChunk]:
        """Retrieve relevant code review guidelines based on query."""
        chunks = []
        query_lower = request.query.lower()
        words = [w for w in query_lower.split() if len(w) > 3]
        
        for kb in self.knowledge_base:
            score = 0
            kb_lower = kb['content'].lower()
            match_count = sum(1 for word in words if word in kb_lower)
            
            if match_count > 0:
                score = kb['relevance'] + (match_count * 0.03)
            elif any(kw in query_lower for kw in ["code", "review", "check", "bug", "fix"]):
                score = 0.4
            
            if score > 0:
                chunks.append(ContextChunk(
                    content=kb['content'],
                    source=kb['source'],
                    relevance_score=min(score, 1.0),
                    metadata={"category": kb['category']}
                ))
        
        if not chunks:
            chunks = [ContextChunk(content=kb['content'], source=kb['source'], relevance_score=0.4)
                      for kb in self.knowledge_base[:4]]
        
        return sorted(chunks, key=lambda x: x.relevance_score, reverse=True)[:5]

    async def augment_context(self, request: CAGRequest, context_chunks: List[ContextChunk]) -> str:
        """Augment prompt with code review knowledge."""
        context_str = "\n".join([f"- [{c.source}] {c.content}" for c in context_chunks])
        
        return f"""You are a Senior Code Reviewer. Analyze the submitted code or question and provide a thorough review.

Code Review Guidelines (Context):
{context_str}

User's Code/Question:
{request.query}

Provide your review in this format:
1. **Summary**: One-line assessment
2. **Issues Found**: List each issue with severity (Critical/Warning/Info)
3. **Suggested Fixes**: Concrete code changes
4. **Best Practices**: Relevant tips
"""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        """Generate code review using Ollama."""
        return await self.ollama_client.generate(augmented_prompt)
