from itertools import tee
from typing import Any, AsyncGenerator, Dict, List

from fastapi import HTTPException

from backend.chat.base import BaseChat
from backend.chat.collate import rerank_and_chunk, to_dict
from backend.chat.custom.utils import get_deployment
from backend.chat.enums import StreamEvent
from backend.config.tools import AVAILABLE_TOOLS, ToolName
from backend.crud.file import get_files_by_conversation_id
from backend.schemas.chat import ChatMessage, ChatRole
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.tool import Tool
from backend.services.logger import get_logger, send_log_message

logger = get_logger()
MAX_STEPS = 15


class CustomChat(BaseChat):
    """Custom chat flow not using integrations for models."""

    async def chat(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> AsyncGenerator[Any, Any]:
        """
        Chat flow for custom models.

        Args:
            chat_request (CohereChatRequest): Chat request.
            **kwargs (Any): Keyword arguments.

        Returns:
            Generator[StreamResponse, None, None]: Chat response.
        """
        # Choose the deployment model - validation already performed by request validator
        deployment_model = get_deployment(kwargs.get("deployment_name"), **kwargs)
        send_log_message(
            logger,
            f"Using deployment {deployment_model.__class__.__name__}",
            level="info",
            conversation_id=kwargs.get("conversation_id"),
            user_id=kwargs.get("user_id", ""),
        )

        if len(chat_request.tools) > 0 and len(chat_request.documents) > 0:
            raise HTTPException(
                status_code=400, detail="Both tools and documents cannot be provided."
            )

        self.chat_request = chat_request
        self.is_first_start = True

        try:
            stream = self.call_chat(self.chat_request, deployment_model, **kwargs)

            async for event in stream:
                result = self.handle_event(event, chat_request)

                if result:
                    yield result

                if event[
                    "event_type"
                ] == StreamEvent.STREAM_END and self.is_final_event(
                    event, chat_request
                ):
                    send_log_message(
                        logger,
                        f"Final event: {event}",
                        level="info",
                        conversation_id=kwargs.get("conversation_id"),
                        user_id=kwargs.get("user_id"),
                    )
                    break
        except Exception as e:
            yield {
                "event_type": StreamEvent.STREAM_END,
                "finish_reason": "ERROR",
                "error": str(e),
                "status_code": 500,
            }

    def is_final_event(
        self, event: Dict[str, Any], chat_request: CohereChatRequest
    ) -> bool:
        # The event is final if:
        # 1. It is a stream end event with no tool calls - direct answer
        # 2. It is a stream end event with tool calls, but no managed tools - tool calls generation only
        if "response" in event:
            response = event["response"]
        else:
            return True

        return not ("tool_calls" in response and response["tool_calls"]) or (
            "tool_calls" in response
            and response["tool_calls"]
            and chat_request.tools
            and not self.get_managed_tools(self.chat_request)
        )

    def handle_event(
        self, event: Dict[str, Any], chat_request: CohereChatRequest
    ) -> Dict[str, Any]:
        # All events other than stream start and stream end are returned
        if (
            event["event_type"] != StreamEvent.STREAM_START
            and event["event_type"] != StreamEvent.STREAM_END
        ):
            return event

        # Only the first occurrence of stream start is returned
        if event["event_type"] == StreamEvent.STREAM_START:
            if self.is_first_start:
                self.is_first_start = False
                return event

        # Only the final occurrence of stream end is returned
        # The final event is the one that does not contain tool calls
        if event["event_type"] == StreamEvent.STREAM_END:
            if self.is_final_event(event, chat_request):
                return event

        return None

    def is_not_direct_answer(self, event: Dict[str, Any]) -> bool:
        # If the event contains tool calls, it is not a direct answer
        return (
            event["event_type"] == StreamEvent.TOOL_CALLS_GENERATION
            and "tool_calls" in event
        )

    async def call_chat(self, chat_request, deployment_model, **kwargs: Any):
        trace_id = kwargs.get("trace_id", "")
        user_id = kwargs.get("user_id", "")
        agent_id = kwargs.get("agent_id", "")
        managed_tools = self.get_managed_tools(chat_request)

        tool_names = []
        if managed_tools:
            chat_request.tools = managed_tools
            tool_names = [tool.name for tool in managed_tools]

        # Add files to chat history if the tool requires it and files are provided
        if chat_request.file_ids:
            if ToolName.Read_File in tool_names or ToolName.Search_File in tool_names:
                chat_request.chat_history = self.add_files_to_chat_history(
                    chat_request.chat_history,
                    kwargs.get("conversation_id"),
                    kwargs.get("session"),
                    kwargs.get("user_id"),
                )
        else:
            # TODO: remove this workaround
            # For now we're removing the Read_File and Search_File tools if no files are provided
            chat_request.tools = [
                tool
                for tool in chat_request.tools
                if tool.name != ToolName.Read_File and tool.name != ToolName.Search_File
            ]

        # Loop until there are no new tool calls
        for step in range(MAX_STEPS):
            send_log_message(
                logger,
                f"Step {step + 1}",
                level="info",
                conversation_id=kwargs.get("conversation_id"),
                user_id=kwargs.get("user_id"),
            )
            send_log_message(
                logger,
                f"Chat request: {chat_request.dict()}",
                level="info",
                conversation_id=kwargs.get("conversation_id"),
                user_id=kwargs.get("user_id"),
            )

            # Invoke chat stream
            has_tool_calls = False
            async for event in deployment_model.invoke_chat_stream(
                chat_request, trace_id=trace_id, user_id=user_id, agent_id=agent_id
            ):
                if event["event_type"] == StreamEvent.STREAM_END:
                    chat_request.chat_history = event["response"].get(
                        "chat_history", []
                    )
                elif event["event_type"] == StreamEvent.TOOL_CALLS_GENERATION:
                    has_tool_calls = True

                yield event

            send_log_message(
                logger,
                f"Chat stream completed. Has tool calls: {has_tool_calls}",
                level="info",
                conversation_id=kwargs.get("conversation_id"),
                user_id=kwargs.get("user_id"),
            )

            # Check for new tool calls in the chat history
            if has_tool_calls:
                # Handle tool calls
                tool_results = await self.call_tools(
                    chat_request.chat_history, deployment_model, **kwargs
                )

                # Remove the message if tool results are present
                if tool_results:
                    chat_request.tool_results = [result for result in tool_results]
                    chat_request.message = ""
            else:
                break  # Exit loop if there are no new tool calls

        # Restore the original chat request message if needed
        self.chat_request = chat_request

    def update_chat_history_with_tool_results(
        self, chat_request: Any, tool_results: List[Dict[str, Any]]
    ):
        if not hasattr(chat_request, "chat_history"):
            chat_request.chat_history = []

        chat_request.chat_history.extend(tool_results)

    async def call_tools(self, chat_history, deployment_model, **kwargs: Any):
        tool_results = []
        if "tool_calls" not in chat_history[-1]:
            return tool_results

        tool_calls = chat_history[-1]["tool_calls"]
        tool_plan = chat_history[-1].get("message", None)
        send_log_message(
            logger,
            f"Tool calls: {tool_calls}",
            level="info",
            conversation_id=kwargs.get("conversation_id"),
            user_id=kwargs.get("user_id"),
        )
        send_log_message(
            logger,
            f"Tool plan: {tool_plan}",
            level="info",
            conversation_id=kwargs.get("conversation_id"),
            user_id=kwargs.get("user_id"),
        )

        # TODO: Call tools in parallel
        for tool_call in tool_calls:
            tool = AVAILABLE_TOOLS.get(tool_call["name"])
            if not tool:
                continue

            outputs = await tool.implementation().call(
                parameters=tool_call.get("parameters"),
                session=kwargs.get("session"),
                model_deployment=deployment_model,
                user_id=kwargs.get("user_id"),
                trace_id=kwargs.get("trace_id"),
                agent_id=kwargs.get("agent_id"),
            )

            # If the tool returns a list of outputs, append each output to the tool_results list
            # Otherwise, append the single output to the tool_results list
            outputs = outputs if isinstance(outputs, list) else [outputs]
            for output in outputs:
                tool_results.append({"call": tool_call, "outputs": [output]})

        tool_results = await rerank_and_chunk(tool_results, deployment_model, **kwargs)
        send_log_message(
            logger,
            f"Tool results: {tool_results}",
            level="info",
            conversation_id=kwargs.get("conversation_id"),
            user_id=kwargs.get("user_id"),
        )

        return tool_results

    async def handle_tool_calls_stream(self, tool_results_stream):
        # Process the stream and return the chat history, and a copy of the stream and a flag indicating if the response is a direct answer
        stream, stream_copy = tee(tool_results_stream)
        is_direct_answer = True

        chat_history = []
        async for event in stream:
            if event["event_type"] == StreamEvent.STREAM_END:
                stream_chat_history = []
                if "response" in event:
                    stream_chat_history = event["response"].get("chat_history", [])
                elif "chat_history" in event:
                    stream_chat_history = event["chat_history"]

                for message in stream_chat_history:
                    if not isinstance(message, dict):
                        message = to_dict(message)

                    chat_history.append(
                        ChatMessage(
                            role=message.get("role"),
                            message=message.get("message", ""),
                            tool_results=message.get("tool_results", None),
                            tool_calls=message.get("tool_calls", None),
                        )
                    )

            elif (
                event["event_type"] == StreamEvent.TOOL_CALLS_GENERATION
                and "tool_calls" in event
            ):
                is_direct_answer = False

        return is_direct_answer, chat_history, stream_copy

    def get_managed_tools(self, chat_request: CohereChatRequest):
        return [
            Tool(**AVAILABLE_TOOLS.get(tool.name).model_dump())
            for tool in chat_request.tools
            if AVAILABLE_TOOLS.get(tool.name)
        ]

    def add_files_to_chat_history(
        self,
        chat_history: List[Dict[str, str]],
        conversation_id: str,
        session: Any,
        user_id: str,
    ) -> List[Dict[str, str]]:
        if session is None or conversation_id is None or len(conversation_id) == 0:
            return chat_history

        available_files = get_files_by_conversation_id(
            session, conversation_id, user_id
        )
        files_message = "The user uploaded the following attachments:\n"

        for file in available_files:
            word_count = len(file.file_content.split())

            # Use the first 25 words as the document preview in the preamble
            num_words = min(25, word_count)
            preview = " ".join(file.file_content.split()[:num_words])

            files_message += f"Filename: {file.file_name}\nWord Count: {word_count} Preview: {preview}\n\n"

        chat_history.append(ChatMessage(message=files_message, role=ChatRole.SYSTEM))
        return chat_history
