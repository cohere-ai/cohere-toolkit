import factory

from backend.config.tools import ToolName
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
                    ToolName.Wiki_Retriever_LangChain,
                    ToolName.Search_File,
                    ToolName.Read_File,
                    ToolName.Python_Interpreter,
                    ToolName.Calculator,
                    ToolName.Tavily_Internet_Search,
                    ToolName.Google_Drive,
                ],
            )
        ]
    )
    agent_id = factory.Faker("uuid4")
    artifacts = factory.List([])
