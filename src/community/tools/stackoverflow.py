from typing import List, Dict, Any
from community.tools import BaseTool
from langchain_community.utilities import StackExchangeAPIWrapper

class StackOverflow(BaseTool):
    def __init__(self):
        self.client = StackExchangeAPIWrapper()

    @classmethod
    def is_available(cls) -> bool:
        return True
    
    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        result = self.client.run(query)
        return [{"text": result}]