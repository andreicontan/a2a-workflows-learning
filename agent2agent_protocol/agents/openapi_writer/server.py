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
from agents.openapi_writer.agent import OpenAPIWriterAgent


class OpenAPIWriterExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = OpenAPIWriterAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        api_spec_json = context.get_user_input()
        openapi_yaml = self.agent.generate(api_spec_json)
        message = Message(role=Role.ROLE_AGENT, parts=[Part(text=openapi_yaml)], message_id="openapi-response")
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


def main() -> None:
    load_dotenv()
    PORT = int(os.environ.get("OPENAPI_WRITER_PORT", 9011))
    HOST = os.environ.get("AGENT_HOST", "localhost")

    skill = AgentSkill(
        id="generate_openapi_spec",
        name="Generate OpenAPI Spec",
        description="Generates valid OpenAPI 3.0 YAML from structured API design JSON.",
        tags=["openapi", "yaml", "specification"],
        examples=["Generate OpenAPI spec for a todo API", "Write OpenAPI YAML for user management endpoints"],
    )

    agent_card = AgentCard(
        name="OpenAPIWriterAgent",
        description="Generates valid OpenAPI 3.0 YAML specifications from structured API designs.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supported_interfaces=[AgentInterface(url=f"http://{HOST}:{PORT}/", protocol_binding="JSONRPC")],
    )

    request_handler = DefaultRequestHandler(agent_executor=OpenAPIWriterExecutor(), task_store=InMemoryTaskStore(), agent_card=agent_card)
    routes = create_agent_card_routes(agent_card) + create_jsonrpc_routes(request_handler, rpc_url="/")
    app = Starlette(routes=routes)

    print(f"OpenAPI Writer Agent running on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
