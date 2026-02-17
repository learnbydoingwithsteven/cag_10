# App 13: Git Sync Assistant

**State-of-the-Art (SOTA) Git Expert System**

This application uses **Expert System CAG** to analyze Git scenarios and provide actionable commands.

## SOTA Features
1.  **Scenario Analysis**: Understands complex git states (conflicts, detached head, rebase issues).
2.  **Command Generation**: Provides exact, copy-pasteable commands.
3.  **Context-Aware**: Uses a knowledge base of Git patterns to ground its advice.
4.  **Process Visualization**: Shows the retrieval and reasoning steps.

## Architecture
- **Backend**: FastAPI + Ollama (Llama 3).
- **Frontend**: React + Material-UI (Interactive Console).

## Status
- **Backend**: Implemented (Port 8013).
- **Frontend**: Implemented (Port 3013), requires local build.

## Quick Start
```bash
# Start Backend
cd backend
python main.py

# Start Frontend
cd ../frontend
npm start
```
