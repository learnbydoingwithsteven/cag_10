# Unified Dashboard Walkthrough

I have implemented a unified dashboard to manage all 10 CAG applications. This dashboard allows you to view the status of each app, start/stop them, and open their respective interfaces.

## Features
- **Centralized Control**: Start and stop any app from a single UI.
- **Real-time Status**: Indicators show if an app is running or stopped.
- **Easy Access**: "Open App" button takes you directly to the correct port.
- **Extensible**: New apps can be added to `unified_dashboard/backend/config.json`.

## How to Run
I have created a convenience script:
1. Double-click `start_dashboard.bat` in the `cag_10` directory.
   - Or run `python run_local.py --install --app 0` manually.
2. The dashboard will open at `http://localhost:3000`.
3. The backend API runs at `http://localhost:8000`.

> [!NOTE]
> The first run may take a few minutes as it installs NPM dependencies for the dashboard frontend.

## Implementation Details

### Architecture
- **Frontend**: React (Vite) + Tailwind CSS + Lucide React icons.
- **Backend**: FastAPI + Uvicorn + Subprocess Management.

### Key Files
- `unified_dashboard/backend/config.json`: Defines ports and paths.
- `unified_dashboard/backend/app_manager.py`: Handles process spawning.
- `run_local.py`: Updated to inject `PORT` env var so apps run on correct ports.

### Configuration
You can add new apps by editing `config.json`:
```json
"11": {
  "id": "11",
  "name": "New App",
  "folder": "app_11_new",
  "frontend_port": 3011,
  "backend_port": 8011,
  "description": "Description here"
}
```

## Validation
- Verified backend startup with `uvicorn`.
- Verified `run_local.py` update.
- Dashboard scaffolding and code generation complete.

## Verification Status
**Unified Dashboard**: 
- **Backend (Port 8000)**: Running successfully.
- **Frontend (Port 3000)**: Running successfully after fixing dependencies.
    ![Unified Dashboard](doc_assets/unified_dashboard_main.png)


## App Verification
### App 01: Legal Analyzer
- **Backend Status**: Running on port 8001.
- **Frontend Status**: Failed to connect on port 3001.
- **Notes**: Frontend dependencies installed, but connection refused on expected port.

### App 02: Medical Assistant
- **Status**: Skipped.
- **Notes**: Failed to install dependencies (`chroma-hnswlib` build error). Requires C++ build tools or pre-built wheels.

### Apps 03 - 10
- **Status**: Skipped.
- **Notes**: All remaining apps share the same `shared/requirements.txt` and thus fail with the same `chroma-hnswlib` build error as App 02 on Windows environment.
  - App 03: Code Reviewer
  - App 04: Support Agent
  - App 05: Financial Analyzer
  - App 06: Paper Summarizer
  - App 07: Product Recommender
  - App 08: Educational Tutor
  - App 09: Compliance Checker
  - App 10: Fact Checker
