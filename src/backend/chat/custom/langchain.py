from typing import Any

from langchain.agents import AgentExecutor
from langchain_cohere.chat_models import ChatCohere
from langchain_cohere.react_multi_hop.agent import create_cohere_react_agent
from langchain_core.prompts import ChatPromptTemplate

from backend.chat.base import BaseChat
from backend.config.tools import AVAILABLE_TOOLS
from backend.schemas.langchain_chat import LangchainChatRequest


class LangChainChat(BaseChat):
    ### WARNING: This is an experimental feature using Langchain. We encourage you to use tool use through the Cohere API!
    ### Please see Langchain Multihop documentation in the Readme

    """Custom experimental chat flow using Langchain. Multihop tool usage is enabled"""

    def chat(self, chat_request: LangchainChatRequest, **kwargs: Any) -> Any:
        """
        Chat flow for custom models.

        Args:
            chat_request (LangchainChatRequest): Chat request.
            **kwargs (Any): Keyword arguments.

        Returns:
            Generator[StreamResponse, None, None]: Chat response.
        """

        llm = ChatCohere(model="command-r-plus")

        self.default_preamble = """
        You are an expert who answers the user's question with the most relevant datasource. You are equipped with an internet search tool and a special vectorstore of information about how to write good essays.
        You also have a 'random_operation_tool' tool, you must use it to compute the random operation between two numbers.
        """

        # Prompt template
        prompt = ChatPromptTemplate.from_template("{input}")

        tools = []
        for req_tool in chat_request.tools:
            tool = AVAILABLE_TOOLS.get(req_tool.name)
            if tool:
                tools.append(tool.implementation().to_langchain_tool())
            else:
                raise ValueError(f"Tool {req_tool.name} not found")

        # Create the ReAct agent
        agent = create_cohere_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
        )

        return self.agent_executor.stream(
            {
                "input": chat_request.message,
                "preamble": self.default_preamble,
            }
        )
