"""
Base classes for Context-Augmented Generation (CAG) engine.
Provides abstract interfaces for different CAG techniques.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContextChunk:
    """Represents a chunk of context retrieved for augmentation."""
    content: str
    source: str
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CAGRequest:
    """Request object for CAG processing."""
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context_limit: int = 5
    temperature: float = 0.7
    max_tokens: int = 1000
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CAGResponse:
    """Response object from CAG processing."""
    answer: str
    context_chunks: List[ContextChunk]
    reasoning_steps: List[str]
    confidence_score: float
    latency_ms: float
    token_usage: Dict[str, int]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessStep:
    """Represents a step in the CAG process for visualization."""
    step_name: str
    description: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "running"  # running, completed, failed
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[float]:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None


class CAGTechnique(ABC):
    """Abstract base class for CAG techniques."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.process_steps: List[ProcessStep] = []

    def _start_step(self, step_name: str, description: str) -> ProcessStep:
        """Start tracking a process step."""
        step = ProcessStep(
            step_name=step_name,
            description=description,
            start_time=time.time()
        )
        self.process_steps.append(step)
        logger.info(f"Started step: {step_name}")
        return step

    def _complete_step(self, step: ProcessStep, details: Optional[Dict[str, Any]] = None):
        """Mark a process step as completed."""
        step.end_time = time.time()
        step.status = "completed"
        if details:
            step.details.update(details)
        logger.info(f"Completed step: {step.step_name} ({step.duration_ms:.2f}ms)")

    def _fail_step(self, step: ProcessStep, error: str):
        """Mark a process step as failed."""
        step.end_time = time.time()
        step.status = "failed"
        step.details["error"] = error
        logger.error(f"Failed step: {step.step_name} - {error}")

    @abstractmethod
    async def retrieve_context(self, request: CAGRequest) -> List[ContextChunk]:
        """
        Retrieve relevant context for the query.
        
        Args:
            request: CAG request containing query and parameters
            
        Returns:
            List of context chunks with relevance scores
        """
        pass

    @abstractmethod
    async def augment_context(
        self, 
        request: CAGRequest, 
        context_chunks: List[ContextChunk]
    ) -> str:
        """
        Augment the query with retrieved context.
        
        Args:
            request: Original CAG request
            context_chunks: Retrieved context chunks
            
        Returns:
            Augmented prompt for generation
        """
        pass

    @abstractmethod
    async def generate_response(
        self, 
        augmented_prompt: str, 
        request: CAGRequest
    ) -> Tuple[str, Dict[str, int]]:
        """
        Generate response using augmented prompt.
        
        Args:
            augmented_prompt: Context-augmented prompt
            request: Original CAG request
            
        Returns:
            Tuple of (generated_text, token_usage)
        """
        pass

    async def process(self, request: CAGRequest) -> CAGResponse:
        """
        Main processing pipeline for CAG.
        
        Args:
            request: CAG request
            
        Returns:
            CAG response with answer and metadata
        """
        start_time = time.time()
        self.process_steps = []  # Reset process steps
        reasoning_steps = []

        try:
            # Step 1: Retrieve context
            step1 = self._start_step("retrieve_context", "Retrieving relevant context")
            context_chunks = await self.retrieve_context(request)
            self._complete_step(step1, {
                "num_chunks": len(context_chunks),
                "avg_relevance": sum(c.relevance_score for c in context_chunks) / len(context_chunks) if context_chunks else 0
            })
            reasoning_steps.append(f"Retrieved {len(context_chunks)} relevant context chunks")

            # Step 2: Augment context
            step2 = self._start_step("augment_context", "Augmenting query with context")
            augmented_prompt = await self.augment_context(request, context_chunks)
            self._complete_step(step2, {
                "prompt_length": len(augmented_prompt)
            })
            reasoning_steps.append("Augmented query with retrieved context")

            # Step 3: Generate response
            step3 = self._start_step("generate_response", "Generating response with LLM")
            answer, token_usage = await self.generate_response(augmented_prompt, request)
            self._complete_step(step3, {
                "token_usage": token_usage,
                "answer_length": len(answer)
            })
            reasoning_steps.append(f"Generated response using {token_usage.get('total', 0)} tokens")

            # Calculate confidence score (can be overridden by subclasses)
            confidence_score = self._calculate_confidence(context_chunks, answer)

            latency_ms = (time.time() - start_time) * 1000

            return CAGResponse(
                answer=answer,
                context_chunks=context_chunks,
                reasoning_steps=reasoning_steps,
                confidence_score=confidence_score,
                latency_ms=latency_ms,
                token_usage=token_usage,
                metadata={
                    "technique": self.name,
                    "process_steps": [
                        {
                            "name": s.step_name,
                            "duration_ms": s.duration_ms,
                            "status": s.status,
                            "details": s.details
                        }
                        for s in self.process_steps
                    ]
                }
            )

        except Exception as e:
            logger.error(f"Error in CAG processing: {str(e)}")
            raise

    def _calculate_confidence(
        self, 
        context_chunks: List[ContextChunk], 
        answer: str
    ) -> float:
        """
        Calculate confidence score for the response.
        Can be overridden by subclasses for custom logic.
        
        Args:
            context_chunks: Retrieved context chunks
            answer: Generated answer
            
        Returns:
            Confidence score between 0 and 1
        """
        if not context_chunks:
            return 0.3
        
        # Simple heuristic: average relevance of context chunks
        avg_relevance = sum(c.relevance_score for c in context_chunks) / len(context_chunks)
        
        # Adjust based on answer length (very short answers might be less confident)
        length_factor = min(len(answer) / 100, 1.0)
        
        return avg_relevance * 0.7 + length_factor * 0.3

    def get_process_visualization(self) -> Dict[str, Any]:
        """
        Get visualization data for the CAG process.
        
        Returns:
            Dictionary with process visualization data
        """
        return {
            "technique": self.name,
            "total_steps": len(self.process_steps),
            "total_duration_ms": sum(s.duration_ms or 0 for s in self.process_steps),
            "steps": [
                {
                    "name": s.step_name,
                    "description": s.description,
                    "duration_ms": s.duration_ms,
                    "status": s.status,
                    "details": s.details
                }
                for s in self.process_steps
            ]
        }


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    async def add_documents(
        self, 
        documents: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """Add documents to the vector store."""
        pass

    @abstractmethod
    async def search(
        self, 
        query: str, 
        limit: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar documents.
        
        Returns:
            List of tuples (document, score, metadata)
        """
        pass

    @abstractmethod
    async def delete(self, ids: List[str]):
        """Delete documents by IDs."""
        pass


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Tuple[str, Dict[str, int]]:
        """
        Generate text from prompt.
        
        Returns:
            Tuple of (generated_text, token_usage)
        """
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        pass
