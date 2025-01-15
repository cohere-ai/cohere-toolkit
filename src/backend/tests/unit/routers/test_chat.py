import json
import os
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.chat.enums import StreamEvent
from backend.database_models.conversation import Conversation
from backend.database_models.message import Message, MessageAgent
from backend.database_models.user import User
from backend.model_deployments.cohere_platform import CohereDeployment
from backend.schemas.tool import ToolCategory
from backend.tests.unit.factories import get_factory
from backend.tests.unit.model_deployments.mock_deployments.mock_cohere_platform import (
    MockCohereDeployment,
)

is_cohere_env_set = (
    os.environ.get("COHERE_API_KEY") is not None
    and os.environ.get("COHERE_API_KEY") != ""
)


@pytest.fixture()
def user(session_chat: Session) -> User:
    return get_factory("User", session_chat).create()


# STREAMING CHAT TESTS
def test_streaming_new_chat(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": MockCohereDeployment.name(),
        },
        json={"message": "Hello", "max_tokens": 10},
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )


def test_streaming_new_chat_with_agent(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    deployment = get_factory("Deployment", session_chat).create()
    model = get_factory("Model", session_chat).create(deployment=deployment)
    agent = get_factory("Agent", session_chat).create(user=user, tools=[], deployment_id=deployment.id,
                                                      model_id=model.id)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": agent.user.id,
            "Deployment-Name": agent.deployment,
        },
        params={"agent_id": agent.id},
        json={"message": "Hello", "max_tokens": 10, "agent_id": agent.id},
    )
    assert response.status_code == 200
    validate_chat_streaming_response(
        response, agent.user, session_chat, session_client_chat, 2
    )


def test_streaming_new_chat_with_agent_existing_conversation(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    deployment = get_factory("Deployment", session_chat).create()
    model = get_factory("Model", session_chat).create(deployment=deployment)
    agent = get_factory("Agent", session_chat).create(user=user, tools=[], deployment_id=deployment.id,
                                                      model_id=model.id)

    agent.preamble = "you are a smart assistant"
    session_chat.refresh(agent)

    conversation = get_factory("Conversation", session_chat).create(
        user_id=agent.user.id, agent_id=agent.id
    )
    _ = get_factory("Message", session_chat).create(
        conversation_id=conversation.id,
        user_id=agent.user.id,
        agent="USER",
        text="Hello",
        position=1,
        is_active=True,
    )

    _ = get_factory("Message", session_chat).create(
        conversation_id=conversation.id,
        user_id=agent.user.id,
        agent="CHATBOT",
        text="Hi",
        position=2,
        is_active=True,
    )

    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": agent.user.id,
            "Deployment-Name": agent.deployment,
        },
        params={"agent_id": agent.id},
        json={"message": "Hello", "max_tokens": 10, "conversation_id": conversation.id, "agent_id": agent.id},
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, agent.user, session_chat, session_client_chat, 4
    )


def test_streaming_chat_with_existing_conversation_from_other_agent(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    agent = get_factory("Agent", session_chat).create(user=user)
    _ = get_factory("Agent", session_chat).create(user=user, id="123")
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
            "Deployment-Name": CohereDeployment.name(),
        },
        params={"agent_id": agent.id},
        json={"message": "Hello", "max_tokens": 10, "conversation_id": conversation.id, "agent_id": agent.id},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Conversation ID {conversation.id} not found for specified agent."
    }


def test_streaming_chat_with_tools_not_in_agent_tools(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    deployment = get_factory("Deployment", session_chat).create()
    model = get_factory("Model", session_chat).create(deployment=deployment)
    agent = get_factory("Agent", session_chat).create(user=user, tools=["wikipedia"], deployment_id=deployment.id,
                                                      model_id=model.id)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": agent.user.id,
            "Deployment-Name": agent.deployment,
        },
        json={
            "message": "Who is a tallest nba player",
            "tools": [{"name": "tavily_web_search"}],
            "agent_id": agent.id,
        },
    )

    assert response.status_code == 200
    validate_chat_streaming_tool_cals_response(response, ["tavily_web_search"])


def test_streaming_chat_with_agent_tools_and_empty_request_tools(
    session_client_chat: TestClient,
    session_chat:
    Session, user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    deployment = get_factory("Deployment", session_chat).create()
    model = get_factory("Model", session_chat).create(deployment=deployment)
    agent = get_factory("Agent", session_chat).create(user=user, tools=["tavily_web_search"],
                                                      deployment_id=deployment.id, model_id=model.id)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": agent.user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        json={
            "message": "Who is a tallest NBA player",
            "tools": [],
            "agent_id": agent.id,
        },
    )

    assert response.status_code == 200
    validate_chat_streaming_tool_cals_response(response, ["tavily_web_search"])


