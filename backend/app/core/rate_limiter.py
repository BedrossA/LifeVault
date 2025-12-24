"""Redis-based rate limiting"""
from app.db.redis import get_redis
from fastapi import HTTPException, status
import time

async def check_rate_limit(
    key: str,
    limit: int,
    window: int
) -> bool:
    """
    Check if rate limit is exceeded
    
    Args:
        key: Unique identifier (e.g., "login:192.168.1.1")
        limit: Maximum number of requests
        window: Time window in seconds
    
    Returns:
        True if within limit, False if exceeded
    """
    redis = await get_redis()
    current = int(time.time())
    window_start = current - window
    
    # Remove old entries
    await redis.zremrangebyscore(key, 0, window_start)
    
    # Count current requests
    request_count = await redis.zcard(key)
    
    if request_count >= limit:
        return False
    
    # Add current request
    await redis.zadd(key, {str(current): current})
    await redis.expire(key, window)
    
    return True

async def rate_limit_dependency(
    key: str,
    limit: int,
    window: int
):
    """FastAPI dependency for rate limiting"""
    if not await check_rate_limit(key, limit, window):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {window} seconds."