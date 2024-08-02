from typing import Any, Dict, List

import requests

from community.tools import BaseTool

"""
Plug in your Connector configuration here. For example:

Url: http://example_connector.com/search
Auth: Bearer token for the connector

More details: https://docs.cohere.com/docs/connectors
"""


class ConnectorRetriever(BaseTool):
    NAME = "example_connector"

    def __init__(self, url: str, auth: str):
        self.url = url
        self.auth = auth

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        body = {"query": parameters}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth}",
        }

        response = requests.post(self.url, json=body, headers=headers)

        return response.json()["results"]
