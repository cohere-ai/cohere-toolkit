from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.services.logger.utils import LoggerFactory
from backend.services.utils import read_pdf
from backend.tools.base import BaseTool
from backend.tools.constants import ASYNC_TIMEOUT

logger = LoggerFactory().get_logger()


class WebScrapeTool(BaseTool):
    ID = "web_scrape"

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return  ToolDefinition(
            name=cls.ID,
            display_name="Web Scrape",
            implementation=cls,
            parameter_definitions={
                "url": {
                    "description": "The url to scrape.",
                    "type": "str",
                    "required": True,
                },
                "query": {
                    "description": "The query to use to select the most relevant passages to return. Using an empty string will return the passages in the order they appear on the webpage",
                    "type": "str",
                    "required": False,
                },
            },
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Scrape and returns the textual contents of a webpage as a list of passages for a given url.",
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any
    ) -> list[dict[str, Any]]:
        url = parameters.get("url", "")

        async with aiohttp.ClientSession(timeout=ASYNC_TIMEOUT) as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        error_message = f"HTTP {response.status} {response.reason}"
                        return [
                            {
                                "text": f"Cannot open and scrape URL {url}, Error: {error_message}",
                                "url": url,
                            }
                        ]

                    return await self.handle_response(response, url)

            except aiohttp.ClientError as e:
                return  [{
                    "text": f"Client error using web scrape: {str(e)}",
                    "url": url,
                }]
            except Exception as e:
                return [{
                    "text": f"Request failed using web scrape: {str(e)}",
                    "url": url,
                }]

    async def handle_response(self, response: aiohttp.ClientResponse, url: str):
        content_type = response.headers.get("content-type", "")
        results = []

        # If URL is a PDF, read contents using helper function
        if "application/pdf" in content_type:
            results.append({
                "text": read_pdf(response.content),
                "url": url,
            })
        elif "text/html" in content_type:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")

            text = soup.get_text().replace("\n", "")
            title = next((tag.text for tag in soup.find_all('h1')), None)

            data = {
                "text": text,
                "url": url,
            }

            if title:
                data["title"] = title

            results.append(data)
        else:
            raise ValueError(f"Unsupported Content Type using web scrape: {content_type}")

        return results
