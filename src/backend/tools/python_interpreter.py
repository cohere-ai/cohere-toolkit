import json
from typing import Any, Mapping

import requests
from dotenv import load_dotenv

from backend.config.settings import Settings
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool

load_dotenv()


class PythonInterpreter(BaseTool):
    """
    This class calls arbitrary code against a Python interpreter.
    It requires a URL at which the interpreter lives
    """

    ID = "toolkit_python_interpreter"
    INTERPRETER_URL = Settings().get('tools.python_interpreter.url')

    @classmethod
    def is_available(cls) -> bool:
        return cls.INTERPRETER_URL is not None

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Python Interpreter",
            implementation=cls,
            parameter_definitions={
                "code": {
                    "description": (
                        "Python code to execute using the Python interpreter with no internet access. "
                        "Do not generate code that tries to open files directly, instead use file contents passed to the interpreter, "
                        "then print output or save output to a file."
                    ),
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=True,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.Function,
            description=(
                "Executes python code and returns the result. The code runs "
                "in a static sandbox without internet access and without interactive mode, "
                "so print output or save output to a file."
            ),
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        if not self.INTERPRETER_URL:
            raise Exception("Python Interpreter tool called while URL not set")

        code = parameters.get("code", "")
        try:
            res = requests.post(self.INTERPRETER_URL, json={"code": code})
            clean_res = self._clean_response(res.json())
        except Exception as e:
            return self.get_tool_error(details=str(e))

        if not clean_res:
            return self.get_no_results_error()

        return clean_res

    def _clean_response(self, result: Any) -> list[dict[str, str]]:
        if "final_expression" in result:
            result["final_expression"] = str(result["final_expression"])

        # split up output files into separate result items, so that we may cite them individually
        result_list = [result]

        output_files = result.pop("output_files", [])
        for f in output_files:
            result_list.append({"output_file": f})

        for r in result_list:
            if r.get("sucess") is not None:
                r.update({"success": r.get("sucess")})
                del r["sucess"]

            if r.get("success") is True:
                r.setdefault("text", r.get("std_out"))
            elif r.get("success") is False:
                error_message = r.get("error", {}).get("message", "")
                # r.setdefault("text", error_message)
                return self.get_tool_error(details=error_message)
            elif r.get("output_file") and r.get("output_file").get("filename"):
                if r["output_file"]["filename"] != "":
                    r.setdefault(
                        "text", f"Created output file {r['output_file']['filename']}"
                    )

            # cast all values to strings, if it's a json object use double quotes
            for key, value in r.items():
                if isinstance(value, Mapping):
                    r[key] = json.dumps(value)
                else:
                    r[key] = str(value)

        return result_list
