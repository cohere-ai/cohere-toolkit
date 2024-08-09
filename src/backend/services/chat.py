import json
from typing import Any, AsyncGenerator, Generator, List, Union
from uuid import uuid4

from cohere.types import StreamedChatResponse
from fastapi import Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from langchain_core.agents import AgentActionMessageLog
from langchain_core.runnables.utils import AddableDict
from pydantic import ValidationError

from backend.chat.collate import to_dict
from backend.chat.enums import StreamEvent
from backend.config.tools import AVAILABLE_TOOLS
from backend.crud import agent as agent_crud
from backend.crud import conversation as conversation_crud
from backend.crud import deployment as deployment_crud
from backend.crud import file as file_crud
from backend.crud import message as message_crud
from backend.crud import tool_call as tool_call_crud
from backend.database_models.citation import Citation
from backend.database_models.conversation import Conversation
from backend.database_models.database import DBSessionDep
from backend.database_models.document import Document
from backend.database_models.message import (
    Message,
    MessageAgent,
    MessageFileAssociation,
)
from backend.database_models.tool_call import ToolCall as ToolCallModel
from backend.schemas.agent import Agent
from backend.schemas.chat import (
    BaseChatRequest,
    ChatMessage,
    ChatResponseEvent,
    ChatRole,
    NonStreamedChatResponse,
    StreamCitationGeneration,
    StreamEnd,
    StreamEventType,
    StreamSearchQueriesGeneration,
    StreamSearchResults,
    StreamStart,
    StreamTextGeneration,
    StreamToolCallsChunk,
    StreamToolCallsGeneration,
    StreamToolInput,
    StreamToolResult,
    ToolInputType,
)
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.schemas.conversation import UpdateConversationRequest
from backend.schemas.search_query import SearchQuery
from backend.schemas.tool import Tool, ToolCall, ToolCallDelta
from backend.services.agent import validate_agent_exists
from backend.services.file import get_file_service
from backend.services.generators import AsyncGeneratorContextManager


def process_chat(
    session: DBSessionDep,
    chat_request: BaseChatRequest,
    request: Request,
    ctx: Context,
) -> tuple[
    DBSessionDep, BaseChatRequest, Union[list[str], None], Message, str, str, dict
]:
    """
    Process a chat request.

    Args:
        chat_request (BaseChatRequest): Chat request data.
        session (DBSessionDep): Database session.
        request (Request): Request object.
        ctx (Context): Context object.

    Returns:
        Tuple: Tuple containing necessary data to construct the responses.
    """
    user_id = ctx.get_user_id()
    ctx.with_deployment_config()
    agent_id = ctx.get_agent_id()

    if agent_id is not None:
        agent = validate_agent_exists(session, agent_id, user_id)
        agent_schema = Agent.model_validate(agent)
        ctx.with_agent(agent_schema)

        if agent is None:
            raise HTTPException(
                status_code=404, detail=f"Agent with ID {agent_id} not found."
            )

        if chat_request.tools:
            for tool in chat_request.tools:
                if tool.name not in agent.tools:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Tool {tool.name} not found in agent {agent.id}",
                    )

        # Set the agent settings in the chat request
        chat_request.preamble = agent.preamble
        chat_request.tools = [Tool(name=tool) for tool in agent.tools]

    should_store = chat_request.chat_history is None and not is_custom_tool_call(
        chat_request
    )
    conversation = get_or_create_conversation(
        session, chat_request, user_id, should_store, agent_id, chat_request.message
    )

    ctx.with_conversation_id(conversation.id)

    # Get position to put next message in
    next_message_position = get_next_message_position(conversation)
    user_message = create_message(
        session,
        chat_request,
        conversation.id,
        user_id,
        next_message_position,
        chat_request.message,
        MessageAgent.USER,
        should_store,
        id=str(uuid4()),
    )
    chatbot_message = create_message(
        session,
        chat_request,
        conversation.id,
        user_id,
        next_message_position,
        "",
        MessageAgent.CHATBOT,
        False,
        id=str(uuid4()),
    )

    file_paths = None
    if isinstance(chat_request, CohereChatRequest):
        file_paths = handle_file_retrieval(session, user_id, chat_request.file_ids)
        if should_store:
            attach_files_to_messages(
                session,
                user_id,
                user_message.id,
                chat_request.file_ids,
            )

    chat_history = create_chat_history(
        conversation, next_message_position, chat_request
    )

    # co.chat expects either chat_history or conversation_id, not both
    chat_request.chat_history = chat_history
    chat_request.conversation_id = ""

    tools = chat_request.tools
    managed_tools = (
        len([tool.name for tool in tools if tool.name in AVAILABLE_TOOLS]) > 0
    )

    return (
        session,
        chat_request,
        file_paths,
        chatbot_message,
        should_store,
        managed_tools,
        next_message_position,
        ctx,
    )


