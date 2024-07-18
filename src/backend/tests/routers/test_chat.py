import json
import os
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.chat.enums import StreamEvent
from backend.config.deployments import ModelDeploymentName
from backend.database_models.conversation import Conversation
from backend.database_models.message import Message, MessageAgent
from backend.database_models.user import User
from backend.schemas.tool import Category
from backend.tests.factories import get_factory

is_cohere_env_set = (
    os.environ.get("COHERE_API_KEY") is not None
    and os.environ.get("COHERE_API_KEY") != ""
)


@pytest.fixture()
def user(session_chat: Session) -> User:
    return get_factory("User", session_chat).create()


# STREAMING CHAT TESTS
@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_new_chat(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_new_chat_with_agent(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    agent = get_factory("Agent", session_chat).create(
        user_id=user.id,
        tools=[],
        name="test agent",
        preamble="you are a smart assistant",
    )
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        params={"agent_id": agent.id},
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_new_chat_with_agent_existing_conversation(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    agent = get_factory("Agent", session_chat).create(
        user_id=user.id,
        tools=[],
        name="test agent",
        preamble="you are a smart assistant",
    )
    conversation = get_factory("Conversation", session_chat).create(
        user_id=user.id, agent_id=agent.id
    )
    _ = get_factory("Message", session_chat).create(
        conversation_id=conversation.id,
        user_id=user.id,
        agent="USER",
        text="Hello",
        position=1,
        is_active=True,
    )

    _ = get_factory("Message", session_chat).create(
        conversation_id=conversation.id,
        user_id=user.id,
        agent="CHATBOT",
        text="Hi",
        position=2,
        is_active=True,
    )

    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        params={"agent_id": agent.id},
        json={"message": "Hello", "max_tokens": 10, "conversation_id": conversation.id},
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 4
    )


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_existing_conversation_from_other_agent(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    agent = get_factory("Agent", session_chat).create(user_id=user.id)
    _ = get_factory("Agent", session_chat).create(user_id=user.id, id="123")
    conversation = get_factory("Conversation", session_chat).create(
        user_id=user.id, agent_id="123"
    )
    _ = get_factory("Message", session_chat).create(
        conversation_id=conversation.id,
        user_id=user.id,
        agent="USER",
        text="Hello",
        position=1,
        is_active=True,
    )

    _ = get_factory("Message", session_chat).create(
        conversation_id=conversation.id,
        user_id=user.id,
        agent="CHATBOT",
        text="Hi",
        position=2,
        is_active=True,
    )

    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        params={"agent_id": agent.id},
        json={"message": "Hello", "max_tokens": 10, "conversation_id": conversation.id},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Conversation ID {conversation.id} not found for specified agent."
    }


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_tools_not_in_agent_tools(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    agent = get_factory("Agent", session_chat).create(user_id=user.id, tools=[])
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        json={
            "message": "Hello",
            "max_tokens": 10,
            "tools": [{"name": "web_search"}],
            "agent_id": agent.id,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Tool web_search not found in agent {agent.id}"
    }


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_existing_chat(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)

    _ = get_factory("Message", session_chat).create(
        conversation_id=conversation.id,
        user_id=user.id,
        agent="USER",
        text="Hello",
        position=1,
        is_active=True,
    )

    _ = get_factory("Message", session_chat).create(
        conversation_id=conversation.id,
        user_id=user.id,
        agent="CHATBOT",
        text="Hi",
        position=2,
        is_active=True,
    )

    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        json={
            "message": "How are you doing?",
            "conversation_id": conversation.id,
            "max_tokens": 10,
        },
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 4
    )


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_fail_chat_missing_user_id(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    response = session_client_chat.post(
        "/v1/chat",
        json={"message": "Hello"},
        headers={"Deployment-Name": ModelDeploymentName.CoherePlatform},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_default_chat_missing_deployment_name(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    response = session_client_chat.post(
        "/v1/chat",
        json={"message": "Hello"},
        headers={"User-Id": user.id},
    )

    assert response.status_code == 200


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_fail_chat_missing_message(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        json={},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "message"],
                "msg": "Field required",
                "input": {},
                "url": "https://errors.pydantic.dev/2.7/v/missing",
            }
        ]
    }


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_custom_tools(session_client_chat, session_chat, user):
    response = session_client_chat.post(
        "/v1/chat-stream",
        json={
            "message": "Give me a number",
            "tools": [
                {
                    "name": "random_number_generator",
                    "description": "generate a random number",
                }
            ],
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 0, is_custom_tools=True
    )


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_managed_tools(session_client_chat, session_chat, user):
    tools = session_client_chat.get("/v1/tools", headers={"User-Id": user.id}).json()
    assert len(tools) > 0
    tool = [t for t in tools if t["is_visible"] and t["category"] != Category.Function][
        0
    ].get("name")

    response = session_client_chat.post(
        "/v1/chat-stream",
        json={"message": "Hello", "tools": [{"name": tool}]},
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_invalid_tool(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    response = session_client_chat.post(
        "/v1/chat-stream",
        json={"message": "Hello", "tools": [{"name": "invalid_tool"}]},
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Custom tools must have a description"}


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_managed_and_custom_tools(
    session_client_chat, session_chat, user
):
    tools = session_client_chat.get("/v1/tools", headers={"User-Id": user.id}).json()
    assert len(tools) > 0
    tool = [t for t in tools if t["is_visible"] and t["category"] != Category.Function][
        0
    ].get("name")

    response = session_client_chat.post(
        "/v1/chat-stream",
        json={
            "message": "Hello",
            "tools": [
                {"name": tool},
                {
                    "name": "random_number_generator",
                    "description": "Generate a random number",
                },
            ],
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot mix both managed and custom tools"}


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_search_queries_only(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    response = session_client_chat.post(
        "/v1/chat-stream",
        json={
            "message": "What is the capital of Ontario?",
            "search_queries_only": True,
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response,
        user,
        session_chat,
        session_client_chat,
        2,
        is_search_queries_only=True,
    )


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_chat_history(
    session_client_chat: TestClient, session_chat: Session
) -> None:
    user = get_factory("User", session_chat).create()

    response = session_client_chat.post(
        "/v1/chat-stream",
        json={
            "message": "Hello",
            "chat_history": [
                {"role": "USER", "message": "Hello"},
                {"role": "CHATBOT", "message": "Hi"},
            ],
            "max_tokens": 10,
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response,
        user,
        session_chat,
        session_client_chat,
        0,
    )


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_existing_chat_with_files_attaches_to_user_message(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)
    file1 = get_factory("File", session_chat).create(
        conversation_id=conversation.id, user_id=user.id
    )
    file2 = get_factory("File", session_chat).create(
        conversation_id=conversation.id, user_id=user.id
    )
    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        json={
            "message": "How are you doing?",
            "conversation_id": conversation.id,
            "file_ids": [file1.id, file2.id],
            "max_tokens": 10,
        },
    )

    conversation = session_chat.get(Conversation, (conversation.id, user.id))

    assert response.status_code == 200
    assert conversation is not None
    # Files now linked to same user message
    assert file1.message_id is not None
    assert file2.message_id is not None
    assert file1.message_id == file2.message_id
    message = session_chat.get(Message, file1.message_id)
    assert message is not None
    assert message.agent == MessageAgent.USER
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_existing_chat_with_attached_files_does_not_attach(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)
    existing_message = get_factory("Message", session_chat).create(
        conversation_id=conversation.id, user_id=user.id, position=0, is_active=True
    )
    file1 = get_factory("File", session_chat).create(
        conversation_id=conversation.id, user_id=user.id, message_id=existing_message.id
    )
    file2 = get_factory("File", session_chat).create(
        conversation_id=conversation.id, user_id=user.id, message_id=existing_message.id
    )
    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        json={
            "message": "How are you doing?",
            "conversation_id": conversation.id,
            "file_ids": [file1.id, file2.id],
            "max_tokens": 10,
        },
    )

    conversation = session_chat.get(Conversation, (conversation.id, user.id))

    assert response.status_code == 200
    assert conversation is not None
    # Files link not changed
    assert file1.message_id == existing_message.id
    assert file2.message_id == existing_message.id
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 3
    )


# NON-STREAMING CHAT TESTS
@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_non_streaming_chat(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    response = session_client_chat.post(
        "/v1/chat",
        json={"message": "Hello", "max_tokens": 10},
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    validate_conversation(session_chat, user, conversation_id, 2)


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_non_streaming_chat_with_managed_tools(session_client_chat, session_chat, user):
    tools = session_client_chat.get("/v1/tools", headers={"User-Id": user.id}).json()
    assert len(tools) > 0
    tool = [t for t in tools if t["is_visible"] and t["category"] != Category.Function][
        0
    ].get("name")

    response = session_client_chat.post(
        "/v1/chat",
        json={"message": "Hello", "tools": [{"name": tool}]},
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    validate_conversation(session_chat, user, conversation_id, 2)


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_non_streaming_chat_with_managed_and_custom_tools(
    session_client_chat, session_chat, user
):
    tools = session_client_chat.get("/v1/tools", headers={"User-Id": user.id}).json()
    assert len(tools) > 0
    tool = [t for t in tools if t["is_visible"] and t["category"] != Category.Function][
        0
    ].get("name")

    response = session_client_chat.post(
        "/v1/chat",
        json={
            "message": "Hello",
            "tools": [
                {"name": tool},
                {
                    "name": "random_number_generator",
                    "description": "Generate a random number",
                },
            ],
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot mix both managed and custom tools"}


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_non_streaming_chat_with_custom_tools(session_client_chat, session_chat, user):
    response = session_client_chat.post(
        "/v1/chat",
        json={
            "message": "Give me a number",
            "tools": [
                {
                    "name": "random_number_generator",
                    "description": "generate a random number",
                }
            ],
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 200
    assert len(response.json()["tool_calls"]) == 1


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_non_streaming_chat_with_search_queries_only(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    response = session_client_chat.post(
        "/v1/chat",
        json={
            "message": "What is the capital of Ontario?",
            "search_queries_only": True,
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    validate_conversation(session_chat, user, conversation_id, 2)


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_non_streaming_chat_with_chat_history(
    session_client_chat: TestClient, session_chat: Session
) -> None:
    user = get_factory("User", session_chat).create()

    response = session_client_chat.post(
        "/v1/chat",
        json={
            "message": "Hello",
            "chat_history": [
                {"role": "USER", "message": "Hello"},
                {"role": "CHATBOT", "message": "Hi"},
            ],
            "max_tokens": 10,
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]
    validate_conversation(session_chat, user, conversation_id, 0)


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_non_streaming_existing_chat_with_files_attaches_to_user_message(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)
    file1 = get_factory("File", session_chat).create(
        conversation_id=conversation.id, user_id=user.id
    )
    file2 = get_factory("File", session_chat).create(
        conversation_id=conversation.id, user_id=user.id
    )
    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        json={
            "message": "How are you doing?",
            "conversation_id": conversation.id,
            "file_ids": [file1.id, file2.id],
            "max_tokens": 10,
        },
    )

    conversation = session_chat.get(Conversation, (conversation.id, user.id))

    assert response.status_code == 200
    assert conversation is not None
    # Files now linked to same user message
    assert file1.message_id is not None
    assert file2.message_id is not None
    assert file1.message_id == file2.message_id
    message = session_chat.get(Message, file1.message_id)
    assert message is not None
    assert message.agent == MessageAgent.USER


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_non_streaming_existing_chat_with_attached_files_does_not_attach(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)
    existing_message = get_factory("Message", session_chat).create(
        conversation_id=conversation.id, user_id=user.id, position=0, is_active=True
    )
    file1 = get_factory("File", session_chat).create(
        conversation_id=conversation.id, user_id=user.id, message_id=existing_message.id
    )
    file2 = get_factory("File", session_chat).create(
        conversation_id=conversation.id, user_id=user.id, message_id=existing_message.id
    )
    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat",
        headers={
            "User-Id": user.id,
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
        },
        json={
            "message": "How are you doing?",
            "conversation_id": conversation.id,
            "file_ids": [file1.id, file2.id],
            "max_tokens": 10,
        },
    )

    conversation = session_chat.get(Conversation, (conversation.id, user.id))

    assert response.status_code == 200
    assert conversation is not None
    # Files link not changed
    assert file1.message_id == existing_message.id
    assert file2.message_id == existing_message.id


def validate_chat_streaming_response(
    response: Any,
    user: User,
    session: Session,
    session_client_chat: TestClient,
    expected_num_messages: int,
    has_citations: bool = False,
    is_search_queries_only: bool = False,
    is_custom_tools: bool = False,
) -> None:
    conversation_id = None
    event_types = set()

    for line in response.iter_lines():
        if not line:
            continue

        # remove the 'data' prefix to make it a valid JSON
        line = line.replace("data: ", "")
        response_json = json.loads(line)
        assert response_json["event"] in [e.value for e in StreamEvent]

        event_types.add(response_json["event"])
        if response_json["event"] == StreamEvent.STREAM_END:
            conversation_id = validate_stream_end_event(
                response_json, is_search_queries_only, is_custom_tools
            )

    if has_citations:
        assert StreamEvent.CITATION_GENERATION in event_types

    if is_search_queries_only:
        assert StreamEvent.SEARCH_QUERIES_GENERATION in event_types

    if is_custom_tools:
        assert StreamEvent.TOOL_CALLS_GENERATION in event_types

    # Check if the conversation was created correctly
    validate_conversation(session, user, conversation_id, expected_num_messages)


def validate_conversation(
    session: Session, user: User, conversation_id: str, expected_num_messages: int
) -> None:
    conversation = session.query(Conversation).filter_by(id=conversation_id).first()
    messages = session.query(Message).filter_by(conversation_id=conversation_id).all()

    if expected_num_messages == 0:
        assert conversation is None
        assert len(messages) == 0
        return

    assert conversation.id == conversation_id
    assert conversation.user_id == user.id
    assert len(conversation.messages) == expected_num_messages
    # Also test DB object
    conversation = session.get(Conversation, (conversation_id, user.id))
    assert conversation is not None
    assert conversation.user_id == user.id
    assert len(conversation.messages) == expected_num_messages


def validate_stream_end_event(
    response_json: dict, is_search_queries_only: bool, is_custom_tools: bool
) -> str:
    data = response_json["data"]
    if is_search_queries_only:
        assert len(data["search_queries"]) > 0
    elif is_custom_tools:
        assert len(data["tool_calls"]) > 0
    else:
        assert len(data["text"]) > 0

    assert is_valid_uuid(data["response_id"])
    assert is_valid_uuid(data["conversation_id"])
    assert is_valid_uuid(data["generation_id"])
    assert data["finish_reason"] == "COMPLETE" or data["finish_reason"] == "MAX_TOKENS"

    return data["conversation_id"]


def is_valid_uuid(id: str) -> bool:
    try:
        uuid.UUID(id, version=4)
        return True
    except ValueError:
        return False
