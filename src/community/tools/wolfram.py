from typing import Any, Dict, List

from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper

from backend.config.settings import Settings
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool


class WolframAlpha(BaseTool):
    """
    Wolfram Alpha tool.

    See: https://python.langchain.com/docs/integrations/tools/wolfram_alpha/
    """

    ID = "wolfram_alpha"

    wolfram_app_id = Settings().get('tools.wolfram_alpha.app_id')

    def __init__(self):
        self.app_id = self.wolfram_app_id
        self.tool = WolframAlphaAPIWrapper(wolfram_alpha_appid=self.app_id)

    @classmethod
    def is_available(cls) -> bool:
        return cls.wolfram_app_id is not None

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Wolfram Alpha",
            implementation=cls,
            is_visible=True,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.Function,
            description="Evaluate arithmetic expressions using Wolfram Alpha.",
        )

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        to_evaluate = parameters.get("expression", "")
        result = self.tool.run(to_evaluate)
        return {"result": result, "text": result}