def is_custom_tool_call(chat_response: BaseChatRequest) -> bool:
    """
    Check if the chat request is called with custom tools

    Args:
        chat_response (BaseChatRequest): Chat request data.

    Returns:
        bool: Whether the chat request is called with custom tools.
    """
    if chat_response.tools is None or len(chat_response.tools) == 0:
        return False

    # check if any of the tools is not in the available tools
    for tool in chat_response.tools:
        if tool.name not in AVAILABLE_TOOLS:
            return True

    return False


def get_or_create_conversation(
    session: DBSessionDep,
    chat_request: BaseChatRequest,
    user_id: str,
    should_store: bool,
    agent_id: str | None = None,
    user_message: str = "",
) -> Conversation:
    """
    Gets or creates a Conversation based on the chat request.

    Args:
        session (DBSessionDep): Database session.
        chat_request (BaseChatRequest): Chat request data.
        user_id (str): User ID.
        should_store (bool): Whether to store the conversation in the database.

    Returns:
        Conversation: Conversation object.
    """
    conversation_id = chat_request.conversation_id or ""
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)

    if conversation is None:
        # Get the first 5 words of the user message as the title
        title = " ".join(user_message.split()[:5])

        conversation = Conversation(
            user_id=user_id,
            id=chat_request.conversation_id,
            agent_id=agent_id,
            title=title,
        )

        if should_store:
            conversation_crud.create_conversation(session, conversation)

    return conversation


def get_next_message_position(conversation: Conversation) -> int:
    """
    Gets message position to create next messages.

    Args:
        conversation (Conversation): current Conversation.

    Returns:
        int: Position to save new messages with
    """

    # Message starts the conversation
    if len(conversation.messages) == 0:
        return 0

    # Get current max position from existing Messages
    current_active_position = max(
        [message.position for message in conversation.messages if message.is_active]
    )

    return current_active_position + 1


def create_message(
    session: DBSessionDep,
    chat_request: BaseChatRequest,
    conversation_id: str,
    user_id: str,
    user_message_position: int,
    text: str | None = None,
    agent: MessageAgent = MessageAgent.USER,
    should_store: bool = True,
    id: str | None = None,
    tool_plan: str | None = None,
) -> Message:
    """
    Create a message object and store it in the database.

    Args:
        session (DBSessionDep): Database session.
        chat_request (BaseChatRequest): Chat request data.
        conversation_id (str): Conversation ID.
        user_id (str): User ID.
        user_message_position (int): User message position.
        id (str): Message ID.
        text (str): Message text.
        agent (MessageAgent): Message agent.
        should_store (bool): Whether to store the message in the database.

    Returns:
        Message: Message object.
    """
    if not id:
        id = str(uuid4())

    message = Message(
        id=id,
        user_id=user_id,
        conversation_id=conversation_id,
        text=text,
        position=user_message_position,
        is_active=True,
        agent=agent,
        tool_plan=tool_plan,
    )

    if should_store:
        return message_crud.create_message(session, message)
    return message


