import logging
from typing import Any

from fastapi import HTTPException

from backend.chat.base import BaseChat
from backend.chat.collate import combine_documents
from backend.chat.custom.utils import get_deployment
from backend.config.tools import AVAILABLE_TOOLS, ToolName
from backend.model_deployments.base import BaseDeployment
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.tool import Category, Tool
from backend.services.logger import get_logger
from typing import Any, Dict, List


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

        if kwargs.get("managed_tools", True):
            chat_request = self.handle_managed_tools(chat_request, deployment_model, **kwargs)

        # Generate Response
        if kwargs.get("stream", True) is True:
            return deployment_model.invoke_chat_stream(chat_request)
        else:
            return deployment_model.invoke_chat(chat_request)

    def handle_managed_tools(self, chat_request, deployment_model, **kwargs):
        tools = [Tool(**AVAILABLE_TOOLS.get(tool.name).model_dump()) for tool in chat_request.tools if AVAILABLE_TOOLS.get(tool.name)]

        if len(tools) == 0:
            return []

        tool_results = self.get_tool_results(
            chat_request.message, chat_request.chat_history, tools, deployment_model
        )

        chat_request.tools = tools
        chat_request.tool_results = tool_results

        return chat_request

    def get_tool_results(
        self, message: str, chat_history: List[Dict[str, str]], tools: list[Tool], model: BaseDeployment
    ) -> list[dict[str, Any]]:
        tool_results = []
        tools_to_use = model.invoke_tools(message, tools, chat_history=chat_history)

        tool_calls = tools_to_use.tool_calls if tools_to_use.tool_calls else []
        for tool_call in tool_calls:
            tool = AVAILABLE_TOOLS.get(tool_call.name)
            if not tool:
                logging.warning(f"Couldn't find tool {tool_call.name}")
                continue

            outputs = tool.implementation().call(
                parameters=tool_call.parameters,
            )

            # If the tool returns a list of outputs, append each output to the tool_results list
            # Otherwise, append the single output to the tool_results list
            outputs = outputs if isinstance(outputs, list) else [outputs]
            for output in outputs:
                tool_results.append({"call": tool_call, "outputs": [output]})

        return tool_results
