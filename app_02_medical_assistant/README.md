# App 02: Medical Diagnosis Assistant

**Technique:** Multi-hop Reasoning with Neo4j Knowledge Graph

## What This App Does
This application demonstrates how to adapt Context-Augmented Generation (CAG) principles using an external structured knowledge graph. It connects to a Neo4j database to perform multi-hop reasoning, mapping symptoms to diseases and identifying potential treatments.

## Architecture
- **Knowledge Graph:** Neo4j Database
- **LLM Engine:** Local Ollama models
- **Port:** HTTP 8002

## Quick Start
```bash
# Note: Requires a running Neo4j container with bolt://neo4j:7687 available
cd backend && py main.py
cd frontend && npm start
```

## Note on Testing
Since this app requires a running Neo4j database, it is excluded from the standard zero-infrastructure CAG automated test suite.
