"""Redis-based rate limiting"""
from app.db.redis import get_redis
import time
from functools import wraps
from fastapi import Request, HTTPException


async def check_rate_limit(key: str, limit: int, window: int) -> bool:
    redis = await get_redis()
    current = int(time.time())
    window_start = current - window
    await redis.zremrangebyscore(key, 0, window_start)
    request_count = await redis.zcard(key)
    if request_count >= limit:
        return False
    await redis.zadd(key, {str(current): current})
    await redis.expire(key, window)
    return True

class RateLimiter:
    """Enhanced rate limiter with per-endpoint limits"""
    
    LIMITS = {
        '/api/v1/auth/login': (5, 60),          # 5 requests per minute
        '/api/v1/auth/register': (3, 3600),     # 3 per hour
        '/api/v1/face/recognize': (30, 60),     # 30 per minute
        'default': (100, 60)                     # 100 per minute default
    }
    
    @staticmethod
    async def check_rate_limit(request: Request, endpoint: str = None):
        """Check rate limit for request"""
        key = f"rate_limit:{request.client.host}:{endpoint or 'default'}"
        limit, window = RateLimiter.LIMITS.get(
            endpoint, 
            RateLimiter.LIMITS['default']
        )
        
        if not await check_rate_limit(key, limit, window):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {window} seconds."
            )