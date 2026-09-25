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
from agents.spec_analyst.agent import SpecAnalystAgent


class SpecAnalystExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = SpecAnalystAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        requirement = context.get_user_input()
        spec_json = self.agent.analyze(requirement)
        message = Message(
            role=Role.ROLE_AGENT,
            parts=[Part(text=spec_json)],
            message_id="spec-response",
        )
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


def main() -> None:
    load_dotenv()
    PORT = int(os.environ.get("SPEC_ANALYST_PORT", 9001))
    HOST = os.environ.get("AGENT_HOST", "localhost")

    skill = AgentSkill(
        id="analyze_requirements",
        name="Analyze Requirements",
        description="Converts raw user stories into structured, testable acceptance criteria (Given/When/Then JSON).",
        tags=["requirements", "specification", "tdd"],
        examples=[
            "Users can reset their password via email",
            "Shopping cart should calculate totals with tax",
        ],
    )

    agent_card = AgentCard(
        name="SpecAnalystAgent",
        description="Converts raw requirements into structured testable acceptance criteria.",
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
        agent_executor=SpecAnalystExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = create_agent_card_routes(agent_card) + create_jsonrpc_routes(request_handler, rpc_url="/")
    app = Starlette(routes=routes)

    print(f"Spec Analyst Agent running on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
