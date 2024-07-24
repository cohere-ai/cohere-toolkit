from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.settings import Settings
from backend.config.tools import AVAILABLE_TOOLS, ToolName
from backend.crud import tool as tool_crud
from backend.schemas.user import User
from backend.tests.factories import get_factory


def test_create_tool(session_client: TestClient, session: Session) -> None:
    response = session_client.post(
        "/v1/tools",
        json={
            "name": "Test Tool",
            "kwargs": {"test": "test"},
            "is_visible": True,
            "description": "Test Description",
            "error_message_text": "Test Error Message",
            "category": "Data loader",
            "default_tool_config": {"test": "test"},
        },
    )
    assert response.status_code == 200
    tool = response.json()
    assert tool["name"] == "Test Tool"
    assert tool["kwargs"] == {"test": "test"}
    assert tool["is_visible"] is True
    assert tool["is_available"] is True
    assert tool["description"] == "Test Description"
    assert tool["category"] == "Data loader"
    assert tool["error_message"] is None


def test_create_tool_default_config_not_set(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.post(
        "/v1/tools",
        json={
            "name": "Test Tool",
            "kwargs": {"test": "test"},
            "is_visible": True,
            "description": "Test Description",
            "error_message_text": "Test Error Message",
            "category": "Data loader",
            "default_tool_config": {"test": ""},
        },
    )
    assert response.status_code == 200
    tool = response.json()
    assert tool["name"] == "Test Tool"
    assert tool["kwargs"] == {"test": "test"}
    assert tool["is_visible"]
    assert not tool["is_available"]
    assert tool["description"] == "Test Description"
    assert tool["category"] == "Data loader"
    assert tool["error_message"] == "Test Error Message"


def test_update_tool(session_client: TestClient, session: Session) -> None:
    tool = get_factory("Tool", session).create(
        name="Test Tool",
        kwargs={"test": "test"},
        is_visible=True,
        description="Test Description",
    )
    response = session_client.put(
        f"/v1/tools/{tool.id}",
        json={
            "name": "Test Tool",
            "kwargs": {"test1": "test1"},
            "is_visible": False,
            "description": "Test Description Updated",
            "error_message_text": "Test Error Message",
            "category": "Data loader",
            "default_tool_config": {"test": "test"},
        },
    )
    assert response.status_code == 200
    tool_updated = tool_crud.get_tool(session, tool.id)

    assert tool_updated.name == "Test Tool"
    assert tool_updated.kwargs == {"test1": "test1"}
    assert not tool.is_visible
    assert tool.is_available
    assert tool.description == "Test Description Updated"
    assert tool.category == "Data loader"
    assert tool.error_message is None


def test_update_tool_default_config_empty(
    session_client: TestClient, session: Session
) -> None:
    tool = get_factory("Tool", session).create(
        name="Test Tool",
        kwargs={"test": "test"},
        is_visible=True,
        description="Test Description",
        default_tool_config={"test": ""},
    )
    response = session_client.put(
        f"/v1/tools/{tool.id}",
        json={
            "name": "Test Tool",
            "kwargs": {"test1": "test1"},
            "is_visible": False,
            "description": "Test Description Updated",
            "error_message_text": "Test Error Message",
            "category": "Data loader",
            "default_tool_config": {},
        },
    )
    assert response.status_code == 200
    tool_updated = tool_crud.get_tool(session, tool.id)

    assert tool_updated.name == "Test Tool"
    assert tool_updated.kwargs == {"test1": "test1"}
    assert not tool.is_visible
    assert tool.is_available
    assert tool.description == "Test Description Updated"
    assert tool.category == "Data loader"
    assert not tool.error_message


def test_get_tool(session_client: TestClient, session: Session) -> None:
    tool = get_factory("Tool", session).create(
        name="Test Tool",
        kwargs={"test": "test"},
        is_visible=True,
        description="Test Description",
    )
    response = session_client.get(f"/v1/tools/{tool.id}")
    assert response.status_code == 200
    tool_response = response.json()
    assert tool_response["name"] == "Test Tool"
    assert tool_response["kwargs"] == {"test": "test"}
    assert tool_response["is_visible"]
    assert tool_response["is_available"]
    assert tool_response["description"] == "Test Description"
    assert tool_response["category"] == "Data loader"
    assert tool_response["error_message"] is None


def test_list_tools(session_client: TestClient, session: Session) -> None:
    response = session_client.get("/v1/tools")
    all_tools = tool_crud.get_tools(session)
    available_tools = {tool.name: tool for tool in all_tools if tool.is_available}
    assert response.status_code == 200
    for tool in response.json():
        assert tool["name"] in available_tools.keys()

        # get tool that has the same name as the tool in the response
        tool_definition = available_tools[tool["name"]]

        assert tool["kwargs"] == tool_definition.kwargs
        assert tool["is_visible"] == tool_definition.is_visible
        assert tool["is_available"] == tool_definition.is_available
        assert not tool["error_message"]
        assert tool["category"] == tool_definition.category
        assert tool["description"] == tool_definition.description


def test_list_tools_error_message_none_if_available(client: TestClient) -> None:
    response = client.get("/v1/tools")
    assert response.status_code == 200
    for tool in response.json():
        if tool["is_available"]:
            assert tool["error_message"] is None


def test_list_all_tools(session_client: TestClient, session: Session) -> None:
    response = session_client.get("/v1/tools?all=1")
    all_tools = tool_crud.get_tools(session)
    all_tools = {tool.name: tool for tool in all_tools}

    assert response.status_code == 200
    for tool in response.json():
        assert tool["name"] in all_tools.keys()

        # get tool that has the same name as the tool in the response
        tool_definition = all_tools[tool["name"]]

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
    agent = get_factory("Agent", session).create(name="test agent", user=user)
    test_tool = get_factory("Tool", session).create(
        name="Test Tool",
        kwargs={"test": "test"},
        is_visible=True,
        description="Test Description",
    )
    agent.associated_tools.append(test_tool)
    response = session_client.get("/v1/tools", params={"agent_id": agent.id})
    assert response.status_code == 200
    assert len(response.json()) == 1

    tool = response.json()[0]
    assert tool["name"] == "Test Tool"

    assert tool["kwargs"] == test_tool.kwargs
    assert tool["is_visible"] == test_tool.is_visible
    assert tool["is_available"] == test_tool.is_available
    assert tool["error_message"] == test_tool.error_message
    assert tool["category"] == test_tool.category
    assert tool["description"] == test_tool.description


def test_list_tools_with_agent_that_doesnt_exist(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.get("/v1/tools", params={"agent_id": "fake_id"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Agent with ID: fake_id not found."}


def test_delete_tool(session_client: TestClient, session: Session) -> None:
    tool = get_factory("Tool", session).create(
        name="Test Tool",
        kwargs={"test": "test"},
        is_visible=True,
        description="Test Description",
    )
    response = session_client.delete(f"/v1/tools/{tool.id}")
    _ = tool_crud.get_tool(session, tool.id)
    assert response.status_code == 200
    assert _ is None
