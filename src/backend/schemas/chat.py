from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, ClassVar, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.chat.enums import StreamEvent
from backend.schemas.citation import Citation
from backend.schemas.document import Document
from backend.schemas.search_query import SearchQuery
from backend.schemas.tool import Tool, ToolCall, ToolCallDelta


@dataclass
class EventState:
    distances_plans: list
    distances_actions: list
    previous_plan: str
    previous_action: str


class ChatRole(StrEnum):
    """
    One of CHATBOT|USER|SYSTEM to identify who the message is coming from.
    """
    CHATBOT = "CHATBOT"
    USER = "USER"
    SYSTEM = "SYSTEM"
    TOOL = "TOOL"


class ChatCitationQuality(StrEnum):
    """
    Dictates the approach taken to generating citations by allowing the user to specify
    whether they want "accurate" results or "fast" results. Defaults to "accurate".
    """
    FAST = "FAST"
    ACCURATE = "ACCURATE"


class ToolInputType(StrEnum):
    """
    Type of input passed to the tool
    """
    QUERY = "QUERY"
    CODE = "CODE"


class ChatMessage(BaseModel):
    """
    A list of previous messages between the user and the model, meant to give the mode
    conversational context for responding to the user's message.
    """
    role: ChatRole = Field(
        ...,
        title="Role",
        description="One of CHATBOT|USER|SYSTEM to identify who the message is coming from.",
    )
    message: Optional[str] = Field(
        None,
        title="Message",
        description="Contents of the chat message.",
    )
    tool_plan: Optional[str] = Field(
        None,
        title="Tool Plan",
        description="Contents of the tool plan.",
    )
    tool_results: Optional[list[dict[str, Any]]] = Field(
        None,
        title="Tool Results",
        description="Results from the tool call.",
    )
    tool_calls: Optional[list[dict[str, Any]]] = Field(
        None,
        title="Tool Calls",
        description="List of tool calls generated for custom tools",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "message": self.message,
            "tool_results": self.tool_results,
            "tool_calls": self.tool_calls,
        }


# TODO: fix titles of these types
class ChatResponse(ABC, BaseModel):
    """
    Abstract class for Chat Responses
    """
    event_type: ClassVar[StreamEvent] = Field(
        ...,
        title="Event Type",
        description="Chat response event type",
    )


class StreamStart(ChatResponse):
    """Stream start event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.STREAM_START
    generation_id: Optional[str] = Field(
        None,
        title="Generation ID",
        description="Generation ID for the event",
    )
    conversation_id: Optional[str] = Field(
        None,
        title="Conversation ID",
        description="Conversation ID for the event",
    )


class StreamTextGeneration(ChatResponse):
    """Stream text generation event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.TEXT_GENERATION
    text: str = Field(
        ...,
        title="Text",
        description="Contents of the chat message",
    )


class StreamCitationGeneration(ChatResponse):
    """Stream citation generation event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.CITATION_GENERATION
    citations: list[Citation] = Field(
        [],
        title="Citations",
        description="Citations for the chat message",
    )


class StreamQueryGeneration(ChatResponse):
    """Stream query generation event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.SEARCH_QUERIES_GENERATION
    query: str = Field(
        ...,
        title="Query",
        description="Search query used to generate grounded response with citations",
    )


class StreamSearchResults(ChatResponse):
    """Stream search generation event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.SEARCH_RESULTS
    search_results: list[dict[str, Any]] = Field(
        [],
        title="Search Results",
        description="Search results used to generate grounded response with citations",
    )
    documents: list[Document] = Field(
        [],
        title="Documents",
        description="Documents used to generate grounded response with citations",
    )


class StreamToolInput(ChatResponse):
    """Stream tool input generation event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.TOOL_INPUT
    input_type: ToolInputType = Field(
        ...,
        title="Input Type",
        description="Tool input type",
    )
    tool_name: str = Field(
        ...,
        title="Tool Name",
        description="Name of the tool to be used",
    )
    input: str = Field(
        ...,
        title="Input",
        description="Tool input",
    )
    text: str = Field(
        ...,
        title="Text",
        description="Contents of the chat message",
    )


