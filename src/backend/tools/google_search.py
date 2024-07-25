import logging
from typing import Any, Dict, List

from backend.config.settings import Settings
from py_expression_eval import Parser

from backend.tools.base import BaseTool

import math
import os
from typing import Dict, List, Optional, Union

import requests

GOOGLE_SEARCH_ENGINE_ID = "b079658ab7adf4ba9"
GOOGLE_ENDPOINT = "https://customsearch.googleapis.com/customsearch/v1"
MAX_NUM_REQUESTS_PER_URL = 5
MAX_NUM_GOOGLE_RESULTS = 100
MAX_NUM_GOOGLE_RESULTS_PER_REQUEST = 10
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
        return self.google_api_search(parameters['query'], 6, GOOGLE_SEARCH_ENGINE_ID, GoogleSearch.API_KEY, GOOGLE_ENDPOINT)
    
    def google_api_search(
        self, query: str, num_results: int, search_engine_code: str, api_key: str, api_url: str, raise_for_errors: bool = True, multilingual: bool = False
    ) -> List[Dict]:
        assert (
            num_results <= MAX_NUM_GOOGLE_RESULTS
        ), f"Google will not return >{MAX_NUM_GOOGLE_RESULTS} results, requested: {num_results}"
        pages = []
        max_num_calls = math.ceil(num_results / MAX_NUM_GOOGLE_RESULTS_PER_REQUEST)

        def _do_request():
            req = {
                "filter": "1",
                "lr": "lang_en" if not multilingual else None,
                "num": min(MAX_NUM_GOOGLE_RESULTS_PER_REQUEST, num_results - len(pages)),
                "q": query,
                "key": api_key,
                "cx": search_engine_code,
                "start": len(pages),
            }
            header = {"Accept": "application/json"}
            response = requests.get(api_url, params=req, headers=header)
            if raise_for_errors:
                try:
                    response.raise_for_status()
                except:
                    print(response.json())
            return response

        calls = 0
        while len(pages) < num_results:
            response = _do_request()
            result = response.json()
            pages += result.get("items", [])
            calls += 1
            if calls >= max_num_calls:
                break
        print(pages)
        return pages

    def _google_search(self, query: str, num_results: int, site: Optional[str] = None, multilingual: Optional[bool] = False) -> List[Dict[str, Union[Dict, str]]]:
        """Run a google webpage search, optionally with restriction to single website

        * Currently, rate limited to 60 queries per second, so as to avoid >100 queries per minute.
        * See https://github.com/cohere-ai/internet-search#readme for up to date info.
        * Requires a google search API key to be under the environment variable `GOOGLE_SEARCH_API_KEY`. Find in Cohere's 1password under "Google Custom Search API Key"
        * API reference is here: https://developers.google.com/custom-search/v1/introduction
        * The endpoint is https://customsearch.googleapis.com/customsearch/v1
        * Cost: currently we pay $5 per 1000 searches
        * Quotas: 1M a day for the org

        query: string to search
        num_results: n docs to return
        site: optionally restrict results to a domain

        returns:
        a list of {'link': url, 'snippet': google text snippet, "title": page title, "raw_response": raw json response}
        """
        GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY", "")
        if site is not None:
            query = f"site:{site} {query}"

        search = self.google_api_search(query, num_results, GOOGLE_SEARCH_ENGINE_ID, GOOGLE_SEARCH_API_KEY, GOOGLE_ENDPOINT, multilingual=multilingual)
        output = []
        for item in search:
            output.append(
                {
                    "link": item["link"],
                    "snippet": item.get("snippet", "").replace("\xa0", " "),
                    "title": item.get("title", "").replace("\xa0", " "),
                    "raw_response": item,
                }
            )
        return output