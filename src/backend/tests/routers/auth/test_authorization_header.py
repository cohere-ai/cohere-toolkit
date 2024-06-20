from unittest.mock import MagicMock

import freezegun
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.services.auth.jwt import JWTService
from backend.services.auth.request_validators import validate_authorization
from backend.tests.factories import get_factory

# Weird issue with freezegun, see: https://stackoverflow.com/questions/73007409/freezeguns-freeze-time-throws-odd-transformers-error-when-used
freezegun.configure(extend_ignore_list=["transformers"])


def test_validate_authorization_valid_token(
    session_client: TestClient,
):
    user = {"user_id": "test"}
    token = JWTService().create_and_encode_jwt(user, "")

    response = session_client.get(
        "/test-auth", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_validate_authorization_no_authorization(session_client: TestClient):
    response = session_client.get("/test-auth", headers={})

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authorization: Bearer <token> required in request headers."
    }


def test_validate_authorization_no_bearer(session_client: TestClient):
    response = session_client.get(
        "/test-auth", headers={"Authorization": "test invalid_token"}
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authorization: Bearer <token> required in request headers."
    }


def test_validate_authorization_invalid_token(session_client: TestClient):
    response = session_client.get(
        "/test-auth", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Bearer token is invalid."}


def test_validate_authorization_expired_token(
    session_client: TestClient,
):
    user = {"user_id": "test"}
    with freezegun.freeze_time("2024-01-01 00:00:00"):
        token = JWTService().create_and_encode_jwt(user, "")

    # Call endpoint a month later
    with freezegun.freeze_time("2024-02-01 00:00:00"):
        response = session_client.get(
            "/test-auth", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 401
    assert response.detail == "Bearer token is invalid or expired."


def test_validate_authorization_blacklisted_token(
    session_client: TestClient, session: Session
):
    user = {"user_id": "test"}
    token = JWTService().create_and_encode_jwt(user, "")
    decoded = JWTService().decode_jwt(token)

    # Create a Blacklist entry
    _ = get_factory("Blacklist", session).create(token_id=decoded["jti"])

    response = session_client.get(
        "/test-auth", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Bearer token is blacklisted."}
