from unittest.mock import patch

import pytest

from backend.config.auth import ENABLED_AUTH_STRATEGY_MAPPING


@pytest.fixture(autouse=True)
def mock_enabled_basic_auth():
    # Can directly use class since no external calls are made
    from backend.services.auth import BasicAuthentication

    mocked_strategies = {BasicAuthentication.NAME: BasicAuthentication}

    with patch.dict(ENABLED_AUTH_STRATEGY_MAPPING, mocked_strategies) as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_session_secret_key_env(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET_KEY", "test_key")
