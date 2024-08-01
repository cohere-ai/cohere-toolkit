import json
from typing import Any, Dict, Mapping

import requests
from dotenv import load_dotenv
from langchain_core.tools import Tool as LangchainTool
from pydantic.v1 import BaseModel, Field

from backend.config.settings import Settings
from backend.tools.base import BaseTool

load_dotenv()


class LangchainPythonInterpreterToolInput(BaseModel):
    code: str = Field(description="Python code to execute.")


class PythonInterpreter(BaseTool):
    """
    This class calls arbitrary code against a Python interpreter.
    It requires a URL at which the interpreter lives
    """

    NAME = "toolkit_python_interpreter"
    INTERPRETER_URL = Settings().tools.python_interpreter.url

    @classmethod
    def is_available(cls) -> bool:
        return cls.INTERPRETER_URL is not None

    async def call(self, parameters: dict, ctx: Any, **kwargs: Any):
        if not self.INTERPRETER_URL:
            raise Exception("Python Interpreter tool called while URL not set")

        code = parameters.get("code", "")
        res = requests.post(self.INTERPRETER_URL, json={"code": code})
        clean_res = self._clean_response(res.json())

        return clean_res

    def _clean_response(self, result: Any) -> Dict[str, str]:
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
                r.setdefault("text", error_message)
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

    # langchain does not return a dict as a parameter, only a code string
    def langchain_call(self, code: str):
        return self.call({"code": code}, ctx=None)

    def to_langchain_tool(self) -> LangchainTool:
        tool = LangchainTool(
            name="python_interpreter",
            description="Executes python code and returns the result. The code runs in a static sandbox without interactive mode, so print output or save output to a file.",
            func=self.langchain_call,
        )
        tool.args_schema = LangchainPythonInterpreterToolInput
        return tool
