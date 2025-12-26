"""Token schemas"""
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """Access and refresh token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Data encoded in JWT token"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None

class TokenRefresh(BaseModel):
    """Request to refresh access token"""
    refresh_token: str