def test_streaming_existing_chat(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
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
            "Deployment-Name": CohereDeployment.name(),
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


def test_fail_chat_missing_user_id(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    response = session_client_chat.post(
        "/v1/chat",
        json={"message": "Hello"},
        headers={"Deployment-Name": CohereDeployment.name()},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_default_chat_missing_deployment_name(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    response = session_client_chat.post(
        "/v1/chat",
        json={"message": "Hello"},
        headers={"User-Id": user.id},
    )

    assert response.status_code == 200


def test_streaming_fail_chat_missing_message(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
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
            }
        ]
    }


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_managed_tools(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    # mock_available_model_deployments: list[dict],
) -> None:
    tools = session_client_chat.get("/v1/tools", headers={"User-Id": user.id}).json()
    assert len(tools) > 0
    tool = [t for t in tools if t["is_visible"] and t["category"] != ToolCategory.Function][
        0
    ].get("name")

    response = session_client_chat.post(
        "/v1/chat-stream",
        json={"message": "Hello", "tools": [{"name": tool}]},
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )

def test_streaming_chat_with_invalid_tool(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    response = session_client_chat.post(
        "/v1/chat-stream",
        json={"message": "Hello", "tools": [{"name": "invalid_tool"}]},
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Custom tools must have a description"}


def test_streaming_chat_with_managed_and_custom_tools(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    tools = session_client_chat.get("/v1/tools", headers={"User-Id": user.id}).json()
    assert len(tools) > 0
    tool = [t for t in tools if t["is_visible"] and t["category"] != ToolCategory.Function][
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
            "Deployment-Name": CohereDeployment.name(),
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot mix both managed and custom tools"}


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_streaming_chat_with_search_queries_only(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    # mock_available_model_deployments: list[dict],
) -> None:
    response = session_client_chat.post(
        "/v1/chat-stream",
        json={
            "message": "What is the capital of Ontario?",
            "search_queries_only": True,
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
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


def test_streaming_chat_with_chat_history(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
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
            "Deployment-Name": CohereDeployment.name(),
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


def test_streaming_existing_chat_with_files_attaches_to_user_message(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)
    file1 = get_factory("File", session_chat).create(user_id=user.id)
    file2 = get_factory("File", session_chat).create(user_id=user.id)
    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
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
    message = conversation.messages[0]
    assert message is not None
    assert message.agent == MessageAgent.USER
    assert file1.id in message.file_ids
    assert file2.id in message.file_ids
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )


def test_streaming_existing_chat_with_attached_files_does_not_attach(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    file1 = get_factory("File", session_chat).create(
        user_id=user.id,
    )
    file2 = get_factory("File", session_chat).create(
        user_id=user.id,
    )
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)
    existing_message = get_factory("Message", session_chat).create(
        conversation_id=conversation.id,
        user_id=user.id,
        position=0,
        is_active=True,
    )

    # Create conversation,message<>file relations
    for file in [file1, file2]:
        _ = get_factory("ConversationFileAssociation", session_chat).create(
            conversation_id=conversation.id, user_id=user.id, file_id=file.id
        )
        _ = get_factory("MessageFileAssociation", session_chat).create(
            message_id=existing_message.id, user_id=user.id, file_id=file.id
        )

    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
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

    # Existing message has file IDs
    message = session_chat.query(Message).filter_by(id=existing_message.id).first()
    assert file1.id in message.file_ids
    assert file2.id in message.file_ids
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 3
    )


def test_streaming_chat_private_agent(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    agent = get_factory("Agent", session_chat).create(
        user=user, is_private=True, tools=[]
    )
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        params={"agent_id": agent.id},
        json={"message": "Hello", "max_tokens": 10, "agent_id": agent.id},
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )


def test_streaming_chat_public_agent(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    agent = get_factory("Agent", session_chat).create(
        user_id=user.id, is_private=False, tools=[]
    )
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        params={"agent_id": agent.id},
        json={"message": "Hello", "max_tokens": 10, "agent_id": agent.id},
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )


def test_streaming_chat_private_agent_by_another_user(
    session_client_chat: TestClient, session_chat: Session, user: User
):
    agent = get_factory("Agent", session_chat).create(
        user_id=user.id, is_private=True, tools=[]
    )
    other_user = get_factory("User", session_chat).create()
    response = session_client_chat.post(
        "/v1/chat-stream",
        headers={
            "User-Id": other_user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        params={"agent_id": agent.id},
        json={"message": "Hello", "max_tokens": 10, "agent_id": agent.id},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Agent with ID {agent.id} not found."}


def test_stream_regenerate_existing_chat(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
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
        position=1,
        is_active=True,
    )

    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream/regenerate",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        json={
            "message": "",
            "conversation_id": conversation.id,
            "max_tokens": 10,
        },
    )

    assert response.status_code == 200
    validate_chat_streaming_response(
        response, user, session_chat, session_client_chat, 2
    )


def test_stream_regenerate_not_existing_chat(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    conversation_id = "test_conversation_id"

    response = session_client_chat.post(
        "/v1/chat-stream/regenerate",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        json={
            "message": "",
            "conversation_id": conversation_id,
            "max_tokens": 10,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Conversation with ID: {conversation_id} not found."}


def test_stream_regenerate_existing_chat_not_existing_user_messages(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)

    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat-stream/regenerate",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        json={
            "message": "",
            "conversation_id": conversation.id,
            "max_tokens": 10,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": f"Messages for user with ID: {user.id} not found."}


# NON-STREAMING CHAT TESTS
def test_non_streaming_chat(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    response = session_client_chat.post(
        "/v1/chat",
        json={"message": "Hello", "max_tokens": 10},
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    validate_conversation(session_chat, user, conversation_id, 2)


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_non_streaming_chat_with_managed_tools(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    # mock_available_model_deployments: list[dict],
) -> None:
    tools = session_client_chat.get("/v1/tools", headers={"User-Id": user.id}).json()
    assert len(tools) > 0
    tool = [t for t in tools if t["is_visible"] and t["category"] != ToolCategory.Function][
        0
    ].get("name")

    response = session_client_chat.post(
        "/v1/chat",
        json={"message": "Hello", "tools": [{"name": tool}]},
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    validate_conversation(session_chat, user, conversation_id, 2)


def test_non_streaming_chat_with_managed_and_custom_tools(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    tools = session_client_chat.get("/v1/tools", headers={"User-Id": user.id}).json()
    assert len(tools) > 0
    tool = [t for t in tools if t["is_visible"] and t["category"] != ToolCategory.Function][
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
            "Deployment-Name": CohereDeployment.name(),
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot mix both managed and custom tools"}


def test_non_streaming_chat_with_search_queries_only(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    response = session_client_chat.post(
        "/v1/chat",
        json={
            "message": "What is the capital of Ontario?",
            "search_queries_only": True,
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    validate_conversation(session_chat, user, conversation_id, 2)


def test_non_streaming_chat_with_chat_history(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
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
            "Deployment-Name": CohereDeployment.name(),
        },
    )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]
    validate_conversation(session_chat, user, conversation_id, 0)


def test_non_streaming_existing_chat_with_files_attaches_to_user_message(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)
    file1 = get_factory("File", session_chat).create(user_id=user.id)
    file2 = get_factory("File", session_chat).create(user_id=user.id)

    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
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
    message = conversation.messages[0]
    assert message.agent == MessageAgent.USER
    assert file1.id in message.file_ids
    assert file2.id in message.file_ids


def test_non_streaming_existing_chat_with_attached_files_does_not_attach(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)
    existing_message = get_factory("Message", session_chat).create(
        conversation_id=conversation.id, user_id=user.id, position=0, is_active=True
    )
    file1 = get_factory("File", session_chat).create(user_id=user.id)
    file2 = get_factory("File", session_chat).create(user_id=user.id)

    # Create conversation,message<>file relations
    for file in [file1, file2]:
        _ = get_factory("ConversationFileAssociation", session_chat).create(
            conversation_id=conversation.id, user_id=user.id, file_id=file.id
        )
        _ = get_factory("MessageFileAssociation", session_chat).create(
            message_id=existing_message.id, user_id=user.id, file_id=file.id
        )

    session_chat.refresh(conversation)

    response = session_client_chat.post(
        "/v1/chat",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
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
    # Existing message has file IDs
    message = session_chat.query(Message).filter_by(id=existing_message.id).first()
    assert file1.id in message.file_ids
    assert file2.id in message.file_ids


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


def test_streaming_chat_with_files(
    session_client_chat: TestClient,
    session_chat: Session,
    user: User,
    mock_available_model_deployments: list[dict],
) -> None:
    # Create convo
    conversation = get_factory("Conversation", session_chat).create(user_id=user.id)

    # Upload the files
    files = [
        (
            "files",
            (
                "Mariana_Trench.pdf",
                open("src/backend/tests/unit/test_data/Mariana_Trench.pdf", "rb"),
            ),
        )
    ]

    response = session_client_chat.post(
        "/v1/conversations/batch_upload_file",
        headers={"User-Id": conversation.user_id},
        files=files,
        data={"conversation_id": conversation.id},
    )

    assert response.status_code == 200
    file_id = response.json()[0]["id"]

    # Send the chat request
    response = session_client_chat.post(
        "/v1/chat",
        json={
            "message": "Hello",
            "max_tokens": 10,
            "file_ids": [file_id],
            "tools": [{"name": "search_file"}],
        },
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
    )

    assert response.status_code == 200


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
    conversation_db = session.get(Conversation, (conversation_id, user.id))
    assert conversation_db is not None
    assert conversation_db.user_id == user.id
    assert len(conversation_db.messages) == expected_num_messages


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


def validate_chat_streaming_tool_cals_response(response: Any, tools: list) -> None:
    data = []
    for line in response.iter_lines():
        if not line or ":ping" in line or ": ping" in line:
            continue

        # remove the 'data' prefix to make it a valid JSON
        line = line.replace("data: ", "")
        if "event" in line:
            response_json = json.loads(line)
            assert response_json["event"] in [e.value for e in StreamEvent]
            if response_json["event"] == StreamEvent.TOOL_CALLS_GENERATION:
                data.append(response_json["data"])

    tool_calls_names = [tool['name'] for entry in data for tool in entry['tool_calls']]

    # Check if all required tools are in the tool_names
    assert all(tool in tool_calls_names for tool in tools)


def is_valid_uuid(id: str) -> bool:
    try:
        uuid.UUID(id, version=4)
        return True
    except ValueError:
        return False
