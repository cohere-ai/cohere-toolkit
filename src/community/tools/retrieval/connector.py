from typing import Any, Dict, List

import requests

from community.tools import BaseRetrieval

"""
Plug in your connector configuration here. For example:

Url: http://example_connector.com/search
Auth: Bearer token for the connector

More details: https://docs.cohere.com/docs/connectors
"""


class ConnectorRetriever(BaseRetrieval):
    def __init__(self, url: str, auth: str):
        self.url = url
        self.auth = auth

    @classmethod
    def is_available(cls) -> bool:
        return True

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        body = {"query": query}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth}",
        }

        response = requests.post(self.url, json=body, headers=headers)

        return response.json()["results"]
