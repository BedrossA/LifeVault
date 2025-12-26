"""Redis caching service"""
from app.db.redis import get_redis
from typing import Optional, Any
import json

class CacheService:
    @staticmethod
    async def set(key: str, value: Any, ttl: int = 3600):
        redis = await get_redis()
        await redis.setex(key, ttl, json.dumps(value))
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        redis = await get_redis()
        value = await redis.get(key)
        return json.loads(value) if value else None
    
    @staticmethod
    async def delete(key: str):
        redis = await get_redis()
        await redis.delete(key)
    
    @staticmethod
    async def cache_session(session_id: str, user_data: dict, ttl: int = 1800):
        await CacheService.set(f"session:{session_id}", user_data, ttl)
    
    @staticmethod
    async def get_session(session_id: str) -> Optional[dict]:
        return await CacheService.get(f"session:{session_id}")
    
    @staticmethod
    async def invalidate_session(session_id: str):
        await CacheService.delete(f"session:{session_id}")