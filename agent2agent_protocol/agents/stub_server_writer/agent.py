import sys
sys.path.insert(0, "../..")
from common import llm_call

SYSTEM_PROMPT = """\
You are a Backend Engineer who writes minimal FastAPI stub servers.

Given an OpenAPI spec and a test file, write a FastAPI application that:

1. Implements all routes defined in the OpenAPI spec.
2. Uses in-memory storage (dict or list) — no database.
3. Returns proper HTTP status codes matching the spec.
4. Validates request bodies and returns 400 for invalid input.
5. Returns 404 for missing resources.
6. Returns 409 for duplicate creation attempts where appropriate.
7. Includes `if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8080)`.
8. Imports only from `fastapi`, `pydantic`, and `uvicorn`.

The goal is to make ALL the provided tests pass. Study the test expectations carefully.

Return ONLY the Python code. No markdown fences, no explanation."""


class StubServerWriterAgent:
    def generate(self, openapi_and_tests: str) -> str:
        return llm_call(SYSTEM_PROMPT, openapi_and_tests)