def handle_file_retrieval(
    session: DBSessionDep, user_id: str, file_ids: List[str] | None = None
) -> list[str] | None:
    """
    Retrieve file paths from the database.

    Args:
        session (DBSessionDep): Database session.
        user_id (str): User ID.
        file_ids (List): List of File IDs.

    Returns:
        list[str] | None: List of file paths or None.
    """
    file_paths = None
    # Use file_ids if provided
    if file_ids is not None:
        files = get_file_service().get_files_by_ids(session, file_ids, user_id)
        file_paths = [file.file_path for file in files]

    return file_paths


def attach_files_to_messages(
    session: DBSessionDep,
    user_id: str,
    message_id: str,
    file_ids: List[str] | None = None,
) -> None:
    """
    Attach Files to Message if the message file association does not exists with the file ID

    Args:
        session (DBSessionDep): Database session.
        user_id (str): User ID.
        message_id (str): Message ID to attach to if needed.
        file_ids (List): List of File IDs.

    Returns:
        None
    """
    if file_ids is not None:
        for file_id in file_ids:
            message_file_association = (
                message_crud.get_message_file_association_by_file_id(
                    session, file_id, user_id
                )
            )

            # If the file is not associated with a file yet, create the association
            if message_file_association is None:
                message_crud.create_message_file_association(
                    session,
                    MessageFileAssociation(
                        message_id=message_id, user_id=user_id, file_id=file_id
                    ),
                )


def create_chat_history(
    conversation: Conversation,
    user_message_position: int,
    chat_request: BaseChatRequest,
) -> list[ChatMessage]:
    """
    Create chat history from conversation messages or request.

    Args:
        conversation (Conversation): Conversation object.
        user_message_position (int): User message position.
        chat_request (BaseChatRequest): Chat request data.

    Returns:
        list[ChatMessage]: List of chat messages.
    """
    if chat_request.chat_history is not None:
        return chat_request.chat_history

    if conversation.messages is None:
        return []

    # Don't include the user message that was just sent
    text_messages = [
        message
        for message in conversation.messages
        if message.position < user_message_position
    ]
    return [
        ChatMessage(
            role=ChatRole(message.agent.value.upper()),
            message=message.text,
        )
        for message in text_messages
    ]


def update_conversation_after_turn(
    session: DBSessionDep,
    response_message: Message,
    conversation_id: str,
    final_message_text: str,
    user_id: str,
) -> None:
    """
    After the last message in a conversation, updates the conversation description with that message's text

    Args:
        session (DBSessionDep): Database session.
        response_message (Message): Response message object.
        conversation_id (str): Conversation ID.
        final_message_text (str): Final message text.
    """
    message_crud.create_message(session, response_message)

    # Update conversation description with final message
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)
    new_conversation = UpdateConversationRequest(
        description=final_message_text,
        user_id=conversation.user_id,
    )
    conversation_crud.update_conversation(session, conversation, new_conversation)


def save_tool_calls_message(
    session: DBSessionDep,
    tool_calls: List[ToolCall],
    text: str,
    user_id: str,
    position: int,
    conversation_id: str,
) -> None:
    """
    Save tool calls to the database.

    Args:
        session (DBSessionDep): Database session.
        tool_calls (List[ToolCall]): List of ToolCall objects.
        message (str): Message text.
        position (int): Message position.
    """
    # Save message to the database
    message = create_message(
        session,
        chat_request=None,
        conversation_id=conversation_id,
        user_id=user_id,
        user_message_position=position,
        text=text,
        tool_plan=text,
        agent=MessageAgent.CHATBOT,
        should_store=True,
    )

    # Save tool calls to the database
    for tool_call in tool_calls:
        tool_call = ToolCallModel(
            name=tool_call.name,
            parameters=to_dict(tool_call.parameters),
            message_id=message.id,
        )
        tool_call_crud.create_tool_call(session, tool_call)


