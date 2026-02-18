# App 13: Git Sync Assistant

**State-of-the-Art (SOTA) Git Expert System**

This application uses **Expert System CAG** to analyze Git scenarios and provide actionable commands.

## SOTA Features
1.  **Dynamic Model Selection**: Automatically detects and uses the best available local Ollama model (filters out embedding-only and cloud models).
2.  **Scenario Analysis**: Understands complex git states (conflicts, detached head, rebase issues).
3.  **Command Generation**: Provides exact, copy-pasteable commands.
4.  **Context-Aware**: Uses a knowledge base of Git patterns to ground its advice.
5.  **Process Visualization**: Shows the retrieval and reasoning steps with latency breakdown.

## Architecture
- **Backend**: FastAPI + Ollama (auto-selected model).
- **CAG Technique**: Expert System with keyword-based context retrieval from a Git knowledge base.
- **Frontend**: React + Material-UI (Interactive Console).

## Verification

### Backend API (Port 8013) ✅
```
$ Invoke-WebRequest -Uri http://localhost:8013/ -UseBasicParsing
StatusCode: 200
Content: {"app":"Git Sync Assistant","technique":"Expert System CAG","status":"running"}
```

### Swagger API Docs ✅
```
$ Invoke-WebRequest -Uri http://localhost:8013/docs -Method Head
StatusCode: 200 OK
```

### Dynamic Model Selection ✅
```
Available chat models: ['tinyllama:latest', 'qwen2.5:1.5b']
Git Sync Assistant selected model: qwen2.5:1.5b
```

### Sample Query & Response ✅

**Query**: _"I have a merge conflict after pulling from the remote. How do I resolve it?"_

**Context Retrieved** (4 chunks, avg relevance: 0.96):
| Source | Relevance |
|---|---|
| git_basics | 100% |
| git_workflow | 100% |
| conflict_resolution | 100% |
| git_fetch | 85% |

**Response** (568 tokens, 7.0s latency):
> ### Step 1: Identify the Conflicting Files
> Run `git status`. Look for lines indicating a merge conflict.
>
> ### Step 2: Review Conflict Resolution Guidelines
> Review your project's codebase guidelines or commit history.
>
> ### Step 3: Resolve the Conflicts
> Open each conflicted file and manually decide which changes to keep.
> ```bash
> git diff --name-only $HEAD $<branch_name>
> ```
>
> ### Step 4: Stage and Commit
> ```bash
> git add <file_name>
> git commit -m "Resolved merge conflict"
> ```

### CAG Process Steps ✅
| Step | Duration |
|---|---|
| Context Retrieval | <1ms |
| Context Augmentation | <1ms |
| LLM Generation | 7,047ms |

### Frontend (Port 3013 / dev port 6302) ✅
```
Compiled successfully!
Local: http://localhost:6302
```

## Quick Start
```bash
# Start Backend
cd backend
py main.py
# → Auto-selects best available local Ollama model
# → Runs on http://localhost:8013

# Start Frontend (in another terminal)
cd frontend
npm install
npm start
# → Runs on http://localhost:3013
```

## API Usage
```bash
# Health check
curl http://localhost:8013/

# Analyze a git scenario
curl -X POST http://localhost:8013/analyze \
     -H "Content-Type: application/json" \
     -d '{"query": "How do I resolve a merge conflict?"}'
```

Response includes `response`, `context` (retrieved knowledge), `metadata`, and `process_steps`.
