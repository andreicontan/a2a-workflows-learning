#!/bin/bash
# Start all API pipeline A2A agents, then run the API orchestrator.
# Usage: ./run_api_agents.sh ["your API requirement here"]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting API Agent Pipeline..."
echo ""

# Start API agents in background
echo "Starting API Analyst on :9010..."
python3 -m agents.api_analyst.server &
PID_ANALYST=$!

echo "Starting OpenAPI Writer on :9011..."
python3 -m agents.openapi_writer.server &
PID_OPENAPI=$!

echo "Starting API Test Generator on :9012..."
python3 -m agents.api_test_generator.server &
PID_TESTGEN=$!

echo "Starting Stub Server Writer on :9013..."
python3 -m agents.stub_server_writer.server &
PID_STUB=$!

echo "Starting MR Creator on :9004..."
python3 -m agents.mr_creator.server &
PID_MR=$!

# Wait for servers to be ready
echo ""
echo "Waiting for agents to start..."
sleep 3

# Run the API orchestrator
echo ""
if [ -n "$1" ]; then
    python3 api_orchestrator.py "$1"
else
    python3 api_orchestrator.py
fi

# Cleanup
echo ""
echo "Shutting down agents..."
kill $PID_ANALYST $PID_OPENAPI $PID_TESTGEN $PID_STUB $PID_MR 2>/dev/null || true
wait $PID_ANALYST $PID_OPENAPI $PID_TESTGEN $PID_STUB $PID_MR 2>/dev/null || true
echo "Done."
