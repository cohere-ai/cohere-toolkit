from backend.services.cache import get_client

def test_redis_client():
    redis = get_client()

    response = redis.ping()

    assert response is True
