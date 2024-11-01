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
                    Tool.Wiki_Retriever_LangChain.value.ID,
                    Tool.Search_File.value.ID,
                    Tool.Read_File.value.ID,
                    Tool.Python_Interpreter.value.ID,
                    Tool.Calculator.value.ID,
                    Tool.Tavily_Web_Search.value.ID,
                    Tool.Google_Drive.value.ID,
                ],
            )
        ]
    )
    agent_id = factory.Faker("uuid4")
    artifacts = factory.List([])
