from unittest.mock import patch

import pytest

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING


@pytest.fixture(autouse=True)
def mock_jwt_secret_key_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test")


@pytest.fixture(autouse=True)
def mock_google_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test")


@pytest.fixture(autouse=True)
def mock_oidc_env(monkeypatch):
    monkeypatch.setenv("OIDC_CLIENT_ID", "test")
    monkeypatch.setenv("OIDC_CLIENT_SECRET", "test")
    monkeypatch.setenv("OIDC_CONFIG_ENDPOINT", "test")


@pytest.fixture(autouse=True)
def mock_enabled_auth(mock_google_env, mock_oidc_env):
    # Can directly use class since no external calls are made
    from backend.services.auth import BasicAuthentication, GoogleOAuth, OpenIDConnect

    mocked_strategies = {
        BasicAuthentication.NAME: BasicAuthentication(),
        GoogleOAuth.NAME: GoogleOAuth(),
        OpenIDConnect.NAME: OpenIDConnect(),
    }

    with patch.dict(ENABLED_AUTH_STRATEGY_MAPPING, mocked_strategies) as mock:
        yield mock
