import factory

from backend.config.tools import ToolName
from backend.database_models.agent import Agent
from backend.tests.factories.base import BaseFactory
from backend.tests.factories.user import UserFactory


class AgentFactory(BaseFactory):
    class Meta:
        model = Agent

    user = factory.SubFactory(UserFactory)
    user_id = factory.SelfAttribute("user.id")
    name = factory.Faker("sentence")
    description = factory.Faker("sentence")
    preamble = factory.Faker("sentence")
    version = factory.Faker("random_int")
    temperature = factory.Faker("pyfloat")
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")
