import os
import sys

import uvicorn
from dotenv import load_dotenv
from starlette.applications import Starlette

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_jsonrpc_routes, create_agent_card_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill, Message, Part, Role

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from agents.test_writer.agent import TestWriterAgent


class TestWriterExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = TestWriterAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        spec_json = context.get_user_input()
        test_code = self.agent.generate_tests(spec_json)
        message = Message(
            role=Role.ROLE_AGENT,
            parts=[Part(text=test_code)],
            message_id="test-response",
        )
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


def main() -> None:
    load_dotenv()
    PORT = int(os.environ.get("TEST_WRITER_PORT", 9002))
    HOST = os.environ.get("AGENT_HOST", "localhost")

    skill = AgentSkill(
        id="generate_tests",
        name="Generate Tests",
        description="Generates pytest test suites from structured acceptance criteria JSON.",
        tags=["testing", "pytest", "tdd"],
        examples=[
            "Generate tests for a password reset feature",
            "Write test cases for a shopping cart calculator",
        ],
    )

    agent_card = AgentCard(
        name="TestWriterAgent",
        description="Generates failing pytest test suites from structured acceptance criteria (red phase of TDD).",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supported_interfaces=[
            AgentInterface(url=f"http://{HOST}:{PORT}/", protocol_binding="JSONRPC"),
        ],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=TestWriterExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = create_agent_card_routes(agent_card) + create_jsonrpc_routes(request_handler, rpc_url="/")
    app = Starlette(routes=routes)

    print(f"Test Writer Agent running on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
