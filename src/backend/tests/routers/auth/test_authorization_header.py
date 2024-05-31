from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from freezegun import freeze_time

from backend.services.auth.jwt import JWTService
from backend.services.auth.request_validators import validate_authorization


def test_validate_authorization_valid_token():
    user = {"user_id": "test"}
    with freeze_time("2024-01-01 00:00:00"):
        token = JWTService().create_and_encode_jwt(user)
        request_mock = MagicMock(headers={"Authorization": f"Bearer {token}"})

        token_user = validate_authorization(request_mock)

    assert token_user == {"user_id": "test"}


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


def test_validate_authorization_expired_token():
    user = {"user_id": "test"}
    with freeze_time("2024-01-01 00:00:00"):
        token = JWTService().create_and_encode_jwt(user)

    request_mock = MagicMock(headers={"Authorization": f"Bearer {token}"})

    with freeze_time("2024-02-01 00:00:00"):
        with pytest.raises(HTTPException) as exc:
            _ = validate_authorization(request_mock)

    exception = exc.value
    assert exception.status_code == 401
    assert exception.detail == "Bearer token is invalid or expired."
