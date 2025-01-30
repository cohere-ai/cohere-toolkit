from typing import Any

from py_expression_eval import Parser

from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool


class Calculator(BaseTool):
    """
    Function Tool that evaluates mathematical expressions.
    """

    ID = "toolkit_calculator"

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Calculator",
            implementation=Calculator,
            parameter_definitions={
                "code": {
                    "description": "The expression for the calculator to evaluate, it should be a valid mathematical expression.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=False,
            is_available=Calculator.is_available(),
            category=ToolCategory.Function,
            error_message=cls.generate_error_message(),
            description="A powerful multi-purpose calculator capable of a wide array of math calculations.",
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any
    ) -> list[dict[str, Any]]:
        logger = ctx.get_logger()

        math_parser = Parser()
        expression = parameters.get("code", "")

        # remove lines that start with # and empty lines
        expression = "\n".join(
            [line for line in expression.split("\n") if not line.startswith("#")]
        )

        to_evaluate = expression.replace("pi", "PI").replace("e", "E")

        try:
            result = {"text": math_parser.parse(to_evaluate).evaluate({})}
        except Exception as e:
            logger.error(event=f"[Calculator] Error parsing expression: {e}")
            return self.get_tool_error(details=str(e))


        return result # type: ignore
