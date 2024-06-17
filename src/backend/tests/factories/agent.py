import factory

from backend.config.deployments import ALL_MODEL_DEPLOYMENTS, ModelDeploymentName
from backend.config.tools import ToolName
from backend.database_models.agent import Agent

from .base import BaseFactory


class AgentFactory(BaseFactory):
    class Meta:
        model = Agent

    user_id = factory.Faker("uuid4")
    name = factory.Faker("sentence")
    description = factory.Faker("sentence")
    preamble = factory.Faker("sentence")
    version = factory.Faker("random_int")
    temperature = factory.Faker("pyfloat")
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    tools = factory.List(
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
                ],
            )
        ]
    )
    model = "command-r-plus"
    deployment = ModelDeploymentName.CoherePlatform
