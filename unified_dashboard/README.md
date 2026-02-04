# Unified Dashboard

This is the centralized dashboard to manage and run all 10 CAG applications.

![Dashboard Main View](file:///C:/Users/wjbea/.gemini/antigravity/brain/f2ca03e3-11b4-407d-9ff1-d8c434fa9e1e/unified_dashboard_main_1770248178420.png)

## Features
- **App Management**: List, Start, Stop all apps.
- **Status Monitoring**: Real-time status updates (Running/Stopped).
- **Direct Access**: Open app frontends directly from the dashboard.

## Setup & Run

### Prerequisites
- Python 3.12+
- Node.js 18+

### Quick Start
Run the following from the root `cag_10` directory:
```bash
.\start_dashboard.bat
```
Or manually:
```bash
# 1. Start Backend (Port 8000)
py run_local.py --app 0

# 2. Start Frontend (Port 3000)
cd unified_dashboard/frontend
npm install
npm run dev -- --port 3000
```

## Configuration
App configurations are stored in `backend/config.json`.
