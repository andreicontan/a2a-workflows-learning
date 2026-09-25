# Getting Started with A2A TDD Agents

A beginner-friendly guide to understanding, setting up, and running multi-agent AI workflows using Google's Agent2Agent (A2A) protocol.

---

## What is this project?

This project uses **AI agents that talk to each other** to automate software development tasks. Instead of one big AI doing everything, we have small, focused agents — each one is an expert at one thing.

Think of it like a software team:

```
+-------------+     +-----------+     +------------+     +-----------+
|  Analyst    | --> | Tester    | --> | Developer  | --> | Reviewer  |
| "What do   |     | "Write    |     | "Write the |     | "Write    |
|  we need?" |     |  tests"   |     |  code"     |     |  the MR"  |
+-------------+     +-----------+     +------------+     +-----------+
```

Each "person" is an AI agent running as its own web server. They communicate using a standard protocol called **A2A** (Agent-to-Agent), created by Google.

---

## Key Concepts (Plain English)

### What is an Agent?

An agent is a small program that:
1. **Listens** on a port (like a website)
2. **Receives** a task (text input)
3. **Thinks** (calls an AI model)
4. **Responds** with a result

### What is the A2A Protocol?

A2A is a set of rules for how agents find and talk to each other:

```
 Agent A                                    Agent B
    |                                          |
    |   1. "Who are you?"                      |
    |   GET /.well-known/agent-card.json  ---> |
    |   <--- JSON: name, skills, URL           |
    |                                          |
    |   2. "Do this task"                      |
    |   POST / (JSON-RPC message)         ---> |
    |   <--- Result text                       |
    |                                          |
```

- **AgentCard**: A JSON file that says "Hi, I'm the Test Writer, I can generate pytest tests, talk to me at port 9002"
- **Skill**: What an agent can do (e.g., "generate_tests")
- **Message**: The text sent between agents
- **Task**: A unit of work that goes through states: submitted -> working -> completed

### What is an Orchestrator?

The orchestrator is the **boss**. It doesn't do the work itself — it tells each agent what to do, in order, and passes results from one agent to the next.

```
Orchestrator (the boss)
    |
    |-- "Here's a requirement" --> Agent 1 (Analyst)
    |                              returns: structured spec
    |
    |-- "Here's the spec"     --> Agent 2 (Tester)
    |                              returns: test file
    |
    |-- "Here's the tests"    --> Agent 3 (Developer)
    |                              returns: code
    |
    |-- Runs pytest to verify
    |
    |-- "Here's everything"   --> Agent 4 (Reviewer)
    |                              returns: MR description
    Done!
```

---

## This Project Has Two Pipelines

### Pipeline 1: TDD (Test-Driven Development)

Turns a requirement into **working, tested Python code**.

```
                    TDD PIPELINE
                    ============

  "Users can register       Spec Analyst         Test Writer
   with email and    -----> (port 9001)   -----> (port 9002)
   password"                     |                    |
                            JSON spec            pytest file
                         (what to build)     (tests that fail)
                                                      |
                                                      v
                            MR Creator          Code Writer
                            (port 9004) <------ (port 9003)
                                 |                    |
                          MR description       Python code
                                            (makes tests pass)
                                                      |
                                                      v
                                                   pytest
                                                (all green!)
```

**Input**: Plain English requirement
**Output**: `spec.json` + `test_feature.py` + `<module>.py` + `mr_description.md`

### Pipeline 2: API (OpenAPI + Acceptance Tests)

Turns a requirement into an **OpenAPI spec, API tests, and a running stub server**.

```
                    API PIPELINE
                    ============

  "Build a REST API      API Analyst          OpenAPI Writer
   for a todo list" ---> (port 9010)   -----> (port 9011)
                              |                    |
                         JSON design          openapi.yaml
                      (endpoints, methods)   (formal spec)
                                                   |
                                                   v
                         Stub Server         API Test Generator
                           Writer            (port 9012)
                         (port 9013) <-----------  |
                              |                    |
                        stub_server.py        test_api.py
                       (FastAPI app)     (pytest + requests)
                              |                    |
                              v                    v
                         Start server ----> Run tests against it
                                                   |
                                                   v
                                             MR Creator
                                             (port 9004)
                                                   |
                                            mr_description.md
```

**Input**: Plain English API requirement
**Output**: `api_spec.json` + `openapi.yaml` + `test_api.py` + `stub_server.py` + `mr_description.md`

---

## Setup (5 minutes)

### What You Need

- **Python 3.11 or newer** (check: `python3 --version`)
- **pip** (comes with Python)
- **A free Gemini API key** from Google

### Step 1: Get a Free API Key

1. Go to https://aistudio.google.com/apikey
2. Click **"Create API Key"**
3. Copy the key (starts with `AI...`)

No credit card. No billing. Completely free.

### Step 2: Clone the Project

