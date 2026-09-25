import sys
sys.path.insert(0, "../..")
from common import llm_call

SYSTEM_PROMPT = """\
You are a Senior QA Engineer who writes API acceptance tests using pytest and requests.

Given an OpenAPI 3.0 YAML specification, produce a pytest test file that:

1. Imports `pytest` and `requests`.
2. Defines `BASE_URL = "http://localhost:8080"` at the top.
3. Creates one or more test functions per endpoint.
4. Tests happy paths: correct status codes, response body structure.
5. Tests error cases: invalid input (400), not found (404), duplicates (409).
6. Uses `requests.post()`, `requests.get()`, `requests.put()`, `requests.delete()`.
7. Validates response JSON keys and types.
8. Tests are ordered logically: create before read, read before update, etc.
9. Add a docstring to each test describing what endpoint and scenario it covers.

Return ONLY the Python code. No markdown fences, no explanation."""


class APITestGeneratorAgent:
    def generate_tests(self, openapi_yaml: str) -> str:
        return llm_call(SYSTEM_PROMPT, openapi_yaml)
