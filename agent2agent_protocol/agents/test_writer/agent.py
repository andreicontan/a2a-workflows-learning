import sys
sys.path.insert(0, "../..")
from common import llm_call

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


class TestWriterAgent:
    def generate_tests(self, spec_json: str) -> str:
        return llm_call(SYSTEM_PROMPT, spec_json)
