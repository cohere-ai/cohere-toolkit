import asyncio
from typing import Any, Dict, List
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.chat.custom.tool_calls import async_call_tools
from backend.config.tools import Tool
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.services.context import Context
from backend.tests.unit.model_deployments.mock_deployments import MockCohereDeployment
from backend.tools.base import BaseTool


@pytest.fixture
def mock_get_available_tools():
    with patch("backend.chat.custom.tool_calls.get_available_tools") as mock:
        yield mock


def test_async_call_tools_success(mock_get_available_tools) -> None:
    class MockCalculator(BaseTool):
        ID = "toolkit_calculator"
        @classmethod
        def get_tool_definition(cls) -> ToolDefinition:
            return ToolDefinition(
                name=cls.ID,
                display_name="Calculator",
                implementation=MockCalculator,
                parameter_definitions={
                    "code": {
                        "description": "The expression for the calculator to evaluate, it should be a valid mathematical expression.",
                        "type": "str",
                        "required": True,
                    }
                },
                is_visible=False,
                is_available=True,
                category=ToolCategory.Function,
                error_message=cls.generate_error_message(),
                description="A powerful multi-purpose calculator capable of a wide array of math calculations.",
            )

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            return [{"result": 42}]

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "toolkit_calculator", "parameters": {"code": "6*7"}}
            ]
        }
    ]
    mock_get_available_tools.return_value = {Tool.Calculator.value.ID: MockCalculator.get_tool_definition()}
    results = asyncio.run(
        async_call_tools(chat_history, MockCohereDeployment(), ctx)
    )
    assert results == [
        {
            "call": {
                "name": "toolkit_calculator",
                "parameters": {"code": "6*7"},
            },
            "outputs": [{"result": 42}],
        }
    ]


def test_async_call_tools_failure(mock_get_available_tools) -> None:
    class MockCalculator(BaseTool):
        ID = "toolkit_calculator"
        @classmethod
        def get_tool_definition(cls) -> ToolDefinition:
            return ToolDefinition(
                name=cls.ID,
                display_name="Calculator",
                implementation=MockCalculator,
                parameter_definitions={
                    "code": {
                        "description": "The expression for the calculator to evaluate, it should be a valid mathematical expression.",
                        "type": "str",
                        "required": True,
                    }
                },
                is_visible=False,
                is_available=True,
                category=ToolCategory.Function,
                error_message=cls.generate_error_message(),
                description="A powerful multi-purpose calculator capable of a wide array of math calculations.",
            )

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            raise Exception("Calculator failed")

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "toolkit_calculator", "parameters": {"code": "6*7"}}
            ]
        }
    ]
    mock_get_available_tools.return_value = {Tool.Calculator.value.ID: MockCalculator.get_tool_definition()}
    results = asyncio.run(
        async_call_tools(chat_history, MockCohereDeployment(), ctx)
    )
    assert results == [
        {
            "call": {
                "name": "toolkit_calculator",
                "parameters": {"code": "6*7"},
            },
            "outputs": [{'type': 'other', 'success': False, 'text': 'Error calling tool toolkit_calculator.', 'details': 'Calculator failed'}],
        },
    ]

@patch("backend.chat.custom.tool_calls.TIMEOUT_SECONDS", 1)
def test_async_call_tools_timeout(mock_get_available_tools) -> None:
    class MockCalculator(BaseTool):
        ID = "toolkit_calculator"
        @classmethod
        def get_tool_definition(cls) -> ToolDefinition:
            return ToolDefinition(
                name=cls.ID,
                display_name="Calculator",
                implementation=MockCalculator,
                parameter_definitions={
                    "code": {
                        "description": "The expression for the calculator to evaluate, it should be a valid mathematical expression.",
                        "type": "str",
                        "required": True,
                    }
                },
                is_visible=False,
                is_available=True,
                category=ToolCategory.Function,
                error_message=cls.generate_error_message(),
                description="A powerful multi-purpose calculator capable of a wide array of math calculations.",
            )

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            await asyncio.sleep(3)
            return [{"result": 42}]

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "toolkit_calculator", "parameters": {"code": "6*7"}}
            ]
        }
    ]
    mock_get_available_tools.return_value = {Tool.Calculator.value.ID: MockCalculator.get_tool_definition()}

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(async_call_tools(chat_history, MockCohereDeployment(), ctx))
    assert str(excinfo.value.status_code) == "500"
    assert (
        str(excinfo.value.detail) == "Timeout while calling tools with timeout: 1"
        )


