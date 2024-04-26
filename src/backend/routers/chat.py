import json
import os
from distutils.util import strtobool
from typing import Any, Generator, List, Union
from uuid import uuid4

from cohere.types import StreamedChatResponse
from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from langchain_core.agents import AgentActionMessageLog
from langchain_core.runnables.utils import AddableDict
from sse_starlette.sse import EventSourceResponse

from backend.chat.custom.custom import CustomChat
from backend.chat.custom.langchain import LangChainChat
from backend.chat.enums import StreamEvent
from backend.config.tools import AVAILABLE_TOOLS
from backend.crud import conversation as conversation_crud
from backend.crud import file as file_crud
from backend.crud import message as message_crud
from backend.models import get_session
from backend.models.citation import Citation
from backend.models.conversation import Conversation
from backend.models.database import DBSessionDep
from backend.models.document import Document
from backend.models.message import Message, MessageAgent, MessageType
from backend.schemas.chat import (
    BaseChatRequest,
    ChatMessage,
    ChatResponseEvent,
    ChatRole,
    NonStreamedChatResponse,
    StreamCitationGeneration,
    StreamEnd,
    StreamSearchQueriesGeneration,
    StreamSearchResults,
    StreamStart,
    StreamTextGeneration,
    StreamToolInput,
    StreamToolResult,
    ToolInputType,
)
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.conversation import UpdateConversation
from backend.schemas.file import UpdateFile
from backend.schemas.langchain_chat import LangchainChatRequest
from backend.schemas.search_query import SearchQuery
from backend.schemas.tool import ToolCall
from backend.services.request_validators import (
    validate_chat_request,
    validate_deployment_header,
    validate_user_header,
)