class StreamToolResult(ChatResponse):
    """Stream tool result generation event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.TOOL_RESULT
    result: Any = Field(
        ...,
        title="Result",
        description="Result from the tool",
    )
    tool_name: str = Field(
        ...,
        title="Tool Name",
        description="Name of tool that generated the result",
    )
    documents: list[Document] = Field(
        [],
        title="Documents",
        description="Documents used to generate grounded response with citations",
    )


class StreamSearchQueriesGeneration(ChatResponse):
    """Stream queries generation event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.SEARCH_QUERIES_GENERATION
    search_queries: list[SearchQuery] = Field(
        [],
        title="Search Queries",
        description="Search query used to generate grounded response with citations",
    )


class StreamToolCallsGeneration(ChatResponse):
    """Stream tool calls generation event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.TOOL_CALLS_GENERATION
    stream_search_results: Optional[StreamSearchResults] = Field(
        None,
        title="Stream Search Results",
        description="Search results used to generate grounded response with citations",
    )
    tool_calls: Optional[list[ToolCall]] = Field(
        [],
        title="Tool Calls",
        description="List of tool calls generated for custom tools",
    )
    text: str | None = Field(
        None,
        title="Text",
        description="Contents of the chat message",
    )


class StreamEnd(ChatResponse):
    """Stream end generation event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.STREAM_END
    message_id: Optional[str] = Field(
        None,
        title="Message ID",
        description="Unique identifier for the message",
    )
    response_id: Optional[str] = Field(
        None,
        title="Response ID",
        description="Unique identifier for the response",
    )
    generation_id: Optional[str] = Field(
        None,
        title="Generation ID",
        description="Unique identifier for the generation",
    )
    conversation_id: Optional[str] = Field(
        None,
        title="Conversation ID",
        description="Unique identifier for the conversation",
    )
    text: str = Field(
        ...,
        title="Text",
        description="Contents of the chat message",
    )
    citations: list[Citation] = Field(
        [],
        title="Citations",
        description="Citations for the chat messae.",
    )
    documents: list[Document] = Field(
        [],
        title="Documents",
        description="Documents used to generate grounded response with citations",
    )
    search_results: list[dict[str, Any]] = Field(
        [],
        title="Search Results",
        description="Search results used to generate grounded response with citations",
    )
    search_queries: list[SearchQuery] = Field(
        [],
        title="Search Queries",
        description="List of generated search queries",
    )
    tool_calls: list[ToolCall] = Field(
        [],
        title="Tool Calls",
        description="List of tool calls generated for custom tools",
    )
    finish_reason: Optional[str] = Field(
        None,
        title="Finish Reason",
        description="Reson why the model finished the request",
    )
    chat_history: Optional[list[ChatMessage]] = Field(
        None,
        title="Chat History",
        description="A list of entries used to construct the conversation. If provided, these messages will be used to build the prompt and the conversation_id will be ignored so no data will be stored to maintain state.",
    )
    error: Optional[str] = Field(
        None,
        title="Error",
        description="Error message if the response is an error",
    )


