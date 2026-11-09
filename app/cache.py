"""Redis cache helpers."""
import os
from typing import Optional

import redis

_redis_client: Optional[redis.Redis] = None

CACHE_TTL_SECONDS = 30


def get_redis() -> Optional[redis.Redis]:
    """Return Redis client, or None when server unreachable (app still works)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True,
        )
    try:
        _redis_client.ping()
        return _redis_client
    except redis.RedisError:
        return None
