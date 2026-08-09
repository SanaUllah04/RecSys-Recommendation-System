import redis.asyncio as redis
import redis.exceptions as redis_exceptions
from app.core.config import get_settings
import json
import logging
from typing import Optional, Any

settings = get_settings()
logger = logging.getLogger(__name__)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class CacheService:
    def __init__(self):
        self.client = redis_client
        self.ttl = settings.REDIS_TTL

    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.client.get(key)
            if data:
                return json.loads(data)
        except (redis_exceptions.RedisError, OSError):
            logger.warning("Redis unavailable, skipping cache get for %s", key)
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        try:
            await self.client.set(key, json.dumps(value, default=str), ex=ttl or self.ttl)
        except (redis_exceptions.RedisError, OSError):
            logger.warning("Redis unavailable, skipping cache set for %s", key)

    async def delete(self, key: str):
        try:
            await self.client.delete(key)
        except (redis_exceptions.RedisError, OSError):
            logger.warning("Redis unavailable, skipping cache delete for %s", key)

    async def invalidate_pattern(self, pattern: str):
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await self.client.delete(*keys)
        except (redis_exceptions.RedisError, OSError):
            logger.warning("Redis unavailable, skipping cache invalidation for %s", pattern)

    async def get_recommendations(self, user_id: int, algo: str) -> Optional[list]:
        return await self.get(f"rec:{user_id}:{algo}")

    async def set_recommendations(self, user_id: int, algo: str, recs: list):
        await self.set(f"rec:{user_id}:{algo}", recs, ttl=1800)


cache = CacheService()
