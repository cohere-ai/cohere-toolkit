from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.tests.factories import get_factory


def test_list_users_empty(session_client: TestClient) -> None:
    response = session_client.get("/users")
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 0


def test_list_users(session_client: TestClient, session: Session) -> None:
    _ = get_factory("User", session).create(fullname="John Doe")

    response = session_client.get("/users")
    results = response.json()

    assert response.status_code == 200
    assert len(results) == 1


def test_get_user(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(fullname="John Doe")

    response = session_client.get(f"/users/{user.id}")
    response_user = response.json()

    assert response.status_code == 200
    assert response_user["id"] == user.id
    assert response_user["fullname"] == "John Doe"


def test_fail_get_nonexistent_user(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.get("/users/123")

    assert response.status_code == 404
    assert response.json() == {"detail": f"User with ID: 123 not found."}


def test_create_user(session_client: TestClient, session: Session) -> None:
    user_data_req = {
        "fullname": "John Doe",
        "email": "john@email.com",
    }

    response = session_client.post("/users", json=user_data_req)
    response_user = response.json()

    user = session.get(User, response_user["id"])

    assert response.status_code == 200
    assert response_user["fullname"] == user_data_req["fullname"]
    assert response_user["email"] == user_data_req["email"]
    assert user is not None
    assert user.fullname == user_data_req["fullname"]
    assert user.email == user_data_req["email"]


def test_fail_create_user_missing_data(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.post("/users", json={})
    response_user = response.json()

    assert response.status_code == 422
    assert response_user == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "fullname"],
                "msg": "Field required",
                "input": {},
                "url": "https://errors.pydantic.dev/2.7/v/missing",
            }
        ]
    }


def test_update_user(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(fullname="John Doe")

    response = session_client.put(f"/users/{user.id}", json={"fullname": "new name"})
    response_user = response.json()

    assert response.status_code == 200
    assert response_user["fullname"] == "new name"

    # Check if user was updated
    updated_user = session.get(User, user.id)
    assert updated_user.fullname == "new name"


def test_update_user_missing_data(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(fullname="John Doe")

    response = session_client.put(f"/users/{user.id}", json={})
    response_user = response.json()

    assert response.status_code == 422
    assert response_user == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "fullname"],
                "msg": "Field required",
                "input": {},
                "url": "https://errors.pydantic.dev/2.7/v/missing",
            }
        ]
    }


def test_fail_update_nonexistent_user(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.put("/users/123", json={"fullname": "new name"})

    assert response.status_code == 404
    assert response.json() == {"detail": f"User with ID: 123 not found."}


def test_delete_user(session_client: TestClient, session: Session) -> None:
    user = get_factory("User", session).create(fullname="John Doe")

    response = session_client.delete(f"/users/{user.id}")

    assert response.status_code == 200
    assert response.json() == {}

    # Check if user was deleted
    user = session.get(User, user.id)
    assert user is None


def test_fail_delete_nonexistent_user(
    session_client: TestClient, session: Session
) -> None:
    response = session_client.delete("/users/123")

    assert response.status_code == 404
    assert response.json() == {"detail": f"User with ID: 123 not found."}
