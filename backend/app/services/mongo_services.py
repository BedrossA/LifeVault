from app.db.mongodb import get_mongo_db
from app.models.mongo_models import LoginHistory, ActivityLog
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MongoService:
    """Unified MongoDB service for all MongoDB operations"""
    
    @staticmethod
    async def log_login_attempt(
        user_id: int,
        username: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None
    ) -> bool:
        """
        Log login attempt to MongoDB
        
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            db = await get_mongo_db()
            
            login_data = LoginHistory(
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                failure_reason=failure_reason,
                timestamp=datetime.now(UTC)
            )
            
            await db.login_history.insert_one(login_data.model_dump())
            return True
            
        except Exception as e:
            logger.error(f"Error logging login attempt: {e}")
            return False
    
    @staticmethod
    async def get_login_history(
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user login history"""
        try:
            db = await get_mongo_db()
            
            cursor = db.login_history.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            logger.error(f"Error getting login history: {e}")
            return []
    
    @staticmethod
    async def log_activity(
        user_id: int,
        action: str,
        resource: str,
        ip_address: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log user activity
        
        Returns:
            bool: True if logged successfully
        """
        try:
            db = await get_mongo_db()
            
            activity = ActivityLog(
                user_id=user_id,
                action=action,
                resource=resource,
                ip_address=ip_address,
                metadata=metadata or {},
                timestamp=datetime.now(UTC)
            )
            
            await db.activity_logs.insert_one(activity.model_dump())
            return True
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False
    
    @staticmethod
    async def get_user_activities(
        user_id: int,
        limit: int = 20,
        activity_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user activities with optional type filter"""
        try:
            db = await get_mongo_db()
            
            query = {"user_id": user_id}
            if activity_type:
                query["action"] = activity_type
            
            cursor = db.activity_logs.find(query).sort("timestamp", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            logger.error(f"Error getting activities: {e}")
            return []
    
    @staticmethod
    async def get_activity_stats(
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get activity statistics for user"""
        try:
            from datetime import timedelta
            db = await get_mongo_db()
            
            cutoff_date = datetime.now(UTC) - timedelta(days=days)
            
            activities = await db.activity_logs.find({
                "user_id": user_id,
                "timestamp": {"$gte": cutoff_date}
            }).to_list(length=10000)
            
            # Calculate stats
            activity_counts = {}
            for activity in activities:
                action = activity.get('action', 'unknown')
                activity_counts[action] = activity_counts.get(action, 0) + 1
            
            most_common = max(activity_counts.items(), key=lambda x: x[1])[0] if activity_counts else None
            
            return {
                'total_activities': len(activities),
                'activity_counts': activity_counts,
                'period_days': days,
                'most_common': most_common
            }
            
        except Exception as e:
            logger.error(f"Error getting activity stats: {e}")
            return {
                'total_activities': 0,
                'activity_counts': {},
                'period_days': days,
                'most_common': None
            }