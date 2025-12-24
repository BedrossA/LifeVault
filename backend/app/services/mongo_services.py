"""MongoDB operations service"""
from app.db.mongodb import get_mongo_db
from app.models.mongo_models import LoginHistory, ActivityLog
from datetime import datetime
from typing import List, Optional

class MongoService:
    
    @staticmethod
    async def log_login_attempt(
        user_id: int,
        username: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None
    ):
        """Log login attempt to MongoDB"""
        db = await get_mongo_db()
        
        login_data = LoginHistory(
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        
        await db.login_history.insert_one(login_data.dict())
    
    @staticmethod
    async def get_login_history(
        user_id: int,
        limit: int = 10
    ) -> List[dict]:
        """Get user login history"""
        db = await get_mongo_db()
        
        cursor = db.login_history.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    @staticmethod
    async def log_activity(
        user_id: int,
        action: str,
        resource: str,
        ip_address: str,
        metadata: Optional[dict] = None
    ):
        """Log user activity"""
        db = await get_mongo_db()
        
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            metadata=metadata or {}
        )
        
        await db.activity_logs.insert_one(activity.dict())
    
    @staticmethod
    async def get_user_activities(
        user_id: int,
        limit: int = 20
    ) -> List[dict]:
        """Get user activities"""
        db = await get_mongo_db()
        
        cursor = db.activity_logs.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)