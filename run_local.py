
import os
import subprocess
import sys
import argparse
import time
import signal
import webbrowser
from pathlib import Path

# Configuration
APPS = {
    "0": {
        "name": "unified_dashboard",
        "port_backend": 8000,
        "port_frontend": 3000
    },
    "1": {
        "name": "app_01_legal_analyzer",
        "port_backend": 8001,
        "port_frontend": 3001,
        "env_vars": {
             "CHROMA_PERSIST_DIRECTORY": "./chroma_data_local"
        }
    },
    "2": { "name": "app_02_medical_assistant", "port_backend": 8002, "port_frontend": 3002 },
    "3": { "name": "app_03_code_reviewer", "port_backend": 8003, "port_frontend": 3003 },
    "4": { "name": "app_04_support_agent", "port_backend": 8004, "port_frontend": 3004 },
    "5": { "name": "app_05_financial_analyzer", "port_backend": 8005, "port_frontend": 3005 },
    "6": { "name": "app_06_paper_summarizer", "port_backend": 8006, "port_frontend": 3006 },
    "7": { "name": "app_07_product_recommender", "port_backend": 8007, "port_frontend": 3007 },
    "8": { "name": "app_08_educational_tutor", "port_backend": 8008, "port_frontend": 3008 },
    "9": { "name": "app_09_compliance_checker", "port_backend": 8009, "port_frontend": 3009 },
    "10": { "name": "app_10_fact_checker", "port_backend": 8010, "port_frontend": 3010 }
}

def install_dependencies(app_id):
    """Install dependencies for the specified app."""
    app_info = APPS[app_id]
    app_dir = Path(app_info["name"])
    
    print(f"Installing dependencies for {app_info['name']}...")
    
    # 1. Shared Requirements
    shared_req = Path("shared/requirements.txt")
    if shared_req.exists():
        try:
            print("Installing shared requirements...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(shared_req)])
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install some shared requirements: {e}. Continuing...")

    # 2. Backend Requirements
    backend_req = app_dir / "backend" / "requirements.txt"
    if backend_req.exists():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(backend_req)])
        except subprocess.CalledProcessError as e:
             print(f"Warning: Failed to install backend requirements: {e}")
        
    # 3. Extra local requirements (not in docker-compose)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "chromadb", "pypdf", "sentence-transformers"])
    
    # 4. Frontend Dependencies
    frontend_dir = app_dir / "frontend"
    if frontend_dir.exists():
        print("Installing frontend dependencies (npm)...")
        # Use shell=True for windows npm compatibility if needed
        subprocess.check_call(["npm", "install"], cwd=str(frontend_dir), shell=True)

def run_app(app_id):
    """Run the specified app (Backend + Frontend)."""
    app_info = APPS[app_id]
    app_dir = Path(app_info["name"])
    
    # Environment variables
    env = os.environ.copy()
    env.update(app_info.get("env_vars", {}))
    # Add shared python path
    env["PYTHONPATH"] = os.getcwd()
    # Set Frontend Port
    env["PORT"] = str(app_info['port_frontend'])
    # Prevent browser auto-open
    env["BROWSER"] = "none"
    
    processes = []
    
    try:
        # 1. Start Backend
        print(f"Starting Backend for {app_info['name']} on port {app_info['port_backend']}...")
        backend_cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", str(app_info['port_backend']),
            "--reload"
        ]
        backend_proc = subprocess.Popen(
            backend_cmd, 
            cwd=str(app_dir / "backend"),
            env=env
        )
        processes.append(backend_proc)
        
        # 2. Start Frontend
        print(f"Starting Frontend for {app_info['name']}...")
        frontend_cmd = ["npm", "start"]
        frontend_proc = subprocess.Popen(
            frontend_cmd, 
            cwd=str(app_dir / "frontend"),
            env=env,
            shell=True
        )
        processes.append(frontend_proc)
        
        print(f"App {app_id} is running!")
        print(f"Backend: http://localhost:{app_info['port_backend']}")
        print(f"Frontend: http://localhost:{app_info['port_frontend']}")
        print("Press Ctrl+C to stop.")
        
        # Open browser after a short delay
        time.sleep(5)
        webbrowser.open(f"http://localhost:{app_info['port_frontend']}")
        
        # Keep alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        for p in processes:
            p.terminate()
            # For Windows special handling if needed, but terminate usually works or user closes window
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                p.kill()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CAG apps locally without Docker")
    parser.add_argument("--app", type=str, default="1", help="App ID to run (default: 1)")
    parser.add_argument("--install", action="store_true", help="Install dependencies before running")
    
    args = parser.parse_args()
    
    if args.app not in APPS:
        print(f"Invalid app ID. Available: {list(APPS.keys())}")
        sys.exit(1)
        
    if args.install:
        install_dependencies(args.app)
        
    run_app(args.app)