async def generate_chat_response(
    session: DBSessionDep,
    model_deployment_stream: Generator[StreamedChatResponse, None, None],
    response_message: Message,
    should_store: bool = True,
    ctx: Context = Context(),
    **kwargs: Any,
) -> NonStreamedChatResponse:
    """
    Generate chat response from model deployment non streaming response.
    Use the stream to generate the response and all the intermediate steps, then
    return only the final step as a non-streamed response.

    Args:
        session (DBSessionDep): Database session.
        model_deployment_stream (Generator[StreamResponse, None, None]): Model deployment stream.
        response_message (Message): Response message object.
        should_store (bool): Whether to store the conversation in the database.
        ctx (Context): Context object.
        **kwargs (Any): Additional keyword arguments.

    Yields:
        bytes: Byte representation of chat response event.
    """
    stream = generate_chat_stream(
        session,
        model_deployment_stream,
        response_message,
        should_store,
        ctx,
        **kwargs,
    )

    non_streamed_chat_response = None
    async for event in stream:
        event = json.loads(event)
        if event["event"] == StreamEvent.STREAM_END:
            data = event["data"]
            response_id = ctx.get_trace_id()
            generation_id = response_message.generation_id if response_message else None

            non_streamed_chat_response = NonStreamedChatResponse(
                text=data.get("text", ""),
                response_id=response_id,
                generation_id=generation_id,
                chat_history=data.get("chat_history", []),
                finish_reason=data.get("finish_reason", ""),
                citations=data.get("citations", []),
                search_queries=data.get("search_queries", []),
                documents=data.get("documents", []),
                search_results=data.get("search_results", []),
                event_type=StreamEvent.NON_STREAMED_CHAT_RESPONSE,
                conversation_id=ctx.get_conversation_id(),
                tool_calls=data.get("tool_calls", []),
            )

    return non_streamed_chat_response


async def generate_chat_stream(
    session: DBSessionDep,
    model_deployment_stream: AsyncGenerator[Any, Any],
    response_message: Message,
    should_store: bool = True,
    ctx: Context = Context(),
    **kwargs: Any,
) -> AsyncGenerator[Any, Any]:
    """
    Generate chat stream from model deployment stream.

    Args:
        session (DBSessionDep): Database session.
        model_deployment_stream (AsyncGenerator[Any, Any]): Model deployment stream.
        response_message (Message): Response message object.
        conversation_id (str): Conversation ID.
        user_id (str): User ID.
        should_store (bool): Whether to store the conversation in the database.
        ctx (Context): Context object.
        **kwargs (Any): Additional keyword arguments.

    Yields:
        bytes: Byte representation of chat response event.
    """
    conversation_id = ctx.get_conversation_id()
    user_id = ctx.get_user_id()

    stream_end_data = {
        "conversation_id": conversation_id,
        "response_id": ctx.get_trace_id(),
        "text": "",
        "citations": [],
        "documents": [],
        "search_results": [],
        "search_queries": [],
        "tool_calls": [],
        "tool_results": [],
    }

    # Map the user facing document_ids field returned from model to storage ID for document model
    document_ids_to_document = {}

    stream_event = None
    async for event in model_deployment_stream:
        (
            stream_event,
            stream_end_data,
            response_message,
            document_ids_to_document,
        ) = handle_stream_event(
            event,
            conversation_id,
            stream_end_data,
            response_message,
            ctx,
            document_ids_to_document,
            session=session,
            should_store=should_store,
            user_id=user_id,
            next_message_position=kwargs.get("next_message_position", 0),
        )

        yield json.dumps(
            jsonable_encoder(
                ChatResponseEvent(
                    event=stream_event.event_type.value,
                    data=stream_event,
                )
            )
        )

    if should_store:
        update_conversation_after_turn(
            session, response_message, conversation_id, stream_end_data["text"], user_id
        )


