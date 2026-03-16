# App 01: Legal Document Analyzer

**Technique:** Traditional RAG (Retrieval-Augmented Generation) with Citation Tracking

## What This App Does
This application serves as a benchmark and comparison point for the rest of the CAG suite. While apps 03-19 use pure Context-Augmented Generation (CAG), this app implements a traditional **RAG** pipeline utilizing ChromaDB as a vector database. It includes citation tracking to point out the specific legal clauses retrieved from the vector store.

## Architecture
- **Vector DB:** ChromaDB (Requires `chroma_store.py`)
- **LLM Engine:** Local Ollama models
- **Port:** HTTP 8001

## Quick Start
```bash
# Note: Ensure you have populated the legal_chroma_db before running
cd backend && py main.py
cd frontend && npm start
```

## Note on Testing
Since this app relies on stateful embeddings in ChromaDB, it is not part of the standard CAG automated test suite, which ensures 0-dependency execution.
