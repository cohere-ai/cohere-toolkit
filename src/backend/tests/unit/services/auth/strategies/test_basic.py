from unittest.mock import Mock, patch

import bcrypt

from backend.database_models.user import User
from backend.services.auth.strategies.basic import BasicAuthentication


def test_login():
    basic_auth = BasicAuthentication()
    password = "test_password"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    test_user = Mock(spec=User)
    test_user.id = 10
    test_user.email = "test@example.com"
    test_user.fullname = "Test User"
    test_user.hashed_password = hashed_password
    session = Mock()
    session.query.return_value.filter.return_value.first.return_value = test_user

    with patch("bcrypt.checkpw") as mock_checkpw:
        result = basic_auth.login(
            session, {"email": "test@example.com", "password": password}
        )
        assert result == {
            "email": "test@example.com",
            "id": 10,
            "fullname": "Test User",
        }
        mock_checkpw.assert_called_once_with(password.encode("utf-8"), hashed_password)


def test_login_user_not_found():
    basic_auth = BasicAuthentication()
    session = Mock()
    session.query.return_value.filter.return_value.first.return_value = None

    result = basic_auth.login(
        session, {"email": "test@example.com", "password": "test_password"}
    )
    assert result is None


def test_login_invalid_password():
    basic_auth = BasicAuthentication()
    password = "test_password"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    test_user = Mock(spec=User)
    test_user.id = 10
    test_user.email = "test@example.com"
    test_user.fullname = "Test User"
    test_user.hashed_password = hashed_password
    session = Mock()
    session.query.return_value.filter.return_value.first.return_value = test_user

    with patch("bcrypt.checkpw") as mock_checkpw:
        mock_checkpw.return_value = False
        result = basic_auth.login(
            session, {"email": "test@example.com", "password": password}
        )
        assert result is None
        mock_checkpw.assert_called_once_with(password.encode("utf-8"), hashed_password)
