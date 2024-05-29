import os
from distutils.util import strtobool
from typing import Any, Generator

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from backend.chat.custom.custom import CustomChat
from backend.chat.custom.langchain import LangChainChat
from backend.database_models import get_session
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
from backend.services.request_validators import (
    validate_chat_request,
    validate_deployment_header,
    validate_user_header,
)

router = APIRouter(
    prefix="/v1",
    dependencies=[
        Depends(get_session),
        Depends(validate_chat_request),
        Depends(validate_user_header),
    ],
)


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
    ) = process_chat(session, chat_request, request)

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
            ),
            response_message,
            conversation_id,
            user_id,
            should_store=should_store,
        ),
        media_type="text/event-stream",
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
    ) = process_chat(session, chat_request, request)

    return generate_chat_response(
        session,
        CustomChat().chat(
            chat_request,
            stream=False,
            deployment_name=deployment_name,
            deployment_config=deployment_config,
            file_paths=file_paths,
            managed_tools=managed_tools,
        ),
        response_message,
        conversation_id,
        user_id,
        should_store=should_store,
    )


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
