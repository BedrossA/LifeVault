"""MongoDB document schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class LoginHistory(BaseModel):
    """User login history stored in MongoDB"""
    user_id: int
    username: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str
    user_agent: str
    success: bool
    failure_reason: Optional[str] = None
    location: Optional[Dict[str, Any]] = None

class ActivityLog(BaseModel):
    """User activity log"""
    user_id: int
    action: str
    resource: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str
    metadata: Optional[Dict[str, Any]] = None

class SessionCache(BaseModel):
    """Session data for Redis caching"""
    session_id: str
    user_id: int
    username: str
    created_at: datetime
    expires_at: datetime
    ip_address: str