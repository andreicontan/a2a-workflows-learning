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
from agents.api_test_generator.agent import APITestGeneratorAgent


class APITestGeneratorExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = APITestGeneratorAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        openapi_yaml = context.get_user_input()
        test_code = self.agent.generate_tests(openapi_yaml)
        message = Message(role=Role.ROLE_AGENT, parts=[Part(text=test_code)], message_id="api-test-response")
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


def main() -> None:
    load_dotenv()
    PORT = int(os.environ.get("API_TEST_GENERATOR_PORT", 9012))
    HOST = os.environ.get("AGENT_HOST", "localhost")

    skill = AgentSkill(
        id="generate_api_tests",
        name="Generate API Tests",
        description="Generates pytest + requests acceptance tests from an OpenAPI 3.0 spec.",
        tags=["testing", "api", "pytest", "requests"],
        examples=["Generate API tests for a todo list API", "Write acceptance tests for user endpoints"],
    )

    agent_card = AgentCard(
        name="APITestGeneratorAgent",
        description="Generates API acceptance tests (pytest + requests) from OpenAPI specs.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supported_interfaces=[AgentInterface(url=f"http://{HOST}:{PORT}/", protocol_binding="JSONRPC")],
    )

    request_handler = DefaultRequestHandler(agent_executor=APITestGeneratorExecutor(), task_store=InMemoryTaskStore(), agent_card=agent_card)
    routes = create_agent_card_routes(agent_card) + create_jsonrpc_routes(request_handler, rpc_url="/")
    app = Starlette(routes=routes)

    print(f"API Test Generator Agent running on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
