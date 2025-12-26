"""Redis-based rate limiting"""
from app.db.redis import get_redis
import time

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