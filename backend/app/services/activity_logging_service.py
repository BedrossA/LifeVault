"""Activity logging service"""
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from typing import Optional, Dict, Any
import logging
from app.models.user import UserActivity
from app.models.activity_log import ActivityLog

logger = logging.getLogger(__name__)

class ActivityLoggingService:
    """Service for logging user activities"""
    
    @staticmethod
    def log_activity(
        db: Session,
        user_id: int,
        activity_type: str,
        activity_name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserActivity:
        """
        Log a user activity
        
        Args:
            db: Database session
            user_id: User ID
            activity_type: Type of activity (e.g., 'login', 'face_enroll', 'analytics_create')
            activity_name: Human-readable activity name
            description: Optional description
            metadata: Optional metadata dictionary
            ip_address: Optional IP address
            user_agent: Optional user agent string
            
        Returns:
            Created UserActivity record
        """
        try:
            activity = UserActivity(
                user_id=user_id,
                action=activity_type,
                details=description or "",
                ip_address=ip_address
            )
            
            db.add(activity)
            db.commit()
            db.refresh(activity)
            
            return activity
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def get_user_activities(
        db: Session,
        user_id: int,
        limit: int = 50,
        activity_type: Optional[str] = None
    ) -> list[UserActivity]:
        """
        Get user activities
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of activities to return
            activity_type: Optional filter by activity type
            
        Returns:
            List of UserActivity records
        """
        try:
            query = db.query(UserActivity).filter(UserActivity.user_id == user_id)
            
            if activity_type:
                query = query.filter(UserActivity.action == activity_type)
            
            return query.order_by(UserActivity.timestamp.desc()).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting user activities: {e}")
            return []
    
    @staticmethod
    def get_activity_stats(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get activity statistics
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with activity statistics
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now(UTC) - timedelta(days=days)
            
            activities = db.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.timestamp >= cutoff_date
            ).all()
            
            # Count by activity type
            activity_counts = {}
            for activity in activities:
                activity_type = activity.action
                activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
            
            return {
                'total_activities': len(activities),
                'activity_counts': activity_counts,
                'period_days': days,
                'most_common': max(activity_counts.items(), key=lambda x: x[1])[0] if activity_counts else None
            }
            
        except Exception as e:
            logger.error(f"Error getting activity stats: {e}")
            return {
                'total_activities': 0,
                'activity_counts': {},
                'period_days': days,
                'most_common': None
            }

