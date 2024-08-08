from typing import Any, Dict, List

from bs4 import BeautifulSoup
from pypdf import PdfReader
from requests import get

from backend.services.utils import read_pdf
from backend.tools.base import BaseTool


class WebScrapeTool(BaseTool):
    NAME = "web_scrape"

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
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

        content_type = response.headers.get("content-type")
        if "application/pdf" in content_type:
            return [
                (
                    {
                        "text": read_pdf(response.content),
                        "url": url,
                    }
                )
            ]
        elif "text/html" in content_type:
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
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
