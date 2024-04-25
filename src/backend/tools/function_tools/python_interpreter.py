import os
from typing import Any

import requests
from langchain_core.tools import Tool as LangchainTool
from pydantic.v1 import BaseModel, Field

from backend.tools.function_tools.base import BaseFunctionTool


class LangchainPythonInterpreterToolInput(BaseModel):
    code: str = Field(description="Python code to execute.")


class PythonInterpreterFunctionTool(BaseFunctionTool):
    """
    This class calls arbitrary code against a Python interpreter.
    It requires a URL at which the interpreter lives
    """

    def __init__(self):
        self.interpreter_url = os.environ.get("PYTHON_INTERPRETER_URL")

    def call(self, parameters: dict, **kwargs: Any):
        if not self.interpreter_url:
            raise Exception("Python Interpreter tool called while URL not set")

        code = parameters.get("code", "")
        res = requests.post(self.interpreter_url, json={"code": code})

        return res.json()

    # langchain does not return a dict as a parameter, only a code string
    def langchain_call(self, code: str):
        return self.call({"code": code})

    def to_langchain_tool(self) -> LangchainTool:
        tool = LangchainTool(
            name="python_interpreter",
            description="Executes python code and returns the result. The code runs in a static sandbox without interactive mode, so print output or save output to a file.",
            func=self.langchain_call,
        )
        tool.args_schema = LangchainPythonInterpreterToolInput
        return tool
