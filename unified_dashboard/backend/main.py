from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import app_manager
import uvicorn
import os

app = FastAPI(title="Unified Dashboard API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev, allow all. In prod, lock down.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AppResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    frontend_port: int
    backend_port: int

@app.get("/apps")
def list_apps():
    apps = app_manager.get_all_apps()
    # Convert dict values to list if needed, but get_all_apps returns a list
    return apps

@app.post("/apps/{app_id}/start")
def start_app(app_id: str):
    result = app_manager.start_app(app_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/apps/{app_id}/stop")
def stop_app(app_id: str):
    result = app_manager.stop_app(app_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
