from typing import Any, Dict, List

import requests

from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool

"""
Plug in your Connector configuration here. For example:

Url: http://example_connector.com/search
Auth: Bearer token for the connector

To see SSO examples, check out our Google Drive or Slack tool implementations

More details: https://docs.cohere.com/docs/connectors
"""


class ConnectorRetriever(BaseTool):
    ID = "example_connector"

    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key

    @classmethod
    def is_available(cls) -> bool:
        return False

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Example Connector Template - Do not use",
            implementation=ConnectorRetriever,
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Example connector for a data source using a basic API.",
        )

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        body = {"query": parameters}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            response = requests.get(self.url, json=body, headers=headers)
            results = response.json()["results"]
        except Exception as e:
            return self.get_tool_error(details=str(e))

        if not results:
            return self.get_no_results_error()

        return results
