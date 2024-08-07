import json
import os
from typing import Any, Dict, Mapping, List

from community.tools import BaseTool

class VectorSearch(BaseTool):
    NAME = "vector_search"

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
        ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        return True

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        return [{"text": 'test'}]
    