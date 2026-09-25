#!/bin/bash
# Start all 4 A2A agent servers in the background, then run the orchestrator.
# Usage: ./run_agents.sh ["your requirement here"]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting TDD Agent Pipeline..."
echo ""

# Start agents in background
echo "Starting Spec Analyst on :9001..."
python3 -m agents.spec_analyst.server &
PID_SPEC=$!

echo "Starting Test Writer on :9002..."
python3 -m agents.test_writer.server &
PID_TEST=$!

echo "Starting Code Writer on :9003..."
python3 -m agents.code_writer.server &
PID_CODE=$!

echo "Starting MR Creator on :9004..."
python3 -m agents.mr_creator.server &
PID_MR=$!

# Wait for servers to be ready
echo ""
echo "Waiting for agents to start..."
sleep 3

# Run the orchestrator
echo ""
if [ -n "$1" ]; then
    python3 orchestrator.py "$1"
else
    python3 orchestrator.py
fi

# Cleanup
echo ""
echo "Shutting down agents..."
kill $PID_SPEC $PID_TEST $PID_CODE $PID_MR 2>/dev/null || true
wait $PID_SPEC $PID_TEST $PID_CODE $PID_MR 2>/dev/null || true
echo "Done."
