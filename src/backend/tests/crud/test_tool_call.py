import pytest

from backend.crud import tool_call as tool_call_crud
from backend.database_models.tool_call import ToolCall
from backend.tests.factories import get_factory


@pytest.fixture(autouse=True)
def conversation(session, user):
    return get_factory("Conversation", session).create(id="1", user_id=user.id)


@pytest.fixture(autouse=True)
def message(session, conversation, user):
    return get_factory("Message", session).create(
        id="1", conversation_id=conversation.id, user_id=user.id
    )


def test_create_tool_call(session):
    tool_call_data = ToolCall(
        name="Hello, World!",
        parameters={"test": "test"},
        message_id="1",
    )

    tool_call = tool_call_crud.create_tool_call(session, tool_call_data)
    assert tool_call.name == tool_call_data.name
    assert tool_call.parameters == tool_call_data.parameters
    assert tool_call.message_id == tool_call_data.message_id

    tool_call = tool_call_crud.get_tool_call_by_id(session, tool_call.id)
    assert tool_call.name == tool_call_data.name
    assert tool_call.parameters == tool_call_data.parameters
    assert tool_call.message_id == tool_call_data.message_id


def test_get_tool_call_by_id(session):
    tool_call_data = ToolCall(
        name="Hello, World!",
        parameters={"test": "test"},
        message_id="1",
    )

    tool_call = tool_call_crud.create_tool_call(session, tool_call_data)
    assert tool_call_crud.get_tool_call_by_id(session, tool_call.id) == tool_call


def test_get_tool_call_by_id_not_found(session):
    assert tool_call_crud.get_tool_call_by_id(session, "1") is None


def test_list_tool_calls_by_message_id(session):
    _ = get_factory("ToolCall", session).create(name="Hello, World!", message_id="1")

    tool_calls = tool_call_crud.list_tool_calls_by_message_id(session, "1")
    assert len(tool_calls) == 1
    assert tool_calls[0].name == "Hello, World!"


def test_list_tool_calls_by_message_id_empty(session):
    tool_calls = tool_call_crud.list_tool_calls_by_message_id(session, "1")
    assert len(tool_calls) == 0
