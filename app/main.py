import os
import json
import uuid
import traceback
import importlib
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

app = FastAPI(title="MDPS Trigger API")

WORKDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(WORKDIR, ".quant_runs")
os.makedirs(OUT_DIR, exist_ok=True)

# MDPS_ENTRYPOINT format: "module.path:callable"
ENTRYPOINT = os.environ.get("MDPS_ENTRYPOINT", "src.api:call")

# tasks.yml mapping file (optional)
TASKS_FILE = os.path.join(WORKDIR, "tasks.yml")  # repo root
TASKS = {}
if os.path.exists(TASKS_FILE):
    try:
        import yaml
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            TASKS = yaml.safe_load(f) or {}
    except Exception:
        TASKS = {}

class RunRequest(BaseModel):
    params: Dict[str, Any] = {}

def _load_entrypoint(entrypoint: str):
    if ":" not in entrypoint:
        raise ValueError("ENTRYPOINT must be in module.path:callable format")
    module_name, fn_name = entrypoint.split(":", 1)
    module = importlib.import_module(module_name)
    fn = getattr(module, fn_name)
    if not callable(fn):
        raise TypeError(f"{fn_name} in {module_name} is not callable")
    return fn

def _write_status(job_id: str, payload: dict):
    path = os.path.join(OUT_DIR, f"{job_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

def _safe_call_entrypoint(fn, params: dict, job_id: str):
    try:
        _write_status(job_id, {"job_id": job_id, "status": "running"})
        result = fn(params)
        if result is None:
            _write_status(job_id, {"job_id": job_id, "status": "completed", "result": "written_by_job"})
        else:
            _write_status(job_id, {"job_id": job_id, "status": "completed", "result": result})
    except Exception as e:
        tb = traceback.format_exc()
        _write_status(job_id, {"job_id": job_id, "status": "failed", "error": str(e), "traceback": tb})

@app.post("/run")
def run_quant(req: RunRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    _write_status(job_id, {"job_id": job_id, "status": "queued"})
    try:
        fn = _load_entrypoint(ENTRYPOINT)
    except Exception as e:
        _write_status(job_id, {"job_id": job_id, "status": "failed", "error": f"entrypoint load error: {e}"})
        raise HTTPException(status_code=500, detail=f"cannot load entrypoint: {e}")
    background_tasks.add_task(_safe_call_entrypoint, fn, req.params, job_id)
    return {"job_id": job_id, "status_url": f"/status/{job_id}"}

@app.post("/run/{task_name}")
def run_task(task_name: str, req: RunRequest, background_tasks: BackgroundTasks):
    if not TASKS:
        try:
            import yaml
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                mapping = yaml.safe_load(f) or {}
        except Exception:
            mapping = {}
    else:
        mapping = TASKS

    if task_name not in mapping:
        raise HTTPException(status_code=404, detail="task not found")
    entry = mapping[task_name]
    job_id = str(uuid.uuid4())
    _write_status(job_id, {"job_id": job_id, "status": "queued", "task": task_name})
    try:
        fn = _load_entrypoint(entry)
    except Exception as e:
        _write_status(job_id, {"job_id": job_id, "status": "failed", "error": f"entrypoint load error: {e}"})
        raise HTTPException(status_code=500, detail=f"cannot load entrypoint: {e}")
    background_tasks.add_task(_safe_call_entrypoint, fn, req.params, job_id)
    return {"job_id": job_id, "status_url": f"/status/{job_id}"}

@app.get("/status/{job_id}")
def job_status(job_id: str):
    status_file = os.path.join(OUT_DIR, f"{job_id}.json")
    if not os.path.exists(status_file):
        raise HTTPException(status_code=404, detail="job not found")
    with open(status_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
