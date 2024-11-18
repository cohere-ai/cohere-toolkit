import asyncio
from typing import Any, Dict, List
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.chat.custom.tool_calls import async_call_tools
from backend.config.tools import Tool
from backend.schemas.tool import ToolDefinition
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
    mock_get_available_tools.return_value = {Tool.Calculator.value.ID: ToolDefinition(implementation=MockCalculator)}
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
    mock_get_available_tools.return_value = {Tool.Calculator.value.ID: ToolDefinition(implementation=MockCalculator)}
    results = asyncio.run(
        async_call_tools(chat_history, MockCohereDeployment(), ctx)
    )
    assert results == [
        {
            "call": {
                "name": "toolkit_calculator",
                "parameters": {"code": "6*7"},
            },
            "outputs": [{'type': 'other', 'success': False, 'text': 'Calculator failed', 'details': ''}],
        },
    ]


@patch("backend.chat.custom.tool_calls.TIMEOUT_SECONDS", 1)
def test_async_call_tools_timeout(mock_get_available_tools) -> None:
    class MockCalculator(BaseTool):
        ID = "toolkit_calculator"

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
    mock_get_available_tools.return_value = {Tool.Calculator.value.ID: ToolDefinition(implementation=MockCalculator)}

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(async_call_tools(chat_history, MockCohereDeployment(), ctx))
    assert str(excinfo.value.status_code) == "500"
    assert (
        str(excinfo.value.detail) == "Timeout while calling tools with timeout: 1"
        )


def test_async_call_tools_failure_and_success(mock_get_available_tools) -> None:
    class MockWebScrape(BaseTool):
        ID = "web_scrape"

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            raise Exception("Web scrape failed")

    class MockCalculator(BaseTool):
        ID = "toolkit_calculator"

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
        Tool.Calculator.value.ID: ToolDefinition(implementation=MockCalculator),
        Tool.Web_Scrape.value.ID: ToolDefinition(implementation=MockWebScrape),
    }

    results = asyncio.run(
        async_call_tools(chat_history, MockCohereDeployment(), ctx)
    )

    assert {
        "call": {"name": "web_scrape", "parameters": {"code": "6*7"}},
        "outputs": [{"type": "other", 'success': False, 'text': 'Web scrape failed', 'details': ''}],
    } in results
    assert {
        "call": {"name": "toolkit_calculator", "parameters": {"code": "6*7"}},
        "outputs": [{"result": 42}],
    } in results
