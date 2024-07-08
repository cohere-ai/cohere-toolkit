import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.database_models import SnapshotLink
from backend.tests.factories import get_factory


@pytest.fixture(autouse=True)
def conversation(session):
    return get_factory("Conversation", session).create(id="1", user_id="1")


@pytest.fixture(autouse=True)
def message(session):
    return get_factory("Message", session).create(id="1", conversation_id="1")


@pytest.fixture(autouse=True)
def organization(session):
    return get_factory("Organization", session).create(id="1")


@pytest.fixture
def snapshot(session):
    return get_factory("Snapshot", session).create(
        id="1",
        user_id="1",
        conversation_id="1",
        last_message_id="1",
        version=1,
        organization_id="1",
        snapshot={
            "title": "Title",
            "description": "Description",
            "agent": None,
            "messages": [
                {
                    "id": "1",
                    "conversation_id": "1",
                    "user_id": "1",
                    "text": "hey",
                    "agent": "USER",
                    "created_at": "2021-01-01T00:00:00",
                    "updated_at": "2021-01-01T00:00:00",
                    "generation_id": "1",
                    "position": 0,
                    "is_active": True,
                    "documents": [],
                    "citations": [],
                    "files": [],
                    "tool_calls": [],
                    "tool_plan": None,
                }
            ],
        },
    )


@pytest.fixture
def snapshot_link(session):
    return get_factory("SnapshotLink", session).create(id="1", snapshot_id="1")


def test_share_conversation(
    session_client: TestClient, session: Session, conversation, message
) -> None:
    conversation.text_messages.append(message)

    request_json = {
        "conversation_id": "1",
    }

    response = session_client.post(
        "/v1/snapshots", json=request_json, headers={"User-Id": "1"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["user_id"] == "1"
    assert "snapshot_id" in response_json
    assert "link_id" in response_json
    assert len(response_json["messages"]) == 1


def test_share_conversation_twice(
    session_client: TestClient, session: Session, conversation, message
) -> None:
    conversation.text_messages.append(message)

    request_json = {
        "conversation_id": "1",
    }

    response = session_client.post(
        "/v1/snapshots", json=request_json, headers={"User-Id": "1"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["user_id"] == "1"
    assert "snapshot_id" in response_json
    assert "link_id" in response_json
    assert len(response_json["messages"]) == 1

    first_snapshot_id = response_json["snapshot_id"]
    first_link_id = response_json["link_id"]

    response = session_client.post(
        "/v1/snapshots", json=request_json, headers={"User-Id": "1"}
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json["user_id"] == "1"
    assert "snapshot_id" in response_json
    assert "link_id" in response_json
    assert len(response_json["messages"]) == 1
    assert first_snapshot_id == response_json["snapshot_id"]
    assert first_link_id != response_json["link_id"]


def test_share_conversation_no_messages(session_client: TestClient) -> None:
    request_json = {
        "conversation_id": "1",
    }

    response = session_client.post(
        "/v1/snapshots", json=request_json, headers={"User-Id": "1"}
    )

    assert response.status_code == 404
    response_json = response.json()

    assert response_json["detail"] == "Conversation has no messages"


def test_share_conversation_not_found(
    session_client: TestClient, session: Session
) -> None:
    request_json = {
        "conversation_id": "123",
    }

    response = session_client.post(
        "/v1/snapshots", json=request_json, headers={"User-Id": "1"}
    )

    assert response.status_code == 404
    response_json = response.json()

    assert response_json["detail"] == "Conversation not found"


def test_list_snapshots(
    session_client: TestClient,
    session: Session,
    conversation,
    message,
    snapshot,
    snapshot_link,
) -> None:
    conversation.text_messages.append(message)

    response = session_client.get("/v1/snapshots", headers={"User-Id": "1"})

    assert response.status_code == 200
    results = response.json()

    assert len(results) == 1


def test_list_snapshots_no_snapshots(session_client: TestClient) -> None:
    response = session_client.get("/v1/snapshots", headers={"User-Id": "123"})

    assert response.status_code == 200
    results = response.json()

    assert len(results) == 0


def test_get_snapshot(
    session_client: TestClient,
    session: Session,
    conversation,
    message,
    snapshot,
    snapshot_link,
) -> None:
    conversation.text_messages.append(message)

    response = session_client.get("/v1/snapshots/link/1", headers={"User-Id": "1"})

    assert response.status_code == 200
    result = response.json()

    assert result["user_id"] == "1"
    assert result["last_message_id"] == "1"
    assert result["conversation_id"] == "1"
    assert isinstance(result["snapshot"], dict)


def test_get_snapshot_not_found(session_client: TestClient) -> None:
    response = session_client.get("/v1/snapshots/link/123", headers={"User-Id": "1"})

    assert response.status_code == 404
    result = response.json()

    assert result["detail"] == "Snapshot link not found"


def test_delete_snapshot(
    session_client: TestClient,
    session: Session,
    conversation,
    message,
    snapshot,
    snapshot_link,
) -> None:
    conversation.text_messages.append(message)

    response = session_client.delete("/v1/snapshots/1", headers={"User-Id": "1"})

    assert response.status_code == 200

    response = session_client.get("/v1/snapshots/link/1", headers={"User-Id": "1"})

    assert response.status_code == 404
    result = response.json()

    assert result["detail"] == "Snapshot link not found"


def test_delete_snapshot_not_found(session_client: TestClient) -> None:
    response = session_client.delete("/v1/snapshots/link123", headers={"User-Id": "1"})

    assert response.status_code == 404


def test_delete_snapshot_wrong_user(
    session_client: TestClient,
    session: Session,
    conversation,
    message,
    snapshot,
    snapshot_link,
) -> None:
    conversation.text_messages.append(message)

    response = session_client.delete("/v1/snapshots/link/1", headers={"User-Id": "2"})

    assert response.status_code == 403
    result = response.json()

    assert (
        result["detail"] == "User does not have permission to delete this snapshot link"
    )
