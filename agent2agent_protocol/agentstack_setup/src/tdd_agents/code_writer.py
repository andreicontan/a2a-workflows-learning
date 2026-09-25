import os

from a2a.types import AgentSkill, Message
from agentstack_sdk.a2a.types import AgentMessage
from agentstack_sdk.server import Server
from agentstack_sdk.server.context import RunContext

from tdd_agents.llm import llm_call

SYSTEM_PROMPT = """\
You are a Senior Software Engineer who writes minimal Python implementations \
to make failing tests pass (green phase of TDD).

You will receive:
1. A test file (pytest) with failing tests
2. The acceptance criteria spec (JSON)

Write the minimal Python module that makes ALL tests pass. Rules:

- Only implement what the tests require — no extra features.
- Use standard library where possible (dataclasses, secrets, datetime, etc.).
- The module name must match what the tests import.
- Include proper type hints.
- Handle edge cases that the tests assert (errors, boundary conditions).

Return ONLY the Python code. No markdown fences, no explanation."""

server = Server()


@server.agent(
    name="Code Writer",
    version="1.0.0",
    default_input_modes=["text", "text/plain"],
    default_output_modes=["text", "text/plain"],
    skills=[
        AgentSkill(
            id="implement_code",
            name="Implement Code",
            description=(
                "Writes minimal Python implementations to make failing tests pass "
                "(green phase of TDD). Takes test code and acceptance criteria, produces "
                "the implementation module."
            ),
            tags=["implementation", "python", "tdd"],
            examples=[
                "Implement password reset functions to pass the test suite",
                "Write a calculator module matching the test expectations",
            ],
        )
    ],
)
async def code_writer(input: Message, context: RunContext):
    """Writes minimal Python implementations to make failing tests pass."""
    tests_and_spec = " ".join(part.text for part in input.parts if part.text)
    impl_code = llm_call(SYSTEM_PROMPT, tests_and_spec)
    yield AgentMessage(text=impl_code)


def serve():
    server.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8002)),
    )


if __name__ == "__main__":
    serve()
