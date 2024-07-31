import pytest

from backend.config.settings import Settings
from backend.services.cache import get_client

# skip if redis is not available
is_redis_env_set = Settings().redis.url


@pytest.mark.skipif(not is_redis_env_set, reason="Redis is not set")
def test_redis_client():
    redis = get_client()

    assert redis.ping() is True
