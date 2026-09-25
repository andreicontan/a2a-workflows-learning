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
from agents.stub_server_writer.agent import StubServerWriterAgent


class StubServerWriterExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = StubServerWriterAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        openapi_and_tests = context.get_user_input()
        stub_code = self.agent.generate(openapi_and_tests)
        message = Message(role=Role.ROLE_AGENT, parts=[Part(text=stub_code)], message_id="stub-server-response")
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


def main() -> None:
    load_dotenv()
    PORT = int(os.environ.get("STUB_SERVER_WRITER_PORT", 9013))
    HOST = os.environ.get("AGENT_HOST", "localhost")

    skill = AgentSkill(
        id="generate_stub_server",
        name="Generate Stub Server",
        description="Generates a FastAPI stub server implementing OpenAPI routes with in-memory state.",
        tags=["fastapi", "stub", "server", "api"],
        examples=["Generate a stub server for a todo API", "Write a FastAPI server matching the OpenAPI spec"],
    )

    agent_card = AgentCard(
        name="StubServerWriterAgent",
        description="Generates minimal FastAPI stub servers from OpenAPI specs to make acceptance tests pass.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supported_interfaces=[AgentInterface(url=f"http://{HOST}:{PORT}/", protocol_binding="JSONRPC")],
    )

    request_handler = DefaultRequestHandler(agent_executor=StubServerWriterExecutor(), task_store=InMemoryTaskStore(), agent_card=agent_card)
    routes = create_agent_card_routes(agent_card) + create_jsonrpc_routes(request_handler, rpc_url="/")
    app = Starlette(routes=routes)

    print(f"Stub Server Writer Agent running on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
