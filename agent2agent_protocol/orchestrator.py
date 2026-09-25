"""
TDD Orchestrator — Chains 3 A2A agents to turn requirements into passing code.

Pipeline: Requirement → Spec Analyst → Test Writer → Code Writer → pytest → MR Creator

Usage:
    python3 orchestrator.py "Users can register with email and password"
    python3 orchestrator.py  # uses a default example requirement
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import httpx
from a2a.client.client import ClientConfig
from a2a.client.client_factory import create_client
from a2a.types import Message, Part, Role, SendMessageRequest
from dotenv import load_dotenv

load_dotenv()

SPEC_ANALYST_URL = os.environ.get("SPEC_ANALYST_URL", "http://localhost:9001")
TEST_WRITER_URL = os.environ.get("TEST_WRITER_URL", "http://localhost:9002")
CODE_WRITER_URL = os.environ.get("CODE_WRITER_URL", "http://localhost:9003")
MR_CREATOR_URL = os.environ.get("MR_CREATOR_URL", "http://localhost:9004")

OUTPUT_DIR = Path(__file__).parent / "output"

DEFAULT_REQUIREMENT = (
    "Users can register with an email and password. "
    "Email must be valid format. Password must be at least 8 characters "
    "with at least one uppercase letter and one digit. "
    "Duplicate emails should be rejected."
)


async def send_to_agent(agent_url: str, prompt: str) -> str:
    """Discover an agent via its AgentCard and send it a message."""
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
    """Remove markdown code fences if the LLM wraps its output."""
    lines = code.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


async def run_pipeline(requirement: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("TDD MULTI-AGENT PIPELINE")
    print("=" * 60)
    print(f"\nRequirement:\n  {requirement}\n")

    # Step 1: Spec Analyst
    print("-" * 60)
    print("[1/4] Spec Analyst -> Analyzing requirements...")
    spec_json = await send_to_agent(SPEC_ANALYST_URL, requirement)
    spec_path = OUTPUT_DIR / "spec.json"
    spec_path.write_text(spec_json)
    print(f"  Done. Spec saved to {spec_path}")
    print(f"  Preview: {spec_json[:200]}...")

    # Step 2: Test Writer
    print("\n" + "-" * 60)
    print("[2/4] Test Writer -> Generating failing tests...")
    test_code = await send_to_agent(TEST_WRITER_URL, spec_json)
    test_code = strip_code_fences(test_code)
    test_path = OUTPUT_DIR / "test_feature.py"
    test_path.write_text(test_code)
    print(f"  Done. Tests saved to {test_path}")

    # Step 3: Code Writer
    print("\n" + "-" * 60)
    print("[3/4] Code Writer -> Implementing code to pass tests...")
    combined_input = (
        f"## TEST FILE:\n{test_code}\n\n## ACCEPTANCE CRITERIA:\n{spec_json}"
    )
    impl_code = await send_to_agent(CODE_WRITER_URL, combined_input)
    impl_code = strip_code_fences(impl_code)

    # Derive module name from test imports
    module_name = "feature"
    for line in test_code.splitlines():
        if line.startswith("from ") and "import" in line:
            module_name = line.split("from ")[1].split(" import")[0].strip()
            break

    impl_path = OUTPUT_DIR / f"{module_name}.py"
    impl_path.write_text(impl_code)
    print(f"  Done. Implementation saved to {impl_path}")

    # Step 4: Run pytest
    print("\n" + "=" * 60)
    print("VERIFICATION: Running pytest...")
    print("=" * 60)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=str(OUTPUT_DIR),
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    pytest_output = result.stdout + (result.stderr or "")
    tests_passed = result.returncode == 0

    if tests_passed:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed - Code Writer may need another iteration.")

    # Step 5: MR Creator
    print("\n" + "-" * 60)
    print("[4/4] MR Creator -> Generating merge request description...")
    mr_input = (
        f"## ORIGINAL REQUIREMENT:\n{requirement}\n\n"
        f"## ACCEPTANCE CRITERIA:\n{spec_json}\n\n"
        f"## TEST FILE:\n{test_code}\n\n"
        f"## IMPLEMENTATION:\n{impl_code}\n\n"
        f"## TEST RESULTS:\n{pytest_output}\n\n"
        f"## FILES:\n- {test_path.name}\n- {impl_path.name}"
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
