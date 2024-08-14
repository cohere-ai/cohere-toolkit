import factory

from backend.database_models.tool_call import ToolCall
from backend.tests.factories.base import BaseFactory


class ToolCallFactory(BaseFactory):
    class Meta:
        model = ToolCall

    name = factory.Faker("name")
    parameters = {"test": "test"}
    message_id = "1"
