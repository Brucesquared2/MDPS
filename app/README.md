# MDPS FastAPI Wrapper

A minimal FastAPI wrapper that dynamically imports and runs MDPS callables, returning job IDs and status files.

## Overview

This FastAPI application provides a REST API to run MDPS processing jobs asynchronously. Jobs are executed in background tasks, with status and outputs written to `.quant_runs/{job_id}/` directories.

## Features

- **Dynamic Entrypoint Loading**: Configurable via `MDPS_ENTRYPOINT` environment variable
- **Asynchronous Job Execution**: Jobs run in background tasks without blocking the API
- **Job Status Tracking**: Real-time status updates written to JSON files
- **Job History**: Persistent job data stored in `.quant_runs/` directory
- **RESTful API**: Standard HTTP endpoints for creating and monitoring jobs

## Installation

### Prerequisites

- Python 3.9+
- FastAPI and dependencies (automatically installed from requirements.txt)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set the MDPS_ENTRYPOINT environment variable (optional, can be set per-request):
```bash
export MDPS_ENTRYPOINT="module:callable"
```

Example:
```bash
export MDPS_ENTRYPOINT="run_mdps:main"
```

## Running the API

### Standard Mode

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or directly:
```bash
python app/main.py
```

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### In DevContainer

Open the project in VS Code with the Dev Containers extension, and the API will be set up automatically:

1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Select "Dev Containers: Reopen in Container"
3. Wait for container setup to complete
4. Run: `python app/main.py`

The API will be accessible at `http://localhost:8000`

## API Endpoints

### Root - GET `/`
Get API information and configuration.

**Response:**
```json
{
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
    "MDPS_ENTRYPOINT": "run_mdps:main",
    "QUANT_RUNS_DIR": "/path/to/.quant_runs"
  }
}
```

### Health Check - GET `/health`
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "active_jobs": 2
}
```

### Create Job - POST `/jobs`
Create and start a new MDPS job.

**Request Body:**
```json
{
  "parameters": {
    "key": "value"
  },
  "entrypoint": "module:callable"  // Optional, overrides MDPS_ENTRYPOINT
}
```

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00.000000",
  "status_file": "/path/to/.quant_runs/a1b2c3d4-.../status.json"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"symbol": "EURUSD", "timeframe": "H1"}}'
```

### Get Job Status - GET `/jobs/{job_id}`
Get the status of a specific job.

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00.000000",
  "started_at": "2024-01-01T00:00:01.000000",
  "completed_at": "2024-01-01T00:05:00.000000",
  "error": null,
  "result": {
    "result": "Job output data"
  }
}
```

**Job Status Values:**
- `pending`: Job created but not yet started
- `running`: Job is currently executing
- `completed`: Job finished successfully
- `failed`: Job encountered an error

**Example:**
```bash
curl http://localhost:8000/jobs/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### List Jobs - GET `/jobs`
List all jobs with optional filtering.

**Query Parameters:**
- `status_filter` (optional): Filter by status (pending, running, completed, failed)
- `limit` (optional): Maximum number of jobs to return (default: 100)

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "...",
      "status": "completed",
      "created_at": "...",
      ...
    }
  ],
  "count": 5,
  "total": 42
}
```

**Example:**
```bash
# List all jobs
curl http://localhost:8000/jobs

# List only running jobs
curl http://localhost:8000/jobs?status_filter=running

# List last 10 jobs
curl http://localhost:8000/jobs?limit=10
```

## Job Output Files

Each job creates a directory in `.quant_runs/{job_id}/` with the following files:

- `status.json` - Current job status and metadata
- `stdout.log` - Standard output (if any)
- `stderr.log` - Standard error and exceptions
- `result.json` - Job result data (if callable returns a value)

### Example status.json:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00.000000",
  "started_at": "2024-01-01T00:00:01.000000",
  "completed_at": "2024-01-01T00:05:00.000000",
  "error": null,
  "result": {
    "result": "Success"
  }
}
```

## Configuration

### Environment Variables

- `MDPS_ENTRYPOINT`: Default entrypoint for job execution (format: `module:callable`)
- `PYTHONPATH`: Add project paths for module imports

