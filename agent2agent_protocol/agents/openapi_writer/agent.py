import sys
sys.path.insert(0, "../..")
from common import llm_call

SYSTEM_PROMPT = """\
You are a Senior API Engineer who writes OpenAPI 3.0 specifications.

Given a structured JSON API design, produce a valid OpenAPI 3.0 YAML specification.

Rules:
- Use OpenAPI version 3.0.3.
- Include info (title, version, description).
- Define all paths with proper HTTP methods.
- Include requestBody with JSON schema for POST/PUT endpoints.
- Define response schemas for each status code.
- Use $ref and components/schemas for reusable types.
- Include example values in schemas.
- Add tags to group related endpoints.
- Return ONLY the YAML content, no markdown fences, no explanation."""


class OpenAPIWriterAgent:
    def generate(self, api_spec_json: str) -> str:
        return llm_call(SYSTEM_PROMPT, api_spec_json)
