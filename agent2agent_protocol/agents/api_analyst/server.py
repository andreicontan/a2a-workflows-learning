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
from agents.api_analyst.agent import APIAnalystAgent


class APIAnalystExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = APIAnalystAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        requirement = context.get_user_input()
        api_spec = self.agent.analyze(requirement)
        message = Message(role=Role.ROLE_AGENT, parts=[Part(text=api_spec)], message_id="api-spec-response")
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


def main() -> None:
    load_dotenv()
    PORT = int(os.environ.get("API_ANALYST_PORT", 9010))
    HOST = os.environ.get("AGENT_HOST", "localhost")

    skill = AgentSkill(
        id="analyze_api_requirements",
        name="Analyze API Requirements",
        description="Converts requirements into structured API design (endpoints, methods, schemas).",
        tags=["api", "rest", "design"],
        examples=["Build a REST API for a todo list", "Create a user management API"],
    )

    agent_card = AgentCard(
        name="APIAnalystAgent",
        description="Designs RESTful APIs from plain-text requirements.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
        supported_interfaces=[AgentInterface(url=f"http://{HOST}:{PORT}/", protocol_binding="JSONRPC")],
    )

    request_handler = DefaultRequestHandler(agent_executor=APIAnalystExecutor(), task_store=InMemoryTaskStore(), agent_card=agent_card)
    routes = create_agent_card_routes(agent_card) + create_jsonrpc_routes(request_handler, rpc_url="/")
    app = Starlette(routes=routes)

    print(f"API Analyst Agent running on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
