from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.tools import Tool, get_available_tools
from backend.schemas.user import User
from backend.tests.unit.factories import get_factory

TOOL_DEFINITION_KEYS = [
    "name",
    "display_name",
    "parameter_definitions",
    "is_visible",
    "is_available",
    "should_return_token",
    "category",
    "description"
]

def test_list_tools(session_client: TestClient, session: Session) -> None:
    response = session_client.get("/v1/tools")
    assert response.status_code == 200
    available_tools = get_available_tools()
    for tool in response.json():
        tool_definition = available_tools.get(tool["name"])
        assert tool_definition is not None

        for key in TOOL_DEFINITION_KEYS:
            assert tool[key] == getattr(tool_definition, key)

def test_list_authed_tool_should_return_token(session_client: TestClient, session: Session) -> None:
    # Patch get_token method for Google Drive
    with patch('backend.tools.google_drive.tool.GoogleDriveAuth.get_token', return_value="Mocked Value"):
        response = session_client.get("/v1/tools")

    assert response.status_code == 200

    for tool in response.json():
        if tool["should_return_token"]:
            assert tool["token"] == "Mocked Value"

def test_list_authed_tool_should_not_return_token(session_client: TestClient, session: Session) -> None:
    response = session_client.get("/v1/tools")

    assert response.status_code == 200

    for tool in response.json():
        if not tool["should_return_token"]:
            assert tool["token"] == ""

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
    tool_definition = get_available_tools().get(tool["name"])

    for key in TOOL_DEFINITION_KEYS:
        assert tool[key] == getattr(tool_definition, key)

def test_list_tools_with_agent_that_doesnt_exist(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.get("/v1/tools", params={"agent_id": "fake_id"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent with ID fake_id not found."}
