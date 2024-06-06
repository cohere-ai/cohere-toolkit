import logging
from itertools import tee
from typing import Any, Dict, Generator, List

from fastapi import HTTPException

from backend.chat.base import BaseChat
from backend.chat.collate import combine_documents
from backend.chat.custom.utils import get_deployment
from backend.chat.enums import StreamEvent
from backend.config.tools import AVAILABLE_TOOLS, ToolName
from backend.crud.file import get_files_by_conversation_id
from backend.model_deployments.base import BaseDeployment
from backend.schemas.chat import ChatMessage
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.tool import Category, Tool
from backend.services.logger import get_logger


class CustomChat(BaseChat):
    """Custom chat flow not using integrations for models."""

    logger = get_logger()

    def chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
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
        self.logger.info(f"Using deployment {deployment_model.__class__.__name__}")

        if len(chat_request.tools) > 0 and len(chat_request.documents) > 0:
            raise HTTPException(
                status_code=400, detail="Both tools and documents cannot be provided."
            )

        # If a direct answer is generated instead of tool calls, the chat will not be called again
        # Instead, the direct answer will be returned from the stream
        stream = self.handle_managed_tools(chat_request, deployment_model, **kwargs)

        first_event, generated_direct_answer = next(stream)

        if generated_direct_answer:
            yield first_event
            for event, _ in stream:
                yield event
        else:
            chat_request = first_event
            invoke_method = (
                deployment_model.invoke_chat_stream
                if kwargs.get("stream", True)
                else deployment_model.invoke_chat
            )

            yield from invoke_method(chat_request)

    def handle_managed_tools(
        self,
        chat_request: CohereChatRequest,
        deployment_model: BaseDeployment,
        **kwargs: Any,
    ) -> Generator[Any, None, None]:
        """
        This function handles the managed tools.

        Args:
            chat_request (CohereChatRequest): The chat request
            deployment_model (BaseDeployment): The deployment model
            **kwargs (Any): The keyword arguments

        Returns:
            Generator[Any, None, None]: The tool results or the chat response, and a boolean indicating if a direct answer was generated
        """
        tools = [
            Tool(**AVAILABLE_TOOLS.get(tool.name).model_dump())
            for tool in chat_request.tools
            if AVAILABLE_TOOLS.get(tool.name)
        ]

        if not tools:
            yield chat_request, False

        for event, should_return in self.get_tool_results(
            chat_request.message,
            chat_request.chat_history,
            tools,
            kwargs.get("conversation_id"),
            deployment_model,
            kwargs,
        ):
            if should_return:
                yield event, True
            else:
                chat_request.tool_results = event
                chat_request.tools = tools
                yield chat_request, False

    def get_tool_results(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        tools: list[Tool],
        conversation_id: str,
        deployment_model: BaseDeployment,
        kwargs: Any,
    ) -> Any:
        """
        Invokes the tools and returns the results. If no tools calls are generated, it returns the chat response
        as a direct answer.

        Args:
            message (str): The message to be processed
            chat_history (List[Dict[str, str]]): The chat history
            tools (list[Tool]): The tools to be invoked
            conversation_id (str): The conversation ID
            deployment_model (BaseDeployment): The deployment model
            kwargs (Any): The keyword arguments

        Returns:
            Any: The tool results or the chat response, and a boolean indicating if a direct answer was generated

        """
        tool_results = []

        # If the tool is Read_File or SearchFile, add the available files to the chat history
        # so that the model knows what files are available
        tool_names = [tool.name for tool in tools]
        if ToolName.Read_File in tool_names or ToolName.Search_File in tool_names:
            chat_history = self.add_files_to_chat_history(
                chat_history,
                conversation_id,
                kwargs.get("session"),
                kwargs.get("user_id"),
            )

        self.logger.info(f"Invoking tools: {tools}")
        stream = deployment_model.invoke_tools(
            message, tools, chat_history=chat_history
        )

        # Invoke tools can return a direct answer or a stream of events with the tool calls
        # If one of the events is a tool call generation, the tools are invoked, and the results are returned
        # Otherwise, the chat response is returned as a direct answer
        stream, stream_copy = tee(stream)

        tool_call_found = False
        for event in stream:
            if event["event_type"] == StreamEvent.TOOL_CALLS_GENERATION:
                tool_call_found = True
                tool_calls = event["tool_calls"]

                self.logger.info(f"Tool calls: {tool_calls}")

                # TODO: parallelize tool calls
                for tool_call in tool_calls:
                    tool = AVAILABLE_TOOLS.get(tool_call.name)
                    if not tool:
                        logging.warning(f"Couldn't find tool {tool_call.name}")
                        continue

                    outputs = tool.implementation().call(
                        parameters=tool_call.parameters,
                        session=kwargs.get("session"),
                        model_deployment=deployment_model,
                        user_id=kwargs.get("user_id"),
                    )

                    # If the tool returns a list of outputs, append each output to the tool_results list
                    # Otherwise, append the single output to the tool_results list
                    outputs = outputs if isinstance(outputs, list) else [outputs]
                    for output in outputs:
                        tool_results.append({"call": tool_call, "outputs": [output]})

                self.logger.info(f"Tool results: {tool_results}")
                tool_results = combine_documents(tool_results, deployment_model)
                yield tool_results, False
                break

        if not tool_call_found:
            for event in stream_copy:
                yield event, True

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

        chat_history.append(ChatMessage(message=files_message, role="SYSTEM"))
        return chat_history
