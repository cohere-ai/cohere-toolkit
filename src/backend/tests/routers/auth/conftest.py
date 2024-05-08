from unittest.mock import patch

import pytest

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING


@pytest.fixture(autouse=True)
def mock_session_secret_key_env(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET_KEY", "test")


@pytest.fixture(autouse=True)
def mock_google_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test")


@pytest.fixture(autouse=True)
def mock_enabled_auth(mock_google_env):
    # Can directly use class since no external calls are made
    from backend.services.auth import BasicAuthentication, GoogleOAuthStrategy

    mocked_strategies = {
        BasicAuthentication.NAME: BasicAuthentication(),
        GoogleOAuthStrategy.NAME: GoogleOAuthStrategy,
    }

    with patch.dict(ENABLED_AUTH_STRATEGY_MAPPING, mocked_strategies) as mock:
        yield mock
