from typing import Any, Dict, List

from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper

from backend.config.settings import Settings
from community.tools import BaseTool


class WolframAlpha(BaseTool):
    """
    Wolfram Alpha tool.

    See: https://python.langchain.com/docs/integrations/tools/wolfram_alpha/
    """

    NAME = "wolfram_alpha"

    wolfram_app_id = Settings().tools.wolfram_alpha.app_id

    def __init__(self):
        self.app_id = self.wolfram_app_id
        self.tool = WolframAlphaAPIWrapper(wolfram_alpha_appid=self.app_id)

    @classmethod
    def is_available(cls) -> bool:
        return cls.wolfram_app_id is not None

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        to_evaluate = parameters.get("expression", "")
        result = self.tool.run(to_evaluate)
        return {"result": result, "text": result}
