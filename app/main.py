#!/usr/bin/env python3
"""
FastAPI Wrapper for MDPS
Dynamically imports and runs MDPS callables, returning job IDs and status files.
"""

import os
import sys
import uuid
import json
import asyncio
import importlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration
QUANT_RUNS_DIR = project_root / ".quant_runs"
QUANT_RUNS_DIR.mkdir(exist_ok=True)


class JobRequest(BaseModel):
    """Request model for creating a job"""
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Job parameters")
    entrypoint: Optional[str] = Field(None, description="Override MDPS_ENTRYPOINT (format: module:callable)")


class JobResponse(BaseModel):
    """Response model for job creation"""
    job_id: str
    status: str
    created_at: str
    status_file: str


class JobStatus(BaseModel):
    """Model for job status"""
    job_id: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


# Global job tracking
active_jobs: Dict[str, JobStatus] = {}


def get_entrypoint(override: Optional[str] = None) -> tuple[str, str]:
    """
    Get the MDPS entrypoint from environment or override.
    
    Args:
        override: Optional entrypoint override in format "module:callable"
    
    Returns:
        Tuple of (module_name, callable_name)
    
    Raises:
        ValueError: If entrypoint is not configured or invalid
    """
    entrypoint = override or os.getenv("MDPS_ENTRYPOINT")
    
    if not entrypoint:
        raise ValueError(
            "MDPS_ENTRYPOINT not configured. Set environment variable or provide in request. "
            "Format: module:callable (e.g., 'MDPS.run_mdps:main')"
        )
    
    if ":" not in entrypoint:
        raise ValueError(
            f"Invalid entrypoint format: {entrypoint}. "
            "Expected format: module:callable (e.g., 'MDPS.run_mdps:main')"
        )
    
    module_name, callable_name = entrypoint.split(":", 1)
    return module_name, callable_name


def load_callable(module_name: str, callable_name: str) -> Callable:
    """
    Dynamically import and return the callable.
    
    Args:
        module_name: Name of the module to import
        callable_name: Name of the callable within the module
    
    Returns:
        The callable function/class
    
    Raises:
        ImportError: If module cannot be imported
        AttributeError: If callable not found in module
    """
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import module '{module_name}': {e}")
    
    try:
        callable_obj = getattr(module, callable_name)
    except AttributeError as e:
        raise AttributeError(
            f"Callable '{callable_name}' not found in module '{module_name}': {e}"
        )
    
    return callable_obj


def create_job_directory(job_id: str) -> Path:
    """Create and return the job directory path."""
    job_dir = QUANT_RUNS_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    return job_dir


def write_status_file(job_dir: Path, status_data: Dict[str, Any]) -> None:
    """Write job status to status.json file."""
    status_file = job_dir / "status.json"
    with open(status_file, "w") as f:
        json.dump(status_data, f, indent=2, default=str)