def handle_stream_event(
    event: dict[str, Any],
    conversation_id: str,
    stream_end_data: dict[str, Any],
    response_message: Message,
    ctx: Context,
    document_ids_to_document: dict[str, Document] = {},
    session: DBSessionDep = None,
    should_store: bool = True,
    user_id: str = "",
    next_message_position: int = 0,
) -> tuple[StreamEventType, dict[str, Any], Message, dict[str, Document]]:
    logger = ctx.get_logger()

    handlers = {
        StreamEvent.STREAM_START: handle_stream_start,
        StreamEvent.TEXT_GENERATION: handle_stream_text_generation,
        StreamEvent.SEARCH_RESULTS: handle_stream_search_results,
        StreamEvent.SEARCH_QUERIES_GENERATION: handle_stream_search_queries_generation,
        StreamEvent.TOOL_CALLS_GENERATION: handle_stream_tool_calls_generation,
        StreamEvent.CITATION_GENERATION: handle_stream_citation_generation,
        StreamEvent.TOOL_CALLS_CHUNK: handle_stream_tool_calls_chunk,
        StreamEvent.STREAM_END: handle_stream_end,
    }
    event_type = event["event_type"]

    if event_type not in handlers.keys():
        logger.warning(
            event=f"[Chat] Error handling stream event: Event type {event_type} not supported"
        )
        return None, stream_end_data, response_message, document_ids_to_document

    return handlers[event_type](
        event,
        conversation_id,
        stream_end_data,
        response_message,
        document_ids_to_document,
        session=session,
        should_store=should_store,
        user_id=user_id,
        next_message_position=next_message_position,
    )


def handle_stream_start(
    event: dict[str, Any],
    conversation_id: str,
    stream_end_data: dict[str, Any],
    response_message: Message,
    document_ids_to_document: dict[str, Document],
    **kwargs: Any,
) -> tuple[StreamStart, dict[str, Any], Message, dict[str, Document]]:
    event["conversation_id"] = conversation_id
    stream_event = StreamStart.model_validate(event)
    if response_message:
        response_message.generation_id = event["generation_id"]
    stream_end_data["generation_id"] = event["generation_id"]
    return stream_event, stream_end_data, response_message, document_ids_to_document


def handle_stream_text_generation(
    event: dict[str, Any],
    _: str,
    stream_end_data: dict[str, Any],
    response_message: Message,
    document_ids_to_document: dict[str, Document],
    **kwargs: Any,
) -> tuple[StreamTextGeneration, dict[str, Any], Message, dict[str, Document]]:
    stream_end_data["text"] += event["text"]
    stream_event = StreamTextGeneration.model_validate(event)
    return stream_event, stream_end_data, response_message, document_ids_to_document


def handle_stream_search_results(
    event: dict[str, Any],
    _: str,
    stream_end_data: dict[str, Any],
    response_message: Message,
    document_ids_to_document: dict[str, Document],
    **kwargs: Any,
) -> tuple[StreamSearchResults, dict[str, Any], Message, dict[str, Document]]:
    for document in event["documents"]:
        storage_document = Document(
            document_id=document.get("id", ""),
            text=document.get("text", ""),
            title=document.get("title", ""),
            url=document.get("url", ""),
            tool_name=document.get("tool_name", ""),
            # all document fields except for id, tool_name and text
            fields={
                k: v
                for k, v in document.items()
                if k not in ["id", "tool_name", "text"]
            },
            user_id=response_message.user_id,
            conversation_id=response_message.conversation_id,
            message_id=response_message.id,
        )
        document_ids_to_document[document["id"]] = storage_document

    documents = list(document_ids_to_document.values())
    response_message.documents = documents

    stream_end_data["documents"].extend(documents)
    if "search_results" not in event or event["search_results"] is None:
        event["search_results"] = []

    stream_event = StreamSearchResults(
        **event
        | {
            "documents": documents,
            "search_results": event["search_results"],
        },
    )
    stream_end_data["search_results"].extend(event["search_results"])
    return stream_event, stream_end_data, response_message, document_ids_to_document


