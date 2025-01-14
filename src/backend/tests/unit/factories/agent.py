import factory

from backend.config.tools import Tool
from backend.database_models.agent import Agent
from backend.tests.unit.factories.base import BaseFactory
from backend.tests.unit.factories.user import UserFactory


class AgentFactory(BaseFactory):
    class Meta:
        model = Agent

    user = factory.SubFactory(UserFactory)
    user_id = factory.SelfAttribute("user.id")
    organization_id = None
    deployment_id = None
    model_id = None
    name = factory.Faker("sentence")
    description = factory.Faker("sentence")
    preamble = factory.Faker("sentence")
    version = factory.Faker("random_int")
    temperature = factory.Faker("pyfloat", min_value=0.0, max_value=1.0)
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
    tools = factory.List(
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
                ],
            )
        ]
    )
    is_private = factory.Faker("boolean", chance_of_getting_true=0)