router = APIRouter(
    dependencies=[
        Depends(get_session),
        Depends(validate_chat_request),
        Depends(validate_user_header),
    ]
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
    ) = process_chat(session, chat_request, request)

    return EventSourceResponse(
        generate_chat_stream(
            session,
            CustomChat().chat(
                chat_request,
                stream=True,
                deployment_name=deployment_name,
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
def chat(
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
    ) = process_chat(session, chat_request, request)

    return generate_chat_response(
        session,
        CustomChat().chat(
            chat_request,
            stream=False,
            deployment_name=deployment_name,
            file_paths=file_paths,
            managed_tools=managed_tools,
        ),
        response_message,
        conversation_id,
        user_id,
        should_store=should_store,
    )


def process_chat(
    session: DBSessionDep, chat_request: BaseChatRequest, request: Request
) -> tuple[DBSessionDep, BaseChatRequest, Union[list[str], None], Message, str, str]:
    """
    Process a chat request.

    Args:
        chat_request (BaseChatRequest): Chat request data.
        session (DBSessionDep): Database session.
        request (Request): Request object.

    Returns:
        Tuple: Tuple containing necessary data to construct the responses.
    """
    user_id = request.headers.get("User-Id", "")
    deployment_name = request.headers.get("Deployment-Name", "")
    should_store = chat_request.chat_history is None
    conversation = get_or_create_conversation(
        session, chat_request, user_id, should_store
    )

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
        attach_files_to_messages(
            session, user_id, user_message.id, chat_request.file_ids
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
        conversation.id,
        user_id,
        deployment_name,
        should_store,
        managed_tools,
    )


def get_or_create_conversation(
    session: DBSessionDep,
    chat_request: BaseChatRequest,
    user_id: str,
    should_store: bool,
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
        conversation = Conversation(
            user_id=user_id,
            id=chat_request.conversation_id,
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
    message = Message(
        id=id,
        user_id=user_id,
        conversation_id=conversation_id,
        text=text,
        position=user_message_position,
        is_active=True,
        agent=agent,
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
        files = file_crud.get_files_by_ids(session, file_ids, user_id)
        file_paths = [file.file_path for file in files]

    return file_paths


def attach_files_to_messages(
    session: DBSessionDep,
    user_id: str,
    message_id: str,
    file_ids: List[str] | None = None,
) -> None:
    """
    Attach Files to Message if the File does not have a message_id foreign key.

    Args:
        session (DBSessionDep): Database session.
        user_id (str): User ID.
        message_id (str): Message ID to attach to if needed.
        file_ids (List): List of File IDs.

    Returns:
        None
    """
    if file_ids is not None:
        files = file_crud.get_files_by_ids(session, file_ids, user_id)
        for file in files:
            if file.message_id is None:
                file_crud.update_file(session, file, UpdateFile(message_id=message_id))


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

    text_messages = [
        message
        for message in conversation.messages[:user_message_position]
        if message.type == MessageType.TEXT
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
    new_conversation = UpdateConversation(
        description=final_message_text,
        user_id=conversation.user_id,
    )
    conversation_crud.update_conversation(session, conversation, new_conversation)


def generate_chat_stream(
    session: DBSessionDep,
    model_deployment_stream: Generator[StreamedChatResponse, None, None],
    response_message: Message,
    conversation_id: str,
    user_id: str,
    should_store: bool = True,
    **kwargs: Any,
) -> Generator[bytes, Any, None]:
    """
    Generate chat stream from model deployment stream.

    Args:
        session (DBSessionDep): Database session.
        model_deployment_stream (Generator[StreamResponse, None, None]): Model deployment stream.
        response_message (Message): Response message object.
        conversation_id (str): Conversation ID.
        user_id (str): User ID.
        should_store (bool): Whether to store the conversation in the database.
        **kwargs (Any): Additional keyword arguments.

    Yields:
        bytes: Byte representation of chat response event.
    """
    stream_end_data = {
        "conversation_id": conversation_id,
        "response_id": response_message.id,
    }

    # Given a stream of CohereEventStream objects, save the final message to DB and yield byte representations
    final_message_text = ""

    # Map the user facing document_ids field returned from model to storage ID for document model
    document_ids_to_document = {}
    all_citations = []

    stream_event = None
    for event in model_deployment_stream:
        if event["event_type"] == StreamEvent.STREAM_START:
            stream_event = StreamStart.model_validate(event)
            response_message.generation_id = event["generation_id"]
            stream_end_data["generation_id"] = event["generation_id"]
        elif event["event_type"] == StreamEvent.TEXT_GENERATION:
            final_message_text += event["text"]
            stream_event = StreamTextGeneration.model_validate(event)
        elif event["event_type"] == StreamEvent.SEARCH_RESULTS:
            for document in event["documents"]:
                storage_document = Document(
                    document_id=document.get("id", ""),
                    text=document.get("text", ""),
                    title=document.get("title", ""),
                    url=document.get("url", ""),
                    user_id=response_message.user_id,
                    conversation_id=response_message.conversation_id,
                    message_id=response_message.id,
                )
                document_ids_to_document[document["id"]] = storage_document

            documents = list(document_ids_to_document.values())
            response_message.documents = documents
            stream_end_data["documents"] = documents
            if "search_results" not in event or event["search_results"] is None:
                event["search_results"] = []
            stream_event = StreamSearchResults(
                **event
                | {
                    "documents": documents,
                    "search_results": event["search_results"],
                },
            )
        elif event["event_type"] == StreamEvent.SEARCH_QUERIES_GENERATION:
            search_queries = []
            for search_query in event["search_queries"]:
                search_queries.append(
                    SearchQuery(
                        text=search_query.text,
                        generation_id=search_query.generation_id,
                    )
                )
            stream_event = StreamSearchQueriesGeneration(
                **event | {"search_queries": search_queries}
            )
            stream_end_data["search_queries"] = search_queries
        elif event["event_type"] == StreamEvent.TOOL_CALLS_GENERATION:
            tool_calls = []
            for tool_call in event["tool_calls"]:
                tool_calls.append(
                    ToolCall(
                        name=tool_call.name,
                        parameters=tool_call.parameters,
                    )
                )
            stream_end_data["tool_calls"] = tool_calls
        elif event["event_type"] == StreamEvent.CITATION_GENERATION:
            citations = []
            for event_citation in event["citations"]:
                citation = Citation(
                    text=event_citation.text,
                    user_id=response_message.user_id,
                    start=event_citation.start,
                    end=event_citation.end,
                    document_ids=event_citation.document_ids,
                )
                for document_id in citation.document_ids:
                    document = document_ids_to_document.get(document_id, None)
                    if document is not None:
                        citation.documents.append(document)
                citations.append(citation)
            stream_event = StreamCitationGeneration(**event | {"citations": citations})
            all_citations.extend(citations)
        elif event["event_type"] == StreamEvent.STREAM_END:
            response_message.citations = all_citations
            response_message.text = final_message_text

            stream_end_data["citations"] = all_citations
            stream_end_data["text"] = final_message_text
            stream_end = StreamEnd.model_validate(event | stream_end_data)
            stream_event = stream_end

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
            session, response_message, conversation_id, final_message_text, user_id
        )


def generate_chat_response(
    session: DBSessionDep,
    model_deployment_response: Generator[StreamedChatResponse, None, None],
    response_message: Message,
    conversation_id: str,
    user_id: str,
    should_store: bool = True,
    **kwargs: Any,
) -> NonStreamedChatResponse:
    """
    Generate chat response from model deployment non streaming response.

    Args:
        session (DBSessionDep): Database session.
        model_deployment_response (Any): Model deployment response.
        response_message (Message): Response message object.
        conversation_id (str): Conversation ID.
        user_id (str): User ID.
        should_store (bool): Whether to store the conversation in the database.
        **kwargs (Any): Additional keyword arguments.

    Returns:
        NonStreamedChatResponse: Chat response.
    """

    if not isinstance(model_deployment_response, dict):
        response = model_deployment_response.__dict__
    else:
        response = model_deployment_response

    chat_history = [
        ChatMessage(
            role=message.role,
            message=message.message,
        )
        for message in response.get("chat_history", [])
    ]

    documents = []
    if "documents" in response and response["documents"]:
        documents = [
            Document(
                document_id=document.get("id", ""),
                text=document.get("text", ""),
                title=document.get("title", ""),
                url=document.get("url", ""),
            )
            for document in response.get("documents")
        ]

    tool_calls = []
    if "tool_calls" in response and response["tool_calls"]:
        for tool_call in response.get("tool_calls", []):
            tool_calls.append(
                ToolCall(
                    name=tool_call.name,
                    parameters=tool_call.parameters,
                )
            )

    non_streamed_chat_response = NonStreamedChatResponse(
        text=response.get("text", ""),
        response_id=response.get("response_id", ""),
        generation_id=response.get("generation_id", ""),
        chat_history=chat_history,
        finish_reason=response.get("finish_reason", ""),
        citations=response.get("citations", []),
        search_queries=response.get("search_queries", []),
        documents=documents,
        search_results=response.get("search_results", []),
        event_type=StreamEvent.NON_STREAMED_CHAT_RESPONSE,
        is_finished=True,
        conversation_id=conversation_id,
        tool_calls=tool_calls,
    )

    response_message.text = non_streamed_chat_response.text
    response_message.generation_id = non_streamed_chat_response.generation_id

    if should_store:
        update_conversation_after_turn(
            session,
            response_message,
            conversation_id,
            non_streamed_chat_response.text,
            user_id,
        )

    return non_streamed_chat_response


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
                    is_finished=False,
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
                        is_finished=False,
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
                        is_finished=False,
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
                        is_finished=False,
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
