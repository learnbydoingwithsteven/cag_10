"""
Prompt Engineering Tutor - CAG Technique: Pedagogical Scaffolding CAG
"""
import sys
import os
from typing import List, Dict, Any, Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.base import CAGTechnique, CAGRequest, ContextChunk
from cag_engine.ollama_client import OllamaClient


class PromptTutorCAG(CAGTechnique):
    def __init__(self, ollama_client):
        # Dynamic Model Selection - pick best available LOCAL chat model
        try:
            available_models = ollama_client.list_models()
            embedding_keywords = ["embed", "nomic-embed", "bge", "e5"]
            chat_models = [
                m for m in available_models
                if not any(kw in m.lower() for kw in embedding_keywords)
                and ":cloud" not in m.lower()
            ]
            print(f"Available chat models: {chat_models}")
            
            preferred_order = ["llama3", "qwen2.5", "qwen2", "mistral", "codellama",
                               "gemma", "llama2", "tinyllama", "phi"]
            selected_model = None
            for pref in preferred_order:
                for m in chat_models:
                    if pref in m.lower():
                        selected_model = m
                        break
                if selected_model:
                    break
            if not selected_model:
                selected_model = chat_models[0] if chat_models else (available_models[0] if available_models else "llama3")
            
            print(f"Prompt Tutor selected model: {selected_model}")
            ollama_client.model = selected_model
        except Exception as e:
            print(f"Warning: Could not list models. Error: {e}")
            selected_model = "llama3"

        super().__init__("Prompt Engineering Tutor", {"model": selected_model})
        self.ollama_client = ollama_client
        
        # Comprehensive prompt engineering knowledge base
        self.knowledge_base = [
            # Core Techniques
            {"content": "Zero-shot prompting: Give the model a task with no examples. Works well for simple, well-defined tasks. Example: 'Classify the following text as positive or negative: ...'", "source": "zero_shot", "category": "technique", "relevance": 0.9},
            {"content": "Few-shot prompting: Provide 2-5 examples before the actual task. This helps the model understand the pattern and desired output format. Always keep examples consistent in format.", "source": "few_shot", "category": "technique", "relevance": 0.95},
            {"content": "Chain-of-Thought (CoT): Add 'Let's think step by step' or provide reasoning examples. This dramatically improves performance on math, logic, and multi-step problems.", "source": "chain_of_thought", "category": "technique", "relevance": 0.95},
            {"content": "Role prompting: Start with 'You are a [role]' to set context and expertise level. Example: 'You are a senior Python developer. Review this code for security issues.'", "source": "role_prompting", "category": "technique", "relevance": 0.9},
            {"content": "Structured output: Request specific formats like JSON, markdown tables, or bullet points. Include a schema or example of desired output structure.", "source": "structured_output", "category": "technique", "relevance": 0.85},
            # Best Practices
            {"content": "Be specific and explicit: Instead of 'Write about dogs', say 'Write a 200-word informative paragraph about the health benefits of adopting rescue dogs, aimed at families with young children.'", "source": "specificity", "category": "best_practice", "relevance": 0.9},
            {"content": "Use delimiters: Separate instructions from content using triple quotes, XML tags, or markdown. This prevents prompt injection and clarifies structure.", "source": "delimiters", "category": "best_practice", "relevance": 0.85},
            {"content": "Iterative refinement: Start simple, test, then add constraints. Don't try to write the perfect prompt on the first attempt. Each iteration should address a specific weakness.", "source": "iteration", "category": "best_practice", "relevance": 0.8},
            # Anti-patterns
            {"content": "Anti-pattern: Vague instructions like 'Make it better' or 'Improve this'. Always specify WHAT to improve and HOW. Provide evaluation criteria.", "source": "anti_vague", "category": "anti_pattern", "relevance": 0.85},
            {"content": "Anti-pattern: Overloading a single prompt with too many tasks. Break complex tasks into sequential prompts, each with a clear objective.", "source": "anti_overload", "category": "anti_pattern", "relevance": 0.8},
            # Advanced
            {"content": "Self-consistency: Generate multiple responses and pick the most common answer. Useful for reasoning tasks where you need higher reliability.", "source": "self_consistency", "category": "advanced", "relevance": 0.85},
            {"content": "ReAct pattern: Combine Reasoning and Acting. The model thinks about what to do, takes an action (like search), observes the result, and repeats until done.", "source": "react", "category": "advanced", "relevance": 0.9},
        ]

    async def retrieve_context(self, request: CAGRequest) -> List[ContextChunk]:
        """Retrieve relevant prompt engineering knowledge based on query."""
        chunks = []
        query_lower = request.query.lower()
        words = [w for w in query_lower.split() if len(w) > 3]
        
        for kb in self.knowledge_base:
            score = 0
            kb_lower = kb['content'].lower()
            match_count = sum(1 for word in words if word in kb_lower)
            
            if match_count > 0:
                score = kb['relevance'] + (match_count * 0.03)
            elif any(kw in query_lower for kw in ["prompt", "llm", "gpt", "model", "technique"]):
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
        """Create a pedagogical prompt with scaffolding."""
        context_str = "\n".join([f"- [{c.source}] {c.content}" for c in context_chunks])
        
        return f"""You are an expert Prompt Engineering Tutor. Your goal is to teach users how to write effective prompts for Large Language Models.

Use a pedagogical approach:
1. First explain the relevant concept(s)
2. Show a concrete "before" (bad prompt) and "after" (good prompt) example
3. Explain WHY the improvement works
4. Give the user a practice exercise

Reference Material:
{context_str}

Student's Question: {request.query}

Respond in a clear, encouraging, teacher-like tone. Use markdown formatting with headers and code blocks for prompt examples.
"""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        """Generate pedagogical response using Ollama."""
        return await self.ollama_client.generate(augmented_prompt)
