"""Authentication schemas"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

# User schemas
class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

# Token schemas
class Token(BaseModel):
    """OAuth2 token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str

# Login history schemas
class LoginHistoryResponse(BaseModel):
    """Login history entry"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool
    timestamp: datetime

# Activity schemas
class UserActivityResponse(BaseModel):
    """User activity entry"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    action: str
    details: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime
