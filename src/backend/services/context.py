import uuid

from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from backend.schemas.context import Context


class ContextMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Import here to avoid circular imports
        from backend.schemas.user import DEFAULT_USER_ID
        from backend.services.auth.utils import get_header_user_id, has_header_user_id

        trace_id = str(uuid.uuid4())

        if scope["type"] != "http":
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

        if has_header_user_id(request):
            user_id = get_header_user_id(request)
        else:
            user_id = DEFAULT_USER_ID

        context.with_user_id(user_id)

        agent_id = request.headers.get("Agent-Id")
        context.with_agent_id(agent_id)

        context.with_logger()

        # Set the context on the scope
        scope["context"] = context

        await self.app(scope, receive, send)

        # Clear the context after the request is complete
        del scope["context"]


def get_context_from_scope(scope: Scope) -> Context:
    return scope.get("context") or Context()


def get_context(request: Request) -> Context:
    return get_context_from_scope(request.scope)
