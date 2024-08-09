import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config.deployments import ModelDeploymentName
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