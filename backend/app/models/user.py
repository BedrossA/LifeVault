"""Complete User models for PostgreSQL"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from datetime import datetime, UTC
from app.db.base import Base
import uuid

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Multi-user support
    family_id = Column(String, nullable=True, index=True)
    role = Column(String, default="member")
    
    # Security tracking
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    def __repr__(self):
        return f"<User {self.username}>"


class LoginHistory(Base):
    """Login history tracking"""
    __tablename__ = "login_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Login details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    success = Column(Boolean, default=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    def __repr__(self):
        return f"<LoginHistory user_id={self.user_id} success={self.success}>"


class UserActivity(Base):
    """User activity log"""
    __tablename__ = "user_activity"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity details
    action = Column(String, nullable=False)  # e.g., "face_enrolled", "analytics_created"
    details = Column(Text, nullable=True)  # Additional JSON or text details
    ip_address = Column(String, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    def __repr__(self):
        return f"<UserActivity user_id={self.user_id} action={self.action}>"
