"""Redis caching service"""
from app.db.redis import get_redis
from typing import Optional, Any
import json
from datetime import timedelta

class CacheService:
    
    @staticmethod
    async def set(key: str, value: Any, ttl: int = 3600):
        """Set cache with TTL in seconds"""
        redis = await get_redis()
        serialized = json.dumps(value)
        await redis.setex(key, ttl, serialized)
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get cached value"""
        redis = await get_redis()
        value = await redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    @staticmethod
    async def delete(key: str):
        """Delete cache key"""
        redis = await get_redis()
        await redis.delete(key)
    
    @staticmethod
    async def exists(key: str) -> bool:
        """Check if key exists"""
        redis = await get_redis()
        return await redis.exists(key) > 0
    
    @staticmethod
    async def cache_session(session_id: str, user_data: dict, ttl: int = 1800):
        """Cache session data"""
        key = f"session:{session_id}"
        await CacheService.set(key, user_data, ttl)
    
    @staticmethod
    async def get_session(session_id: str) -> Optional[dict]:
        """Get cached session"""
        key = f"session:{session_id}"
        return await CacheService.get(key)
    
    @staticmethod
    async def invalidate_session(session_id: str):
        """Invalidate session cache"""
        key = f"session:{session_id}"
        await CacheService.delete(key)