# MDPS FastAPI Wrapper - Quick Start Guide

This guide will help you get the MDPS FastAPI wrapper up and running in minutes.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

## Installation

1. **Navigate to the MDPS directory**:
   ```bash
   cd /path/to/MDPS
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python app/test_setup.py
   ```
   
   You should see: `✓ All tests passed! Setup is complete and working.`

## Running the API

### Option 1: Using the startup script (Recommended)

```bash
./app/start.sh
```

This will start the API server on `http://localhost:8000`

### Option 2: Direct uvicorn command

```bash
# With default entrypoint
MDPS_ENTRYPOINT="app.example_callables:simple_example" \
  uvicorn app.main:app --host 0.0.0.0 --port 8000

# With custom entrypoint
MDPS_ENTRYPOINT="your_module:your_callable" \
  uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Option 3: Development mode with auto-reload

```bash
MDPS_ENTRYPOINT="app.example_callables:simple_example" \
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Using the API

Once the server is running, you can interact with it using any HTTP client.

### 1. Check API Health

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "active_jobs": 0
}
```

### 2. Create a Job

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"symbol": "EURUSD", "timeframe": "H1"}}'
```

**Response:**
```json
{
  "job_id": "abc123...",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00.000000",
  "status_file": "/path/to/.quant_runs/abc123.../status.json"
}
```

**Save the `job_id` for later!**

### 3. Check Job Status

```bash
curl http://localhost:8000/jobs/abc123...
```

**Response:**
```json
{
  "job_id": "abc123...",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00.000000",
  "started_at": "2024-01-01T00:00:01.000000",
  "completed_at": "2024-01-01T00:05:00.000000",
  "error": null,
  "result": {
    "result": "Your job results here"
  }
}
```

**Job Status Values:**
- `pending` - Job created, waiting to start
- `running` - Job is currently executing
- `completed` - Job finished successfully
- `failed` - Job encountered an error

### 4. List All Jobs

```bash
# List all jobs
curl http://localhost:8000/jobs

# List only completed jobs
curl "http://localhost:8000/jobs?status_filter=completed"

# List last 10 jobs
curl "http://localhost:8000/jobs?limit=10"
```

### 5. Interactive Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test all endpoints.

## Configuration

### Setting the Entrypoint

The entrypoint determines which function gets called when a job is created.

**Format**: `module:callable`

**Examples:**
```bash
# Using a module function
export MDPS_ENTRYPOINT="run_mdps:main"

# Using a class method
export MDPS_ENTRYPOINT="MDPS.main:MDPSSystem"

# Using example callables
export MDPS_ENTRYPOINT="app.example_callables:simple_example"
export MDPS_ENTRYPOINT="app.example_callables:async_example"
```

### Per-Request Entrypoint

You can override the default entrypoint per request:

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {"key": "value"},
    "entrypoint": "app.example_callables:async_example"
  }'
```

## Using with DevContainer

### VS Code

1. Install the "Dev Containers" extension
2. Open the MDPS folder in VS Code
3. Press `F1` and select "Dev Containers: Reopen in Container"
4. Wait for the container to build and dependencies to install
5. Run the API:
   ```bash
   ./app/start.sh
   ```

The API will be accessible at `http://localhost:8000`

## Example Workflows

### Example 1: Simple Job

```bash
# Start the server
./app/start.sh &

# Create a job
JOB_ID=$(curl -s -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"test": "value"}}' | jq -r .job_id)

echo "Job ID: $JOB_ID"

# Wait a few seconds
sleep 3

# Check status
curl -s http://localhost:8000/jobs/$JOB_ID | jq .
```

### Example 2: Monitoring Job Progress

```python
import requests
import time

# Create job
response = requests.post(
    "http://localhost:8000/jobs",
    json={"parameters": {"symbol": "EURUSD"}}
)
job_id = response.json()["job_id"]
print(f"Job created: {job_id}")

# Poll for completion
while True:
    response = requests.get(f"http://localhost:8000/jobs/{job_id}")
    status = response.json()
    
    print(f"Status: {status['status']}")
    
    if status["status"] in ["completed", "failed"]:
        if status["status"] == "completed":
            print(f"Result: {status['result']}")
        else:
            print(f"Error: {status['error']}")
        break
    
    time.sleep(2)
```

### Example 3: Long-Running Job

```bash
# Create a long-running job
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {"duration": 60},
    "entrypoint": "app.example_callables:long_running_example"
  }'

# The job will run for 60 seconds in the background
# You can check its status at any time
```

## Job Output Files

Each job creates a directory in `.quant_runs/{job_id}/`:

```
.quant_runs/
└── abc123.../
    ├── status.json    # Current job status
    ├── result.json    # Job results (if any)
    └── stderr.log     # Error logs (if any)
```

You can access these files directly:

```bash
# View job status
cat .quant_runs/{job_id}/status.json

# View results
cat .quant_runs/{job_id}/result.json

# Check for errors
cat .quant_runs/{job_id}/stderr.log
```

## Troubleshooting

### Problem: "MDPS_ENTRYPOINT not configured"

**Solution**: Set the environment variable:
```bash
export MDPS_ENTRYPOINT="module:callable"
```

Or provide it in the request:
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"entrypoint": "module:callable", "parameters": {}}'
```

### Problem: "Failed to import module"

**Solution**: Ensure PYTHONPATH includes the project root:
```bash
export PYTHONPATH=/path/to/MDPS:$PYTHONPATH
```

### Problem: Port 8000 already in use

**Solution**: Use a different port:
```bash
uvicorn app.main:app --port 8001
```

### Problem: Job stays in "pending" status

**Solution**: Check the server logs for errors. The job may have failed to start.

### Problem: Job results not showing

**Solution**: 
1. Check `.quant_runs/{job_id}/result.json` for raw output
2. Ensure your callable returns a JSON-serializable value
3. Check `.quant_runs/{job_id}/stderr.log` for errors

## Next Steps

- Read the full [API Documentation](app/README.md)
- Create your own callables (see `app/example_callables.py` for examples)
- Integrate with your existing MDPS workflows
- Deploy to production with proper authentication and security

## Support

For issues or questions:
- Check the full documentation in `app/README.md`
- Run the test suite: `python app/test_setup.py`
- Review example callables: `app/example_callables.py`

---

**Happy Job Running! 🚀**
