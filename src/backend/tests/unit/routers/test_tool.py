from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest 
from unittest.mock import patch

from backend.config.tools import Tool, get_available_tools
from backend.schemas.user import User
from backend.tests.unit.factories import get_factory

@pytest.fixture()
def mock_get_available_tools():
    with patch("backend.chat.custom.custom.get_deployment") as mock:
        yield mock

def test_list_tools(session_client: TestClient, session: Session) -> None:
    response = session_client.get("/v1/tools")
    assert response.status_code == 200
    available_tools = get_available_tools()
    for tool in response.json():
        assert tool["name"] in available_tools.keys()
        assert tool["kwargs"] is not None
        assert tool["is_visible"] is not None
        assert tool["is_available"] is not None
        assert tool["category"] is not None
        assert tool["description"] is not None


def test_list_tools_error_message_none_if_available(client: TestClient) -> None:
    response = client.get("/v1/tools")
    assert response.status_code == 200
    for tool in response.json():
        if tool["is_available"]:
            assert tool["error_message"] is None


def test_list_tools_with_agent(
    session_client: TestClient, session: Session, user: User
) -> None:
    agent = get_factory("Agent", session).create(
        name="test agent", tools=[Tool.Wiki_Retriever_LangChain.value.ID], user=user
    )

    response = session_client.get("/v1/tools", params={"agent_id": agent.id})
    assert response.status_code == 200
    assert len(response.json()) == 1

    tool = response.json()[0]
    assert tool["name"] == Tool.Wiki_Retriever_LangChain.value.ID

    # get tool that has the same name as the tool in the response
    tool_definition = get_available_tools()[tool["name"]]

    assert tool["kwargs"] == tool_definition.kwargs
    assert tool["is_visible"] == tool_definition.is_visible
    assert tool["is_available"] == tool_definition.is_available
    assert tool["error_message"] == tool_definition.error_message
    assert tool["category"] == tool_definition.category
    assert tool["description"] == tool_definition.description


def test_list_tools_with_agent_that_doesnt_exist(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.get("/v1/tools", params={"agent_id": "fake_id"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent with ID fake_id not found."}