def handle_stream_search_queries_generation(
    event: dict[str, Any],
    _: str,
    stream_end_data: dict[str, Any],
    response_message: Message,
    document_ids_to_document: dict[str, Document],
    **kwargs: Any,
) -> tuple[StreamSearchQueriesGeneration, dict[str, Any], Message, dict[str, Document]]:
    search_queries = []
    for search_query in event["search_queries"]:
        search_queries.append(
            SearchQuery(
                text=search_query.get("text", ""),
                generation_id=search_query.get("generation_id", ""),
            )
        )
    stream_event = StreamSearchQueriesGeneration(
        **event | {"search_queries": search_queries}
    )
    stream_end_data["search_queries"] = search_queries
    return stream_event, stream_end_data, response_message, document_ids_to_document


def handle_stream_tool_calls_generation(
    event: dict[str, Any],
    conversation_id: str,
    stream_end_data: dict[str, Any],
    response_message: Message,
    document_ids_to_document: dict[str, Document],
    session: DBSessionDep,
    should_store: bool,
    user_id: str,
    next_message_position: int,
) -> tuple[StreamToolCallsGeneration, dict[str, Any], Message, dict[str, Document]]:
    tool_calls = []
    tool_calls_event = event.get("tool_calls", [])
    for tool_call in tool_calls_event:
        tool_calls.append(
            ToolCall(
                name=tool_call.get("name"),
                parameters=tool_call.get("parameters"),
            )
        )
    stream_event = StreamToolCallsGeneration(**event | {"tool_calls": tool_calls})
    stream_end_data["tool_calls"].extend(tool_calls)

    if should_store:
        save_tool_calls_message(
            session,
            tool_calls,
            event.get("text", ""),
            user_id,
            next_message_position,
            conversation_id,
        )

    return stream_event, stream_end_data, response_message, document_ids_to_document


def handle_stream_citation_generation(
    event: dict[str, Any],
    _: str,
    stream_end_data: dict[str, Any],
    response_message: Message,
    document_ids_to_document: dict[str, Document],
    **kwargs: Any,
) -> tuple[StreamCitationGeneration, dict[str, Any], Message, dict[str, Document]]:
    citations = []
    for event_citation in event["citations"]:
        citation = Citation(
            text=event_citation.get("text"),
            user_id=response_message.user_id,
            start=event_citation.get("start"),
            end=event_citation.get("end"),
        )

        document_ids = event_citation.get("document_ids")
        for document_id in document_ids:
            document = document_ids_to_document.get(document_id, None)
            if document is not None:
                citation.documents.append(document)

        # Populates CitationDocuments table
        citations.append(citation)
    stream_event = StreamCitationGeneration(**event | {"citations": citations})
    stream_end_data["citations"].extend(citations)
    return stream_event, stream_end_data, response_message, document_ids_to_document


def handle_stream_tool_calls_chunk(
    event: dict[str, Any],
    _: str,
    stream_end_data: dict[str, Any],
    response_message: Message,
    document_ids_to_document: dict[str, Document],
    **kwargs: Any,
) -> tuple[StreamToolCallsChunk, dict[str, Any], Message, dict[str, Document]]:
    event["text"] = event.get("text", "")
    tool_call_delta = event.get("tool_call_delta", None)
    if tool_call_delta:
        tool_call = ToolCallDelta(
            name=tool_call_delta.get("name"),
            index=tool_call_delta.get("index"),
            parameters=tool_call_delta.get("parameters"),
        )
        event["tool_call_delta"] = tool_call

    stream_event = StreamToolCallsChunk.model_validate(event)
    return stream_event, stream_end_data, response_message, document_ids_to_document


def handle_stream_end(
    event: dict[str, Any],
    _: str,
    stream_end_data: dict[str, Any],
    response_message: Message,
    document_ids_to_document: dict[str, Document],
    **kwargs: Any,
) -> tuple[StreamEnd, dict[str, Any], Message, dict[str, Document]]:
    if response_message:
        response_message.citations = stream_end_data["citations"]
        response_message.text = stream_end_data["text"]

    stream_end_data["chat_history"] = (
        to_dict(event).get("response", {}).get("chat_history", [])
    )
    stream_end = StreamEnd.model_validate(event | stream_end_data)
    stream_event = stream_end
    return stream_event, stream_end_data, response_message, document_ids_to_document


