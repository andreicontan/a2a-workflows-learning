import os

from a2a.types import AgentSkill, Message
from agentstack_sdk.a2a.types import AgentMessage
from agentstack_sdk.server import Server
from agentstack_sdk.server.context import RunContext

from tdd_agents.llm import llm_call

SYSTEM_PROMPT = """\
You are a Principal QA Engineer who converts raw requirements into structured, \
testable acceptance criteria.

Given a user story or feature requirement, produce a JSON object with this schema:

{
  "feature": "<snake_case_feature_name>",
  "module": "<module_name_for_imports>",
  "criteria": [
    {
      "id": "AC-1",
      "given": "<precondition>",
      "when": "<action>",
      "then": "<expected outcome>",
      "function_hint": "<suggested_function_name>"
    }
  ]
}

Rules:
- Extract 3-6 acceptance criteria covering happy path, edge cases, and error cases.
- Each criterion must be independently testable.
- function_hint should suggest a Python function name the implementation would expose.
- module should be a valid Python module name (snake_case, no spaces).
- Return ONLY the JSON object, no markdown fences, no explanation."""

server = Server()


@server.agent(
    name="Spec Analyst",
    version="1.0.0",
    default_input_modes=["text", "text/plain"],
    default_output_modes=["text", "text/plain"],
    skills=[
        AgentSkill(
            id="analyze_requirements",
            name="Analyze Requirements",
            description=(
                "Converts raw user stories into structured, testable acceptance criteria "
                "(Given/When/Then JSON). Takes a plain-text requirement and produces a JSON "
                "spec with feature name, module name, and acceptance criteria."
            ),
            tags=["requirements", "specification", "tdd", "testing"],
            examples=[
                "Users can reset their password via email",
                "Shopping cart should calculate totals with tax",
                "Build a calculator with add, subtract, multiply, divide",
            ],
        )
    ],
)
async def spec_analyst(input: Message, context: RunContext):
    """Converts raw requirements into structured testable acceptance criteria."""
    user_text = " ".join(part.text for part in input.parts if part.text)
    spec_json = llm_call(SYSTEM_PROMPT, user_text)
    yield AgentMessage(text=spec_json)


def serve():
    server.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
    )


if __name__ == "__main__":
    serve()
