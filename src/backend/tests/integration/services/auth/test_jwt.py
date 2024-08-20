from unittest.mock import patch

import jwt

from backend.services.auth.jwt import JWTService


def test_decode_jwt():
    jwt_service = JWTService()
    with patch("jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.return_value = {"context": "test_context", "jti": "test_jti"}
        result = jwt_service.decode_jwt("fake_token")
        assert result == {"context": "test_context", "jti": "test_jti"}


def test_decode_jwt_expired():
    jwt_service = JWTService()
    with patch("jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError
        result = jwt_service.decode_jwt("fake_token")
        assert result is None


def test_decode_jwt_invalid_token():
    jwt_service = JWTService()
    with patch("jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.side_effect = jwt.InvalidTokenError
        result = jwt_service.decode_jwt("fake_token")
        assert result is None