### Entrypoint Format

The entrypoint must be in the format `module:callable`:

- **module**: Python module path (e.g., `MDPS.main`, `run_mdps`)
- **callable**: Function or class name within the module (e.g., `main`, `run_analysis`)

**Valid Examples:**
- `run_mdps:main`
- `MDPS.main:MDPSSystem`
- `my_module.analysis:run_analysis`

**Invalid Examples:**
- `run_mdps.main` (missing colon separator)
- `run_mdps:` (missing callable name)
- `:main` (missing module name)

### Custom Callables

Your callable can be:
- A regular function: `def my_function(**kwargs):`
- An async function: `async def my_async_function(**kwargs):`
- A callable class: `class MyCallable: def __call__(self, **kwargs):`

**Important:** The callable should accept keyword arguments (`**kwargs`) for parameters.

## Examples

### Python Client Example

```python
import requests
import time

# Create a job
response = requests.post(
    "http://localhost:8000/jobs",
    json={
        "parameters": {
            "symbol": "EURUSD",
            "timeframe": "H1"
        }
    }
)
job = response.json()
job_id = job["job_id"]
print(f"Job created: {job_id}")

# Poll for status
while True:
    response = requests.get(f"http://localhost:8000/jobs/{job_id}")
    status = response.json()
    
    print(f"Status: {status['status']}")
    
    if status["status"] in ["completed", "failed"]:
        if status["status"] == "completed":
            print(f"Result: {status.get('result')}")
        else:
            print(f"Error: {status.get('error')}")
        break
    
    time.sleep(5)
```

### JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

async function runJob() {
  // Create job
  const createResponse = await axios.post('http://localhost:8000/jobs', {
    parameters: {
      symbol: 'EURUSD',
      timeframe: 'H1'
    }
  });
  
  const jobId = createResponse.data.job_id;
  console.log(`Job created: ${jobId}`);
  
  // Poll for status
  while (true) {
    const statusResponse = await axios.get(`http://localhost:8000/jobs/${jobId}`);
    const status = statusResponse.data;
    
    console.log(`Status: ${status.status}`);
    
    if (status.status === 'completed' || status.status === 'failed') {
      if (status.status === 'completed') {
        console.log(`Result: ${JSON.stringify(status.result)}`);
      } else {
        console.log(`Error: ${status.error}`);
      }
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 5000));
  }
}

runJob().catch(console.error);
```

## Testing

### Manual Testing

1. Start the API:
```bash
python app/main.py
```

2. Create a test job:
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"parameters": {}}'
```

3. Check job status:
```bash
curl http://localhost:8000/jobs/{job_id}
```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

**1. MDPS_ENTRYPOINT not set**
```
Solution: Set the environment variable or provide entrypoint in request:
export MDPS_ENTRYPOINT="run_mdps:main"
```

**2. Module import error**
```
Solution: Ensure PYTHONPATH includes the project root:
export PYTHONPATH=/path/to/MDPS
```

**3. Callable not found**
```
Solution: Verify the callable exists in the module:
python -c "from module import callable_name; print(callable_name)"
```

**4. Port already in use**
```
Solution: Change the port or kill the process using port 8000:
uvicorn app.main:app --port 8001
```

### Debug Mode

Enable debug logging:
```bash
uvicorn app.main:app --log-level debug
```

### Logs

Check job-specific logs in `.quant_runs/{job_id}/`:
- `stdout.log` - Standard output
- `stderr.log` - Errors and exceptions
- `status.json` - Current status

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (app/main.py) │
└────────┬────────┘
         │
         ├──> POST /jobs ──> Background Task ──> MDPS Callable
         │                        │
         │                        v
         │                   .quant_runs/{job_id}/
         │                        ├── status.json
         │                        ├── stdout.log
         │                        ├── stderr.log
         │                        └── result.json
         │
         └──> GET /jobs/{job_id} ──> Read status.json
```

## Contributing

When adding new features:

1. Maintain backwards compatibility
2. Update API documentation
3. Add tests if applicable
4. Follow existing code style

## License

Same as parent MDPS project.
