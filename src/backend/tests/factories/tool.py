import factory

from backend.database_models import Tool
from backend.tests.factories.base import BaseFactory
from backend.tests.factories.deployment import DeploymentFactory


class ToolFactory(BaseFactory):
    class Meta:
        model = Tool

    name = factory.Faker("name")
    display_name = factory.Faker("name")
    description = factory.Faker("text")
    implementation_class_name = "LangChainWikiRetriever"
    parameter_definitions = {
        "query": {
            "description": "Query for retrieval test.",
            "type": "str",
            "required": True,
        }
    }
    kwargs = {"chunk_size": 400, "chunk_overlap": 0}
    default_tool_config = {}
    is_visible = True
    is_community = False
    auth_implementation_class_name = ""
    error_message_text = "LangChainWikiRetriever not available."
    category = "Data loader"
