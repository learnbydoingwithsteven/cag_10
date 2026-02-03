import subprocess
import sys
import os
import json
import time
import signal
import psutil
from pathlib import Path

# Load config
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

with open(BASE_DIR / "config.json", "r") as f:
    CONFIG = json.load(f)["apps"]

# Store running processes: { app_id: { "backend": Popen, "frontend": Popen } }
RUNNING_APPS = {}

def get_app_config(app_id: str):
    return CONFIG.get(app_id)

def get_all_apps():
    # Add status to config
    apps_list = []
    for app_id, data in CONFIG.items():
        status = "stopped"
        if app_id in RUNNING_APPS:
            # Check if processes are actually alive
            if is_app_running(app_id):
                status = "running"
            else:
                # Cleanup if they died unexpectedly
                stop_app(app_id) 
        
        app_data = data.copy()
        app_data["status"] = status
        apps_list.append(app_data)
    return apps_list

def is_app_running(app_id: str):
    if app_id not in RUNNING_APPS:
        return False
    
    procs = RUNNING_APPS[app_id]
    backend = procs.get("backend")
    frontend = procs.get("frontend")
    
    # Check if they are None or poll() is not None (meaning terminated)
    if backend and backend.poll() is not None:
        return False
    if frontend and frontend.poll() is not None:
        return False
        
    return True

def start_app(app_id: str):
    if is_app_running(app_id):
        return {"success": False, "message": "App already running"}
    
    app_info = get_app_config(app_id)
    if not app_info:
        return {"success": False, "message": "App not found"}
        
    app_dir = PROJECT_ROOT / app_info["folder"]
    
    # Environment Setup
    env = os.environ.copy()
    env.update(app_info.get("env_vars", {}))
    env["PYTHONPATH"] = str(PROJECT_ROOT) # Ensure shared modules are found
    # For React/CRA to set port
    env["PORT"] = str(app_info["frontend_port"])
    # Prevent browser auto-open
    env["BROWSER"] = "none"

    try:
        # 1. Start Backend
        print(f"Starting Backend for {app_info['name']} on port {app_info['backend_port']}...")
        backend_cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", str(app_info['backend_port']),
            "--reload"
        ]
        
        backend_proc = subprocess.Popen(
            backend_cmd, 
            cwd=str(app_dir / "backend"),
            env=env,
            # We could redirect stdout/stderr to capture logs
        )
        
        # 2. Start Frontend
        print(f"Starting Frontend for {app_info['name']} on port {app_info['frontend_port']}...")
        # Note: 'npm start' usually runs react-scripts start. 
        # We need to ensure it sees the PORT env var.
        # Window shell=True is often needed for npm.
        frontend_cmd = ["npm", "start"]
        frontend_proc = subprocess.Popen(
            frontend_cmd, 
            cwd=str(app_dir / "frontend"),
            env=env,
            shell=True
        )
        
        RUNNING_APPS[app_id] = {
            "backend": backend_proc,
            "frontend": frontend_proc
        }
        
        return {"success": True, "message": f"Started {app_info['name']}"}
        
    except Exception as e:
        print(f"Error starting app {app_id}: {e}")
        # Cleanup if half-started
        stop_app(app_id)
        return {"success": False, "message": str(e)}

def stop_app(app_id: str):
    if app_id not in RUNNING_APPS:
        return {"success": False, "message": "App not running"}
    
    procs = RUNNING_APPS[app_id]
    
    _kill_proc(procs.get("backend"))
    _kill_proc(procs.get("frontend"))
    
    del RUNNING_APPS[app_id]
    return {"success": True, "message": "App stopped"}

def _kill_proc(proc):
    if not proc:
        return
    
    # Simple terminate
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        _kill_process_tree(proc.pid)

def _kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass
