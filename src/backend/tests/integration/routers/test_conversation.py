import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config import Settings
from backend.database_models import Conversation
from backend.model_deployments.cohere_platform import CohereDeployment
from backend.schemas.user import User
from backend.tests.unit.factories import get_factory

_IS_GOOGLE_CLOUD_API_KEY_SET = bool(Settings().get('google_cloud.api_key'))


def test_search_conversations(
    session_client: TestClient,
    session: Session,
    user: User,
    mock_available_model_deployments,
) -> None:
    conversation = get_factory("Conversation", session).create(
        title="test title", user_id=user.id
    )
    response = session_client.get(
        "/v1/conversations:search",
        headers={"User-Id": user.id},
        params={"query": "test"},
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["id"] == conversation.id


def test_search_conversations_with_reranking(
    session_client: TestClient,
    session: Session,
    user: User,
    mock_available_model_deployments,
) -> None:
    _ = get_factory("Conversation", session).create(
        title="Hello, how are you?", text_messages=[], user_id=user.id
    )
    conversation2 = get_factory("Conversation", session).create(
        title="There are are seven colors in the rainbow",
        text_messages=[],
        user_id=user.id,
    )
    response = session_client.get(
        "/v1/conversations:search",
        headers={
            "User-Id": user.id,
            "Deployment-Name": CohereDeployment.name(),
        },
        params={"query": "color"},
    )
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["id"] == conversation2.id


def test_search_conversations_no_conversations(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    _ = get_factory("Conversation", session).create(title="test title", user_id=user.id)
    user2 = get_factory("User", session).create()

    response = session_client.get(
        "/v1/conversations:search",
        headers={"User-Id": user2.id},
        params={"query": "test"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_generate_title(
    session_client: TestClient,
    session: Session,
    user: User,
    mock_available_model_deployments,
) -> None:
    conversation_initial = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.post(
        f"/v1/conversations/{conversation_initial.id}/generate-title",
        headers={"User-Id": conversation_initial.user_id},
    )
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["title"] is not None

    # Check if the conversation was updated
    conversation = (
        session.query(Conversation)
        .filter_by(id=conversation_initial.id, user_id=conversation_initial.user_id)
        .first()
    )
    assert conversation is not None
    assert conversation.title == response_json["title"]
    assert response_json["error"] is None


def test_fail_generate_title_missing_user_id(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.post(
        f"/v1/conversations/{conversation.id}/generate-title"
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "User-Id required in request headers."}


def test_fail_generate_title_nonexistent_conversation(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    response = session_client.post(
        "/v1/conversations/123/generate-title", headers={"User-Id": user.id}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation with ID: 123 not found."}


@pytest.mark.skip(reason="Restore this test when we get access to run models on Huggingface")
def test_generate_title_error_invalid_model(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.post(
        f"/v1/conversations/{conversation.id}/generate-title?model=invalid",
        headers={"User-Id": conversation.user_id},
    )

    assert response.status_code == 200
    response = response.json()

    # Since it's a streaming endpoint, the error is silent
    # The response code is 200 but there's an error message
    assert (
        response["error"]
        == "status_code: 404, body: {'message': \"model 'invalid' not found, make sure the correct model ID was used and that you have access to the model.\"}"
    )
    assert response["title"] == ""


# SYNTHESIZE


@pytest.mark.skipif(not _IS_GOOGLE_CLOUD_API_KEY_SET, reason="Google Cloud API key not set, skipping test")
def test_synthesize_english_message(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    message = get_factory("Message", session).create(
        id="1", text="Hello world!", conversation_id=conversation.id, user_id=user.id
    )
    response = session_client.get(
        f"/v1/conversations/{conversation.id}/synthesize/{message.id}",
        headers={"User-Id": conversation.user_id},
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "audio/mp3"


@pytest.mark.skipif(not _IS_GOOGLE_CLOUD_API_KEY_SET, reason="Google Cloud API key not set, skipping test")
def test_synthesize_non_english_message(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    message = get_factory("Message", session).create(
        id="1", text="Bonjour le monde!", conversation_id=conversation.id, user_id=user.id
    )
    response = session_client.get(
        f"/v1/conversations/{conversation.id}/synthesize/{message.id}",
        headers={"User-Id": conversation.user_id},
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "audio/mp3"


def test_fail_synthesize_message_nonexistent_message(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    response = session_client.get(
        "/v1/conversations/123/synthesize/456",
        headers={"User-Id": user.id},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Message with ID: 456 not found."}
