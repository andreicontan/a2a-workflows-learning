# TDD Agents for AgentStack

The same 3 TDD agents (Spec Analyst, Test Writer, Code Writer) packaged for the AgentStack platform.

## Structure

```
agentstack_setup/
├── src/tdd_agents/
│   ├── llm.py              # Shared Gemini LLM client
│   ├── spec_analyst.py     # Requirements -> JSON spec
│   ├── test_writer.py      # JSON spec -> pytest tests
│   └── code_writer.py      # Tests + spec -> implementation
├── Dockerfile.spec-analyst
├── Dockerfile.test-writer
├── Dockerfile.code-writer
├── pyproject.toml
└── setup.sh                # Build & register all 3 agents
```

## Quick Setup

```bash
# 1. Make sure AgentStack is running
agentstack platform start

# 2. Set your Gemini API key
export GEMINI_API_KEY=your-key-here

# 3. Build and register all agents
./setup.sh

# 4. Verify
agentstack list
```

## Run Agents

```bash
# Via AgentStack CLI
agentstack run "Spec Analyst"

# Or test locally without Docker
cd agentstack_setup
pip install -e .
GEMINI_API_KEY=your-key python3 -m tdd_agents.spec_analyst
```

## Key Difference from the A2A-only Version

| | A2A Direct (`agents/`) | AgentStack (`agentstack_setup/`) |
|---|---|---|
| Runtime | Raw uvicorn processes | Docker containers managed by AgentStack |
| Discovery | Manual `curl` to AgentCard | `agentstack list` / `agentstack info` |
| Running | `python3 -m agents.spec_analyst.server` | `agentstack run "Spec Analyst"` |
| Env vars | `.env` file | `agentstack env add KEY=VALUE` |
| SDK | `a2a-sdk` directly | `agentstack-sdk` (wraps a2a-sdk) |
