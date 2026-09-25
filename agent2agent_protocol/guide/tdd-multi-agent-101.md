# TDD Multi-Agent Pipeline: A 101 Guide

From zero to a working AI-powered TDD pipeline using Google's Agent2Agent protocol.

---

## Table of Contents

1. [What You're Building](#1-what-youre-building)
2. [Prerequisites](#2-prerequisites)
3. [Project Setup](#3-project-setup)
4. [Understanding the Architecture](#4-understanding-the-architecture)
5. [How the A2A Protocol Works](#5-how-the-a2a-protocol-works)
6. [Walkthrough: Each Agent](#6-walkthrough-each-agent)
7. [Running the Pipeline](#7-running-the-pipeline)
8. [What the Pipeline Produces](#8-what-the-pipeline-produces)
9. [Troubleshooting](#9-troubleshooting)
10. [Next Steps](#10-next-steps)

---

## 1. What You're Building

A multi-agent system that automates the Test-Driven Development (TDD) cycle:

```
  Your Requirement (plain English)
         |
         v
  +----------------+     A2A      +---------------+     A2A      +---------------+
  | Spec Analyst   | -----------> | Test Writer   | -----------> | Code Writer   |
  | (port 9001)    |   JSON spec  | (port 9002)   |  test code   | (port 9003)   |
  +----------------+              +---------------+              +---------------+
         ^                                                              |
         |                                                              v
         +------------- Orchestrator (client) <---- pytest results -----+
```

You type a requirement like *"Users can register with email and password"* and the system:

1. **Spec Analyst** breaks it into structured, testable acceptance criteria
2. **Test Writer** generates a failing pytest test suite (red phase)
3. **Code Writer** writes the minimal Python code to make all tests pass (green phase)
4. **Orchestrator** runs pytest to verify everything works

Each agent is an independent HTTP server. They discover each other and communicate via the A2A protocol.

---

## 2. Prerequisites

| Requirement | How to Get It |
|-------------|--------------|
| **Python 3.11+** | `python3 --version` to check |
| **pip** | Comes with Python |
| **Gemini API key** (free) | Go to https://aistudio.google.com/apikey and click "Create API Key" |

No cloud billing, no paid subscriptions, no Docker. Just Python and a free API key.

---

## 3. Project Setup

### 3.1 Clone or Navigate to the Project

```bash
cd agent2agent_protocol
```

### 3.2 Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `a2a-sdk[starlette]` -- The A2A protocol SDK with HTTP server support
- `google-genai` -- Google's Gemini AI SDK
- `pytest` -- Test runner
- `uvicorn` -- ASGI server for running agents
- `python-dotenv` -- Environment variable management

### 3.3 Configure Your API Key

```bash
cp .env.example .env
```

Edit `.env` and paste your Gemini API key:

```env
# Gemini API key (free from https://aistudio.google.com/apikey)
GEMINI_API_KEY=your-actual-api-key-here

# LLM model
LLM_MODEL=gemini-3.5-flash-lite

# Agent ports (defaults shown)
SPEC_ANALYST_PORT=9001
TEST_WRITER_PORT=9002
CODE_WRITER_PORT=9003
AGENT_HOST=localhost
```

### 3.4 Verify the LLM Connection

```bash
python3 -c "
from common import llm_call
print(llm_call('Reply with one word.', 'Say hello'))
"
```

Expected output: `Hello` (or similar). If you see an error, check your API key.

---

## 4. Understanding the Architecture

### File Structure

```
agent2agent_protocol/
├── common.py                      # Shared LLM client (Gemini)
├── orchestrator.py                # Client that chains the 3 agents
├── run_agents.sh                  # One-command launcher
├── .env                           # Your API key (not committed)
├── requirements.txt
│
├── agents/
│   ├── spec_analyst/
│   │   ├── agent.py               # LLM logic: requirement -> JSON spec
│   │   └── server.py              # A2A server wrapper (port 9001)
│   ├── test_writer/
│   │   ├── agent.py               # LLM logic: JSON spec -> pytest code
│   │   └── server.py              # A2A server wrapper (port 9002)
│   └── code_writer/
│       ├── agent.py               # LLM logic: tests + spec -> Python code
│       └── server.py              # A2A server wrapper (port 9003)
│
└── output/                        # Generated files land here
    ├── spec.json
    ├── test_feature.py
    └── <module>.py
```

### Separation of Concerns

Each agent has two files:

- **`agent.py`** -- Pure business logic. A Python class with one method that takes input and returns output. Knows nothing about A2A.
- **`server.py`** -- A2A protocol wrapper. Declares the agent's identity (AgentCard), handles incoming requests, and runs the HTTP server.

This means you can swap the LLM, change the prompts, or replace an entire agent without touching the protocol layer.

---

## 5. How the A2A Protocol Works

### Key Concepts

| Concept | What It Does | Where in Our Code |
|---------|-------------|-------------------|
| **AgentCard** | JSON document advertising who the agent is, what it can do, and how to reach it | `server.py` -- served at `/.well-known/agent-card.json` |
| **AgentSkill** | Declares a specific capability (e.g., "generate tests") | Inside AgentCard |
| **AgentInterface** | The URL and protocol for communicating with the agent | Inside AgentCard |
| **AgentExecutor** | Handles incoming task execution | `server.py` -- the `execute()` method |
| **Message** | A unit of communication with role (user/agent) and parts (text) | Used in both client and server |
| **Task lifecycle** | submitted -> working -> completed | Managed by the SDK |

### Communication Flow

```
1. Orchestrator fetches   GET http://localhost:9001/.well-known/agent-card.json
                          <-- Returns AgentCard with skills and interface URL

2. Orchestrator sends     POST http://localhost:9001/
                          {"jsonrpc": "2.0", "method": "message/send", "params": {...}}
                          <-- Returns the agent's response (JSON spec)

3. Repeat for agents 2 and 3
```

The orchestrator never hardcodes what an agent does -- it discovers capabilities from the AgentCard, then sends tasks via JSON-RPC.

---

## 6. Walkthrough: Each Agent

### Agent 1: Spec Analyst

**File:** `agents/spec_analyst/agent.py`

The system prompt instructs the LLM to act as a Principal QA Engineer. Given a plain-text requirement, it outputs structured JSON with Given/When/Then acceptance criteria:

```json
{
  "feature": "user_registration",
  "module": "user_auth",
  "criteria": [
    {
      "id": "AC-1",
      "given": "A user provides a unique valid email and a compliant password",
      "when": "The registration request is submitted",
      "then": "The user account is successfully created and stored",
      "function_hint": "register_user"
    }
  ]
}
```

The `module` field tells the Test Writer what Python module to import from. The `function_hint` suggests function names for the implementation.

### Agent 2: Test Writer

**File:** `agents/test_writer/agent.py`

Takes the JSON spec and generates a pytest test file. Each acceptance criterion becomes one test:

```python
def test_user_account_is_successfully_created_and_stored():
    """AC-1: Given A user provides a unique valid email..."""
    result = register_user("test@example.com", "SecurePass1!")
    assert result is True
```

These tests are designed to **fail initially** (red phase of TDD) because the functions they call don't exist yet.

### Agent 3: Code Writer

**File:** `agents/code_writer/agent.py`

Receives both the test file and the spec. Writes the **minimal** Python implementation to make all tests pass:

```python
def register_user(email: str, password: str) -> bool:
    validate_email_format(email)
    check_email_uniqueness(email)
    validate_password_strength(password)
    validate_password_complexity(password)
    _users.add(email)
    return True
```

### The A2A Server Pattern (same for all 3 agents)

Each `server.py` follows the same structure:

```python
# 1. Define the executor (bridges A2A to your agent logic)
class MyExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        user_input = context.get_user_input()
        result = self.agent.do_work(user_input)
        message = Message(role=Role.ROLE_AGENT, parts=[Part(text=result)], ...)
        await event_queue.enqueue_event(message)

# 2. Declare identity (AgentCard with skills and interface)
agent_card = AgentCard(
    name="MyAgent",
    skills=[AgentSkill(id="my_skill", ...)],
    supported_interfaces=[AgentInterface(url="http://...", protocol_binding="JSONRPC")],
    ...
)

# 3. Wire up and run
handler = DefaultRequestHandler(executor, task_store, agent_card)
routes = create_agent_card_routes(agent_card) + create_jsonrpc_routes(handler, rpc_url="/")
app = Starlette(routes=routes)
uvicorn.run(app, host="localhost", port=9001)
```

---

## 7. Running the Pipeline

### Option A: One Command

```bash
./run_agents.sh "Users can register with email and password"
```

This starts all 3 agents in the background, runs the orchestrator, and shuts everything down.

### Option B: Step by Step (recommended for learning)

**Terminal 1** -- Start the agents:

```bash
python3 -m agents.spec_analyst.server &
python3 -m agents.test_writer.server &
python3 -m agents.code_writer.server &
```

You should see:
```
Spec Analyst Agent running on http://localhost:9001
Test Writer Agent running on http://localhost:9002
Code Writer Agent running on http://localhost:9003
```

**Verify they're running** -- Open a new terminal and check the AgentCards:

```bash
curl -s http://localhost:9001/.well-known/agent-card.json | python3 -m json.tool
```

You'll see the full AgentCard JSON with the agent's name, description, skills, and interface.

**Terminal 2** -- Run the orchestrator:

```bash
python3 orchestrator.py "Users can register with email and password"
```

Or run with the default requirement:

```bash
python3 orchestrator.py
```

**Stop the agents** when done:

```bash
pkill -f "agents.spec_analyst.server"
pkill -f "agents.test_writer.server"
pkill -f "agents.code_writer.server"
```

---

## 8. What the Pipeline Produces

After a successful run, `output/` contains three files:

### `spec.json` -- Structured Acceptance Criteria

```json
{
  "feature": "user_registration",
  "module": "user_auth",
  "criteria": [
    {
      "id": "AC-1",
      "given": "A user provides a unique valid email and a compliant password",
      "when": "The registration request is submitted",
      "then": "The user account is successfully created and stored",
      "function_hint": "register_user"
    },
    {
      "id": "AC-2",
      "given": "A user provides an email address with an invalid format",
      "when": "The registration request is submitted",
      "then": "The registration fails with a validation error indicating invalid email",
      "function_hint": "validate_email_format"
    },
    {
      "id": "AC-3",
      "given": "A user provides a password with fewer than 8 characters",
      "when": "The registration request is submitted",
      "then": "The registration fails with a validation error regarding password length",
      "function_hint": "validate_password_strength"
    },
    {
      "id": "AC-4",
      "given": "A user provides a password missing an uppercase letter or a digit",
      "when": "The registration request is submitted",
      "then": "The registration fails with a validation error regarding password complexity",
      "function_hint": "validate_password_complexity"
    },
    {
      "id": "AC-5",
      "given": "An account with the specified email already exists in the system",
      "when": "A new user attempts to register with the same email",
      "then": "The registration fails with a duplicate email error",
      "function_hint": "check_email_uniqueness"
    }
  ]
}
```

### `test_feature.py` -- Failing Test Suite (Red Phase)

```python
import pytest
from user_auth import (
    register_user,
    validate_email_format,
    validate_password_strength,
    validate_password_complexity,
    check_email_uniqueness,
)


def test_user_account_is_successfully_created_and_stored():
    """AC-1"""
    result = register_user("test@example.com", "SecurePass1!")
    assert result is True


def test_registration_fails_with_a_validation_error_indicating_invalid_email():
    """AC-2"""
    with pytest.raises((ValueError, Exception)):
        validate_email_format("invalid-email-format")


def test_registration_fails_with_a_validation_error_regarding_password_length():
    """AC-3"""
    with pytest.raises((ValueError, Exception)):
        validate_password_strength("Short1!")


def test_registration_fails_with_a_validation_error_regarding_password_complexity():
    """AC-4"""
    with pytest.raises((ValueError, Exception)):
        validate_password_complexity("alllowercasepassword")


def test_registration_fails_with_a_duplicate_email_error():
    """AC-5"""
    with pytest.raises((ValueError, Exception)):
        check_email_uniqueness("existing@example.com")
```

### `user_auth.py` -- Implementation (Green Phase)

```python
import re

_users = {"existing@example.com"}


def validate_email_format(email: str) -> bool:
    if not isinstance(email, str) or "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Invalid email format")
    return True


def validate_password_strength(password: str) -> bool:
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    return True


def validate_password_complexity(password: str) -> bool:
    if not isinstance(password, str):
        raise ValueError("Invalid password")
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_upper and has_digit):
        raise ValueError("Password must contain an uppercase letter and a digit")
    return True


def check_email_uniqueness(email: str) -> bool:
    if email in _users:
        raise ValueError("Email already exists")
    return True


def register_user(email: str, password: str) -> bool:
    validate_email_format(email)
    check_email_uniqueness(email)
    validate_password_strength(password)
    validate_password_complexity(password)
    _users.add(email)
    return True
```

### pytest Output

```
test_feature.py::test_user_account_is_successfully_created_and_stored PASSED     [ 20%]
test_feature.py::test_registration_fails_with_a_validation_error_indicating_invalid_email PASSED [ 40%]
test_feature.py::test_registration_fails_with_a_validation_error_regarding_password_length PASSED [ 60%]
test_feature.py::test_registration_fails_with_a_validation_error_regarding_password_complexity PASSED [ 80%]
test_feature.py::test_registration_fails_with_a_duplicate_email_error PASSED     [100%]

============================== 5 passed in 0.09s ===============================
```

---

## 9. Troubleshooting

### "no compatible transports found"

The AgentCard is missing `supported_interfaces`. Each agent must declare:

```python
supported_interfaces=[
    AgentInterface(url=f"http://{HOST}:{PORT}/", protocol_binding="JSONRPC"),
]
```

Note: `protocol_binding` must be exactly `"JSONRPC"` (uppercase), not `"jsonrpc/http"`.

### "Client Request timed out"

The LLM call takes longer than the default HTTP timeout. The orchestrator uses a 120-second timeout via:

```python
config = ClientConfig(
    httpx_client=httpx.AsyncClient(timeout=httpx.Timeout(120.0)),
    streaming=False,
)
```

If you still see timeouts, increase `120.0` to `180.0` or higher.

### "503 UNAVAILABLE - model experiencing high demand"

Gemini free-tier models can be overloaded. Try:

1. Wait 30 seconds and retry
2. Switch to a different model in `.env`:
   ```
   LLM_MODEL=gemini-3.5-flash-lite
   ```
3. List available models:
   ```bash
   python3 -c "
   from google import genai
   from dotenv import load_dotenv; import os; load_dotenv()
   client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
   for m in client.models.list():
       if 'flash' in m.name: print(m.name)
   "
   ```

### "404 NOT_FOUND - model is no longer available"

Google deprecates models frequently. Use the listing command above to find a current model.

### "Address already in use"

A previous agent is still running on that port. Kill it:

```bash
pkill -f "agents.spec_analyst.server"
pkill -f "agents.test_writer.server"
pkill -f "agents.code_writer.server"
```

### Tests fail after generation

This is expected occasionally -- the LLM-generated code may not perfectly match the tests. Run the pipeline again or adjust the prompts in the agent's `agent.py` file.

---

## 10. Next Steps

Now that you have a working pipeline, you can:

- **Try different requirements**: `python3 orchestrator.py "Build a calculator with add, subtract, multiply, divide"`
- **Add a 4th agent**: A "Refactorer" that takes the green code and improves it (refactor phase of TDD)
- **Add streaming**: Set `capabilities=AgentCapabilities(streaming=True)` and use SSE for real-time progress
- **Add error handling**: Retry failed agents, validate JSON between steps
- **Swap the LLM**: Change `common.py` to use OpenAI, Anthropic, or a local model -- the A2A layer doesn't care
- **Deploy to separate machines**: Since agents communicate over HTTP, they can run anywhere
