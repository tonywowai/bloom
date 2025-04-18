from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from typing import Dict, Any, Optional
from model import MyModel
import os
from pydantic import BaseModel

# Models for request validation
class InstallServiceRequest(BaseModel):
    git: str

class ServiceInfoRequest(BaseModel):
    directory: str
    port_map: Optional[int] = None

class StopServiceRequest(BaseModel):
    port_map: int
    directory: Optional[str] = None

class DashboardRequest(BaseModel):
    directory: str

app = FastAPI(
    title="MyModel API",
    openapi_url="/swagger.json",
    docs_url="/swagger"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus and Loki configuration
LOKI_URL = os.getenv("LOKI_URL", "http://207.246.109.178:3100")
JOB_NAME = os.getenv("JOB_NAME", "test-fastapi")
PUSH_GATEWAY_URL = os.getenv("PUSH_GATEWAY_URL", "http://207.246.109.178:9091")
JOB_INTERVAL = int(os.getenv("JOB_INTERVAL", 60))

model = MyModel()

@app.post("/action")
async def action(project: str, command: str, collection: str, data: Optional[Dict[str, Any]] = None):
    try:
        result = model.action(project, command, collection, **(data or {}))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def model_endpoint(data: Optional[Dict[str, Any]] = None):
    try:
        result = model.model(**(data or {}))
        if "share_url" in result:
            return RedirectResponse(url=result["share_url"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/model")
async def model_endpoint(data: Optional[Dict[str, Any]] = None):
    try:
        result = model.model(**(data or {}))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/model-trial")
async def model_trial(project: str, data: Optional[Dict[str, Any]] = None):
    try:
        result = model.model_trial(project, **(data or {}))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download")
async def download(project: str, data: Optional[Dict[str, Any]] = None):
    try:
        result = model.download(project, **(data or {}))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/downloads")
async def download_file(path: str):
    if not path:
        raise HTTPException(status_code=400, detail="File name is required")
    
    current_dir = os.getcwd()
    full_path = os.path.join(current_dir, path)
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(full_path, filename=os.path.basename(full_path))


# @app.on_event("shutdown")
# async def shutdown_event():
#     scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn 
    import ssl 
    import socket 
 
    def find_available_port(start_port=8000, max_port=9000): 
        for port in range(start_port, max_port + 1): 
            try: 
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
                    s.bind(('0.0.0.0', port)) 
                    return port 
            except OSError: 
                continue 
        raise RuntimeError("No available ports found") 
 
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH) 
    ssl_context.load_cert_chain( 
        certfile="ssl/cert.pem", 
        keyfile="ssl/key.pem" 
    ) 
 
    available_port = find_available_port() 
    print(f"Starting server on port {available_port}") 
 
    uvicorn.run( 
        app, 
        host="0.0.0.0", 
        port=available_port, 
        ssl_keyfile="ssl/key.pem", 
        ssl_certfile="ssl/cert.pem" 
    )
