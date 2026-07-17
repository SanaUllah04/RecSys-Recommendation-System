import redis.asyncio as redis
from app.core.config import get_settings
import json
from typing import Optional, Any

settings = get_settings()

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class CacheService:
    def __init__(self):
        self.client = redis_client
        self.ttl = settings.REDIS_TTL

    async def get(self, key: str) -> Optional[Any]:
        data = await self.client.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        await self.client.set(key, json.dumps(value, default=str), ex=ttl or self.ttl)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def invalidate_pattern(self, pattern: str):
        keys = []
        async for key in self.client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.client.delete(*keys)

    async def get_recommendations(self, user_id: int, algo: str) -> Optional[list]:
        return await self.get(f"rec:{user_id}:{algo}")

    async def set_recommendations(self, user_id: int, algo: str, recs: list):
        await self.set(f"rec:{user_id}:{algo}", recs, ttl=1800)


cache = CacheService()
