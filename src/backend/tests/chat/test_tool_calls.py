import asyncio
from typing import Any, Dict, List
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.chat.custom.tool_calls import async_call_tools
from backend.config.tools import AVAILABLE_TOOLS, ToolName
from backend.schemas.tool import ManagedTool
from backend.services.context import Context
from backend.tests.model_deployments.mock_deployments import MockCohereDeployment
from backend.tools.base import BaseTool


def test_async_call_tools_success() -> None:
    class MockCalculator(BaseTool):
        NAME = "toolkit_calculator"

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            return [{"result": 42}]

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "toolkit_calculator", "parameters": {"expression": "6*7"}}
            ]
        }
    ]
    MOCKED_TOOLS = {ToolName.Calculator: ManagedTool(implementation=MockCalculator)}
    with patch.dict(AVAILABLE_TOOLS, MOCKED_TOOLS) as mock:
        results = asyncio.run(
            async_call_tools(chat_history, MockCohereDeployment(), ctx)
        )
        assert results == [
            {
                "call": {
                    "name": "toolkit_calculator",
                    "parameters": {"expression": "6*7"},
                },
                "outputs": [{"result": 42}],
            }
        ]


def test_async_call_tools_failure() -> None:
    class MockCalculator(BaseTool):
        NAME = "toolkit_calculator"

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            raise Exception("Calculator failed")

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "toolkit_calculator", "parameters": {"expression": "6*7"}}
            ]
        }
    ]
    MOCKED_TOOLS = {ToolName.Calculator: ManagedTool(implementation=MockCalculator)}
    with patch.dict(AVAILABLE_TOOLS, MOCKED_TOOLS) as mock:
        with pytest.raises(HTTPException) as excinfo:
            results = asyncio.run(
                async_call_tools(chat_history, MockCohereDeployment(), ctx)
            )
        assert str(excinfo.value.status_code) == "500"
        assert (
            str(excinfo.value.detail)
            == "Error while calling tool toolkit_calculator: Calculator failed"
        )


@patch("backend.chat.custom.tool_calls.TIMEOUT", 1)
def test_async_call_tools_timeout() -> None:
    class MockCalculator(BaseTool):
        NAME = "toolkit_calculator"

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            await asyncio.sleep(3)
            return [{"result": 42}]

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "toolkit_calculator", "parameters": {"expression": "6*7"}}
            ]
        }
    ]
    MOCKED_TOOLS = {ToolName.Calculator: ManagedTool(implementation=MockCalculator)}
    with patch.dict(AVAILABLE_TOOLS, MOCKED_TOOLS) as mock:
        with pytest.raises(HTTPException) as excinfo:
            asyncio.run(async_call_tools(chat_history, MockCohereDeployment(), ctx))
        assert str(excinfo.value.status_code) == "500"
        assert (
            str(excinfo.value.detail) == "Timeout while calling tools with timeout: 1"
        )


def test_async_call_tools_failure_and_success() -> None:
    class MockWebScrape(BaseTool):
        NAME = "web_scrape"

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            raise Exception("Web scrape failed")

    class MockCalculator(BaseTool):
        NAME = "toolkit_calculator"

        async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
        ) -> List[Dict[str, Any]]:
            return [{"result": 42}]

    ctx = Context()
    chat_history = [
        {
            "tool_calls": [
                {"name": "web_scrape", "parameters": {"expression": "6*7"}},
                {"name": "toolkit_calculator", "parameters": {"expression": "6*7"}},
            ]
        }
    ]
    MOCKED_TOOLS = {
        ToolName.Calculator: ManagedTool(implementation=MockCalculator),
        ToolName.Web_Scrape: ManagedTool(implementation=MockWebScrape),
    }
    with patch.dict(AVAILABLE_TOOLS, MOCKED_TOOLS) as mock:
        with pytest.raises(HTTPException) as excinfo:
            asyncio.run(async_call_tools(chat_history, MockCohereDeployment(), ctx))
        assert str(excinfo.value.status_code) == "500"
        assert (
            str(excinfo.value.detail)
            == "Error while calling tool web_scrape: Web scrape failed"
        )
