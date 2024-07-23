import factory

from backend.config.tools import ToolName
from backend.database_models.agent_tool_metadata import AgentToolMetadata

from .base import BaseFactory


class AgentToolMetadataFactory(BaseFactory):
    class Meta:
        model = AgentToolMetadata

    user_id = factory.Faker("uuid4")
    tool_id = factory.Faker("uuid4")
    agent_id = factory.Faker("uuid4")
    artifacts = factory.List([])
