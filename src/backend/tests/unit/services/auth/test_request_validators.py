from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from backend.services.auth.request_validators import validate_authorization


def test_validate_authorization_with_valid_request():
    request = Mock(spec=Request)
    request.headers.get.return_value = "Bearer fake_token"
    session = Mock(spec=Session)
    session.query.return_value.filter.return_value.first.return_value = None

    with patch(
        "backend.services.auth.jwt.JWTService.decode_jwt",
        return_value={"context": "test_context", "jti": "test_jti"},
    ) as mock_decode_jwt:
        result = validate_authorization(request, session=session)
        assert isinstance(result, dict)


def test_validate_authorization_no_auth_header():
    request = Mock(spec=Request)
    request.headers.get.return_value = None
    session = Mock(spec=Session)

    with pytest.raises(HTTPException) as exc:
        validate_authorization(request, session=session)
        assert exc.status_code == 401


def test_validate_authorization_invalid_auth_header():
    request = Mock(spec=Request)
    request.headers.get.return_value = "fake_token"
    session = Mock(spec=Session)

    with pytest.raises(HTTPException) as exc:
        validate_authorization(request, session=session)
        assert exc.status_code == 401


def test_validate_invalid_jwt():
    request = Mock(spec=Request)
    request.headers.get.return_value = "Bearer fake_token"

    with patch(
        "backend.services.auth.jwt.JWTService.decode_jwt",
        return_value=None,
    ) as mock_decode_jwt:
        with pytest.raises(HTTPException) as exc:
            validate_authorization(request)
            assert exc.status_code == 401


def test_validate_blacklisted_token():
    request = Mock(spec=Request)
    request.headers.get.return_value = "Bearer fake_token"
    session = Mock(spec=Session)
    session.query.return_value.filter.return_value.first.return_value = Mock()

    with patch(
        "backend.services.auth.jwt.JWTService.decode_jwt",
        return_value={"context": "test_context", "jti": "test_jti"},
    ) as mock_decode_jwt:
        with pytest.raises(HTTPException) as exc:
            validate_authorization(request, session=session)
            assert exc.status_code == 401
