import sys
sys.path.insert(0, "../..")
from common import llm_call

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


class SpecAnalystAgent:
    def analyze(self, requirement: str) -> str:
        return llm_call(SYSTEM_PROMPT, requirement)
