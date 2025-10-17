#!/bin/bash
# MDPS FastAPI Wrapper Startup Script

# Default configuration
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-1}"
RELOAD="${RELOAD:-false}"

# Set default entrypoint if not set
if [ -z "$MDPS_ENTRYPOINT" ]; then
    echo "Warning: MDPS_ENTRYPOINT not set. Using example: app.example_callables:simple_example"
    export MDPS_ENTRYPOINT="app.example_callables:simple_example"
fi

echo "Starting MDPS FastAPI Wrapper..."
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Entrypoint: $MDPS_ENTRYPOINT"
echo "  Reload: $RELOAD"
echo ""

# Build uvicorn command
CMD="uvicorn app.main:app --host $HOST --port $PORT --workers $WORKERS"

if [ "$RELOAD" = "true" ]; then
    CMD="$CMD --reload"
fi

# Run the server
exec $CMD
