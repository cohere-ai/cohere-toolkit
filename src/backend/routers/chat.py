import os
from distutils.util import strtobool
from typing import Any, Generator

from fastapi import APIRouter, Depends, Header, Request
from sse_starlette.sse import EventSourceResponse

from backend.chat.custom.custom import CustomChat
from backend.chat.custom.langchain import LangChainChat
from backend.config.routers import RouterName
from backend.database_models.database import DBSessionDep
from backend.schemas.chat import ChatResponseEvent, NonStreamedChatResponse
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.langchain_chat import LangchainChatRequest
from backend.services.chat import (
    generate_chat_response,
    generate_chat_stream,
    generate_langchain_chat_stream,
    process_chat,
)
from backend.services.request_validators import validate_deployment_header

router = APIRouter(
    prefix="/v1",
)
router.name = RouterName.CHAT


@router.post("/chat-stream", dependencies=[Depends(validate_deployment_header)])
async def chat_stream(
    session: DBSessionDep,
    chat_request: CohereChatRequest,
    request: Request,
) -> Generator[ChatResponseEvent, Any, None]:
    """
    Stream chat endpoint to handle user messages and return chatbot responses.

    Args:
        session (DBSessionDep): Database session.
        chat_request (CohereChatRequest): Chat request data.
        request (Request): Request object.

    Returns:
        EventSourceResponse: Server-sent event response with chatbot responses.
    """
    trace_id = None
    if hasattr(request.state, "trace_id"):
        trace_id = request.state.trace_id

    user_id = request.headers.get("User-Id", None)
    agent_id = chat_request.agent_id
    (
        session,
        chat_request,
        file_paths,
        response_message,
        conversation_id,
        user_id,
        deployment_name,
        should_store,
        managed_tools,
        deployment_config,
        next_message_position,
    ) = process_chat(session, chat_request, request, agent_id)

    return EventSourceResponse(
        generate_chat_stream(
            session,
            CustomChat().chat(
                chat_request,
                stream=True,
                deployment_name=deployment_name,
                deployment_config=deployment_config,
                file_paths=file_paths,
                managed_tools=managed_tools,
                session=session,
                conversation_id=conversation_id,
                user_id=user_id,
                trace_id=trace_id,
                agent_id=agent_id,
            ),
            response_message,
            conversation_id,
            user_id,
            should_store=should_store,
            next_message_position=next_message_position,
        ),
        media_type="text/event-stream",
        headers={"Connection": "keep-alive"},
        send_timeout=300,
        ping=5,
    )


@router.post("/chat", dependencies=[Depends(validate_deployment_header)])
async def chat(
    session: DBSessionDep,
    chat_request: CohereChatRequest,
    request: Request,
) -> NonStreamedChatResponse:
    """
    Chat endpoint to handle user messages and return chatbot responses.

    Args:
        chat_request (CohereChatRequest): Chat request data.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        NonStreamedChatResponse: Chatbot response.
    """
    trace_id = None
    if hasattr(request.state, "trace_id"):
        trace_id = request.state.trace_id

    user_id = request.headers.get("User-Id", None)
    agent_id = chat_request.agent_id

    (
        session,
        chat_request,
        file_paths,
        response_message,
        conversation_id,
        user_id,
        deployment_name,
        should_store,
        managed_tools,
        deployment_config,
        next_message_position,
    ) = process_chat(session, chat_request, request, agent_id)

    response = await generate_chat_response(
        session,
        CustomChat().chat(
            chat_request,
            stream=False,
            deployment_name=deployment_name,
            deployment_config=deployment_config,
            file_paths=file_paths,
            managed_tools=managed_tools,
            trace_id=trace_id,
            user_id=user_id,
            agent_id=agent_id,
        ),
        response_message,
        conversation_id,
        user_id,
        should_store=should_store,
        next_message_position=next_message_position,
    )
    return response


@router.post("/langchain-chat")
def langchain_chat_stream(
    session: DBSessionDep, chat_request: LangchainChatRequest, request: Request
):
    use_langchain = bool(strtobool(os.getenv("USE_EXPERIMENTAL_LANGCHAIN", "false")))
    if not use_langchain:
        return {"error": "Langchain is not enabled."}

    (
        session,
        chat_request,
        _,
        response_message,
        conversation_id,
        user_id,
        _,
        should_store,
        managed_tools,
        _,
        _,
    ) = process_chat(session, chat_request, request)

    return EventSourceResponse(
        generate_langchain_chat_stream(
            session,
            LangChainChat().chat(chat_request, managed_tools=managed_tools),
            response_message,
            conversation_id,
            user_id,
            should_store,
        ),
        media_type="text/event-stream",
    )
