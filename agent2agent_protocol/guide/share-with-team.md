# Communication Templates

Ready-to-use messages for sharing the A2A TDD Agents project with your team.

---

## Slack / Teams Message (Short)

```
Hey team! I've been exploring Google's Agent2Agent (A2A) protocol and built a hands-on playground you can try.

It's a multi-agent system where AI agents collaborate like a dev team:
- One agent analyzes requirements
- Another writes tests
- Another writes the code
- Another writes the MR description

You type a requirement in plain English → get working, tested code + an MR description out the other end.

Two pipelines available:
1. TDD: Requirement → Tests → Code → MR
2. API: Requirement → OpenAPI spec → API tests → Stub server → MR

Setup takes ~5 minutes (free Gemini API key, no billing).

Interactive guide: [link to interactive-guide.html]
Repo: [link to repo]

If you're curious about how AI agents can work together instead of doing everything in a single prompt, this is a good starting point. Happy to walk anyone through it.
```

---

## Email (Longer, for wider audience)

```
Subject: Hands-on playground: AI agents that collaborate using Google's A2A protocol

Hi everyone,

I wanted to share something I've been building to learn about multi-agent AI systems. It's a practical, working example you can run locally in about 5 minutes.

THE IDEA

Instead of sending one big prompt to an AI and hoping for the best, what if we had specialized AI agents — each expert at one thing — that collaborate like a real dev team?

That's what Google's Agent2Agent (A2A) protocol enables. It's an open standard (announced April 2025) that lets AI agents discover each other, communicate, and hand off work — regardless of what framework or language they're built with.

WHAT I BUILT

A learning playground with two working pipelines:

Pipeline 1 — TDD (Test-Driven Development)
You type: "Users can register with email and password"
You get:
  - Structured acceptance criteria (JSON)
  - A pytest test suite (failing tests first — red phase)
  - A Python implementation that makes all tests pass (green phase)
  - A ready-to-paste merge request description

Pipeline 2 — API Development
You type: "Build a REST API for a todo list"
You get:
  - API endpoint design
  - An OpenAPI 3.0 specification (YAML)
  - API acceptance tests (pytest + requests)
  - A working FastAPI stub server
  - A merge request description

Each step is handled by a different AI agent, running as its own HTTP server, communicating via the A2A protocol.

WHY THIS MATTERS

- Agents are composable: swap one out without touching the others
- Agents are discoverable: each advertises what it can do via a standard JSON card
- Agents are language/framework agnostic: the protocol is HTTP + JSON-RPC
- This pattern scales: add new agents, reorder them, or run them on different machines

HOW TO TRY IT

1. Get a free Gemini API key (no credit card): https://aistudio.google.com/apikey
2. Clone the repo: [link]
3. pip install -r requirements.txt
4. Copy .env.example to .env, paste your key
5. Run: ./run_agents.sh "Check if a year is a leap year"

There's also an interactive HTML guide with diagrams and knowledge-check quizzes if you want a structured walkthrough before running anything.

I'd love feedback — especially if you see ways this pattern could apply to our work.

[Your name]
```

---

## Lunch & Learn / Demo Script (5 min pitch)

```
SLIDE 1: The Problem
- We use AI as a single-shot tool: one prompt, one response
- Complex tasks need multiple skills: analysis, testing, coding, review
- One prompt trying to do everything produces inconsistent results

SLIDE 2: The Idea
- What if AI agents specialized, like a team?
- Each agent does ONE thing well
- They pass work to each other using a standard protocol
- Google's A2A protocol makes this possible (open standard, April 2025)

SLIDE 3: What I Built (show the diagram)
  Requirement → Spec Analyst → Test Writer → Code Writer → pytest → MR Creator
  
- 4 agents, each running as its own HTTP server
- Orchestrator chains them together
- A2A protocol handles discovery and communication

SLIDE 4: Live Demo
- Type: "Users can register with email and password"
- Watch 4 agents work in sequence (~40 seconds)
- Show the output: spec, tests, code, MR description
- Run pytest: all green

SLIDE 5: Why This Matters for Us
- Agents are independently deployable and swappable
- The same MR Creator agent is reused across both pipelines
- Adding a new agent = copy a folder, change the prompt
- Could apply to: code review, documentation, test generation, etc.

SLIDE 6: Try It Yourself
- Free setup, 5 minutes
- Interactive guide included
- Repo link: [...]
```

---

## LinkedIn / Blog Post (Public sharing)

```
I built a multi-agent AI system where specialized agents collaborate 
like a dev team — and you can try it in 5 minutes.

The setup:
- Spec Analyst agent: breaks requirements into testable criteria  
- Test Writer agent: generates pytest tests (red phase of TDD)
- Code Writer agent: writes minimal code to pass the tests (green phase)
- MR Creator agent: writes a merge request description

Each agent runs as its own HTTP server. They discover each other 
and communicate using Google's Agent2Agent (A2A) protocol — an open 
standard for agent-to-agent collaboration.

You type: "Users can register with email and password"
You get: working code, passing tests, and an MR description.

There's also a second pipeline for API development:
Requirement → OpenAPI spec → API tests → FastAPI stub → MR description

What I learned:
1. Small, focused agents produce more reliable output than one mega-prompt
2. The A2A protocol makes agents discoverable and swappable
3. Adding a new agent is just: copy folder, change prompt, pick a port
4. The same pattern works for TDD, API design, and more

The whole thing runs locally with a free Gemini API key. No cloud 
billing, no Docker required.

Repo and interactive guide: [link]

#AI #MultiAgent #A2A #TDD #SoftwareEngineering #Testing
```