class NonStreamedChatResponse(ChatResponse):
    """Non streamed chat response"""
    response_id: Optional[str] = Field(
        None,
        title="Response ID",
        description="Unique identifier for the response",
    )
    generation_id: Optional[str] = Field(
        None,
        title="Generation ID",
        description="Unique identifier for the generation",
    )
    chat_history: Optional[list[ChatMessage]] = Field(
        None,
        title="Chat History",
        description="A list of previous messages between the user and the model, meant to give the model conversational context for responding to the user's message.",
    )
    finish_reason: str = Field(
        ...,
        title="Finish Reason",
        description="Reason the chat stream ended",
    )
    text: str = Field(
        ...,
        title="Text",
        description="Contents of the chat message",
    )
    citations: list[Citation] | None = Field(
        [],
        title="Citations",
        description="Citations for the chat message",
    )
    documents: list[Document] | None = Field(
        [],
        title="Documents",
        description="Documents used to generate grounded response with citations",
    )
    search_results: list[dict[str, Any]] | None = Field(
        [],
        title="Search Results",
        description="Search results used to generate grounded response with citations",
    )
    search_queries: list[SearchQuery] | None = Field(
        [],
        title="Search Queries",
        description="List of generated search queries.",
    )
    conversation_id: Optional[str] = Field(
        None,
        title="Conversation ID",
        description="To store a conversation then create a conversation id and use it for every related request",
    )
    tool_calls: list[ToolCall] | None = Field(
        [],
        title="Tool Calls",
        description="List of tool calls generated for custom tools",
    )
    error: Optional[str] = Field(
        None,
        title="Error",
        description="Error message if the response is an error",
    )


class StreamToolCallsChunk(ChatResponse):
    """Stream tool call chunk generated event"""
    event_type: ClassVar[StreamEvent] = StreamEvent.TOOL_CALLS_CHUNK
    tool_call_delta: Optional[ToolCallDelta] = Field(
        ToolCallDelta(
            name=None,
            index=None,
            parameters=None,
        ),
        title="Tool Call Delta",
        description="Partial tool call",
    )
    text: Optional[str] = Field(
        None,
        title="Text",
        description="Contents of the chat message",
    )


StreamEventType = Union[
    StreamStart,
    StreamTextGeneration,
    StreamCitationGeneration,
    StreamQueryGeneration,
    StreamSearchResults,
    StreamEnd,
    StreamToolInput,
    StreamToolResult,
    StreamSearchQueriesGeneration,
    StreamToolCallsGeneration,
    StreamToolCallsChunk,
    NonStreamedChatResponse,
]


class ChatResponseEvent(BaseModel):
    """
    Chat Response Event
    """
    event: StreamEvent = Field(
        ...,
        title="Event",
        description="Type of stream event",
    )
    data: StreamEventType = Field(
        ...,
        title="Data",
        description="Data returned from chat response of a given event type",
    )


class BaseChatRequest(BaseModel):
    """
    Base Chat Request
    """
    message: str = Field(
        ...,
        title="Message",
        description="The message to send to the chatbot",
    )
    chat_history: list[ChatMessage] | None = Field(
        None,
        title="Chat History",
        description="A list of entries used to construct the conversation. If provided, these messages will be used to build the prompt and the conversation_id will be ignored so no data will be stored to maintain state.",
    )
    conversation_id: str = Field(
        default_factory=lambda: str(uuid4()),
        title="Conversation ID",
        description="To store a conversation then create a conversation id and use it for every related request",
    )
    tools: Optional[list[Tool]] = Field(
        default_factory=list,
        title="Tools",
        description="""
            List of custom or managed tools to use for the response.
            If passing in managed tools, you only need to provide the name of the tool.
            If passing in custom tools, you need to provide the name, description, and optionally parameter defintions of the tool.
            Passing a mix of custom and managed tools is not supported.

            Managed Tools Examples:
            tools=[
                {
                    "name": "Wiki Retriever - LangChain",
                },
                {
                    "name": "Calculator",
                }
            ]

            Custom Tools Examples:
            tools=[
                {
                    "name": "movie_title_generator",
                    "description": "tool to generate a cool movie title",
                    "parameter_definitions": {
                        "synopsis": {
                            "description": "short synopsis of the movie",
                            "type": "str",
                            "required": true
                        }
                    }
                },
                {
                    "name": "random_number_generator",
                    "description": "tool to generate a random number between min and max",
                    "parameter_definitions": {
                        "min": {
                            "description": "minimum number",
                            "type": "int",
                            "required": true
                        },
                        "max": {
                            "description": "maximum number",
                            "type": "int",
                            "required": true
                        }
                    }
                },
                {
                    "name": "joke_generator",
                    "description": "tool to generate a random joke",
                }
            ]
        """,
    )