def read_status_file(job_id: str) -> Optional[Dict[str, Any]]:
    """Read job status from status.json file."""
    job_dir = QUANT_RUNS_DIR / job_id
    status_file = job_dir / "status.json"
    
    if not status_file.exists():
        return None
    
    try:
        with open(status_file, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to read status file: {e}"}


async def run_job_task(
    job_id: str,
    callable_obj: Callable,
    parameters: Dict[str, Any],
    job_dir: Path
) -> None:
    """
    Background task to run the MDPS callable.
    
    Args:
        job_id: Unique job identifier
        callable_obj: The callable to execute
        parameters: Job parameters to pass to callable
        job_dir: Directory to write job outputs
    """
    job_status = active_jobs.get(job_id)
    if not job_status:
        return
    
    # Update status to running
    job_status.status = "running"
    job_status.started_at = datetime.utcnow().isoformat()
    write_status_file(job_dir, job_status.dict())
    
    try:
        # Create output files
        stdout_file = job_dir / "stdout.log"
        stderr_file = job_dir / "stderr.log"
        result_file = job_dir / "result.json"
        
        # Execute the callable
        # Check if it's a coroutine function (async)
        if asyncio.iscoroutinefunction(callable_obj):
            result = await callable_obj(**parameters)
        else:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            # Use lambda to pass kwargs to the callable
            result = await loop.run_in_executor(None, lambda: callable_obj(**parameters))
        
        # Store result
        if result is not None:
            with open(result_file, "w") as f:
                json.dump({"result": result}, f, indent=2, default=str)
            job_status.result = {"result": result}
        
        # Update status to completed
        job_status.status = "completed"
        job_status.completed_at = datetime.utcnow().isoformat()
        
    except Exception as e:
        # Update status to failed
        job_status.status = "failed"
        job_status.completed_at = datetime.utcnow().isoformat()
        job_status.error = str(e)
        
        # Write error to stderr
        stderr_file = job_dir / "stderr.log"
        with open(stderr_file, "a") as f:
            f.write(f"Error: {e}\n")
            import traceback
            f.write(traceback.format_exc())
    
    finally:
        # Always write final status
        write_status_file(job_dir, job_status.dict())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    print(f"FastAPI MDPS Wrapper starting...")
    print(f"Job output directory: {QUANT_RUNS_DIR}")
    
    # Check for MDPS_ENTRYPOINT
    entrypoint = os.getenv("MDPS_ENTRYPOINT")
    if entrypoint:
        print(f"Default MDPS_ENTRYPOINT: {entrypoint}")
    else:
        print("Warning: MDPS_ENTRYPOINT not set. Provide entrypoint in requests.")
    
    yield
    
    # Shutdown
    print("FastAPI MDPS Wrapper shutting down...")


# Create FastAPI app
app = FastAPI(
    title="MDPS FastAPI Wrapper",
    description="Dynamically imports and runs MDPS callables, managing job execution and status",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "MDPS FastAPI Wrapper",
        "version": "1.0.0",
        "description": "Dynamically imports and runs MDPS callables",
        "endpoints": {
            "POST /jobs": "Create and start a new job",
            "GET /jobs/{job_id}": "Get job status",
            "GET /jobs": "List all jobs",
            "GET /health": "Health check"
        },
        "configuration": {
            "MDPS_ENTRYPOINT": os.getenv("MDPS_ENTRYPOINT", "Not set"),
            "QUANT_RUNS_DIR": str(QUANT_RUNS_DIR)
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_jobs": len([j for j in active_jobs.values() if j.status == "running"])
    }


@app.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: JobRequest,
    background_tasks: BackgroundTasks
) -> JobResponse:
    """
    Create and start a new MDPS job.
    
    Args:
        request: Job request with parameters and optional entrypoint override
        background_tasks: FastAPI background tasks handler
    
    Returns:
        JobResponse with job ID and status file location
    
    Raises:
        HTTPException: If entrypoint configuration is invalid or callable cannot be loaded
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    try:
        # Get entrypoint
        module_name, callable_name = get_entrypoint(request.entrypoint)
        
        # Load callable
        callable_obj = load_callable(module_name, callable_name)
        
    except (ValueError, ImportError, AttributeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Create job directory
    job_dir = create_job_directory(job_id)
    
    # Create job status
    created_at = datetime.utcnow().isoformat()
    job_status = JobStatus(
        job_id=job_id,
        status="pending",
        created_at=created_at
    )
    
    # Store in active jobs
    active_jobs[job_id] = job_status
    
    # Write initial status file
    write_status_file(job_dir, job_status.dict())
    
    # Schedule background task
    background_tasks.add_task(
        run_job_task,
        job_id,
        callable_obj,
        request.parameters,
        job_dir
    )
    
    # Return response
    return JobResponse(
        job_id=job_id,
        status="pending",
        created_at=created_at,
        status_file=str(job_dir / "status.json")
    )


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str) -> JobStatus:
    """
    Get the status of a specific job.
    
    Args:
        job_id: Unique job identifier
    
    Returns:
        JobStatus with current job information
    
    Raises:
        HTTPException: If job not found
    """
    # First check in-memory
    if job_id in active_jobs:
        return active_jobs[job_id]
    
    # Try to read from status file
    status_data = read_status_file(job_id)
    if status_data:
        return JobStatus(**status_data)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Job {job_id} not found"
    )


@app.get("/jobs")
async def list_jobs(
    status_filter: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    List all jobs.
    
    Args:
        status_filter: Optional status filter (pending, running, completed, failed)
        limit: Maximum number of jobs to return
    
    Returns:
        Dictionary with jobs list and metadata
    """
    jobs = []
    
    # Get jobs from memory
    for job_status in active_jobs.values():
        if status_filter and job_status.status != status_filter:
            continue
        jobs.append(job_status.dict())
    
    # Also scan .quant_runs directory for persisted jobs
    if QUANT_RUNS_DIR.exists():
        for job_dir in QUANT_RUNS_DIR.iterdir():
            if not job_dir.is_dir():
                continue
            
            job_id = job_dir.name
            if job_id in active_jobs:
                continue  # Already have this one
            
            status_data = read_status_file(job_id)
            if status_data:
                if status_filter and status_data.get("status") != status_filter:
                    continue
                jobs.append(status_data)
    
    # Sort by created_at (newest first) and limit
    jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    jobs = jobs[:limit]
    
    return {
        "jobs": jobs,
        "count": len(jobs),
        "total": len(list(QUANT_RUNS_DIR.iterdir())) if QUANT_RUNS_DIR.exists() else 0
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
