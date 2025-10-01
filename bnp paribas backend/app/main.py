from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ML Analytics API",
    description="FastAPI backend for ML Analytics Dashboard with UiPath integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for caching (kept minimal; frontend now fetches fresh data)
analysis_cache: Dict[str, Any] = {}
file_cache: Dict[str, Any] = {}

@app.get("/")
async def root():
    return {"message": "ML Analytics API is running", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")

        os.makedirs("uploads", exist_ok=True)
        ts = int(datetime.now().timestamp() * 1000)
        filename = f"uipath_{ts}{ext}"
        file_path = os.path.join("uploads", filename)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        file_info = {
            "file_id": str(ts),
            "filename": filename,
            "file_path": file_path,
            "size": len(content),
            "upload_time": datetime.now().isoformat(),
            "status": "uploaded"
        }

        file_cache[file_info["file_id"]] = file_info
        background_tasks.add_task(run_ml_analysis, file_info["file_id"], file_path)

        return {"success": True, "file_id": file_info["file_id"], "analysis_url": f"/analysis/{file_info['file_id']}"}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/{file_id}")
async def get_analysis(file_id: str):
    if file_id not in analysis_cache:
        return {"success": False, "status": "processing", "file_id": file_id}
    return {"success": True, "file_id": file_id, "analysis": analysis_cache[file_id]}

async def run_ml_analysis(file_id: str, file_path: str):
    try:
        results = await execute_ml_analysis(file_path)
        analysis_cache[file_id] = {"status": "completed", "results": results}
        if file_id in file_cache:
            file_cache[file_id]["status"] = "completed"
    except Exception as e:
        logger.error(f"ML analysis error: {e}")
        analysis_cache[file_id] = {"status": "error", "error": str(e)}

async def execute_ml_analysis(file_path: str) -> Dict[str, Any]:
    # Find ml_analyzer.py relative to project root
    script_candidates = [
        os.path.join("..", "scripts", "ml_analyzer.py"),
        os.path.join("scripts", "ml_analyzer.py"),
    ]
    script_path = next((p for p in script_candidates if os.path.exists(p)), None)
    if not script_path:
        raise Exception("ML analyzer script not found")

    analyses = ['churn', 'segmentation', 'sales']
    results: Dict[str, Any] = {}
    for analysis_type in analyses:
        proc = await asyncio.create_subprocess_exec(
            'python', script_path, analysis_type, file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            try:
                results[analysis_type] = json.loads(stdout.decode())
            except Exception as e:
                results[analysis_type] = {"success": False, "error": f"Parse error: {e}"}
        else:
            results[analysis_type] = {"success": False, "error": stderr.decode()}
    return results

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


