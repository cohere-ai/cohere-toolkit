from backend.services.cache import get_client


def test_redis_client():
    redis = get_client()

    assert redis.ping() is True
