from typing import Any, Dict, List

from bs4 import BeautifulSoup
from requests import get

from backend.tools.base import BaseTool


class WebScrapeTool(BaseTool):
    @classmethod
    def is_available(cls) -> bool:
        return True

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        url = parameters.get("url")

        page_content = get(url).text
        soup = BeautifulSoup(page_content, "html.parser")
        text = soup.get_text(separator="\n")

        return [
            (
                {
                    "text": text,
                    "url": url,
                }
            )
        ]
