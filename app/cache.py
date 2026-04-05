import os
import json
import redis
import logging
from pydantic import BaseModel

logger = logging.getLogger("app")

# In Docker, redis resolves to the container named 'redis'. Outside, it falls back to localhost.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Connection pool to prevent TCP handshake overhead per request
redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)

def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)

def get_cache(client: redis.Redis, key: str):
    """Fetch and decode JSON data from Redis, gracefully failing if offline."""
    try:
        data = client.get(key)
        if data:
            return json.loads(data)
    except redis.exceptions.ConnectionError:
        logger.warning(f"Redis GET failed for key {key}. Bypassing cache.")
    return None

def set_cache(client: redis.Redis, key: str, data: dict | list | BaseModel, ttl: int = 60):
    """Encode and store data in Redis, gracefully failing if offline."""
    try:
        # If the data is a Pydantic model (or list of models), convert to JSON-safe dict first
        if hasattr(data, "model_dump"):
            dumped = data.model_dump(mode='json')
        elif isinstance(data, list) and len(data) > 0 and hasattr(data[0], "model_dump"):
            dumped = [item.model_dump(mode='json') for item in data]
        else:
            dumped = data

        client.setex(key, ttl, json.dumps(dumped))
    except redis.exceptions.ConnectionError:
        logger.warning(f"Redis SET failed for key {key}. Bypassing cache.")

def invalidate_cache(client: redis.Redis, pattern: str):
    """Delete all keys matching a specific pattern, gracefully failing if offline."""
    try:
        # SCAN is safer than KEYS in production to avoid blocking the Redis thread
        for key in client.scan_iter(pattern):
            client.delete(key)
    except redis.exceptions.ConnectionError:
        logger.warning(f"Redis INVALIDATE failed for pattern {pattern}. Bypassing cache.")
