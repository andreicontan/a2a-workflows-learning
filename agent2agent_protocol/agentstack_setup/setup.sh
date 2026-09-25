#!/bin/bash
# Setup TDD agents in AgentStack
# Run this from the agentstack_setup/ directory

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== TDD Multi-Agent AgentStack Setup ==="
echo ""

# Check API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "ERROR: Set GEMINI_API_KEY first: export GEMINI_API_KEY=your-key"
    echo "  Get a free key at https://aistudio.google.com/apikey"
    exit 1
fi

# Step 1: Build and register Spec Analyst
echo "[1/3] Building Spec Analyst agent..."
agentstack client-side-build \
    --dockerfile Dockerfile.spec-analyst \
    --tag tdd-spec-analyst:latest \
    "$SCRIPT_DIR"
echo "  Done."

# Step 2: Build and register Test Writer
echo ""
echo "[2/3] Building Test Writer agent..."
agentstack client-side-build \
    --dockerfile Dockerfile.test-writer \
    --tag tdd-test-writer:latest \
    "$SCRIPT_DIR"
echo "  Done."

# Step 3: Build and register Code Writer
echo ""
echo "[3/3] Building Code Writer agent..."
agentstack client-side-build \
    --dockerfile Dockerfile.code-writer \
    --tag tdd-code-writer:latest \
    "$SCRIPT_DIR"
echo "  Done."

# Step 4: Set env vars on each agent
echo ""
echo "Configuring environment variables..."
for AGENT in "Spec Analyst" "Test Writer" "Code Writer"; do
    agentstack env add "$AGENT" \
        GEMINI_API_KEY="$GEMINI_API_KEY" \
        LLM_MODEL="${LLM_MODEL:-gemini-3.5-flash-lite}" \
        -y 2>/dev/null && echo "  $AGENT: env configured" || echo "  $AGENT: env will be set after first run"
done

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Verify with: agentstack list"
echo "Run an agent: agentstack run 'Spec Analyst'"
