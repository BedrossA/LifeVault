from fastapi import APIRouter, status
from datetime import datetime, UTC
from app.db.base import engine
from app.db.mongodb import mongodb
from app.db.redis import redis_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check"""
    health = {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "services": {}
    }
    
    # Check PostgreSQL
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health["services"]["postgresql"] = "healthy"
    except Exception as e:
        health["services"]["postgresql"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check MongoDB
    try:
        await mongodb.client.admin.command('ping')
        health["services"]["mongodb"] = "healthy"
    except Exception as e:
        health["services"]["mongodb"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check Redis
    try:
        await redis_db.client.ping()
        health["services"]["redis"] = "healthy"
    except Exception as e:
        health["services"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    status_code = status.HTTP_200_OK if health["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return health, status_code