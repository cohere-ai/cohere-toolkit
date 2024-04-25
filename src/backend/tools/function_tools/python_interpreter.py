import os
from typing import Any

import requests
from langchain_core.tools import Tool as LangchainTool
from pydantic.v1 import BaseModel, Field
from e2b_code_interpreter import CodeInterpreter

from backend.tools.function_tools.base import BaseFunctionTool


class LangchainPythonInterpreterToolInput(BaseModel):
    code: str = Field(description="Python code to execute.")


class PythonInterpreterFunctionTool(BaseFunctionTool):
    """
    This class calls arbitrary code against a Python Jupyter notebook.
    It requires an E2B_API_KEY to create a sandbox.
    """

    def __init__(self):
        # Instantiate the E2B sandbox - this is a long lived object
        # that's pinging E2B cloud to keep the sandbox alive.
        self.code_interpreter = CodeInterpreter()

    def call(self, parameters: dict, **kwargs: Any):
        # TODO: E2B supports generating and streaming charts and other rich data
        # because it has a full Jupyter server running inside the sandbox.
        # What's the best way to send this data back to frontend and render them in chat?

        # TODO: Will be E2B_API_KEY
        if "E2B_API_KEY" not in os.environ:
            raise Exception(
                "Python Interpreter tool called while E2B_API_KEY environment variable is not set"
            )

        code = parameters.get("code", "")
        print("Code to run", code)
        execution = self.code_interpreter.notebook.exec_cell(code)
        return {
            "results": execution.results,
            "stdout": execution.logs.stdout,
            "stderr": execution.logs.stderr,
            "error": execution.error,
        }

    # langchain does not return a dict as a parameter, only a code string
    def langchain_call(self, code: str):
        return self.call({"code": code})

    def to_langchain_tool(self) -> LangchainTool:
        tool = LangchainTool(
            name="python_interpreter",
            description="Execute python code in a Jupyter notebook cell and returns any result, stdout, stderr, display_data, and error.",
            func=self.langchain_call,
        )
        tool.args_schema = LangchainPythonInterpreterToolInput
        return tool
