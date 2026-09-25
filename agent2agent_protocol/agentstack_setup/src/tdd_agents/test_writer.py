import os

from a2a.types import AgentSkill, Message
from agentstack_sdk.a2a.types import AgentMessage
from agentstack_sdk.server import Server
from agentstack_sdk.server.context import RunContext

from tdd_agents.llm import llm_call

SYSTEM_PROMPT = """\
You are a Senior Test Engineer who writes pytest test suites from structured \
acceptance criteria.

You will receive a JSON spec with acceptance criteria in Given/When/Then format. \
Write a complete pytest test file that:

1. Imports from the module specified in the spec's "module" field.
2. Creates one test function per acceptance criterion, named test_<description>.
3. Uses the function_hint from each criterion to call the right functions.
4. Tests MUST be designed to FAIL initially (red phase of TDD) — they call \
   functions that don't exist yet.
5. Include appropriate assertions and pytest.raises where errors are expected.
6. Add a docstring to each test referencing the AC id.

Return ONLY the Python code. No markdown fences, no explanation."""

server = Server()


@server.agent(
    name="Test Writer",
    version="1.0.0",
    default_input_modes=["text", "text/plain"],
    default_output_modes=["text", "text/plain"],
    skills=[
        AgentSkill(
            id="generate_tests",
            name="Generate Tests",
            description=(
                "Generates pytest test suites from structured acceptance criteria JSON. "
                "Takes a JSON spec and produces a complete Python test file with failing tests "
                "(red phase of TDD)."
            ),
            tags=["testing", "pytest", "tdd"],
            examples=[
                "Generate tests for a password reset feature",
                "Write test cases for a shopping cart calculator",
            ],
        )
    ],
)
async def test_writer(input: Message, context: RunContext):
    """Generates failing pytest test suites from structured acceptance criteria."""
    spec_json = " ".join(part.text for part in input.parts if part.text)
    test_code = llm_call(SYSTEM_PROMPT, spec_json)
    yield AgentMessage(text=test_code)


def serve():
    server.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8001)),
    )


if __name__ == "__main__":
    serve()
