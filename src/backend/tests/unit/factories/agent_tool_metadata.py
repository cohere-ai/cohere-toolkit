import factory

from backend.config.tools import Tool
from backend.database_models.agent_tool_metadata import AgentToolMetadata

from .base import BaseFactory


class AgentToolMetadataFactory(BaseFactory):
    class Meta:
        model = AgentToolMetadata

    user_id = factory.Faker("uuid4")
    tool_name = factory.List(
        [
            factory.Faker(
                "random_element",
                elements=[
                    Tool.Wiki_Retriever_LangChain,
                    Tool.Search_File,
                    Tool.Read_File,
                    Tool.Python_Interpreter,
                    Tool.Calculator,
                    Tool.Tavily_Web_Search,
                    Tool.Google_Drive,
                ],
            )
        ]
    )
    agent_id = factory.Faker("uuid4")
    artifacts = factory.List([])
