from typing import Any, Dict, List

from py_expression_eval import Parser

from backend.tools.base import BaseTool


class Calculator(BaseTool):
    """
    Function Tool that evaluates mathematical expressions.
    """

    @classmethod
    def is_available(cls) -> bool:
        return True

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        math_parser = Parser()
        to_evaluate = parameters.get("code", "").replace("pi", "PI").replace("e", "E")

        result = []
        try:
            result = {"result": math_parser.parse(to_evaluate).evaluate({})}
        except Exception:
            result = {"result": "Parsing error - syntax not allowed."}
        return result
