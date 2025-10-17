"""
Legal RAG Technique - Retrieval-Augmented Generation with Citation Tracking
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.base import CAGTechnique, CAGRequest, ContextChunk, LLMClient, VectorStore
from typing import List, Tuple, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class LegalRAGTechnique(CAGTechnique):
    """
    Legal-specific RAG technique with citation tracking and legal terminology handling.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        vector_store: VectorStore,
        config: Dict[str, Any] = None
    ):
        super().__init__("LegalRAG", config or {})
        self.llm_client = llm_client
        self.vector_store = vector_store
        
        # Legal-specific configuration
        self.citation_format = config.get("citation_format", "inline") if config else "inline"
        self.min_relevance_threshold = config.get("min_relevance", 0.6) if config else 0.6

    async def retrieve_context(self, request: CAGRequest) -> List[ContextChunk]:
        """
        Retrieve relevant legal context with citation tracking.
        
        Args:
            request: CAG request with query
            
        Returns:
            List of context chunks with legal citations
        """
        try:
            # Search vector store
            results = await self.vector_store.search(
                query=request.query,
                limit=request.context_limit
            )
            
            # Convert to ContextChunk objects
            context_chunks = []
            for doc, score, metadata in results:
                # Only include if above relevance threshold
                if score >= self.min_relevance_threshold:
                    chunk = ContextChunk(
                        content=doc,
                        source=metadata.get("title", "Unknown Document"),
                        relevance_score=score,
                        metadata={
                            **metadata,
                            "chunk_index": metadata.get("chunk_index", 0),
                            "citation_id": f"[{len(context_chunks) + 1}]"
                        }
                    )
                    context_chunks.append(chunk)
            
            logger.info(f"Retrieved {len(context_chunks)} relevant legal contexts")
            return context_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            raise

    async def augment_context(
        self,
        request: CAGRequest,
        context_chunks: List[ContextChunk]
    ) -> str:
        """
        Augment query with legal context and citation markers.
        
        Args:
            request: Original request
            context_chunks: Retrieved context chunks
            
        Returns:
            Augmented prompt with legal context
        """
        # Build context section with citations
        context_text = "## Relevant Legal Context:\n\n"
        
        for i, chunk in enumerate(context_chunks, 1):
            citation_id = f"[{i}]"
            source = chunk.source
            content = chunk.content
            
            context_text += f"{citation_id} **{source}**\n"
            context_text += f"{content}\n\n"
        
        # Build augmented prompt
        augmented_prompt = f"""You are a legal analysis assistant. Analyze the following query using the provided legal context.

{context_text}

## Query:
{request.query}

## Instructions:
1. Provide a comprehensive legal analysis based on the context provided
2. Cite sources using the citation numbers [1], [2], etc. when referencing specific information
3. If the context doesn't fully answer the query, acknowledge the limitations
4. Use precise legal terminology
5. Structure your response clearly with relevant sections

## Analysis:"""

        return augmented_prompt

    async def generate_response(
        self,
        augmented_prompt: str,
        request: CAGRequest
    ) -> Tuple[str, Dict[str, int]]:
        """
        Generate legal analysis response.
        
        Args:
            augmented_prompt: Context-augmented prompt
            request: Original request
            
        Returns:
            Tuple of (generated_text, token_usage)
        """
        system_prompt = """You are an expert legal analyst. Provide accurate, well-cited legal analysis based on the provided context. Always cite your sources using the provided citation numbers."""
        
        response, token_usage = await self.llm_client.generate(
            prompt=augmented_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=system_prompt
        )
        
        return response, token_usage

    def chunk_document(
        self,
        document: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        Chunk a legal document intelligently.
        
        Tries to split on:
        1. Section boundaries
        2. Paragraph boundaries
        3. Sentence boundaries
        4. Character boundaries (fallback)
        
        Args:
            document: Full document text
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of document chunks
        """
        # Try to split on section markers
        section_pattern = r'\n(?:Section|Article|Chapter|§)\s+\d+[:\.]?\s*'
        sections = re.split(section_pattern, document)
        
        chunks = []
        current_chunk = ""
        
        for section in sections:
            # Split section into paragraphs
            paragraphs = section.split('\n\n')
            
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # If adding this paragraph exceeds chunk size
                if len(current_chunk) + len(para) > chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    if overlap > 0:
                        current_chunk = current_chunk[-overlap:] + " " + para
                    else:
                        current_chunk = para
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Split document into {len(chunks)} chunks")
        return chunks

    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract legal entities from text (cases, statutes, parties, etc.).
        
        Args:
            text: Legal text
            
        Returns:
            Dictionary of entity types and extracted entities
        """
        entities = {
            "cases": [],
            "statutes": [],
            "sections": [],
            "parties": []
        }
        
        # Extract case citations (simplified pattern)
        case_pattern = r'\b[A-Z][a-z]+\s+v\.?\s+[A-Z][a-z]+\b'
        entities["cases"] = re.findall(case_pattern, text)
        
        # Extract statute references
        statute_pattern = r'\b\d+\s+U\.S\.C\.?\s+§?\s*\d+\b'
        entities["statutes"] = re.findall(statute_pattern, text)
        
        # Extract section references
        section_pattern = r'§\s*\d+(?:\.\d+)*'
        entities["sections"] = re.findall(section_pattern, text)
        
        return entities

    def validate_citation(self, citation: str) -> bool:
        """
        Validate legal citation format.
        
        Args:
            citation: Citation string
            
        Returns:
            True if valid citation format
        """
        # Basic validation patterns
        patterns = [
            r'\d+\s+U\.S\.?\s+\d+',  # U.S. Reports
            r'\d+\s+F\.\d+d?\s+\d+',  # Federal Reporter
            r'\d+\s+S\.Ct\.\s+\d+',  # Supreme Court Reporter
            r'[A-Z][a-z]+\s+v\.?\s+[A-Z][a-z]+',  # Case name
        ]
        
        for pattern in patterns:
            if re.search(pattern, citation):
                return True
        
        return False
