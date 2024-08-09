from typing import Any, Generator

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from backend.chat.custom.custom import CustomChat
from backend.chat.custom.langchain import LangChainChat
from backend.config.routers import RouterName
from backend.config.settings import Settings
from backend.crud import agent as agent_crud
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.database_models.database import DBSessionDep
from backend.schemas.agent import Agent, AgentToolMetadata
from backend.schemas.chat import ChatResponseEvent, NonStreamedChatResponse
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.schemas.langchain_chat import LangchainChatRequest
from backend.schemas.metrics import DEFAULT_METRICS_AGENT, agent_to_metrics_agent
from backend.services.agent import validate_agent_exists
from backend.services.chat import (
    generate_chat_response,
    generate_chat_stream,
    generate_langchain_chat_stream,
    process_chat,
)
from backend.services.context import get_context
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
    ctx: Context = Depends(get_context),
) -> Generator[ChatResponseEvent, Any, None]:
    """
    Stream chat endpoint to handle user messages and return chatbot responses.

    Args:
        session (DBSessionDep): Database session.
        chat_request (CohereChatRequest): Chat request data.
        request (Request): Request object.
        ctx (Context): Context object.

    Returns:
        EventSourceResponse: Server-sent event response with chatbot responses.
    """
    ctx.with_model(chat_request.model)
    agent_id = chat_request.agent_id
    ctx.with_agent_id(agent_id)
    user_id = ctx.get_user_id()

    if agent_id:
        agent = validate_agent_exists(session, agent_id, user_id)
        agent_schema = Agent.model_validate(agent)
        ctx.with_agent(agent_schema)
        agent_tool_metadata = (
            agent_tool_metadata_crud.get_all_agent_tool_metadata_by_agent_id(
                session, agent_id
            )
        )
        agent_tool_metadata_schema = [
            AgentToolMetadata.model_validate(x) for x in agent_tool_metadata
        ]
        ctx.with_agent_tool_metadata(agent_tool_metadata_schema)

        ctx.with_metrics_agent(agent_to_metrics_agent(agent))
    else:
        ctx.with_metrics_agent(DEFAULT_METRICS_AGENT)

    (
        session,
        chat_request,
        file_paths,
        response_message,
        should_store,
        managed_tools,
        next_message_position,
        ctx,
    ) = process_chat(session, chat_request, request, ctx)

    return EventSourceResponse(
        generate_chat_stream(
            session,
            CustomChat().chat(
                chat_request,
                stream=True,
                file_paths=file_paths,
                managed_tools=managed_tools,
                session=session,
                ctx=ctx,
            ),
            response_message,
            should_store=should_store,
            next_message_position=next_message_position,
            ctx=ctx,
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
    ctx: Context = Depends(get_context),
) -> NonStreamedChatResponse:
    """
    Chat endpoint to handle user messages and return chatbot responses.

    Args:
        chat_request (CohereChatRequest): Chat request data.
        session (DBSessionDep): Database session.
        request (Request): Request object.
        ctx (Context): Context object.

    Returns:
        NonStreamedChatResponse: Chatbot response.
    """
    ctx.with_model(chat_request.model)
    agent_id = chat_request.agent_id
    ctx.with_agent_id(agent_id)
    user_id = ctx.get_user_id()

    if agent_id:
        agent = validate_agent_exists(session, agent_id, user_id)
        agent_schema = Agent.model_validate(agent)
        ctx.with_agent(agent_schema)
        agent_tool_metadata = (
            agent_tool_metadata_crud.get_all_agent_tool_metadata_by_agent_id(
                session, agent_id
            )
        )
        agent_tool_metadata_schema = [
            AgentToolMetadata.model_validate(x) for x in agent_tool_metadata
        ]
        ctx.with_agent_tool_metadata(agent_tool_metadata_schema)
        ctx.with_metrics_agent(agent_to_metrics_agent(agent))
    else:
        ctx.with_metrics_agent(DEFAULT_METRICS_AGENT)

    (
        session,
        chat_request,
        file_paths,
        response_message,
        should_store,
        managed_tools,
        next_message_position,
        ctx,
    ) = process_chat(session, chat_request, request, ctx)

    response = await generate_chat_response(
        session,
        CustomChat().chat(
            chat_request,
            stream=False,
            file_paths=file_paths,
            managed_tools=managed_tools,
            ctx=ctx,
        ),
        response_message,
        should_store=should_store,
        next_message_position=next_message_position,
        ctx=ctx,
    )
    return response


@router.post("/langchain-chat")
def langchain_chat_stream(
    session: DBSessionDep,
    chat_request: LangchainChatRequest,
    request: Request,
    ctx: Context = Depends(get_context),
):
    """
    Stream chat endpoint to handle user messages and return chatbot responses using langchain.

    Args:
        session (DBSessionDep): Database session.
        chat_request (LangchainChatRequest): Chat request data.
        request (Request): Request object.
        ctx (Context): Context object.

    Returns:
        EventSourceResponse: Server-sent event response with chatbot responses.
    """
    logger = ctx.get_logger()
    user_id = ctx.get_user_id()
    use_langchain = Settings().feature_flags.use_experimental_langchain
    if not use_langchain:
        logger.error(
            event="[Chat] Error handling LangChain streaming chat request: LangChain is not enabled",
        )
        return {"error": "Langchain is not enabled."}

    (
        session,
        chat_request,
        _,
        response_message,
        _,
        should_store,
        managed_tools,
        _,
        _,  # ctx
    ) = process_chat(session, chat_request, request, ctx)

    return EventSourceResponse(
        generate_langchain_chat_stream(
            session,
            LangChainChat().chat(chat_request, managed_tools=managed_tools),
            response_message,
            ctx.get_conversation_id(),
            user_id,
            should_store,
        ),
        media_type="text/event-stream",
    )
