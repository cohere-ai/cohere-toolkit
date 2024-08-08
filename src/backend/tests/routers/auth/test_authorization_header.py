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
    token = JWTService().create_and_encode_jwt(user)

    # Use /logout endpoint to test request validator
    response = session_client.get(
        "/v1/logout", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_validate_authorization_no_authorization():
    request_mock = MagicMock(headers={})

    with pytest.raises(HTTPException) as exc:
        _ = validate_authorization(request_mock)

    exception = exc.value
    assert exception.status_code == 401
    assert (
        exception.detail == "Authorization: Bearer <token> required in request headers."
    )


def test_validate_authorization_no_bearer():
    request_mock = MagicMock(headers={"Authorization": "test invalid_token"})

    with pytest.raises(HTTPException) as exc:
        _ = validate_authorization(request_mock)

    exception = exc.value
    assert exception.status_code == 401
    assert (
        exception.detail == "Authorization: Bearer <token> required in request headers."
    )


def test_validate_authorization_invalid_token():
    request_mock = MagicMock(headers={"Authorization": "Bearer invalid_token"})

    with pytest.raises(HTTPException) as exc:
        _ = validate_authorization(request_mock)

    exception = exc.value
    assert exception.status_code == 401
    assert exception.detail == "Bearer token is invalid or expired."


def test_validate_authorization_expired_token(session):
    user = {"user_id": "test"}
    with freezegun.freeze_time("2023-01-01 00:00:00"):
        token = JWTService().create_and_encode_jwt(user)

    request_mock = MagicMock(headers={"Authorization": f"Bearer {token}"})

    with freezegun.freeze_time("2024-05-01 00:00:00"):
        with pytest.raises(HTTPException) as exc:
            _ = validate_authorization(request_mock, session)

    exception = exc.value
    assert exception.status_code == 401
    assert exception.detail == "Bearer token is invalid or expired."


def test_validate_authorization_blacklisted_token(
    session_client: TestClient, session: Session
):
    user = {"user_id": "test"}
    token = JWTService().create_and_encode_jwt(user)
    decoded = JWTService().decode_jwt(token)

    # Create a Blacklist entry
    _ = get_factory("Blacklist", session).create(token_id=decoded["jti"])

    response = session_client.get(
        "/v1/logout", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Bearer token is blacklisted."}
