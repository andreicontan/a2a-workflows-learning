# TDD Multi-Agent Pipeline (A2A Protocol)

A simple multi-agent system that automates the TDD cycle using Google's Agent2Agent protocol.

```
Requirement → Spec Analyst → Test Writer → Code Writer → pytest ✓
                (A2A)          (A2A)         (A2A)
```

## Architecture

| Agent | Port | A2A Skill | Input | Output |
|-------|------|-----------|-------|--------|
| **Spec Analyst** | 9001 | `analyze_requirements` | Raw user story | Structured JSON spec (Given/When/Then) |
| **Test Writer** | 9002 | `generate_tests` | JSON spec | Failing pytest test file |
| **Code Writer** | 9003 | `implement_code` | Tests + spec | Python implementation |
| **Orchestrator** | — | Client only | Requirement string | All files + pytest run |

Each agent runs as an independent A2A server (Starlette + uvicorn). The orchestrator discovers them via AgentCards and chains tasks through the pipeline.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
# Edit .env with your Google Cloud project ID

# 3. Run the full pipeline
./run_agents.sh "Users can register with email and password"
```

Or run step-by-step:

```bash
# Terminal 1: Start agents
python -m agents.spec_analyst.server &
python -m agents.test_writer.server &
python -m agents.code_writer.server &

# Terminal 2: Run orchestrator
python orchestrator.py "Users can reset their password via email"
```

## Output

Generated files land in `output/`:
- `spec.json` — Structured acceptance criteria
- `test_feature.py` — Failing test suite (red phase)
- `<module>.py` — Implementation (green phase)

## A2A Protocol Concepts Used

- **AgentCard** — Each agent advertises identity, URL, and skills at `/.well-known/agent.json`
- **AgentSkill** — Declares what each agent can do
- **AgentExecutor** — Handles incoming task execution
- **A2AClient** — Orchestrator discovers and calls agents
- **Task lifecycle** — submitted → working → completed
