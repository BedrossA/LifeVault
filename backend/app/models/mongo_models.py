"""MongoDB document schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class LoginHistory(BaseModel):
    """User login history"""
    user_id: int
    username: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str
    user_agent: str
    success: bool
    failure_reason: Optional[str] = None

class ActivityLog(BaseModel):
    """User activity log"""
    user_id: int
    action: str
    resource: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str
    metadata: Optional[Dict[str, Any]] = None
