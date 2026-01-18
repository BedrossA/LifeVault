"""Redis caching service"""
from app.db.redis import get_redis
from typing import Optional, Any, Callable
from functools import wraps
import json

def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            redis = await get_redis()
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await redis.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator


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