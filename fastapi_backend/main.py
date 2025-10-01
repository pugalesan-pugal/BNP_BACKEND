from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
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
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for caching
analysis_cache: Dict[str, Any] = {}
file_cache: Dict[str, Any] = {}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ML Analytics API is running",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /upload",
            "status": "GET /status",
            "analysis": "GET /analysis/{file_id}",
            "health": "GET /health"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(analysis_cache)
    }

@app.get("/status")
async def get_status():
    """Get API status and supported formats"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "supported_formats": ["csv", "xlsx", "xls"],
        "max_file_size": "50MB",
        "python_available": await check_python_availability(),
        "uploads_directory": os.path.exists("uploads")
    }

@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload file and trigger ML analysis"""
    try:
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Generate unique filename
        timestamp = int(datetime.now().timestamp() * 1000)
        filename = f"uipath_{timestamp}{file_extension}"
        file_path = os.path.join("uploads", filename)
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create file info
        file_info = {
            "file_id": str(timestamp),
            "filename": filename,
            "original_name": file.filename,
            "file_path": file_path,
            "size": len(content),
            "upload_time": datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        # Cache file info
        file_cache[file_info["file_id"]] = file_info
        
        # Start background analysis
        background_tasks.add_task(run_ml_analysis, file_info["file_id"], file_path)
        
        return {
            "success": True,
            "message": "File uploaded successfully. Analysis started.",
            "file_id": file_info["file_id"],
            "file_info": file_info,
            "analysis_url": f"/analysis/{file_info['file_id']}"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/{file_id}")
async def get_analysis(file_id: str):
    """Get analysis results for a specific file"""
    try:
        if file_id not in analysis_cache:
            return {
                "success": False,
                "message": "Analysis not found or still in progress",
                "file_id": file_id,
                "status": "processing"
            }
        
        analysis_data = analysis_cache[file_id]
        file_info = file_cache.get(file_id, {})
        
        return {
            "success": True,
            "file_id": file_id,
            "file_info": file_info,
            "analysis": analysis_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analysis retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis")
async def get_all_analyses():
    """Get all cached analyses"""
    return {
        "success": True,
        "analyses": analysis_cache,
        "count": len(analysis_cache),
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/analysis/{file_id}")
async def delete_analysis(file_id: str):
    """Delete analysis and file"""
    try:
        # Remove from cache
        if file_id in analysis_cache:
            del analysis_cache[file_id]
        
        # Remove file info
        if file_id in file_cache:
            file_info = file_cache[file_id]
            # Delete physical file
            if os.path.exists(file_info["file_path"]):
                os.remove(file_info["file_path"])
            del file_cache[file_id]
        
        return {
            "success": True,
            "message": f"Analysis {file_id} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_ml_analysis(file_id: str, file_path: str):
    """Background task to run ML analysis"""
    try:
        logger.info(f"Starting ML analysis for file {file_id}")
        
        # Update file status
        if file_id in file_cache:
            file_cache[file_id]["status"] = "analyzing"
        
        # Run ML analysis
        analysis_results = await execute_ml_analysis(file_path)
        
        # Cache results
        analysis_cache[file_id] = {
            "status": "completed",
            "results": analysis_results,
            "completed_at": datetime.now().isoformat()
        }
        
        # Update file status
        if file_id in file_cache:
            file_cache[file_id]["status"] = "completed"
        
        logger.info(f"ML analysis completed for file {file_id}")
        
    except Exception as e:
        logger.error(f"ML analysis error for {file_id}: {str(e)}")
        
        # Update status to error
        analysis_cache[file_id] = {
            "status": "error",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }
        
        if file_id in file_cache:
            file_cache[file_id]["status"] = "error"

async def execute_ml_analysis(file_path: str) -> Dict[str, Any]:
    """Execute ML analysis using Python scripts"""
    try:
        # Check if ml_analyzer.py exists
        script_path = os.path.join("..", "scripts", "ml_analyzer.py")
        if not os.path.exists(script_path):
            script_path = os.path.join("scripts", "ml_analyzer.py")
        
        if not os.path.exists(script_path):
            raise Exception("ML analyzer script not found")
        
        # Run analyses
        analyses = ['churn', 'segmentation', 'sales']
        results = {}
        
        for analysis_type in analyses:
            try:
                # Run Python script
                process = await asyncio.create_subprocess_exec(
                    'python', script_path, analysis_type, file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    # Parse JSON output
                    result_data = json.loads(stdout.decode())
                    results[analysis_type] = {
                        "success": True,
                        "data": result_data
                    }
                else:
                    results[analysis_type] = {
                        "success": False,
                        "error": stderr.decode()
                    }
                    
            except Exception as e:
                results[analysis_type] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
        
    except Exception as e:
        logger.error(f"ML analysis execution error: {str(e)}")
        raise e

async def check_python_availability() -> bool:
    """Check if Python is available"""
    try:
        process = await asyncio.create_subprocess_exec(
            'python', '--version',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        return process.returncode == 0
    except:
        return False

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )



