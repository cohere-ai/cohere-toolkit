from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.database_models.user import User
from backend.services.auth.request_validators import validate_authorization


def test_validate_authorization_with_valid_request(session: Session):
    mock_user = Mock(spec=User)
    mock_user.id = "user-name"
    mock_user.active = True

    with patch(
        "backend.services.auth.jwt.JWTService.decode_jwt",
        return_value={"context": {"id": "user-name"}, "jti": "test_jti"},
    ):
        with patch(
            "backend.crud.user.get_user",
            return_value=mock_user,
        ):
            result = validate_authorization(session, "Bearer fake_token")
        assert isinstance(result, dict)


def test_validate_authorization_no_auth_header(session: Session):
    with pytest.raises(HTTPException) as exc:
        validate_authorization(session, None)
    assert exc.value.status_code == 401


def test_validate_authorization_invalid_auth_header(session: Session):
    with pytest.raises(HTTPException) as exc:
        validate_authorization(session, "fake_token")
    assert exc.value.status_code == 401


def test_validate_invalid_jwt(session: Session):
    with patch(
        "backend.services.auth.jwt.JWTService.decode_jwt",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc:
            validate_authorization(session, "Bearer fake_token")
        assert exc.value.status_code == 401


def test_validate_blacklisted_token():
    session = Mock(spec=Session)
    session.query.return_value.filter.return_value.first.return_value = Mock()

    with patch(
        "backend.services.auth.jwt.JWTService.decode_jwt",
        return_value={"context": "test_context", "jti": "test_jti"},
    ):
        with pytest.raises(HTTPException) as exc:
            validate_authorization(session, "Bearer fake_token")
        assert exc.value.status_code == 401
