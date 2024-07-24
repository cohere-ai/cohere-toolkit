import pytest

from backend.crud import tool as tool_crud
from backend.database_models.tool import Tool
from backend.schemas.tool import ManagedTool, ToolCreate, ToolUpdate
from backend.tests.factories import get_factory


def test_create_tool(session):
    tool_data = ToolCreate(
        name="Test Tool",
        display_name="Test Tool Display Name",
        description="Test Tool Description",
        implementation_class_name="LangChainWikiRetriever",
        parameter_definitions={
            "query": {
                "description": "Query for retrieval test.",
                "type": "str",
                "required": True,
            }
        },
        kwargs={"chunk_size": 400, "chunk_overlap": 0},
        default_tool_config={},
        is_visible=True,
        is_community=False,
        auth_implementation_class_name="",
        error_message_text="LangChainWikiRetriever not available.",
        category="DataLoader",
    )

    tool = tool_crud.create_tool(session, tool_data)
    assert tool.name == tool_data.name
    assert tool.description == tool_data.description
    assert tool.display_name == tool_data.display_name
    assert tool.implementation_class_name == tool_data.implementation_class_name
    assert tool.parameter_definitions == tool_data.parameter_definitions
    assert tool.kwargs == tool_data.kwargs
    tool = tool_crud.get_tool(session, tool.id)
    assert tool.name == tool_data.name


def test_get_tool(session, tool):
    retrieved_tool = tool_crud.get_tool(session, tool.id)
    assert retrieved_tool.id == tool.id
    assert retrieved_tool.name == tool.name
    assert retrieved_tool.description == tool.description


def test_fail_get_nonexistent_tool(session):
    tool = tool_crud.get_tool(session, "123")
    assert tool is None


def test_list_tools(session):
    # Delete default tools
    session.query(Tool).delete()
    _ = get_factory("Tool", session).create(name="Test Tool")

    tools = tool_crud.get_tools(session)
    assert len(tools) == 1
    assert tools[0].name == "Test Tool"


def test_list_tools_empty(session):
    # Delete default tools
    session.query(Tool).delete()
    tools = tool_crud.get_tools(session)
    assert len(tools) == 0


def test_list_tools_with_pagination(session):
    # Delete default tools
    session.query(Tool).delete()
    for i in range(10):
        _ = get_factory("Tool", session).create(name=f"Test Model {i}")

    tools = tool_crud.get_tools(session, offset=5, limit=5)
    assert len(tools) == 5
    tools.sort(key=lambda x: x.name)
    for i, tool in enumerate(tools):
        assert tool.name == f"Test Model {i + 5}"


def test_get_tools_by_agent_id(session, user):
    agent = get_factory("Agent", session).create(user=user)
    for i in range(10):
        tool = get_factory("Tool", session).create(name=f"Test Tool {i}")
        agent.associated_tools.append(tool)

    tools = tool_crud.get_tools_by_agent_id(session, agent.id)

    assert len(tools) == 10
    for i, tool in enumerate(tools):
        assert tool.name == f"Test Tool {i}"


def test_get_tools_by_deployment_id_empty(session, user):
    agent = get_factory("Agent", session).create(user=user)
    tools = tool_crud.get_tools_by_agent_id(session, agent.id)
    assert len(tools) == 0


def test_get_tools_by_agent_id_with_pagination(session, user):
    agent = get_factory("Agent", session).create(user=user)
    for i in range(10):
        tool = get_factory("Tool", session).create(name=f"Test Tool {i}")
        agent.associated_tools.append(tool)

    tools = tool_crud.get_tools_by_agent_id(session, agent.id, offset=5, limit=5)
    assert len(tools) == 5

    for i, tool in enumerate(tools):
        assert tool.name == f"Test Tool {i + 5}"


def test_update_tool(session, tool):

    new_tool_data = ToolUpdate(
        name="Tool Updated",
        description="Updated Description",
    )

    updated_tool = tool_crud.update_tool(session, tool, new_tool_data)

    assert updated_tool.name == new_tool_data.name
    assert updated_tool.description == new_tool_data.description
    assert updated_tool.display_name == tool.display_name

    tool = tool_crud.get_tool(session, tool.id)
    assert tool.name == new_tool_data.name
    assert tool.description == new_tool_data.description


def test_assign_tool_to_agent(session, user, tool):
    agent = get_factory("Agent", session).create(user=user)
    tool_crud.assign_tool_to_agent(session, tool, agent, {})

    agent_tool = tool_crud.get_agent_tool_by_name(session, agent.id, tool.name)
    assert agent_tool is not None
    assert agent_tool.id == tool.id


def test_remove_tool_from_agent(session, user, tool):
    agent = get_factory("Agent", session).create(user=user)
    tool_crud.assign_tool_to_agent(session, tool, agent, {})

    agent_tool = tool_crud.get_agent_tool_by_name(session, agent.id, tool.name)
    assert agent_tool is not None
    assert agent_tool.id == tool.id

    tool_crud.remove_tool_from_agent(session, tool, agent)

    agent_tool = tool_crud.get_agent_tool_by_name(session, agent.id, tool.name)
    assert agent_tool is None


def test_remove_all_tools_from_agent(session, user):
    agent = get_factory("Agent", session).create(user=user)
    for i in range(5):
        tool = get_factory("Tool", session).create(name=f"Test Tool {i}")
        agent.associated_tools.append(tool)

    tool_crud.remove_all_tools_from_agent(session, agent)

    agent_tools = tool_crud.get_tools_by_agent_id(session, agent.id)
    assert agent_tools == []


def test_delete_tool(session, deployment):
    tool = get_factory("Tool", session).create(name="Test Tool")

    tool_crud.delete_tool(session, tool.id)

    tool = tool_crud.get_tool(session, tool.id)
    assert tool is None


def test_delete_nonexistent_tool(session):
    tool_crud.delete_tool(session, "123")  # no error
    tool = tool_crud.get_tool(session, "123")
    assert tool is None
