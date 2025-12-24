"""Redis connection and utilities"""
import redis.asyncio as redis
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisDB:
    pool: Optional[redis.ConnectionPool] = None
    client: Optional[redis.Redis] = None

redis_db = RedisDB()

async def connect_redis():
    """Connect to Redis"""
    try:
        redis_db.pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True
        )
        redis_db.client = redis.Redis(connection_pool=redis_db.pool)
        
        # Test connection
        await redis_db.client.ping()
        logger.info(f"Connected to Redis: {settings.REDIS_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

async def close_redis():
    """Close Redis connection"""
    if redis_db.client:
        await redis_db.client.close()
        logger.info("Redis connection closed")

async def get_redis():
    """Get Redis client"""
    if not redis_db.client:
        raise Exception("Redis not connected")
    return redis_db.client