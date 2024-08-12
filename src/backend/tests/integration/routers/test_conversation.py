import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.deployments import ModelDeploymentName
from backend.database_models import Conversation
from backend.schemas.metrics import MetricsData, MetricsMessageType
from backend.schemas.user import User
from backend.tests.unit.factories import get_factory


def test_search_conversations(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(
        title="test title", user_id=user.id
    )
    response = session_client.get(
        "/v1/conversations:search",
        headers={"User-Id": user.id},
        params={"query": "test"},
    )
    print("here")
    print(response.json)
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["id"] == conversation.id


@pytest.mark.skipif(
    os.environ.get("COHERE_API_KEY") is None,
    reason="Cohere API key not set, skipping test",
)
def test_search_conversations_with_reranking(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation1 = get_factory("Conversation", session).create(
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
            "Deployment-Name": ModelDeploymentName.CoherePlatform,
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


@pytest.mark.skipif(
    os.environ.get("COHERE_API_KEY") is None,
    reason="Cohere API key not set, skipping test",
)
def test_search_conversations_with_reranking_sends_metrics(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation1 = get_factory("Conversation", session).create(
        title="Hello, how are you?", text_messages=[], user_id=user.id
    )
    conversation2 = get_factory("Conversation", session).create(
        title="There are are seven colors in the rainbow",
        text_messages=[],
        user_id=user.id,
    )
    with patch(
        "backend.services.metrics.report_metrics",
        return_value=None,
    ) as mock_metrics:
        response = session_client.get(
            "/v1/conversations:search",
            headers={
                "User-Id": user.id,
                "Deployment-Name": ModelDeploymentName.CoherePlatform,
            },
            params={"query": "color"},
        )
        results = response.json()
        assert response.status_code == 200
        m_args: MetricsData = mock_metrics.await_args.args[0].signal
        assert m_args.user_id == user.id
        assert m_args.model == "rerank-english-v2.0"

        assert m_args.message_type == MetricsMessageType.RERANK_API_SUCCESS
        assert m_args.duration_ms is not None and m_args.duration_ms > 0
        assert m_args.assistant_id is not None
        assert m_args.assistant.name is not None
        assert m_args.model is not None
        assert m_args.search_units > 0


# MISC


def test_generate_title(
    session_client: TestClient,
    session: Session,
    user: User,
) -> None:
    conversation = get_factory("Conversation", session).create(user_id=user.id)
    response = session_client.post(
        f"/v1/conversations/{conversation.id}/generate-title",
        headers={"User-Id": conversation.user_id},
    )
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["title"] is not None

    # Check if the conversation was updated
    conversation = (
        session.query(Conversation)
        .filter_by(id=conversation.id, user_id=conversation.user_id)
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
    assert response.json() == {"detail": f"Conversation with ID: 123 not found."}


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
