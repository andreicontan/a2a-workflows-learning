"""
API Orchestrator — Chains agents to turn requirements into OpenAPI spec, tests, and stub server.

Pipeline: Requirement → API Analyst → OpenAPI Writer → Test Generator → Stub Server Writer → pytest → MR Creator

Usage:
    python3 api_orchestrator.py "Build a REST API for a todo list with CRUD operations"
    python3 api_orchestrator.py  # uses a default example requirement
"""

import asyncio
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import httpx
from a2a.client.client import ClientConfig
from a2a.client.client_factory import create_client
from a2a.types import Message, Part, Role, SendMessageRequest
from dotenv import load_dotenv

load_dotenv()

API_ANALYST_URL = os.environ.get("API_ANALYST_URL", "http://localhost:9010")
OPENAPI_WRITER_URL = os.environ.get("OPENAPI_WRITER_URL", "http://localhost:9011")
API_TEST_GEN_URL = os.environ.get("API_TEST_GEN_URL", "http://localhost:9012")
STUB_SERVER_URL = os.environ.get("STUB_SERVER_URL", "http://localhost:9013")
MR_CREATOR_URL = os.environ.get("MR_CREATOR_URL", "http://localhost:9004")

OUTPUT_DIR = Path(__file__).parent / "api_output"
STUB_PORT = 8080

DEFAULT_REQUIREMENT = (
    "Build a REST API for a todo list application. "
    "Users can create todos with a title and optional description. "
    "Todos have a completed status that defaults to false. "
    "Support full CRUD: create, list all, get by ID, update, and delete. "
    "Return 404 for missing todos."
)


async def send_to_agent(agent_url: str, prompt: str) -> str:
    config = ClientConfig(
        httpx_client=httpx.AsyncClient(timeout=httpx.Timeout(120.0)),
        streaming=False,
    )
    client = await create_client(agent=agent_url, client_config=config)

    request = SendMessageRequest(
        message=Message(
            role=Role.ROLE_USER,
            parts=[Part(text=prompt)],
            message_id=str(uuid4()),
        ),
    )

    result_text = ""
    async for response in client.send_message(request):
        if response.HasField("message"):
            for part in response.message.parts:
                if part.text:
                    result_text += part.text
        elif response.HasField("task"):
            if response.task.history:
                for msg in response.task.history:
                    if msg.role == Role.ROLE_AGENT:
                        for part in msg.parts:
                            if part.text:
                                result_text += part.text
            if response.task.artifacts:
                for artifact in response.task.artifacts:
                    for part in artifact.parts:
                        if part.text:
                            result_text += part.text

    return result_text


def strip_code_fences(code: str) -> str:
    lines = code.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def strip_yaml_fences(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and (lines[0].startswith("```yaml") or lines[0].startswith("```yml") or lines[0] == "```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


async def run_pipeline(requirement: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("API MULTI-AGENT PIPELINE")
    print("=" * 60)
    print(f"\nRequirement:\n  {requirement}\n")

    # Step 1: API Analyst
    print("-" * 60)
    print("[1/5] API Analyst -> Designing API endpoints...")
    api_spec_json = await send_to_agent(API_ANALYST_URL, requirement)
    api_spec_json = strip_code_fences(api_spec_json)
    spec_path = OUTPUT_DIR / "api_spec.json"
    spec_path.write_text(api_spec_json)
    print(f"  Done. API spec saved to {spec_path}")
    print(f"  Preview: {api_spec_json[:200]}...")

    # Step 2: OpenAPI Writer
    print("\n" + "-" * 60)
    print("[2/5] OpenAPI Writer -> Generating OpenAPI 3.0 YAML...")
    openapi_yaml = await send_to_agent(OPENAPI_WRITER_URL, api_spec_json)
    openapi_yaml = strip_yaml_fences(openapi_yaml)
    openapi_path = OUTPUT_DIR / "openapi.yaml"
    openapi_path.write_text(openapi_yaml)
    print(f"  Done. OpenAPI spec saved to {openapi_path}")

    # Step 3: API Test Generator
    print("\n" + "-" * 60)
    print("[3/5] API Test Generator -> Writing acceptance tests...")
    test_code = await send_to_agent(API_TEST_GEN_URL, openapi_yaml)
    test_code = strip_code_fences(test_code)
    test_path = OUTPUT_DIR / "test_api.py"
    test_path.write_text(test_code)
    print(f"  Done. Tests saved to {test_path}")

    # Step 4: Stub Server Writer
    print("\n" + "-" * 60)
    print("[4/5] Stub Server Writer -> Generating FastAPI stub...")
    stub_input = f"## OPENAPI SPEC:\n{openapi_yaml}\n\n## TEST FILE:\n{test_code}"
    stub_code = await send_to_agent(STUB_SERVER_URL, stub_input)
    stub_code = strip_code_fences(stub_code)
    stub_path = OUTPUT_DIR / "stub_server.py"
    stub_path.write_text(stub_code)
    print(f"  Done. Stub server saved to {stub_path}")

    # Step 5: Start stub server and run tests
    print("\n" + "=" * 60)
    print("VERIFICATION: Starting stub server and running pytest...")
    print("=" * 60)

    stub_process = subprocess.Popen(
        [sys.executable, str(stub_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    for i in range(15):
        time.sleep(1)
        try:
            httpx.get(f"http://localhost:{STUB_PORT}/", timeout=2.0)
            break
        except Exception:
            if i == 14:
                print("  Warning: Stub server may not have started properly")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    pytest_output = result.stdout + (result.stderr or "")
    tests_passed = result.returncode == 0

    stub_process.send_signal(signal.SIGTERM)
    stub_process.wait(timeout=5)

    if tests_passed:
        print("\nAll API tests passed!")
    else:
        print("\nSome tests failed - Stub server may need adjustment.")

    # Step 6: MR Creator
    print("\n" + "-" * 60)
    print("[5/5] MR Creator -> Generating merge request description...")
    mr_input = (
        f"## ORIGINAL REQUIREMENT:\n{requirement}\n\n"
        f"## API DESIGN:\n{api_spec_json}\n\n"
        f"## OPENAPI SPEC:\n{openapi_yaml}\n\n"
        f"## API TESTS:\n{test_code}\n\n"
        f"## STUB SERVER:\n{stub_code}\n\n"
        f"## TEST RESULTS:\n{pytest_output}\n\n"
        f"## FILES:\n- openapi.yaml\n- test_api.py\n- stub_server.py"
    )
    mr_description = await send_to_agent(MR_CREATOR_URL, mr_input)
    mr_path = OUTPUT_DIR / "mr_description.md"
    mr_path.write_text(mr_description)
    print(f"  Done. MR description saved to {mr_path}")

    # Final summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\nGenerated files in {OUTPUT_DIR}/:")
    for f in sorted(OUTPUT_DIR.glob("*")):
        if f.is_file():
            print(f"  {f.name}")
    print(f"\nMR Description:\n")
    print(mr_description)


def main() -> None:
    requirement = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else DEFAULT_REQUIREMENT
    asyncio.run(run_pipeline(requirement))


if __name__ == "__main__":
    main()
