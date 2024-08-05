from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.database_models.user import User
from backend.schemas.metrics import MetricsData, MetricsMessageType
from backend.services.auth import BasicAuthentication
from backend.services.metrics import report_metrics
from backend.tests.factories import get_factory


def test_list_users_empty(session_client: TestClient, session: Session) -> None:
    # Delete the default user
    session.query(User).delete()
    response = session_client.get("/v1/users")
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 0


def test_list_users(session_client: TestClient, session: Session) -> None:
    session.query(User).delete()
    _ = get_factory("User", session).create(fullname="John Doe")

    response = session_client.get("/v1/users")
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1


def test_get_user(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(fullname="John Doe")

    response = session_client.get(f"/v1/users/{user.id}")
    response_user = response.json()

    assert response.status_code == 200
    assert response_user["id"] == user.id
    assert response_user["fullname"] == "John Doe"


def test_fail_get_nonexistent_user(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.get("/v1/users/123")

    assert response.status_code == 404
    assert response.json() == {"detail": f"User with ID: 123 not found."}


@pytest.mark.asyncio
def test_create_user_metric(session_client: TestClient, session: Session) -> None:
    user_data_req = {
        "fullname": "John Doe",
        "email": "john@email.com",
    }
    with patch(
        "backend.services.metrics.report_metrics",
        return_value=None,
    ) as mock_metrics:
        response = session_client.post("/v1/users", json=user_data_req)
        assert response.status_code == 200
        response_user = response.json()
        m_args: MetricsData = mock_metrics.await_args.args[0].signal
        assert m_args.message_type == MetricsMessageType.USER_CREATED
        assert m_args.user.fullname == user_data_req["fullname"]


def test_create_user(session_client: TestClient, session: Session) -> None:
    user_data_req = {
        "fullname": "John Doe",
        "email": "john@email.com",
    }

    response = session_client.post("/v1/users", json=user_data_req)
    response_user = response.json()

    user = session.get(User, response_user["id"])

    assert response.status_code == 200
    assert response_user["fullname"] == user_data_req["fullname"]
    assert response_user["email"] == user_data_req["email"]
    assert user is not None
    assert user.fullname == user_data_req["fullname"]
    assert user.email == user_data_req["email"]


def test_create_user_with_password_saves_hashed_password(
    session_client: TestClient, session: Session
) -> None:
    user_data_req = {
        "fullname": "John Doe",
        "email": "john@email.com",
        "password": "abcd",
    }

    response = session_client.post("/v1/users", json=user_data_req)
    response_user = response.json()

    user = session.get(User, response_user["id"])

    assert response.status_code == 200
    assert response_user["fullname"] == user_data_req["fullname"]
    assert response_user["email"] == user_data_req["email"]
    assert user is not None
    assert user.fullname == user_data_req["fullname"]
    assert user.email == user_data_req["email"]
    assert BasicAuthentication.check_password("abcd", user.hashed_password)


def test_fail_create_user_missing_fullname(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.post("/v1/users", json={})
    response_user = response.json()

    assert response.status_code == 422
    assert response_user == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "fullname"],
                "msg": "Field required",
                "input": {},
                "url": "https://errors.pydantic.dev/2.8/v/missing",
            }
        ]
    }


def test_update_user_metric(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(fullname="John Doe")
    with patch(
        "backend.services.metrics.report_metrics",
        return_value=None,
    ) as mock_metrics:
        response = session_client.put(
            f"/v1/users/{user.id}",
            json={"fullname": "new name"},
            headers={"User-Id": user.id},
        )
        response_user = response.json()
        assert response.status_code == 200
        m_args: MetricsData = mock_metrics.await_args.args[0].signal
        assert m_args.message_type == MetricsMessageType.USER_UPDATED
        assert m_args.user_id == user.id
        assert m_args.user.fullname == "new name"


def test_update_user(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(fullname="John Doe")

    response = session_client.put(f"/v1/users/{user.id}", json={"fullname": "new name"})
    response_user = response.json()

    assert response.status_code == 200
    assert response_user["fullname"] == "new name"

    # Check if user was updated
    updated_user = session.get(User, user.id)
    assert updated_user.fullname == "new name"


def test_update_user_password_saves_hashed_password(
    session_client: TestClient, session: Session
) -> None:
    user = get_factory("User", session).create(fullname="John Doe")

    response = session_client.put(f"/v1/users/{user.id}", json={"password": "abcd"})

    assert response.status_code == 200
    # Check if user was updated
    updated_user = session.get(User, user.id)
    assert BasicAuthentication.check_password("abcd", updated_user.hashed_password)


def test_fail_update_nonexistent_user(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.put("/v1/users/123", json={"fullname": "new name"})

    assert response.status_code == 404
    assert response.json() == {"detail": f"User with ID: 123 not found."}


def test_delete_user_metric(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(fullname="John Doe")
    with patch(
        "backend.services.metrics.report_metrics",
        return_value=None,
    ) as mock_metrics:
        response = session_client.delete(
            f"/v1/users/{user.id}", headers={"User-Id": user.id}
        )
        assert response.status_code == 200
        m_args: MetricsData = mock_metrics.await_args.args[0].signal
        assert m_args.message_type == MetricsMessageType.USER_DELETED
        assert m_args.user_id == user.id


def test_delete_user(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(fullname="John Doe")

    response = session_client.delete(f"/v1/users/{user.id}")

    assert response.status_code == 200
    assert response.json() == {}

    # Check if user was deleted
    user = session.get(User, user.id)
    assert user is None


def test_fail_delete_nonexistent_user(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.delete("/v1/users/123")

    assert response.status_code == 404
    assert response.json() == {"detail": f"User with ID: 123 not found."}
