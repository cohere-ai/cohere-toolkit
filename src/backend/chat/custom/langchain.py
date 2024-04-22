from typing import Any

from langchain.agents import AgentExecutor
from langchain_cohere.chat_models import ChatCohere
from langchain_cohere.react_multi_hop.agent import create_cohere_react_agent
from langchain_core.prompts import ChatPromptTemplate

from backend.chat.base import BaseChat
from backend.config.tools import AVAILABLE_TOOLS, ToolName
from backend.schemas.langchain_chat import LangchainChatRequest


class LangChainChat(BaseChat):
    ### WARNING: This is an experimental feature using Langchain. We encourage you to use tool use through the Cohere API!
    """Custom chat flow using Langchain"""

    def __init__(self) -> None:
        llm = ChatCohere(model="command-r-plus")

        self.default_preamble = """
        You are an expert who answers the user's question with the most relevant datasource. You are equipped with an internet search tool and a special vectorstore of information about how to write good essays.
        You also have a 'random_operation_tool' tool, you must use it to compute the random operation between two numbers.
        """

        # Prompt template
        prompt = ChatPromptTemplate.from_template("{input}")

        python_tool = AVAILABLE_TOOLS[ToolName.Python_Interpreter].implementation()
        tavily_search_tool = AVAILABLE_TOOLS[
            ToolName.Tavily_Internet_Search
        ].implementation()
        # Create the ReAct agent
        agent = create_cohere_react_agent(
            llm=llm,
            # TODO get tools from chat req
            tools=[
                tavily_search_tool.to_langchain_tool(),
                python_tool.to_langchain_tool(),
            ],
            prompt=prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=[
                tavily_search_tool.to_langchain_tool(),
                python_tool.to_langchain_tool(),
            ],
            verbose=True,
        )

    def chat(self, chat_request: LangchainChatRequest, **kwargs: Any) -> Any:
        """
        Chat flow for custom models.

        Args:
            chat_request (LangchainChatRequest): Chat request.
            **kwargs (Any): Keyword arguments.

        Returns:
            Generator[StreamResponse, None, None]: Chat response.
        """
        # TODO: handle chat history and persistence

        return self.agent_executor.stream(
            {
                "input": chat_request.message,
                "preamble": self.default_preamble,
            }
        )
