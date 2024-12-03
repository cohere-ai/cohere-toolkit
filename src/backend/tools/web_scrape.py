import json
from typing import Any, Dict, List

import aiohttp
from langchain_text_splitters import MarkdownHeaderTextSplitter

from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool

logger = LoggerFactory().get_logger()


class WebScrapeTool(BaseTool):
    ID = "web_scrape"
    ENDPOINT = "http://co-reader"
    ENABLE_CHUNKING = True

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
        )

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        url = parameters.get("url")

        headers = {
            "X-Respond-With": "markdown",
            "x-no-cache": "true",
            "Content-Type": "application/json",
        }
        data = {"url": url}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.ENDPOINT, data=json.dumps(data), headers=headers
                ) as response:
                    if response.status != 200:
                        error_message = f"HTTP {response.status} {response.reason}"
                        return [
                            {
                                "text": f"Cannot open and scrape URL {url}, Error: {error_message}",
                                "url": url,
                            }
                        ]

                    content = await response.text()
                    return self.parse_content(content, url, self.ENABLE_CHUNKING)

            except aiohttp.ClientError as e:
                return [
                    {
                        "text": f"Request failed: {str(e)}",
                        "url": url,
                    }
                ]

    def parse_content(
        self, content: str, url: str, enable_chunking: bool
    ) -> list[dict]:
        if enable_chunking:
            splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=[
                    ("#", "Header 1"),
                    ("##", "Header 2"),
                    ("###", "Header 3"),
                    ("####", "Header 4"),
                    ("#####", "Header 5"),
                ],
                strip_headers=False,
            )
            docs = splitter.split_text(content)
            return [
                {"text": doc.page_content, "url": url, **doc.metadata} for doc in docs
            ]

        return [
            {
                "text": content,
                "url": url,
            }
        ]
