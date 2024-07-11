from typing import Any, Dict, List

from bs4 import BeautifulSoup
from requests import get

from backend.tools.base import BaseTool


class WebScrapeTool(BaseTool):
    NAME = "web_scrape"

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        url = parameters.get("url")

        response = get(url)
        if not response.ok:
            error_message = f"HTTP {response.status_code} {response.reason}"
            return [
                (
                    {
                        "text": f"Cannot open and scrape URL {url}, Error: {error_message}",
                        "url": url,
                    }
                )
            ]

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n")

        return [
            (
                {
                    "text": text,
                    "url": url,
                }
            )
        ]
