"""
Git Sync Expert CAG Technique
"""
import sys
import os
from typing import List, Dict, Any, Tuple

# Add shared path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.base import CAGTechnique, CAGRequest, ContextChunk
from cag_engine.ollama_client import OllamaClient

class GitSyncCAG(CAGTechnique):
    def __init__(self, ollama_client):
        # Dynamic Model Selection - pick best available LOCAL chat model
        try:
            available_models = ollama_client.list_models()
            
            # Filter out embedding-only models and cloud-only models
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
            
            # Fallback: use first available chat model, or first model at all
            if not selected_model:
                selected_model = chat_models[0] if chat_models else (available_models[0] if available_models else "llama3")
            
            print(f"Git Sync Assistant selected model: {selected_model}")
            ollama_client.model = selected_model
        except Exception as e:
            print(f"Warning: Could not list models, using default. Error: {e}")
            selected_model = "llama3"

        super().__init__("Git Sync Expert", {"model": selected_model})
        self.ollama_client = ollama_client
        self.knowledge_base = [
            {"content": "To synchronize your local repository with a remote repository, use `git pull origin <branch_name>` to fetch and merge changes.", "source": "git_basics", "relevance": 0.95},
            {"content": "If you have uncommitted changes that conflict with the pull, consider stashing them with `git stash` before pulling.", "source": "git_workflow", "relevance": 0.9},
            {"content": "To push your committed changes to the remote repository, use `git push origin <branch_name>`. If the push is rejected, you may need to pull first.", "source": "git_pushing", "relevance": 0.95},
            {"content": "Resolve merge conflicts by manually editing the files to choose between current and incoming changes, then `git add` and `git commit` to finalize the merge.", "source": "conflict_resolution", "relevance": 0.85},
            {"content": "Check the status of your working directory using `git status` to see staged, unstaged, and untracked files.", "source": "status_check", "relevance": 0.9},
            {"content": "Use `git fetch` to download objects and refs from another repository without merging.", "source": "git_fetch", "relevance": 0.8},
            {"content": "Use `git rebase` to reapply commits on top of another base tip.", "source": "git_rebase", "relevance": 0.85}
        ]

    async def retrieve_context(self, request: CAGRequest) -> List[ContextChunk]:
        """Simple keyword matching for relevant git knowledge."""
        chunks = []
        query_lower = request.query.lower()
        
        # Simple relevance scoring based on keywords
        words = query_lower.split()
        for kb in self.knowledge_base:
            score = 0
            kb_content_lower = kb['content'].lower()
            match_count = sum(1 for word in words if word in kb_content_lower and len(word) > 3)
            
            if match_count > 0:
                score = kb['relevance'] + (match_count * 0.05)
            elif "git" in query_lower:
                score = 0.5 # Default low relevance if general git query
            
            if score > 0:
                chunks.append(ContextChunk(
                    content=kb['content'],
                    source=kb['source'],
                    relevance_score=min(score, 1.0)
                ))
        
        # Fallback if no specific matches found
        if not chunks:
            chunks = [ContextChunk(content=kb['content'], source=kb['source'], relevance_score=0.4) 
                      for kb in self.knowledge_base[:3]]
            
        return sorted(chunks, key=lambda x: x.relevance_score, reverse=True)[:5]

    async def augment_context(self, request: CAGRequest, context_chunks: List[ContextChunk]) -> str:
        """Augment the prompt with retrieved git knowledge."""
        context_str = "\n".join([f"- {c.content} (Source: {c.source})" for c in context_chunks])
        
        return f"""You are a Git Expert Assistant. Your goal is to help the user understand git operations and resolve synchronization issues.

Context from Knowledge Base:
{context_str}

User Query: {request.query}

Please provide a clear, step-by-step explanation and the exact git commands to run. Format commands inside code blocks.
"""

    async def generate_response(self, augmented_prompt: str, request: CAGRequest) -> Tuple[str, Dict[str, int]]:
        """Generate response using Ollama."""
        return await self.ollama_client.generate(augmented_prompt)
