from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.settings import Settings
from backend.config.tools import AVAILABLE_TOOLS, ToolName
from backend.schemas.user import User
from backend.tests.factories import get_factory


def test_list_tools(session_client: TestClient, session: Session) -> None:
    response = session_client.get("/v1/tools")
    assert response.status_code == 200
    for tool in response.json():
        assert tool["name"] in AVAILABLE_TOOLS.keys()

        # get tool that has the same name as the tool in the response
        tool_definition = AVAILABLE_TOOLS[tool["name"]]

        assert tool["kwargs"] == tool_definition.kwargs
        assert tool["is_visible"] == tool_definition.is_visible
        assert tool["is_available"] == tool_definition.is_available
        assert tool["error_message"] == tool_definition.error_message
        assert tool["category"] == tool_definition.category
        assert tool["description"] == tool_definition.description


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
        name="test agent", tools=[ToolName.Wiki_Retriever_LangChain], user=user
    )

    response = session_client.get("/v1/tools", params={"agent_id": agent.id})
    assert response.status_code == 200
    assert len(response.json()) == 1

    tool = response.json()[0]
    assert tool["name"] == ToolName.Wiki_Retriever_LangChain

    # get tool that has the same name as the tool in the response
    tool_definition = AVAILABLE_TOOLS[tool["name"]]

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
