import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.tests.factories import get_factory


def test_login_success(session_client: TestClient, session: Session):
    _ = get_factory("User", session).create(
        id="test", fullname="Test User", email="test@gmail.com", password="abcd"
    )

    response = session_client.post(
        "/login",
        json={
            "strategy": "Basic",
            "payload": {"email": "test@gmail.com", "password": "abcd"},
        },
    )

    assert response.status_code == 200

    # Retrieve session after login
    response = session_client.get("/session")
    assert response.status_code == 200
    assert response.json() == {
        "id": "test",
        "fullname": "Test User",
        "email": "test@gmail.com",
    }


def test_logout_removes_session(session_client: TestClient, session: Session):
    _ = get_factory("User", session).create(
        id="test", fullname="Test User", email="test@gmail.com", password="abcd"
    )

    response = session_client.post(
        "/login",
        json={
            "strategy": "Basic",
            "payload": {"email": "test@gmail.com", "password": "abcd"},
        },
    )

    assert response.status_code == 200

    # Retrieve session after login
    response = session_client.get("/session")
    assert response.status_code == 200
    assert response.json() == {
        "id": "test",
        "fullname": "Test User",
        "email": "test@gmail.com",
    }

    # Logout
    response = session_client.get("/logout")
    assert response.status_code == 200

    # Retrieve session after logout
    response = session_client.get("/session")
    assert response.status_code == 401