```bash
git clone https://github.com/YOUR_USERNAME/a2a-tdd-agents.git
cd a2a-tdd-agents
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
| Package | What it does |
|---------|-------------|
| `a2a-sdk[starlette]` | The A2A protocol — lets agents talk to each other |
| `google-genai` | Connects to Google's Gemini AI |
| `pytest` | Runs the generated tests |
| `uvicorn` | Web server that runs each agent |
| `requests` | HTTP client for API tests |
| `fastapi` | Framework for the stub server |

### Step 4: Configure Your API Key

```bash
cp .env.example .env
```

Open `.env` in any text editor and paste your key:

```
GEMINI_API_KEY=paste-your-key-here
LLM_MODEL=gemini-3.5-flash-lite
```

### Step 5: Verify It Works

```bash
python3 -c "from common import llm_call; print(llm_call('Say one word.', 'Hello'))"
```

You should see a single word like `Hello`. If you get an error, double-check your API key.

---

## Running Pipeline 1: TDD

### One-Command Run

```bash
./run_agents.sh "Users can register with email and password"
```

### Step-by-Step Run (recommended for learning)

**Terminal 1** — Start the agents:

```bash
python3 -m agents.spec_analyst.server &
python3 -m agents.test_writer.server &
python3 -m agents.code_writer.server &
python3 -m agents.mr_creator.server &
```

You should see:
```
Spec Analyst Agent running on http://localhost:9001
Test Writer Agent running on http://localhost:9002
Code Writer Agent running on http://localhost:9003
MR Creator Agent running on http://localhost:9004
```

**Terminal 2** — Run the orchestrator:

```bash
python3 orchestrator.py "Users can register with email and password"
```

**What happens:**

```
[1/4] Spec Analyst -> Analyzing requirements...          ~10 seconds
[2/4] Test Writer -> Generating failing tests...         ~10 seconds
[3/4] Code Writer -> Implementing code to pass tests...  ~10 seconds
       VERIFICATION: Running pytest...                   ~1 second
[4/4] MR Creator -> Generating merge request...          ~10 seconds

PIPELINE COMPLETE
  spec.json           <- acceptance criteria
  test_feature.py     <- 5 pytest tests
  user_auth.py        <- Python implementation
  mr_description.md   <- ready-to-use MR description
```

**Stop the agents when done:**

```bash
pkill -f "agents.spec_analyst.server"
pkill -f "agents.test_writer.server"
pkill -f "agents.code_writer.server"
pkill -f "agents.mr_creator.server"
```

---

## Running Pipeline 2: API

### One-Command Run

```bash
./run_api_agents.sh "Build a REST API for a todo list with CRUD operations"
```

### Step-by-Step Run

**Terminal 1** — Start the agents:

```bash
python3 -m agents.api_analyst.server &
python3 -m agents.openapi_writer.server &
python3 -m agents.api_test_generator.server &
python3 -m agents.stub_server_writer.server &
python3 -m agents.mr_creator.server &
```

**Terminal 2** — Run the API orchestrator:

```bash
python3 api_orchestrator.py "Build a REST API for a todo list with CRUD operations"
```

**What happens:**

```
[1/5] API Analyst -> Designing API endpoints...          ~10 seconds
[2/5] OpenAPI Writer -> Generating OpenAPI YAML...       ~10 seconds
[3/5] API Test Generator -> Writing acceptance tests...  ~10 seconds
[4/5] Stub Server Writer -> Generating FastAPI stub...   ~10 seconds
       VERIFICATION: Starting server + running pytest... ~15 seconds
[5/5] MR Creator -> Generating merge request...          ~10 seconds

PIPELINE COMPLETE
  api_spec.json       <- endpoint design
  openapi.yaml        <- OpenAPI 3.0 specification
  test_api.py         <- API acceptance tests (pytest + requests)
  stub_server.py      <- working FastAPI server
  mr_description.md   <- MR description
