"""FastAPI dependencies"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  # ← ADD THIS
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User
from app.core import security
from app.core.config import settings

# OAuth2 scheme for token extraction
# This creates the "Authorize" button in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")  # ← ADD THIS


def get_current_user(
    token: str = Depends(oauth2_scheme),  # ← CHANGED from Header
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token
    Uses OAuth2PasswordBearer for automatic token extraction
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = security.decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (not disabled)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
