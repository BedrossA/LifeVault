"""Activity logging models"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from datetime import datetime, UTC
from app.db.base import Base

class ActivityLog(Base):
    """Activity log model for tracking user activities"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)  # e.g., 'login', 'face_enroll', 'analytics_create', etc.
    activity_name = Column(String, nullable=False)  # Human-readable name
    description = Column(Text, nullable=True)
    activity_metadata = Column(JSON, nullable=True)  # Additional data
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    
  
    
    def __repr__(self):
        return f"<ActivityLog {self.id} user_id={self.user_id} type={self.activity_type}>"