```

**Stop the agents:**

```bash
pkill -f "agents.api_analyst.server"
pkill -f "agents.openapi_writer.server"
pkill -f "agents.api_test_generator.server"
pkill -f "agents.stub_server_writer.server"
pkill -f "agents.mr_creator.server"
```

---

## Project Structure

```
a2a-tdd-agents/
|
|-- common.py                  <- Shared AI client (Gemini)
|
|-- orchestrator.py            <- TDD pipeline orchestrator
|-- api_orchestrator.py        <- API pipeline orchestrator
|
|-- run_agents.sh              <- Start TDD pipeline (one command)
|-- run_api_agents.sh          <- Start API pipeline (one command)
|
|-- agents/                    <- All the AI agents
|   |
|   |-- [TDD Pipeline Agents]
|   |-- spec_analyst/          <- Requirement -> JSON spec
|   |   |-- agent.py           <-   AI logic (system prompt + LLM call)
|   |   +-- server.py          <-   A2A web server (port 9001)
|   |-- test_writer/           <- JSON spec -> pytest tests
|   |   |-- agent.py
|   |   +-- server.py          <-   port 9002
|   |-- code_writer/           <- Tests -> Python code
|   |   |-- agent.py
|   |   +-- server.py          <-   port 9003
|   |
|   |-- [API Pipeline Agents]
|   |-- api_analyst/           <- Requirement -> API design JSON
|   |   |-- agent.py
|   |   +-- server.py          <-   port 9010
|   |-- openapi_writer/        <- API JSON -> OpenAPI YAML
|   |   |-- agent.py
|   |   +-- server.py          <-   port 9011
|   |-- api_test_generator/    <- OpenAPI -> pytest + requests tests
|   |   |-- agent.py
|   |   +-- server.py          <-   port 9012
|   |-- stub_server_writer/    <- OpenAPI + tests -> FastAPI stub
|   |   |-- agent.py
|   |   +-- server.py          <-   port 9013
|   |
|   |-- [Shared Agent]
|   +-- mr_creator/            <- All artifacts -> MR description
|       |-- agent.py
|       +-- server.py          <-   port 9004
|
|-- output/                    <- TDD pipeline output files
|-- api_output/                <- API pipeline output files
|
|-- requirements.txt
+-- .env                       <- Your API key (not committed)
```

---

## How Every Agent is Built (The Pattern)

Every agent follows the exact same two-file pattern:

### File 1: `agent.py` — The Brain

```python
from common import llm_call

SYSTEM_PROMPT = """You are a [role]. Given [input], produce [output]..."""

class MyAgent:
    def do_work(self, input_text: str) -> str:
        return llm_call(SYSTEM_PROMPT, input_text)
```

That's it. One class, one method, one LLM call.

### File 2: `server.py` — The Body

```python
# 1. Wrap the agent in an A2A Executor
class MyExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        input = context.get_user_input()
        result = self.agent.do_work(input)
        message = Message(role=Role.ROLE_AGENT, parts=[Part(text=result)])
        await event_queue.enqueue_event(message)

# 2. Declare an AgentCard (identity + skills)
agent_card = AgentCard(
    name="MyAgent",
    skills=[AgentSkill(id="my_skill", name="My Skill", ...)],
    supported_interfaces=[AgentInterface(url="http://...", protocol_binding="JSONRPC")],
)

# 3. Create routes and run
routes = create_agent_card_routes(agent_card) + create_jsonrpc_routes(handler, rpc_url="/")
app = Starlette(routes=routes)
uvicorn.run(app, port=9001)
```

**To create a new agent**: copy any existing agent folder, change the system prompt in `agent.py`, and change the port/skill in `server.py`.

---

## Inspecting an Agent

While agents are running, you can talk to them directly:

### See an agent's identity card

```bash
curl -s http://localhost:9001/.well-known/agent-card.json | python3 -m json.tool
```

Returns:
```json
{
    "name": "SpecAnalystAgent",
    "description": "Converts raw requirements into structured testable acceptance criteria.",
    "version": "1.0.0",
    "skills": [
        {
            "id": "analyze_requirements",
            "name": "Analyze Requirements",
            "description": "Converts raw user stories into structured...",
            "tags": ["requirements", "specification", "tdd"]
        }
    ]
}
```

### Check all agents are running

```bash
for port in 9001 9002 9003 9004; do
    name=$(curl -s http://localhost:$port/.well-known/agent-card.json | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])" 2>/dev/null)
    echo "Port $port: $name"
done
```

---

## Try These Requirements

### TDD Pipeline (`orchestrator.py`)

```bash
# Simple logic
python3 orchestrator.py "Check if a year is a leap year"

# Data validation
python3 orchestrator.py "Validate credit card numbers using the Luhn algorithm"

# String manipulation
python3 orchestrator.py "Convert Roman numerals to integers and back"
```

### API Pipeline (`api_orchestrator.py`)

```bash
# Classic CRUD
python3 api_orchestrator.py "Build a REST API for a bookstore with books and authors"

# Simple service
python3 api_orchestrator.py "Create an API for a URL shortener service"

# With authentication
python3 api_orchestrator.py "Build a notes API where users can create, read, update, and delete personal notes"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `ValueError: No API key` | Check your `.env` file has `GEMINI_API_KEY=...` |
| `503 UNAVAILABLE` | Gemini is overloaded. Wait 30 seconds, retry. |
| `Client Request timed out` | LLM is slow. The timeout is 120s — just wait. |
| `Address already in use` | Old agent still running. Run: `pkill -f "agents."` |
| Tests fail after generation | Normal — LLM output varies. Run the pipeline again. |

---

## Next Steps

Once you're comfortable running the pipelines, try:

1. **Read an agent's system prompt** — Open any `agent.py` to see how the AI is instructed
2. **Modify a system prompt** — Change how an agent behaves (no code changes needed)
3. **Create your own agent** — Copy a folder, change the prompt and port
4. **Chain differently** — Edit the orchestrator to skip or reorder agents
5. **Swap the LLM** — Change `common.py` to use OpenAI, Anthropic, or a local model
