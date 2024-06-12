import factory

from backend.config.tools import ToolName
from backend.database_models.agent import Agent, AgentDeployment, AgentModel

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
    model = factory.Faker(
        "random_element",
        elements=(
            AgentModel.COMMAND_R,
            AgentModel.COMMAND_R_PLUS,
            AgentModel.COMMAND_LIGHT,
            AgentModel.COMMAND,
        ),
    )
    deployment = factory.Faker(
        "random_element",
        elements=(
            AgentDeployment.COHERE_PLATFORM,
            AgentDeployment.SAGE_MAKER,
            AgentDeployment.AZURE,
            AgentDeployment.BEDROCK,
        ),
    )