def generate_langchain_chat_stream(
    session: DBSessionDep,
    model_deployment_stream: Generator[Any, None, None],
    response_message: Message,
    conversation_id: str,
    user_id: str,
    should_store: bool,
    **kwargs: Any,
):
    final_message_text = ""

    # send stream start event
    yield json.dumps(
        jsonable_encoder(
            ChatResponseEvent(
                event=StreamEvent.STREAM_START,
                data=StreamStart(
                    conversation_id=conversation_id,
                ),
            )
        )
    )
    for event in model_deployment_stream:
        stream_event = None
        if isinstance(event, AddableDict):
            # Generate tool queries
            if event.get("actions"):
                actions = [
                    action
                    for action in event.get("actions", [])
                    if isinstance(action, AgentActionMessageLog)
                ]
                for action in actions:
                    tool_name = action.tool

                    tool_input = ""
                    if isinstance(action.tool_input, str):
                        tool_input = action.tool_input
                    elif isinstance(action.tool_input, dict):
                        tool_input = "".join(
                            [str(val) for val in action.tool_input.values()]
                        )
                    content = (
                        action.message_log[0].content
                        if len(action.message_log) > 0
                        and isinstance(action.message_log[0].content, str)
                        else ""
                    )
                    # only take the first part of content before the newline
                    content = content.split("\n")[0]

                    # shape: "Plan: I will search for tips on writing an essay and fun facts about the Roman Empire. I will then write an answer using the information I find.\nAction: ```json\n[\n    {\n        \"tool_name\": \"internet_search\",\n        \"parameters\": {\n            \"query\": \"tips for writing an essay\"\n        }\n    },\n    {\n        \"tool_name\": \"internet_search\",\n        \"parameters\": {\n            \"query\": \"fun facts about the roman empire\"\n        }\n
                    stream_event = StreamToolInput(
                        # TODO: switch to diff types
                        input_type=ToolInputType.CODE,
                        tool_name=tool_name,
                        input=tool_input,
                        text=content,
                    )
            # Generate documents / call tool
            if steps := event.get("steps"):
                step = steps[0] if len(steps) > 0 else None

                if not step:
                    continue

                result = step.observation
                # observation can be a dictionary for python interpreter or a list of docs for web search

                """
                internet search results
                "observation": [
                    {
                        "url": "https://www.businessinsider.com/billionaire-bill-gates-net-worth-spending-2018-8?op=1",
                        "content": "Source: Business Inside"
                    }...
                ]
                """
                if isinstance(result, list):
                    stream_event = StreamToolResult(
                        tool_name=step.action.tool,
                        result=result,
                        documents=[],
                    )

                """
                Python interpreter output
                "observation": {
                    "output_files": [],
                    "sucess": true,
                    "std_out": "20572000000000\n",
                    "std_err": "",
                    "code_runtime": 1181
                }
                """
                if isinstance(result, dict):
                    stream_event = StreamToolResult(
                        tool_name=step.action.tool,
                        result=result,
                        documents=[],
                    )

            # final output
            if event.get("output", "") and event.get("citations", []):
                final_message_text = event.get("output", "")
                stream_event = StreamEnd(
                    conversation_id=conversation_id,
                    text=event.get("output", ""),
                    # WARNING: Citations are not yet supported in langchain
                    citations=[],
                    documents=[],
                    search_results=[],
                    finish_reason="COMPLETE",
                )

            if stream_event:
                yield json.dumps(
                    jsonable_encoder(
                        ChatResponseEvent(
                            event=stream_event.event_type,
                            data=stream_event,
                        )
                    )
                )
    if should_store:
        update_conversation_after_turn(
            session, response_message, conversation_id, final_message_text, user_id
        )
