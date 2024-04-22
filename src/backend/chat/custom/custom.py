import logging
from typing import Any

from fastapi import HTTPException

from backend.chat.base import BaseChat
from backend.chat.custom.model_deployments.base import BaseDeployment
from backend.chat.custom.model_deployments.deployment import get_deployment
from backend.config.tools import AVAILABLE_TOOLS, ToolName
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.tool import Category, Tool
from backend.services.logger import get_logger
from backend.tools.retrieval.collate import combine_documents


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
        deployment_model = get_deployment(kwargs.get("deployment_name"))
        self.logger.info(f"Using deployment {deployment_model.__class__.__name__}")

        if len(chat_request.tools) > 0 and len(chat_request.documents) > 0:
            raise HTTPException(
                status_code=400, detail="Both tools and documents cannot be provided."
            )

        if kwargs.get("managed_tools", True):
            # Generate Search Queries
            chat_history = [message.to_dict() for message in chat_request.chat_history]

            function_tools: list[Tool] = []
            for tool in chat_request.tools:
                available_tool = AVAILABLE_TOOLS.get(tool.name)
                if available_tool and available_tool.category == Category.Function:
                    function_tools.append(Tool(**available_tool.model_dump()))

            if len(function_tools) > 0:
                tool_results = self.get_tool_results(
                    chat_request.message, function_tools, deployment_model
                )

                chat_request.tools = None
                if kwargs.get("stream", True) is True:
                    return deployment_model.invoke_chat_stream(
                        chat_request,
                        tool_results=tool_results,
                    )
                else:
                    return deployment_model.invoke_chat(
                        chat_request,
                        tool_results=tool_results,
                    )

            queries = deployment_model.invoke_search_queries(
                chat_request.message, chat_history
            )
            self.logger.info(f"Search queries generated: {queries}")

            # Fetch Documents
            retrievers = self.get_retrievers(
                kwargs.get("file_paths", []), [tool.name for tool in chat_request.tools]
            )
            self.logger.info(
                f"Using retrievers: {[retriever.__class__.__name__ for retriever in retrievers]}"
            )

            # No search queries were generated but retrievers were selected, use user message as query
            if len(queries) == 0 and len(retrievers) > 0:
                queries = [chat_request.message]

            all_documents = {}
            # TODO: call in parallel and error handling
            for retriever in retrievers:
                for query in queries:
                    all_documents.setdefault(query, []).extend(
                        retriever.retrieve_documents(query)
                    )

            # Collate Documents
            documents = combine_documents(all_documents, deployment_model)
            chat_request.documents = documents
            chat_request.tools = []

        # Generate Response
        if kwargs.get("stream", True) is True:
            return deployment_model.invoke_chat_stream(chat_request)
        else:
            return deployment_model.invoke_chat(chat_request)

    def get_retrievers(
        self, file_paths: list[str], req_tools: list[ToolName]
    ) -> list[Any]:
        """
        Get retrievers for the required tools.

        Args:
            file_paths (list[str]): File paths.
            req_tools (list[str]): Required tools.

        Returns:
            list[Any]: Retriever implementations.
        """
        retrievers = []

        # If no tools are required, return an empty list
        if not req_tools:
            return retrievers

        # Iterate through the required tools and check if they are available
        # If so, add the implementation to the list of retrievers
        # If not, raise an HTTPException
        for tool_name in req_tools:
            tool = AVAILABLE_TOOLS.get(tool_name)
            if tool is None:
                raise HTTPException(
                    status_code=404, detail=f"Tool {tool_name} not found."
                )

            # Check if the tool is visible, if not, skip it
            if not tool.is_visible:
                continue

            if tool.category == Category.FileLoader and file_paths is not None:
                for file_path in file_paths:
                    retrievers.append(tool.implementation(file_path, **tool.kwargs))
            elif tool.category != Category.FileLoader:
                retrievers.append(tool.implementation(**tool.kwargs))

        return retrievers

    def get_tool_results(
        self, message: str, tools: list[Tool], model: BaseDeployment
    ) -> list[dict[str, Any]]:
        tool_results = []
        tools_to_use = model.invoke_tools(message, tools)

        tool_calls = tools_to_use.tool_calls if tools_to_use.tool_calls else []
        for tool_call in tool_calls:
            tool = AVAILABLE_TOOLS.get(tool_call.name)
            if not tool:
                logging.warning(f"Couldn't find tool {tool_call.name}")
                continue

            outputs = tool.implementation().call(
                parameters=tool_call.parameters,
            )
            tool_results.append({"call": tool_call, "outputs": [outputs]})

        return tool_results
