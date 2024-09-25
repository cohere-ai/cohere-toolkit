import os
from enum import StrEnum
from typing import Dict, Optional

import httpx
import requests
from pydantic import BaseModel
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed


class SafeSearchTypes(StrEnum):
    OFF = "off"
    MODERATE = "moderate"
    STRICT = "strict"


class WebSearchResponse(BaseModel):
    """
    Web search response model.
    """

    type: str = "search"
    discussions: Dict = {}
    faq: Dict = {}
    infobox: Dict = {}
    locations: Dict = {}
    mixed: Dict = {}
    news: Dict = {}
    query: Dict = {}
    videos: Dict = {}
    web: Dict = {}
    summarizer: Dict = {}


class BraveApiException(Exception):
    """
    Custom exception for Brave API errors.
    """

    pass


class BraveClient:
    BASE_URL = "https://api.search.brave.com/res/v1/"
    WEB_SEARCH_API_ENDPOINT = "web/search"
    MAX_RESULTS = 20
    MAX_OFFSET = 9
    WAIT_RETRY_SECONDS = 2
    RETRY_ATTEMPTS = 2

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key if api_key else os.environ.get("BRAVE_API_KEY", None)
        self.web_search_endpoint = f"{self.BASE_URL}{self.WEB_SEARCH_API_ENDPOINT}"

    def _get_headers(self) -> Dict:
        """
        Construct the request headers with the API key.
        """
        return {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }

    def _prepare_params(
        self,
        q: str,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        ui_lang: Optional[str] = None,
        count: Optional[int] = MAX_RESULTS,
        offset: Optional[int] = 0,
        safesearch: Optional[str] = SafeSearchTypes.MODERATE,
        freshness: Optional[str] = None,
        text_decorations: Optional[bool] = False,
        spellcheck: Optional[bool] = True,
        goggles_id: Optional[str] = None,
        extra_snippets: Optional[bool] = False,
        include_domains: Optional[list[str]] = [],
    ) -> Dict:
        """
        Prepare the query parameters for the API request.
        """
        # Validate the query parameter - limits set by the API endpoint
        # see https://api.search.brave.com/app/documentation/web-search/query
        if not q or len(q) > 400 or len(q.split()) > 50:
            raise ValueError("Invalid query parameter 'q'")

        # Construct the query parameters - see here for more details:
        # https://search.brave.com/help/operators
        if include_domains:
            q_domains = " OR ".join([f"site:{item}" for item in include_domains])
            q = f"{q} {q_domains}"

        params = {
            "q": q,
            "country": country,
            "search_lang": search_lang,
            "ui_lang": ui_lang,
            "count": min(count, self.MAX_RESULTS),
            "offset": min(offset, self.MAX_OFFSET),
            "safesearch": safesearch,
            "freshness": freshness,
            "text_decorations": text_decorations,
            "spellcheck": spellcheck,
            "goggles_id": goggles_id,
            "extra_snippets": extra_snippets,
        }
        # Filter None values
        params = {k: v for k, v in params.items() if v is not None}

        return params

    def _get(self, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        GET request method placeholder.
        """

        headers = self._get_headers()
        response = requests.get(
            self.web_search_endpoint, headers=headers, params=params
        )

        return response

    def search(
        self,
        q: str,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        ui_lang: Optional[str] = None,
        count: Optional[int] = MAX_RESULTS,
        offset: Optional[int] = 0,
        safesearch: Optional[str] = SafeSearchTypes.MODERATE,
        freshness: Optional[str] = None,
        text_decorations: Optional[bool] = False,
        spellcheck: Optional[bool] = True,
        goggles_id: Optional[str] = None,
        extra_snippets: Optional[bool] = False,
        include_domains: Optional[list[str]] = [],
        raw: Optional[bool] = False,
    ) -> WebSearchResponse:
        """
        Perform a web search using the Brave Search API.

        Parameters:
            q: str
                The search query (required).
            country: str
                The 2-character country code.
            search_lang: str
                The search language preference.
            ui_lang: str
                The user interface language preference.
            count: int
                The number of results to return (default: 20, max: 20).
            offset: int
                The number of results to skip.
            safesearch: str
                Filter for adult content ('off', 'moderate', 'strict').
            freshness: str
                Filter for search result freshness.
            text_decorations: bool
                Include decoration markers in result strings.
            spellcheck: bool
                Spellcheck the query (default: True).
            goggles_id: str
                Custom re-ranking goggles ID.
            extra_snippets: bool
                Include extra snippets in the search results.
            include_domains: list[str]
                List of domains to include in the search results.
            raw: bool
                Return the raw API response (default: False).

        Returns:
            WebSearchApiResponse
        """

        params = self._prepare_params(
            q,
            country,
            search_lang,
            ui_lang,
            count,
            offset,
            safesearch,
            freshness,
            text_decorations,
            spellcheck,
            goggles_id,
            extra_snippets,
            include_domains,
        )

        response = self._get(params=params)

        if response.status_code != 200:
            raise BraveApiException(
                f"Brave API Error: {response.status_code} - {response.text}"
            )

        if raw:
            return response.json()
        return WebSearchResponse.model_validate(response.json())

    async def _get_async(self, params: Optional[Dict] = None) -> httpx.Response:
        """
        Asynchronous GET request method.
        """
        headers = self._get_headers()

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.RETRY_ATTEMPTS),
            wait=wait_fixed(self.WAIT_RETRY_SECONDS),
        ):
            with attempt:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self.web_search_endpoint, headers=headers, params=params
                    )
                    return response

    async def search_async(
        self,
        q: str,
        country: Optional[str] = None,
        search_lang: Optional[str] = None,
        ui_lang: Optional[str] = None,
        count: Optional[int] = MAX_RESULTS,
        offset: Optional[int] = 0,
        safesearch: Optional[str] = SafeSearchTypes.MODERATE,
        freshness: Optional[str] = None,
        text_decorations: Optional[bool] = False,
        spellcheck: Optional[bool] = True,
        goggles_id: Optional[str] = None,
        extra_snippets: Optional[bool] = False,
        include_domains: Optional[list[str]] = [],
        raw: Optional[bool] = False,
    ) -> WebSearchResponse:
        """
        Perform a web search using the Brave Search API asynchronously.

        Parameters:
            q: str
                The search query (required).
            country: str
                The 2-character country code.
            search_lang: str
                The search language preference.
            ui_lang: str
                The user interface language preference.
            count: int
                The number of results to return (default: 20, max: 20).
            offset: int
                The number of results to skip.
            safesearch: str
                Filter for adult content ('off', 'moderate', 'strict').
            freshness: str
                Filter for search result freshness.
            text_decorations: bool
                Include decoration markers in result strings.
            spellcheck: bool
                Spellcheck the query (default: True).
            goggles_id: str
                Custom re-ranking goggles ID.
            extra_snippets: bool
                Include extra snippets in the search results.
            include_domains: list[str]
                List of domains to include in the search results.
            raw: bool
                Return the raw API response (default: False).

        Returns:
            WebSearchApiResponse
        """

        # Construct the query parameters
        params = self._prepare_params(
            q,
            country,
            search_lang,
            ui_lang,
            count,
            offset,
            safesearch,
            freshness,
            text_decorations,
            spellcheck,
            goggles_id,
            extra_snippets,
            include_domains,
        )

        response = await self._get_async(params=params)

        if response.status_code != 200:
            raise BraveApiException(
                f"Brave API Error: {response.status_code} - {response.text}"
            )

        if raw:
            return response.json()
        return WebSearchResponse.model_validate(response.json())
