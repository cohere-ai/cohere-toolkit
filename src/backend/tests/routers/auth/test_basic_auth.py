from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.database_models import Blacklist
from backend.services.auth.jwt import JWTService
from backend.tests.factories import get_factory


def test_login_success(session_client: TestClient, session: Session):
    _ = get_factory("User", session).create(email="test@gmail.com", password="abcd")

    response = session_client.post(
        "/v1/login",
        json={
            "strategy": "Basic",
            "payload": {"email": "test@gmail.com", "password": "abcd"},
        },
    )

    assert response.status_code == 200
    assert response.json().get("token") is not None


def test_login_invalid_password(session_client: TestClient, session: Session):
    _ = get_factory("User", session).create(email="test@gmail.com", password="hello")
    response = session_client.post(
        "/v1/login",
        json={
            "strategy": "Basic",
            "payload": {"email": "test@gmail.com", "password": "test"},
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Error performing Basic authentication with payload: {'email': 'test@gmail.com', 'password': 'test'}."
    }


def test_login_no_user(session_client: TestClient):
    response = session_client.post(
        "/v1/login",
        json={
            "strategy": "Basic",
            "payload": {"email": "nouser@gmail.com", "password": "test"},
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Error performing Basic authentication with payload: {'email': 'nouser@gmail.com', 'password': 'test'}."
    }


def test_login_invalid_strategy(session_client: TestClient):
    response = session_client.post(
        "/v1/login", json={"strategy": "test", "payload": {}}
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid Authentication strategy: test."}


def test_login_invalid_payload(session_client: TestClient):
    response = session_client.post(
        "/v1/login", json={"strategy": "Basic", "payload": {}}
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Missing the following keys in the payload: ['email', 'password']."
    }


def test_login_no_strategy(session_client: TestClient):
    response = session_client.post("/v1/login", json={"payload": {}})

    assert response.status_code == 422


def test_login_no_payload(session_client: TestClient):
    response = session_client.post("/v1/login", json={"strategy": ""})

    assert response.status_code == 422


def test_logout_success(session_client: TestClient, session: Session):
    user = {"user_id": "test"}
    token = JWTService().create_and_encode_jwt(user)
    decoded = JWTService().decode_jwt(token)

    response = session_client.get(
        "/v1/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    # Adds a Blacklist entry
    blacklist = (
        session.query(Blacklist).filter(Blacklist.token_id == decoded["jti"]).first()
    )
    assert blacklist is not None
