"""
Ollama client implementation for LLM operations.
"""

import ollama
from typing import List, Dict, Tuple, Any
import logging
from .base import LLMClient

logger = logging.getLogger(__name__)


class OllamaClient(LLMClient):
    """Client for interacting with Ollama models."""

    def __init__(
        self,
        model: str = "llama3",
        embedding_model: str = "nomic-embed-text",
        host: str = "http://localhost:11434"
    ):
        self.model = model
        self.embedding_model = embedding_model
        self.host = host
        self.client = ollama.Client(host=host)
        logger.info(f"Initialized Ollama client with model: {model}")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: str = None,
        **kwargs
    ) -> Tuple[str, Dict[str, int]]:
        """
        Generate text using Ollama.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            **kwargs: Additional Ollama parameters

        Returns:
            Tuple of (generated_text, token_usage)
        """
        try:
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    **kwargs
                }
            )

            generated_text = response['message']['content']
            
            # Extract token usage
            token_usage = {
                "prompt_tokens": response.get('prompt_eval_count', 0),
                "completion_tokens": response.get('eval_count', 0),
                "total": response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
            }

            logger.info(f"Generated {token_usage['completion_tokens']} tokens")
            return generated_text, token_usage

        except Exception as e:
            logger.error(f"Error generating with Ollama: {str(e)}")
            raise

    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text using Ollama.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            return response['embedding']

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = await self.embed(text)
            embeddings.append(embedding)
        return embeddings

    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []

    def pull_model(self, model_name: str):
        """Pull a model from Ollama registry."""
        try:
            logger.info(f"Pulling model: {model_name}")
            self.client.pull(model_name)
            logger.info(f"Successfully pulled model: {model_name}")
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
            raise

    async def stream_generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: str = None,
        **kwargs
    ):
        """
        Generate text with streaming response.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            **kwargs: Additional Ollama parameters

        Yields:
            Generated text chunks
        """
        try:
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            stream = self.client.chat(
                model=self.model,
                messages=messages,
                stream=True,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    **kwargs
                }
            )

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']

        except Exception as e:
            logger.error(f"Error in streaming generation: {str(e)}")
            raise


class OllamaModelManager:
    """Manager for Ollama model operations."""

    def __init__(self, host: str = "http://localhost:11434"):
        self.client = ollama.Client(host=host)

    def ensure_models(self, models: List[str]):
        """
        Ensure required models are available.

        Args:
            models: List of model names to check/pull
        """
        available_models = [m['name'] for m in self.client.list()['models']]
        
        for model in models:
            if model not in available_models:
                logger.info(f"Model {model} not found, pulling...")
                self.client.pull(model)
                logger.info(f"Successfully pulled {model}")
            else:
                logger.info(f"Model {model} already available")

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        try:
            return self.client.show(model_name)
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            return {}

    def delete_model(self, model_name: str):
        """Delete a model from local storage."""
        try:
            self.client.delete(model_name)
            logger.info(f"Deleted model: {model_name}")
        except Exception as e:
            logger.error(f"Error deleting model: {str(e)}")
            raise
