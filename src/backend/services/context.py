import uuid

from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from backend.schemas.context import Context
from backend.services.auth.utils import get_header_user_id


class ContextMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        trace_id = str(uuid.uuid4())

        if request.scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create a new context for the request
        context = Context()
        context.set_request(scope)
        context.set_response(send)
        context.set_receive(receive)
        context.with_trace_id(trace_id)

        request = Request(scope)
        context.with_deployment_name(request.headers.get("Deployment-Name", ""))

        request = Request(scope)
        user_id = get_header_user_id(request)
        context.with_user_id(user_id)

        agent_id = request.headers.get("Agent-Id")
        context.with_agent_id(agent_id)

        # Set the context on the scope
        scope["context"] = context

        await self.app(scope, receive, send)

        # Clear the context after the request is complete
        del scope["context"]


def get_context_from_scope(scope: Scope) -> Context:
    return scope.get("context") or Context()


def get_context(request: Request) -> Context:
    return get_context_from_scope(request.scope)