def test_async_call_tools_failure_and_success(mock_get_available_tools) -> None:
    class MockWebScrape(BaseTool):
        ID = "web_scrape"

        @classmethod
        def get_tool_definition(cls) -> ToolDefinition:
            return ToolDefinition(
                name=cls.ID,
                display_name="Web Scrape",
                implementation=MockWebScrape,
                parameter_definitions={
                    "url": {
                        "description": "The url to scrape.",
                        "type": "str",
                        "required": True,
                    },
                    "query": {
                        "description": "The query to use to select the most relevant passages to return. Using an empty string will return the passages in the order they appear on the webpage",
                        "type": "str",
                        "required": False,
                    },
                },
                is_visible=False,
                is_available=True,
                error_message=cls.generate_error_message(),
                category=ToolCategory.DataLoader,
                description="Scrape and returns the textual contents of a webpage as a list of passages for a given url.",
            )
        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            raise Exception("Web scrape failed")

    class MockCalculator(BaseTool):
        ID = "toolkit_calculator"

        @classmethod
        def get_tool_definition(cls) -> ToolDefinition:
            return ToolDefinition(
                name=cls.ID,
                display_name="Calculator",
                implementation=MockCalculator,
                parameter_definitions={
                    "code": {
                        "description": "The expression for the calculator to evaluate, it should be a valid mathematical expression.",
                        "type": "str",
                        "required": True,
                    }
                },
                is_visible=False,
                is_available=True,
                category=ToolCategory.Function,
                error_message=cls.generate_error_message(),
                description="A powerful multi-purpose calculator capable of a wide array of math calculations.",
            )

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            return [{"result": 42}]

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "web_scrape", "parameters": {"code": "6*7"}},
                {"name": "toolkit_calculator", "parameters": {"code": "6*7"}},
            ]
        }
    ]
    mock_get_available_tools.return_value = {
        Tool.Calculator.value.ID: MockCalculator.get_tool_definition(),
        Tool.Web_Scrape.value.ID: MockWebScrape.get_tool_definition(),
    }

    results = asyncio.run(
        async_call_tools(chat_history, MockCohereDeployment(), ctx)
    )

    assert {'call': {'name': 'web_scrape', 'parameters': {'code': '6*7'}}, 'outputs': [
        {'type': 'other', 'success': False, 'text': 'Error calling tool web_scrape.',
         'details': "Model didn't pass required parameter: url"}]} in results
    assert {
        "call": {"name": "toolkit_calculator", "parameters": {"code": "6*7"}},
        "outputs": [{"result": 42}],
    } in results


def test_tools_params_checker_invalid_param(mock_get_available_tools) -> None:
    class MockCalculator(BaseTool):
        ID = "toolkit_calculator"

        @classmethod
        def get_tool_definition(cls) -> ToolDefinition:
            return ToolDefinition(
                name=cls.ID,
                display_name="Calculator",
                implementation=MockCalculator,
                parameter_definitions={
                    "code": {
                        "description": "The expression for the calculator to evaluate, it should be a valid mathematical expression.",
                        "type": "str",
                        "required": True,
                    }
                },
                is_visible=False,
                is_available=True,
                category=ToolCategory.Function,
                error_message=cls.generate_error_message(),
                description="A powerful multi-purpose calculator capable of a wide array of math calculations.",
            )

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            return [{"result": 42}]

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "toolkit_calculator", "parameters": {"invalid_param": "6*7"}},
            ]
        }
    ]
    mock_get_available_tools.return_value = {Tool.Calculator.value.ID: MockCalculator.get_tool_definition()}
    results = asyncio.run(
        async_call_tools(chat_history, MockCohereDeployment(), ctx)
    )
    assert {'call': {'name': 'toolkit_calculator', 'parameters': {'invalid_param': '6*7'}}, 'outputs': [
        {'details': "Model didn't pass required parameter: code", 'success': False, 'text': 'Error calling tool toolkit_calculator.',
         'type': 'other'}]} in results

def test_tools_params_checker_invalid_param_type(mock_get_available_tools) -> None:
    class MockCalculator(BaseTool):
        ID = "toolkit_calculator"
        @classmethod
        def get_tool_definition(cls) -> ToolDefinition:
            return ToolDefinition(
                name=cls.ID,
                display_name="Calculator",
                implementation=MockCalculator,
                parameter_definitions={
                    "code": {
                        "description": "The expression for the calculator to evaluate, it should be a valid mathematical expression.",
                        "type": "str",
                        "required": True,
                    }
                },
                is_visible=False,
                is_available=True,
                category=ToolCategory.Function,
                error_message=cls.generate_error_message(),
                description="A powerful multi-purpose calculator capable of a wide array of math calculations.",
            )

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            return [{"result": 42}]

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "toolkit_calculator", "parameters": {"code": 6}},
            ]
        }
    ]
    mock_get_available_tools.return_value = {Tool.Calculator.value.ID: MockCalculator.get_tool_definition()}
    results = asyncio.run(
        async_call_tools(chat_history, MockCohereDeployment(), ctx)
    )
    assert {'call': {'name': 'toolkit_calculator', 'parameters': {'code': 6}}, 'outputs': [
        {'type': 'other', 'success': False, 'text': 'Error calling tool toolkit_calculator.',
         'details': "Model passed invalid parameter. Parameter 'code' must be of type str, but got int"}]} in results

def test_tools_params_checker_required_param_empty(mock_get_available_tools) -> None:
    class MockCalculator(BaseTool):
        ID = "toolkit_calculator"
        @classmethod
        def get_tool_definition(cls) -> ToolDefinition:
            return ToolDefinition(
                name=cls.ID,
                display_name="Calculator",
                implementation=MockCalculator,
                parameter_definitions={
                    "code": {
                        "description": "The expression for the calculator to evaluate, it should be a valid mathematical expression.",
                        "type": "str",
                        "required": True,
                    }
                },
                is_visible=False,
                is_available=True,
                category=ToolCategory.Function,
                error_message=cls.generate_error_message(),
                description="A powerful multi-purpose calculator capable of a wide array of math calculations.",
            )

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            return [{"result": 42}]

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "toolkit_calculator", "parameters": {"code": ""}},
            ]
        }
    ]
    mock_get_available_tools.return_value = {Tool.Calculator.value.ID: MockCalculator.get_tool_definition()}
    results = asyncio.run(
        async_call_tools(chat_history, MockCohereDeployment(), ctx)
    )
    assert {'call': {'name': 'toolkit_calculator', 'parameters': {'code': ''}}, 'outputs': [
        {'details': 'Model passed empty value for required parameter: code', 'success': False,
         'text': 'Error calling tool toolkit_calculator.', 'type': 'other'}]} in results
