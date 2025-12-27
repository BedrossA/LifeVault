"""FastAPI dependencies"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User
from app.core.security import decode_token
from app.core.rate_limiter import check_rate_limit
from app.core.config import settings

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                           db: Session = Depends(get_db)) -> User:
    try:
        # 1. Print the token to ensure it's actually arriving
        print(f"DEBUG: Token: {credentials.credentials}") 
        
        payload = decode_token(credentials.credentials)
        print(f"DEBUG: Decoded payload = {payload}")
        
        if not payload:
            # This means decode_token returned None (likely a JWTError)
            raise HTTPException(status_code=401, detail="Token decode failed")

        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Not an access token")

        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        return user
    except Exception as e:
        # This will show you if it's a ValueError, AttributeError, etc.
        print(f"DEBUG: Decode Error = {str(e)}")
        raise HTTPException(status_code=401, detail="Token invalid")

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user

async def rate_limit_login(request: Request):
    key = f"login:{request.client.host}"
    if not await check_rate_limit(key, settings.RATE_LIMIT_LOGIN, settings.RATE_LIMIT_WINDOW):
        raise HTTPException(status_code=429, detail="Too many login attempts")
