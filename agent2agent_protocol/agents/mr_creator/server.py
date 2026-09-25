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
from agents.mr_creator.agent import MRCreatorAgent


class MRCreatorExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent = MRCreatorAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        pipeline_context = context.get_user_input()
        mr_description = self.agent.create_description(pipeline_context)
        message = Message(
            role=Role.ROLE_AGENT,
            parts=[Part(text=mr_description)],
            message_id="mr-response",
        )
        await event_queue.enqueue_event(message)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass


def main() -> None:
    load_dotenv()
    PORT = int(os.environ.get("MR_CREATOR_PORT", 9004))
    HOST = os.environ.get("AGENT_HOST", "localhost")

    skill = AgentSkill(
        id="create_mr_description",
        name="Create MR Description",
        description="Generates a merge request description from TDD pipeline artifacts (spec, tests, implementation, pytest results).",
        tags=["merge-request", "code-review", "documentation"],
        examples=[
            "Create an MR description for a user registration feature",
            "Write a merge request summary from test results and implementation",
        ],
    )

    agent_card = AgentCard(
        name="MRCreatorAgent",
        description="Generates professional merge request descriptions from TDD pipeline artifacts.",
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
        agent_executor=MRCreatorExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = create_agent_card_routes(agent_card) + create_jsonrpc_routes(request_handler, rpc_url="/")
    app = Starlette(routes=routes)

    print(f"MR Creator Agent running on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
