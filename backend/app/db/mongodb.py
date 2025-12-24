"""MongoDB connection and utilities"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    
mongodb = MongoDB()

async def connect_mongodb():
    """Connect to MongoDB"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        # Verify connection
        await mongodb.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.MONGODB_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongodb():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")

def get_mongodb():
    """Get MongoDB database"""
    if not mongodb.client:
        raise Exception("MongoDB not connected")
    return mongodb.client[settings.MONGODB_DB_NAME]

async def get_mongo_db():
    """Async dependency for MongoDB"""
    return get_mongodb()