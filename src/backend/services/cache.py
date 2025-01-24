from typing import Any

from redis import Redis

from backend.config.settings import Settings
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()


def get_client() -> Redis:
    redis_url = Settings().get('redis.url')

    if not redis_url:
        error = "Tried retrieving Redis client but redis.url in configuration.yaml is not set."
        logger.error(event=error)
        raise ValueError(error)

    client = Redis.from_url(redis_url, decode_responses=True)

    return client


def cache_put(key: str, value: Any) -> None:
    client = get_client()

    if isinstance(value, dict):
        client.hset(key, mapping=value)
    else:
        client.set(key, value)


def cache_get(key: str) -> Any:
    client = get_client()

    return client.get(key)


def cache_get_dict(key: str) -> dict:
    client = get_client()

    return client.hgetall(key)


def cache_del(key: str) -> None:
    client = get_client()

    client.delete(key)
