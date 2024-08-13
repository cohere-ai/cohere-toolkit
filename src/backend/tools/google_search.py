from typing import Any, Dict, List

import requests
from py_expression_eval import Parser

from backend.config.settings import Settings
from backend.tools.base import BaseTool

GOOGLE_SEARCH_ENGINE_ID = "b079658ab7adf4ba9"
GOOGLE_ENDPOINT = "https://customsearch.googleapis.com/customsearch/v1"
MAX_RESULTS = 6
GOOGLE_MAX_DELAY = 10


class GoogleSearch(BaseTool):
    """
    Tool that calls google search API to get search results.
    """

    NAME = "google_search"
    API_KEY = Settings().tools.google_search.api_key

    @classmethod
    def is_available(cls) -> bool:
        return GoogleSearch.API_KEY is not None

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        # if site is not None:
        #    query = f"site:{site} {query}"
        query = parameters.get("query", "")
        req = {
            "filter": "1",
            "num": MAX_RESULTS,
            "q": query,
            "key": GoogleSearch.API_KEY,
            "cx": GOOGLE_SEARCH_ENGINE_ID,
        }
        header = {"Accept": "application/json"}
        response = requests.get(GOOGLE_ENDPOINT, params=req, headers=header)
        result = response.json()
        output = []
        for item in result.get("items", []):
            output.append(
                {
                    "link": item["link"],
                    "text": item.get("snippet", "").replace("\xa0", " "),
                    "title": item.get("title", "").replace("\xa0", " "),
                    "raw_response": item,
                }
            )
        return output
