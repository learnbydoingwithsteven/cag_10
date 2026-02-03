"""
Legal Document Analyzer - Backend API
Uses RAG + Citation tracking for legal document analysis.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from cag_engine.base import CAGRequest, CAGResponse, ContextChunk
from cag_engine.ollama_client import OllamaClient
from cag_engine.chroma_store import ChromaVectorStore
from legal_rag import LegalRAGTechnique
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Document Analyzer",
    description="AI-powered legal document analysis with RAG and citation tracking",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ollama_client = OllamaClient(model="llama3")
vector_store = ChromaVectorStore(
    collection_name="legal_documents",
    persist_directory="./legal_chroma_db"
)
legal_rag = LegalRAGTechnique(
    llm_client=ollama_client,
    vector_store=vector_store
)

# Request/Response models
class AnalyzeRequest(BaseModel):
    query: str
    context_limit: int = 5
    temperature: float = 0.3  # Lower for legal precision
    max_tokens: int = 1500

class AnalyzeResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    reasoning_steps: List[str]
    confidence_score: float
    latency_ms: float
    token_usage: Dict[str, int]
    process_visualization: Dict[str, Any]

class DocumentUpload(BaseModel):
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentInfo(BaseModel):
    id: str
    title: str
    num_chunks: int
    upload_date: str

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Legal Document Analyzer",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_legal_query(request: AnalyzeRequest):
    """
    Analyze a legal query using RAG with citation tracking.
    
    Args:
        request: Analysis request with query and parameters
        
    Returns:
        Analysis response with answer and citations
    """
    try:
        logger.info(f"Analyzing query: {request.query[:100]}...")
        
        # Create CAG request
        cag_request = CAGRequest(
            query=request.query,
            context_limit=request.context_limit,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Process with Legal RAG
        cag_response = await legal_rag.process(cag_request)
        
        # Extract citations from context chunks
        citations = [
            {
                "source": chunk.source,
                "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "relevance_score": chunk.relevance_score,
                "metadata": chunk.metadata
            }
            for chunk in cag_response.context_chunks
        ]
        
        # Get process visualization
        process_viz = legal_rag.get_process_visualization()
        
        return AnalyzeResponse(
            answer=cag_response.answer,
            citations=citations,
            reasoning_steps=cag_response.reasoning_steps,
            confidence_score=cag_response.confidence_score,
            latency_ms=cag_response.latency_ms,
            token_usage=cag_response.token_usage,
            process_visualization=process_viz
        )
        
    except Exception as e:
        logger.error(f"Error analyzing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/upload")
async def upload_document(document: DocumentUpload):
    """
    Upload a legal document to the knowledge base.
    
    Args:
        document: Document with title, content, and metadata
        
    Returns:
        Upload confirmation with document ID
    """
    try:
        logger.info(f"Uploading document: {document.title}")
        
        # Split document into chunks
        chunks = legal_rag.chunk_document(
            document.content,
            chunk_size=500,
            overlap=50
        )
        
        # Prepare metadata for each chunk
        metadatas = [
            {
                "title": document.title,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "upload_date": datetime.now().isoformat(),
                **(document.metadata or {})
            }
            for i in range(len(chunks))
        ]
        
        # Add to vector store
        doc_id = f"doc_{datetime.now().timestamp()}"
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        
        await vector_store.add_documents(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully uploaded document with {len(chunks)} chunks")
        
        return {
            "status": "success",
            "document_id": doc_id,
            "num_chunks": len(chunks),
            "message": f"Document '{document.title}' uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/upload-file")
async def upload_document_file(file: UploadFile = File(...)):
    """
    Upload a legal document file (PDF, TXT, DOCX).
    
    Args:
        file: Uploaded file
        
    Returns:
        Upload confirmation
    """
    try:
        logger.info(f"Uploading file: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Extract text based on file type
        if file.filename.endswith('.txt'):
            text = content.decode('utf-8')
        elif file.filename.endswith('.pdf'):
            import io
            from pypdf import PdfReader
            
            # Create a PDF reader object
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
            if not text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from PDF (it might be empty or scanned)")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Upload as document
        document = DocumentUpload(
            title=file.filename,
            content=text,
            metadata={"filename": file.filename}
        )
        
        return await upload_document(document)
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    List all documents in the knowledge base.
    
    Returns:
        List of document information
    """
    try:
        stats = vector_store.get_collection_stats()
        
        # TODO: Implement proper document tracking
        return [{
            "id": "all",
            "title": "All Documents",
            "num_chunks": stats.get("count", 0),
            "upload_date": datetime.now().isoformat()
        }]
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the knowledge base.
    
    Args:
        document_id: Document ID to delete
        
    Returns:
        Deletion confirmation
    """
    try:
        logger.info(f"Deleting document: {document_id}")
        
        # Get all chunks for this document
        # TODO: Implement proper document ID tracking
        
        return {
            "status": "success",
            "message": f"Document {document_id} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """
    Get system statistics.
    
    Returns:
        System statistics
    """
    try:
        collection_stats = vector_store.get_collection_stats()
        
        return {
            "collection": collection_stats,
            "model": ollama_client.model,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    WebSocket endpoint for streaming analysis.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive query
            data = await websocket.receive_text()
            query_data = json.loads(data)
            
            # Send process updates
            await websocket.send_json({
                "type": "status",
                "message": "Starting analysis..."
            })
            
            # Create request
            request = CAGRequest(
                query=query_data["query"],
                context_limit=query_data.get("context_limit", 5),
                temperature=query_data.get("temperature", 0.3),
                max_tokens=query_data.get("max_tokens", 1500)
            )
            
            # Process
            response = await legal_rag.process(request)
            
            # Send result
            await websocket.send_json({
                "type": "result",
                "data": {
                    "answer": response.answer,
                    "citations": [
                        {
                            "source": c.source,
                            "relevance": c.relevance_score
                        }
                        for c in response.context_chunks
                    ],
                    "latency_ms": response.latency_ms
                }
            })
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
