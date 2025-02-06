import freezegun
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.services.auth.jwt import JWTService
from backend.services.auth.request_validators import validate_authorization
from backend.tests.unit.factories import get_factory

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


def test_validate_authorization_no_authorization(session: Session):
    with pytest.raises(HTTPException) as exc:
        _ = validate_authorization(session, "")

    exception = exc.value
    assert exception.status_code == 401
    assert (
        exception.detail == "Authorization: Bearer <token> required in request headers."
    )


def test_validate_authorization_no_bearer(session: Session):
    with pytest.raises(HTTPException) as exc:
        _ = validate_authorization(session, "test invalid_token")

    exception = exc.value
    assert exception.status_code == 401
    assert (
        exception.detail == "Authorization: Bearer <token> required in request headers."
    )


def test_validate_authorization_invalid_token(session: Session):
    with pytest.raises(HTTPException) as exc:
        _ = validate_authorization(session, "Bearer invalid_token")

    exception = exc.value
    assert exception.status_code == 401
    assert exception.detail == "Bearer token is invalid or expired."


def test_validate_authorization_expired_token(session: Session):
    user = {"user_id": "test"}
    with freezegun.freeze_time("2023-01-01 00:00:00"):
        token = JWTService().create_and_encode_jwt(user)

    with freezegun.freeze_time("2024-05-01 00:00:00"):
        with pytest.raises(HTTPException) as exc:
            _ = validate_authorization(session, f"Bearer {token}")

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
